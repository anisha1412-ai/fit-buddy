"""
Shared Gemini helper with model fallback.

Free-tier API keys have a small per-model daily quota. Each model setting in
.env may therefore list several models, comma-separated, e.g.

    GEMINI_PRO_MODEL=gemini-3.7-flash,gemini-3.6-flash,gemini-3.5-flash

If a model is out of quota (429) or retired (404), the next one is tried.
"""

import os

import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core.exceptions import NotFound, ResourceExhausted

load_dotenv()

# Configure the Gemini SDK once with the API key from .env
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)


def model_list(env_var: str, default: str) -> list:
    """Read a comma-separated list of model names from an env variable."""
    names = os.getenv(env_var, default)
    return [name.strip() for name in names.split(",") if name.strip()]


def generate_with_fallback(model_names: list, prompt: str) -> str:
    """
    Send the prompt to each model in turn until one succeeds.

    Raises:
        RuntimeError: if the API key is missing or every model failed.
    """
    if not API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not set. Add it to your .env file and restart the server.")

    failures = []
    for name in model_names:
        try:
            response = genai.GenerativeModel(name).generate_content(prompt)
            return response.text
        except ResourceExhausted:
            failures.append(f"{name}: quota exceeded")
        except NotFound:
            failures.append(f"{name}: model not available")

    raise RuntimeError(
        "All Gemini models are unavailable right now (" + "; ".join(failures) + "). "
        "Free-tier quotas reset daily - try again later or add more models in .env."
    )
