import requests
import math
from collections import defaultdict

# ── Payload factories ────────────────────────────────────────────────────────

json_data = {
    "gpt-5-pro": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "gpt-5-pro",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },

    "gpt-5": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "gpt-5",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },
    "gpt-5-mini": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "gpt-5-mini",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },
    # OpenAI
    "gpt-4o-mini": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },
    "gpt-4o": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },
    "gpt-4.1": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "gpt-4.1",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },
    "gpt-4.1-mini": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "gpt-4.1-mini",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },
    "o1": lambda text, max_tokens=2000, **_: {
        "model": "o1",
        "messages": [{"role": "user", "content": text}],
        "max_completion_tokens": max_tokens,
    },
    "o3-mini": lambda text, max_tokens=2000, **_: {
        "model": "o3-mini",
        "messages": [{"role": "user", "content": text}],
        "max_completion_tokens": max_tokens,
    },
    "gpt-4o-mini-logprobs": lambda text, **_: {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": text}],
        "max_tokens": 1,
        "logprobs": True,
        "top_logprobs": 10,
    },
    # Anthropic
    "claude-3-5-haiku": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "claude-3-5-haiku-20241022",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": text}],
    },
    "claude-sonnet-4": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": text}],
    },
    "claude-opus-4": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "claude-opus-4-20250514",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": text}],
    },
    # Google Gemini
    "gemini-2.0-flash": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "gemini-2.0-flash",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },
    "gemini-2.5-pro": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "gemini-2.5-pro-preview-05-06",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },
    # Meta via Together AI
    "llama-3.3-70b": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },
    "llama-3.1-8b": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },
    # Mistral
    "mistral-large": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "mistral-large-latest",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },
    "mistral-small": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },
    # DeepSeek
    "deepseek-chat": lambda text, temperature=1.0, max_tokens=2000: {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    },
    "deepseek-reasoner": lambda text, max_tokens=2000, **_: {
        "model": "deepseek-reasoner",
        "messages": [{"role": "user", "content": text}],
        "max_tokens": max_tokens,
    },
}

# ── Routing ──────────────────────────────────────────────────────────────────

OPENAI_URL    = "https://api.openai.com/v1/chat/completions"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
GEMINI_URL    = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
TOGETHER_URL  = "https://api.together.xyz/v1/chat/completions"
MISTRAL_URL   = "https://api.mistral.ai/v1/chat/completions"
DEEPSEEK_URL  = "https://api.deepseek.com/chat/completions"

MODEL_URLS = {
    "gpt-5-pro": OPENAI_URL,
    "gpt-5":      OPENAI_URL,
    "gpt-5-mini": OPENAI_URL,
    "gpt-4o-mini":          OPENAI_URL,
    "gpt-4o":               OPENAI_URL,
    "gpt-4.1":              OPENAI_URL,
    "gpt-4.1-mini":         OPENAI_URL,
    "o1":                   OPENAI_URL,
    "o3-mini":              OPENAI_URL,
    "gpt-4o-mini-logprobs": OPENAI_URL,
    "claude-3-5-haiku":     ANTHROPIC_URL,
    "claude-sonnet-4":      ANTHROPIC_URL,
    "claude-opus-4":        ANTHROPIC_URL,
    "gemini-2.0-flash":     GEMINI_URL,
    "gemini-2.5-pro":       GEMINI_URL,
    "llama-3.3-70b":        TOGETHER_URL,
    "llama-3.1-8b":         TOGETHER_URL,
    "mistral-large":        MISTRAL_URL,
    "mistral-small":        MISTRAL_URL,
    "deepseek-chat":        DEEPSEEK_URL,
    "deepseek-reasoner":    DEEPSEEK_URL,
}

# Anthropic requires different headers and response parsing
ANTHROPIC_MODELS = {"claude-3-5-haiku", "claude-sonnet-4", "claude-opus-4"}

# ── Core caller ──────────────────────────────────────────────────────────────

def call_model(model_key, api_key, **kwargs):
    if model_key not in json_data:
        raise ValueError(f"Unknown model key: {model_key}. Available: {list(json_data)}")

    url     = MODEL_URLS[model_key]
    payload = json_data[model_key](**kwargs)

    is_anthropic = model_key in ANTHROPIC_MODELS
    headers = {"Content-Type": "application/json"}
    if is_anthropic:
        headers["x-api-key"]         = api_key
        headers["anthropic-version"] = "2023-06-01"
    else:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError("Request timed out")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text}") from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request failed: {e}") from e

    return response.json()

# ── Public API ───────────────────────────────────────────────────────────────

def chat(text, model="gpt-4o-mini", api_key="", temperature=1.0, max_tokens=2000):
    data = call_model(model, api_key, text=text, temperature=temperature, max_tokens=max_tokens)
    if model in ANTHROPIC_MODELS:
        return data["content"][0]["text"]
    return data["choices"][0]["message"]["content"]


def next_token_p(text, api_key=""):
    data    = call_model("gpt-4o-mini-logprobs", api_key, text=text)
    entries = data["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
    result  = defaultdict(float)
    for entry in entries:
        result[entry["token"]] = math.exp(entry["logprob"])
    return result

# ── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    API_KEYS = {
        "openai":    "your-openai-key",
        "anthropic": "your-anthropic-key",
        "gemini":    "your-gemini-key",
        "together":  "your-together-key",
        "mistral":   "your-mistral-key",
        "deepseek":  "your-deepseek-key",
    }

    PROVIDER_KEY = {
        "gpt-5-pro": "openai",
        "gpt-5":      "openai",
        "gpt-5-mini": "openai",
        "gpt-4o-mini":       "openai",
        "gpt-4o":            "openai",
        "gpt-4.1":           "openai",
        "gpt-4.1-mini":      "openai",
        "o1":                "openai",
        "o3-mini":           "openai",
        "claude-3-5-haiku":  "anthropic",
        "claude-sonnet-4":   "anthropic",
        "claude-opus-4":     "anthropic",
        "gemini-2.0-flash":  "gemini",
        "gemini-2.5-pro":    "gemini",
        "llama-3.3-70b":     "together",
        "llama-3.1-8b":      "together",
        "mistral-large":     "mistral",
        "mistral-small":     "mistral",
        "deepseek-chat":     "deepseek",
        "deepseek-reasoner": "deepseek",
    }

    prompt = "Name one planet in one word."

    for model_key, provider in PROVIDER_KEY.items():
        key = API_KEYS[provider]
        try:
            reply = chat(prompt, model=model_key, api_key=key)
            print(f"[{model_key:30s}] {reply.strip()}")
        except Exception as e:
            print(f"[{model_key:30s}] ERROR: {e}")
