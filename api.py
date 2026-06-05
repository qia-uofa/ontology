import requests
import math
from collections import defaultdict

# ── Endpoints ────────────────────────────────────────────────────────────────

OPENAI_URL           = "https://api.openai.com/v1/chat/completions"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
ANTHROPIC_URL        = "https://api.anthropic.com/v1/messages"
GEMINI_URL           = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
TOGETHER_URL         = "https://api.together.xyz/v1/chat/completions"
MISTRAL_URL          = "https://api.mistral.ai/v1/chat/completions"
DEEPSEEK_URL         = "https://api.deepseek.com/chat/completions"

# ── Model sets ────────────────────────────────────────────────────────────────

ANTHROPIC_MODELS = {"claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-7"}
RESPONSES_MODELS = {
    "gpt-5", "gpt-5.4-mini", "gpt-5.4-nano",
    "gpt-5.4", "gpt-5.4-pro", "gpt-5.5", "gpt-5.5-pro",
}

# ── Payload factories ─────────────────────────────────────────────────────────

def _oai(model):
    return lambda text, temperature=1.0, max_tokens=2000: {
        "model": model,
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

def _oai_responses(model):
    """OpenAI /v1/responses — used by all GPT-5+ models."""
    return lambda text, temperature=1.0, max_tokens=2000: {
        "model": model,
        "input": text,
        "temperature": temperature,
        "max_output_tokens": max_tokens,
    }

def _oai_reasoning(model):
    """Reasoning models: no temperature, max_completion_tokens."""
    return lambda text, max_tokens=2000, **_: {
        "model": model,
        "messages": [{"role": "user", "content": text}],
        "max_completion_tokens": max_tokens,
    }

def _anthropic(model):
    return lambda text, temperature=1.0, max_tokens=2000: {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": text}],
    }

def _compat(model):
    return lambda text, temperature=1.0, max_tokens=2000: {
        "model": model,
        "messages": [{"role": "user", "content": text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

json_data = {
    # ── OpenAI legacy chat/completions (still valid) ──
    "gpt-4o-mini":          _oai("gpt-4o-mini"),
    "gpt-4o":               _oai("gpt-4o"),
    "gpt-4.1":              _oai("gpt-4.1"),
    "gpt-4.1-mini":         _oai("gpt-4.1-mini"),
    "gpt-4.1-nano":         _oai("gpt-4.1-nano"),
    # ── OpenAI reasoning ──
    "o1":                   _oai_reasoning("o1"),
    "o3-mini":              _oai_reasoning("o3-mini"),
    "o3":                   _oai_reasoning("o3"),
    # ── OpenAI logprobs ──
    "gpt-4o-mini-logprobs": lambda text, **_: {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": text}],
        "max_tokens": 1,
        "logprobs": True,
        "top_logprobs": 10,
    },
    # ── GPT-5 family (/v1/responses) ──
    "gpt-5":                _oai_responses("gpt-5"),
    "gpt-5.4":              _oai_responses("gpt-5.4"),
    "gpt-5.4-pro":          _oai_responses("gpt-5.4-pro"),
    "gpt-5.4-mini":         _oai_responses("gpt-5.4-mini"),
    "gpt-5.4-nano":         _oai_responses("gpt-5.4-nano"),
    "gpt-5.5":              _oai_responses("gpt-5.5"),
    "gpt-5.5-pro":          _oai_responses("gpt-5.5-pro"),
    # ── Anthropic (updated strings — old 20250514 variants retired Apr 2026) ──
    "claude-haiku-4-5":     _anthropic("claude-haiku-4-5-20251001"),
    "claude-sonnet-4-6":    _anthropic("claude-sonnet-4-6"),
    "claude-opus-4-7":      _anthropic("claude-opus-4-7"),
    # ── Gemini (2.0-flash retiring Jun 1 2026; 2.5 stable until Oct 2026) ──
    "gemini-2.5-flash":     _compat("gemini-2.5-flash"),
    "gemini-2.5-pro":       _compat("gemini-2.5-pro"),
    "gemini-3-flash":       _compat("gemini-3-flash-preview"),
    "gemini-3-pro":         _compat("gemini-3-pro-preview"),
    # ── Meta via Together AI ──
    "llama-3.3-70b":        _compat("meta-llama/Llama-3.3-70B-Instruct-Turbo"),
    "llama-3.1-8b":         _compat("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"),
    # ── Mistral (updated strings) ──
    "mistral-large":        _compat("mistral-large-latest"),
    "mistral-medium":       _compat("mistral-medium-latest"),   # Medium 3.5, Apr 2026
    "mistral-small":        _compat("mistral-small-2603"),      # Small 4, Mar 2026
    # ── DeepSeek ──
    "deepseek-chat":        _compat("deepseek-chat"),
    "deepseek-reasoner":    _oai_reasoning("deepseek-reasoner"),
}

MODEL_URLS = {
    "gpt-4o-mini":          OPENAI_URL,
    "gpt-4o":               OPENAI_URL,
    "gpt-4.1":              OPENAI_URL,
    "gpt-4.1-mini":         OPENAI_URL,
    "gpt-4.1-nano":         OPENAI_URL,
    "o1":                   OPENAI_URL,
    "o3-mini":              OPENAI_URL,
    "o3":                   OPENAI_URL,
    "gpt-4o-mini-logprobs": OPENAI_URL,
    "gpt-5":                OPENAI_RESPONSES_URL,
    "gpt-5.4":              OPENAI_RESPONSES_URL,
    "gpt-5.4-pro":          OPENAI_RESPONSES_URL,
    "gpt-5.4-mini":         OPENAI_RESPONSES_URL,
    "gpt-5.4-nano":         OPENAI_RESPONSES_URL,
    "gpt-5.5":              OPENAI_RESPONSES_URL,
    "gpt-5.5-pro":          OPENAI_RESPONSES_URL,
    "claude-haiku-4-5":     ANTHROPIC_URL,
    "claude-sonnet-4-6":    ANTHROPIC_URL,
    "claude-opus-4-7":      ANTHROPIC_URL,
    "gemini-2.5-flash":     GEMINI_URL,
    "gemini-2.5-pro":       GEMINI_URL,
    "gemini-3-flash":       GEMINI_URL,
    "gemini-3-pro":         GEMINI_URL,
    "llama-3.3-70b":        TOGETHER_URL,
    "llama-3.1-8b":         TOGETHER_URL,
    "mistral-large":        MISTRAL_URL,
    "mistral-medium":       MISTRAL_URL,
    "mistral-small":        MISTRAL_URL,
    "deepseek-chat":        DEEPSEEK_URL,
    "deepseek-reasoner":    DEEPSEEK_URL,
}

# ── Core caller ───────────────────────────────────────────────────────────────

def call_model(model_key, api_key, **kwargs):
    if model_key not in json_data:
        raise ValueError(f"Unknown model key: '{model_key}'. Available: {list(json_data)}")

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

# ── Public API ────────────────────────────────────────────────────────────────

def _parse_responses_output(data):
    """
    Extract text from a /v1/responses payload.
    output is a list of items; each has a 'type'.
    Text lives in items of type 'message' -> content[0]['text'].
    Reasoning models also emit a 'reasoning' item — skip it.
    """
    for item in data.get("output", []):
        if item.get("type") == "message":
            content = item.get("content", [])
            for block in content:
                if block.get("type") == "output_text":
                    return block["text"]
            # fallback: first block regardless of type
            if content:
                return content[0].get("text", "")
    raise ValueError(f"No message output found in response: {data}")


def chat(text, model="gpt-5.5", api_key="", temperature=1.0, max_tokens=2000):
    data = call_model(model, api_key, text=text, temperature=temperature, max_tokens=max_tokens)
    if model in ANTHROPIC_MODELS:
        return data["content"][0]["text"]
    if model in RESPONSES_MODELS:
        return _parse_responses_output(data)
    return data["choices"][0]["message"]["content"]

def next_token_p(text, api_key=""):
    data    = call_model("gpt-4o-mini-logprobs", api_key, text=text)
    entries = data["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
    result  = defaultdict(float)
    for entry in entries:
        result[entry["token"]] = math.exp(entry["logprob"])
    return result

# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    API_KEYS = {
        "mistral":   "jE15SjhCZ6GoMKqbQnDofr0t1U8wHyJu"
    }

    PROVIDER_KEY = {
        "mistral-large":     "mistral",
        "mistral-medium":    "mistral",
        "mistral-small":     "mistral",
    }

    prompt = "Name one planet in one word."

    for model_key, provider in PROVIDER_KEY.items():
        key = API_KEYS[provider]
        try:
            reply = chat(prompt, model=model_key, api_key=key)
            print(f"[{model_key:25s}] {reply.strip()}")
        except Exception as e:
            print(f"[{model_key:25s}] ERROR: {e}")
