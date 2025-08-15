# Default parameters for AI Horde text generation requests
# These can be overridden by parameters in the OpenAI request if mapped.

DEFAULT_HORDE_PARAMS = {
    "n": 1, # Number of generations to produce
    "max_length": 500, # Max tokens to generate
    # "temperature": 0.7,
    # "top_p": 0.9,
    # "top_k": 50,
    # "sampler_order": ["temperature", "top_k", "top_p"],
    # "stop_sequence": [],
    # "tfs": 1,
    # "typical": 1,
    # "repetition_penalty": 1.1,
    # "do_sample": True,
    # "return_type": "text",
    # "seed": None,
    # Add other common parameters as needed
    # "cfg_scale": 1.0,
    # "min_length": 0,
    # "max_new_tokens": None,
    # "truncation_length": 2048,
    # "bad_words_ids": [],
    # "force_words_ids": [],
    # "guidance_scale": 1,
    # "negative_prompt": "",
}

# Other AI Horde specific settings
HORDE_SETTINGS = {
    # "shared_key": "", # Optional: Your shared key if you have one
    # "trusted_workers": True,
    # "slow_workers": False,
    # "r_rated": False,
    # "nsfw": False,
    # "censor_nsfw": False,
    # "dry_run": False, # Set to True for testing request validity without actual generation
    # "priority": 0,
}
