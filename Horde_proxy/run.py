import subprocess
import os
import time
import re
import logging
from pyngrok import ngrok
from config import HOST, PORT, TUNNEL_PROVIDER, NGROK_AUTH_TOKEN, NGROK_STATIC_DOMAIN, CLOUDFLARED_TUNNEL_TOKEN, CLOUDFLARED_STATIC_DOMAIN, FLASK_LOG_FILE, TUNNEL_LOG_FILE, COMBINED_LOG_FILE

def start_tunnel():
    if TUNNEL_PROVIDER == 'ngrok':
        print("Starting ngrok tunnel with pyngrok...")
        ngrok.kill() # Ensure any running ngrok processes are killed and binary removed
        
        # Configure pyngrok logging to file
        import logging
        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), TUNNEL_LOG_FILE)
        logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode='a',
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        if NGROK_AUTH_TOKEN:
            ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        
        try:
            public_url = ngrok.connect(addr=PORT, bind_tls=True, domain=NGROK_STATIC_DOMAIN).public_url
            print(f"ngrok tunnel URL: {public_url}")
            # pyngrok manages the process internally, so we return a dummy object
            # that can be terminated later.
            class NgrokProcess:
                def terminate(self):
                    ngrok.kill()
                def wait(self):
                    pass # pyngrok manages its own process lifecycle
            return NgrokProcess(), None # Return None for log file handle
        except Exception as e:
            print(f"Error starting ngrok tunnel: {e}")
            return None, None # Return None for both process and log file handle
    elif TUNNEL_PROVIDER == 'cloudflared':
        print("Starting cloudflared tunnel...")
        tunnel_log_file_handle = open(TUNNEL_LOG_FILE, 'a')
        command = ['cloudflared', 'tunnel']
        if CLOUDFLARED_TUNNEL_TOKEN:
            command.extend(['--token', CLOUDFLARED_TUNNEL_TOKEN])
        command.extend(['--url', f'http://{HOST}:{PORT}'])
        
        # Run cloudflared in a separate process, capture stdout/stderr
        cloudflared_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        print(f"cloudflared started. Logs are being written to {TUNNEL_LOG_FILE}. Waiting for URL...")
        url = None
        for line in iter(cloudflared_process.stdout.readline, ''):
            tunnel_log_file_handle.write(line) # Write to log file
            if "Your quick Tunnel has been created! Visit it at" in line:
                # The URL is on the next line
                next_line = cloudflared_process.stdout.readline()
                match = re.search(r'https?://[^\s]+', next_line)
                if match:
                    url = match.group(0)
                    # Remove trailing characters like ')' if present
                    if url.endswith(')'):
                        url = url[:-1]
                    print(f"cloudflared tunnel URL: {url}")
                    break
        if not url:
            print("Could not find cloudflared tunnel URL in output.")
        return cloudflared_process, tunnel_log_file_handle
    else:
        print("No tunnel provider configured.")
        return None

def start_flask_app():
    print(f"Starting Flask app on http://{HOST}:{PORT}...")
    flask_log_file_handle = open(FLASK_LOG_FILE, 'a')
    # Use a simple subprocess.run for now, can be improved for better process management
    flask_process = subprocess.Popen(['python', 'app.py'], cwd=os.path.dirname(os.path.abspath(__file__)), stdout=flask_log_file_handle, stderr=flask_log_file_handle)
    print(f"Flask app started. Logs are being written to {FLASK_LOG_FILE}")
    return flask_process, flask_log_file_handle

if __name__ == '__main__':
    tunnel_process = None
    flask_process = None
    flask_log_file_handle = None
    tunnel_log_file_handle = None
    try:
        flask_process, flask_log_file_handle = start_flask_app()
        time.sleep(5) # Give Flask app some time to start
        tunnel_process, tunnel_log_file_handle = start_tunnel()

        # Keep the script running until processes are terminated
        if flask_process:
            flask_process.wait()
        if tunnel_process:
            tunnel_process.wait()

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        if tunnel_process:
            print("Terminating tunnel process...")
            tunnel_process.terminate()
            tunnel_process.wait()
        if tunnel_log_file_handle:
            tunnel_log_file_handle.close()
        if flask_process:
            print("Terminating Flask process...")
            flask_process.terminate()
            flask_process.wait()
        if flask_log_file_handle:
            flask_log_file_handle.close()
        print("Shutdown complete.")
