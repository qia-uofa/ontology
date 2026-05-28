import requests
import math
from collections import defaultdict

def next_token_p(text, url="https://api.openai.com/v1/chat/completions", api_key=''):
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": text}],
            "max_tokens": 1,
            "logprobs": True,
            "top_logprobs": 10
        }
    )

    data = response.json()

    if "choices" not in data:
        raise RuntimeError(f"API error: {data}")

    logprobs = data["choices"][0]["logprobs"]["content"][0]["top_logprobs"]

    result = defaultdict(float)
    for entry in logprobs:
        result[entry["token"]] = math.exp(entry["logprob"])

    return result

def chat(text, url="https://api.openai.com/v1/chat/completions", api_key='', temperature=1.0, max_tokens=2000):
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": text}],
            "temperature": temperature,
            "max_tokens": max_tokens,

        }
    )

    data = response.json()

    if "choices" not in data:
        raise RuntimeError(f"API error: {data}")

    return data["choices"][0]["message"]["content"]