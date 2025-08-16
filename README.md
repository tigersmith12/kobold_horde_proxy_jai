# AI Proxy for Janitor AI and Kobold Horde

This project provides a Python-based proxy server that allows you to connect Janitor AI (or any OpenAI-compatible client) to the Kobold Horde (AI Horde) for text generation. It handles the translation between the OpenAI Chat Completions API and the AI Horde's asynchronous text generation API.

## Features

*   **OpenAI API Compatibility:** Exposes an endpoint compatible with OpenAI's Chat Completions API (`/v1/chat/completions`).
*   **Kobold Horde Integration:** Forwards requests to the AI Horde's text generation API (`/api/v2/generate/text/async`).
*   **Asynchronous Generation Handling:** Manages the asynchronous request-response cycle with the AI Horde (initiate, poll for status, retrieve result).
*   **CORS Enabled:** Allows requests from different origins (e.g., Janitor AI web client).
*   **Flexible Model Selection:**
    *   Use specific AI Horde model names.
    *   Use `"random"` to automatically select from available text models on the Horde.
    *   Use `"list"` to use a predefined list of models from `config.py`.
*   **Tunneling Support:** Integrates with `ngrok` and `cloudflared` to expose your local proxy to the internet.
*   **Configurable:** Key settings (host, port, API tokens, model lists) are managed in `config.py`.
*   **Logging:** Detailed logs for Flask proxy and tunnel operations are written to separate files.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd Horde_proxy
    ```

2.  **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Cloudflared (if using):**
    If you plan to use `cloudflared` for tunneling, you need to install the binary.
    For Linux (Debian/Ubuntu):
    ```bash
    sudo apt update
    sudo apt install cloudflared
    ```
    For other operating systems, please refer to the official Cloudflare Tunnel documentation: [https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)

5.  **Configure `config.py`:**
    Open `config.py` and update the following settings:

    *   **`HOST` / `PORT`:** (Optional) Change if you want the Flask app to run on a different host or port.
    *   **`TUNNEL_PROVIDER`:** Set to `'ngrok'`, `'cloudflared'`, or `None` to disable tunneling.
    *   **`NGROK_AUTH_TOKEN`:** If using `ngrok`, get your auth token from the ngrok dashboard and replace `"YOUR_AUTH_TOKEN_HERE"`.
    *   **`NGROK_STATIC_DOMAIN`:** (Optional) If you have a paid ngrok plan and a static domain.
    *   **`CLOUDFLARED_TUNNEL_TOKEN`:** (Optional) If using a named Cloudflare Tunnel.
    *   **`CLOUDFLARED_STATIC_DOMAIN`:** (Optional) If you have a static Cloudflare domain.
    *   **`PREDEFINED_MODEL_LIST`:** If you plan to use `"list"` as your model name in Janitor AI, populate this list with specific AI Horde model names (e.g., `["koboldcpp/MythoMax L2 13B", "koboldcpp/Llama-2-70B-GGJTv3-q4_1"]`).

5.  **Configure `horde_params.py`:**
    Open `horde_params.py` to adjust default generation parameters for the AI Horde. You can modify `DEFAULT_HORDE_PARAMS` and `HORDE_SETTINGS` as needed.

6.  **Set `dry_run` to `False` in `app.py`:**
    For actual usage, ensure the `dry_run` flag is set to `False`.
    Find the line:
    ```python
    "dry_run": True, # Keep dry_run for testing
    ```
    Change it to:
    ```python
    "dry_run": False,
    ```

## How to Run

After completing the setup:

```bash
python run.py
```

This will start the Flask proxy server and your chosen tunneling service (ngrok or cloudflared). The tunnel URL will be printed to your console.

## Usage with Janitor AI

1.  **Get the Proxy URL:**
    When `python run.py` is running, note the `ngrok tunnel URL:` or `cloudflared tunnel URL:` printed in your console. It will look something like `https://your-subdomain.ngrok-free.app` or `https://your-subdomain.trycloudflare.com`.

2.  **Configure Janitor AI:**
    In Janitor AI's settings (usually under "API Settings", "Model Settings", or "Connection Settings"), change the API endpoint (or "Base URL") to the proxy URL you obtained (e.g., `https://your-subdomain.ngrok-free.app/v1/chat/completions`).

3.  **Select Model in Janitor AI:**
    *   **Specific Model:** Enter the exact name of an AI Horde text model (e.g., `TheDrummer/Valkyrie-49B-v1`). You can find available models on `https://aihorde.net/`.
    *   **Random Model:** Enter `"random"` as the model name. The proxy will automatically select an available text model from the Horde.
    *   **Predefined List:** Enter `"list"` as the model name. The proxy will use the models defined in `PREDEFINED_MODEL_LIST` in your `config.py`.

4.  **API Key:**
    Enter your AI Horde API key into Janitor AI's API key field. The proxy will forward this key to the AI Horde.

5.  **Disable Text Streaming in Janitor AI:**
    If Janitor AI has a "text streaming" or "stream response" option, ensure it is **disabled**. The proxy currently sends a complete response after generation, not a streaming one.

## Troubleshooting

*   **`400 Client Error: Bad Request` from Horde:**
    *   Ensure your prompt is not excessively long. The proxy truncates it, but very long initial prompts can still cause issues.
    *   Verify the model name is correct and available.
*   **`401 Client Error: Unauthorized` from Horde:**
    *   Your AI Horde API key is incorrect or invalid. Double-check it on `https://aihorde.net/`.
*   **`403 Client Error: Forbidden` from Horde:**
    *   This often indicates insufficient kudos, API key permissions issues, or IP-based blocking (e.g., ngrok/cloudflared IP ranges might be restricted).
    *   Ensure your AI Horde account has enough kudos.
    *   If using a personal API key, contact AI Horde support if the issue persists.
*   **`PROXY ERROR: No response from bot` from Janitor AI:**
    *   This is usually a timeout on Janitor AI's side. Check Janitor AI's settings for configurable timeouts and increase them.
    *   Ensure text streaming is disabled in Janitor AI.
*   **Proxy stuck at "Waiting for URL..." (ngrok/cloudflared):**
    *   Ensure the Flask app is running on the correct host/port.
    *   Check your ngrok/cloudflared setup and authentication.
    *   For Cloudflared, ensure the `cloudflared` binary is correctly installed and accessible.

## Contributing

Feel free to fork this repository and contribute!
