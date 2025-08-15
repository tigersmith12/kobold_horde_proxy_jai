# Configuration for the AI Proxy

# Flask app settings
HOST = "127.0.0.1"
PORT = 5000

# Tunneling settings
# Set to 'ngrok' or 'cloudflared' to enable tunneling, or None to disable
#TUNNEL_PROVIDER = 'ngrok' # or 'cloudflared' or None
TUNNEL_PROVIDER = 'cloudflared'

# ngrok specific settings
NGROK_AUTH_TOKEN = "YOUR_NGROK_AUTH_TOKEN" # Get from ngrok dashboard

#NGROK_STATIC_DOMAIN = "YOUR_STATIC_NGROK_DOMAIN" # Optional: Your static ngrok domain if you have one

NGROK_STATIC_DOMAIN = None # Optional: random domain

# Cloudflared specific settings
CLOUDFLARED_TUNNEL_TOKEN = None # Optional: Your Cloudflare Tunnel token if using a named tunnel
CLOUDFLARED_STATIC_DOMAIN = None # Optional: Your static Cloudflare domain if you have one

# Log file settings
FLASK_LOG_FILE = 'flask_proxy.log'
TUNNEL_LOG_FILE = 'tunnel.log'
COMBINED_LOG_FILE = 'combined.log'

# AI Horde settings
MAX_PROMPT_LENGTH = 2048 # Max characters for the prompt sent to AI Horde

# Predefined list of models for "list" special model name
# Example: PREDEFINED_MODEL_LIST = ["koboldcpp/MythoMax L2 13B", "koboldcpp/Llama-2-70B-GGJTv3-q4_1"]
PREDEFINED_MODEL_LIST = [] # Populate this list with your desired model names
