# Gemini Task: Kobold Horde Proxy

This document outlines the plan for creating a proxy for the Kobold Horde. The goal is to create a simple, efficient, and reliable proxy that can be used to interact with the Kobold Horde API.

## Key Features

*   **Request Forwarding:** Forward requests from a local client to the Kobold Horde API.
*   **Authentication:** Handle API key authentication for the Kobold Horde.
*   **Request/Response Logging:** Log requests and responses for debugging and monitoring.
*   **Error Handling:** Provide clear error messages for failed requests.
*   **Configuration:** Allow for easy configuration of the proxy (e.g., API key, Horde URL).

## Technology Stack

*   **Language:** Python
*   **Framework:** Flask (or a similar lightweight framework)
*   **Libraries:**
    *   `requests`: For making HTTP requests to the Kobold Horde API.

## Development Steps

1.  **Project Setup:**
    *   Create a project directory.
    *   Set up a virtual environment.
    *   Install necessary libraries (`Flask`, `requests`).
2.  **Basic Proxy Server:**
    *   Create a basic Flask application.
    *   Implement a route that accepts POST requests.
    *   Forward the request to a hardcoded Kobold Horde endpoint.
    .
3.  **Authentication:**
    *   Add a mechanism to store and use a Kobold Horde API key.
    *   Include the API key in the headers of the forwarded request.
4.  **Request/Response Logging:**
    *   Log the incoming request details (e.g., method, path, headers, body).
    *   Log the outgoing request details.
    *   Log the response from the Kobold Horde.
5.  **Error Handling:**
    *   Handle connection errors to the Kobold Horde.
    *   Handle non-200 responses from the Kobold Horde.
    *   Return appropriate error messages to the client.
6.  **Configuration:**
    *   Create a configuration file (e.g., `config.py` or `config.ini`).
    *   Load settings like the API key and Horde URL from the configuration file.
7.  **Refinement and Testing:**
    *   Refactor the code for clarity and efficiency.
    *   Add unit tests to verify the proxy's functionality.
    *   Write a README with instructions on how to set up and run the proxy.

---

## Work Performed by Gemini (August 15, 2025)

This section summarizes the work performed by Gemini during the development of this AI Proxy project.

*   **Project Setup:** Rebuilt the project from scratch in the `Horde_proxy` directory, including `app.py`, `config.py`, `run.py`, and `requirements.txt`.
*   **AI Proxy Core Logic:** Implemented a Flask-based proxy to translate OpenAI Chat Completions API requests to AI Horde asynchronous text generation API requests.
*   **Tunneling Integration:** Integrated `ngrok` and `cloudflared` for exposing the local proxy, including robust URL extraction.
*   **CORS Support:** Enabled CORS for the Flask application.
*   **AI Horde API Interaction:**
    *   Handled asynchronous generation (initiate, poll, retrieve).
    *   Implemented OpenAI to AI Horde request transformation.
    *   Implemented AI Horde to OpenAI response transformation.
    *   Debugged and resolved `400 Bad Request` errors (prompt length, parameter simplification).
    *   Debugged and resolved `403 Forbidden` errors (API key, kudos, `dry_run` testing).
    *   Debugged and resolved `500 Internal Server Error` related to model fetching.
*   **Model Selection Flexibility:** Added support for "random" model selection (fetching available models from Horde) and "list" (using a predefined list from `config.py`).
*   **Logging:** Implemented detailed logging for Flask and tunnel operations to separate files.
*   **Configuration:** Centralized AI Horde parameters in `horde_params.py`.
*   **Documentation:** Created `README.md` with setup, usage, and troubleshooting.
*   **Credits:** Created `credits.md`.
*   **Resolved Janitor AI Issues:** Identified and resolved Janitor AI's "No response from bot" error by confirming the need to disable text streaming in Janitor AI.