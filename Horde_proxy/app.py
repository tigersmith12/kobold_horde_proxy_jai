from flask import Flask, request, jsonify, make_response
import requests
import os
import time
import logging # Import logging module
from config import HOST, PORT, MAX_PROMPT_LENGTH, PREDEFINED_MODEL_LIST
from flask_cors import CORS
from horde_params import DEFAULT_HORDE_PARAMS, HORDE_SETTINGS

SPECIAL_MODEL_NAMES = ["random", "any_text_model", "list"] # Keywords for selecting multiple models

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG) # Set logger level to DEBUG

CORS(app)

# Placeholder for Kobold Horde API base URL
KOBOLD_HORDE_API_BASE_URL = "https://aihorde.net/api/v2"

def get_available_models():
    try:
        models_response = requests.get(f"{KOBOLD_HORDE_API_BASE_URL}/stats/text/models")
        models_response.raise_for_status()
        all_models = models_response.json()
        
        # This endpoint returns a dictionary of dictionaries, e.g., {'day': {'model_name': count}}
        text_models = []
        for time_of_day_models in all_models.values():
            for model_name, count in time_of_day_models.items():
                if count > 0: # Only include models with active workers
                    text_models.append(model_name)
        app.logger.debug(f"Available text models from Horde: {text_models}")
        return text_models[:10] # Limit to top 10 models for now
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Failed to fetch models from Horde: {e}")
        return []

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions_proxy():
    api_key = request.headers.get('Authorization')
    if api_key and api_key.startswith('Bearer '):
        api_key = api_key.split(' ')[1] # Extract the actual token
    else:
        return jsonify({"error": "Authentication required"}), 401

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    openai_request = request.get_json()
    model_name = openai_request.get('model')
    messages = openai_request.get('messages')

    if not model_name or not messages:
        return jsonify({"error": "Missing 'model' or 'messages' in request body"}), 400

    target_models = []
    if model_name == "random":
        app.logger.info(f"Special model name '{model_name}' detected. Fetching available models from Horde.")
        target_models = get_available_models()
        if not target_models:
            return jsonify({"error": "No available text models found on Horde."}), 503
    elif model_name == "list":
        app.logger.info(f"Special model name '{model_name}' detected. Using predefined model list.")
        if not PREDEFINED_MODEL_LIST:
            return jsonify({"error": "PREDEFINED_MODEL_LIST is empty in config.py when 'list' model is used."}), 400
        target_models = PREDEFINED_MODEL_LIST
    else: # Default to single model
        target_models = [model_name]

    # Convert OpenAI messages to a single prompt string for Kobold Horde
    prompt_parts = []
    for message in messages:
        role = message.get('role')
        content = message.get('content')
        if role == 'system':
            prompt_parts.append(f"System: {content}")
        elif role == 'user':
            prompt_parts.append(f"User: {content}")
        elif role == 'assistant':
            prompt_parts.append(f"Assistant: {content}")
    prompt = " ".join(prompt_parts) # Join with spaces instead of newlines
    if len(prompt) > MAX_PROMPT_LENGTH:
        app.logger.warning(f"Prompt length ({len(prompt)}) exceeds MAX_PROMPT_LENGTH ({MAX_PROMPT_LENGTH}). Truncating prompt.")
        prompt = prompt[-MAX_PROMPT_LENGTH:] # Truncate from the end

    # Default parameters for Kobold Horde, can be mapped from OpenAI request if needed
    params = DEFAULT_HORDE_PARAMS.copy() # Start with default horde params
    params["max_length"] = openai_request.get('max_tokens', params.get("max_length", 500)) # Map max_tokens from OpenAI to max_length
    params["temperature"] = openai_request.get('temperature', params.get("temperature", 0.7))
    params["top_p"] = openai_request.get('top_p', params.get("top_p", 0.9))
    params["top_k"] = openai_request.get('top_k', params.get("top_k", 50))
    params["seed"] = openai_request.get('seed', params.get("seed"))
    # Ensure return_type is text for chat completions
    params["return_type"] = "text"
    
    # Construct Kobold Horde request
    horde_request_payload = {
        "prompt": prompt,
        "params": params,
        "models": target_models, # Use target_models here
        #"dry_run": True, # Keep dry_run for testing
    }
    app.logger.debug(f"Sending to Horde: {horde_request_payload}")

    # Send async request to Kobold Horde
    try:
        async_response = requests.post(f"{KOBOLD_HORDE_API_BASE_URL}/generate/text/async", 
                                       headers={'Content-Type': 'application/json', 'apikey': api_key, 'User-Agent': 'Mozilla/5.0'}, 
                                       json=horde_request_payload)
        async_response.raise_for_status()
        generation_id = async_response.json().get('id')
        if not generation_id:
            return jsonify({"error": "Failed to get generation ID from Horde"}), 500

        # Poll for status
        timeout = 120 # seconds (increased timeout)
        start_time = time.time()
        while time.time() - start_time < timeout:
            status_response = requests.get(f"{KOBOLD_HORDE_API_BASE_URL}/generate/text/status/{generation_id}",
                                           headers={'apikey': api_key})
            status_response.raise_for_status()
            status_data = status_response.json()

            if status_data.get('done'):
                generated_text = status_data['generations'][0]['text']
                app.logger.debug(f"Generated text from Horde: {generated_text}") # Debug log
                # Transform to OpenAI response format
                openai_response = {
                    "id": f"chatcmpl-{generation_id}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model_name,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": generated_text
                            },
                            "logprobs": None,
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": len(prompt.split()), # Simple token count
                        "completion_tokens": len(generated_text.split()),
                        "total_tokens": len(prompt.split()) + len(generated_text.split())
                    }
                }
                app.logger.debug(f"Sending response to Janitor AI: {openai_response}")
                return jsonify(openai_response)
            
            time.sleep(1) # Wait before polling again
        
        return jsonify({"error": "Generation timed out"}), 504

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Horde API request failed: {e}")
        return jsonify({"error": "Horde API request failed", "details": str(e)}), 500

# Generic proxy for other paths (if needed, otherwise remove)
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def generic_proxy(path):
    api_key = request.headers.get('Authorization')
    if api_key and api_key.startswith('Bearer '):
        api_key = api_key.split(' ')[1]
    
    headers = {key: value for key, value in request.headers if key.lower() not in ['host', 'content-length']}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'

    upstream_url = f"{KOBOLD_HORDE_API_BASE_URL}/{path}"

    try:
        if request.method == 'POST':
            resp = requests.post(upstream_url, headers=headers, data=request.get_data(), stream=True)
        elif request.method == 'GET':
            resp = requests.get(upstream_url, headers=headers, params=request.args, stream=True)
        elif request.method == 'PUT':
            resp = requests.put(upstream_url, headers=headers, data=request.get_data(), stream=True)
        elif request.method == 'DELETE':
            resp = requests.delete(upstream_url, headers=headers, stream=True)
        else:
            return jsonify({"error": "Method not allowed"}), 405

        response = make_response(resp.iter_content(chunk_size=8192))
        for key, value in resp.headers.items():
            if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding']:
                response.headers[key] = value
        response.status_code = resp.status_code
        return response

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Generic proxy request failed: {e}")
        return jsonify({"error": "Generic proxy request failed", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(HOST,PORT)
