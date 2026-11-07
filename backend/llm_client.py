"""
CodeAcharya — Provider-Neutral LLM Client Integration for BharatCode API

Encapsulates all communication with the BharatCode API (and OpenAI-compatible LLM endpoints).
Credentials and models are strictly read from the backend environment and never hardcoded.
Errors (timeouts, 401, 429, 500, network disconnects) are safely caught, logged without secrets,
and return None so the question generator can seamlessly fallback to deterministic blueprints.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger("codeacharya.llm_client")

# Environment configuration defaults
DEFAULT_BHARATCODE_BASE_URL = "https://bharatcode.ai/api/model/v1"
DEFAULT_BHARATCODE_MODEL = "qwen-3.8-27b"
DEFAULT_REQUEST_TIMEOUT = 15


def get_llm_config() -> Dict[str, Any]:
    """
    Returns the current LLM configuration loaded from the backend environment.
    Never exposes API secrets.
    """
    api_key = os.environ.get("BHARATCODE_API_KEY")
    base_url = os.environ.get("BHARATCODE_BASE_URL", DEFAULT_BHARATCODE_BASE_URL).strip()
    model = os.environ.get("BHARATCODE_MODEL", DEFAULT_BHARATCODE_MODEL).strip()

    return {
        "has_api_key": bool(api_key and api_key.strip()),
        "base_url": base_url or DEFAULT_BHARATCODE_BASE_URL,
        "model": model or DEFAULT_BHARATCODE_MODEL,
        "provider": "bharatcode"
    }


def extract_text_from_response(data: Any) -> Optional[str]:
    """
    Extracts text from various response structures returned by BharatCode / OpenAI-compatible APIs:
    - OpenAI format: choices[0].message.content or choices[0].text
    - BharatCode native responses format: data.get("output"), data.get("response"), data.get("text")
    """
    if not isinstance(data, dict):
        if isinstance(data, str) and data.strip():
            return data.strip()
        return None

    # 1. Standard OpenAI choices format
    choices = data.get("choices")
    if isinstance(choices, list) and len(choices) > 0:
        first = choices[0]
        if isinstance(first, dict):
            msg = first.get("message")
            if isinstance(msg, dict):
                content = msg.get("content")
                if content and isinstance(content, str) and content.strip():
                    return content.strip()
            text = first.get("text")
            if text and isinstance(text, str) and text.strip():
                return text.strip()

    # 2. BharatCode native responses format (output, response, text, result, content)
    for key in ("output", "response", "text", "result", "content"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
        if isinstance(val, dict):
            sub = extract_text_from_response(val)
            if sub:
                return sub
        if isinstance(val, list) and len(val) > 0 and isinstance(val[0], str) and val[0].strip():
            return val[0].strip()

    return None


def call_llm(
    system_instruction: str,
    prompt: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    timeout: int = DEFAULT_REQUEST_TIMEOUT
) -> Optional[str]:
    """
    Sends a prompt to the configured LLM provider (BharatCode) and returns the generated text.

    Parameters:
        system_instruction: Guiding context / schema instructions for the AI
        prompt: User / problem generation specification prompt
        api_key: Optional API key override (defaults to BHARATCODE_API_KEY environment variable)
        base_url: Optional base URL override (defaults to BHARATCODE_BASE_URL or https://bharatcode.ai/api/model/v1)
        model: Optional model override (defaults to BHARATCODE_MODEL or qwen-3.8-27b)
        timeout: Maximum seconds to wait before timeout

    Returns:
        Generated text string on success, or None on any failure/timeout/missing credentials.
    """
    effective_api_key = (api_key or os.environ.get("BHARATCODE_API_KEY") or "").strip()
    if not effective_api_key:
        # Missing API key activates deterministic blueprint fallback cleanly
        return None

    effective_base_url = (base_url or os.environ.get("BHARATCODE_BASE_URL") or DEFAULT_BHARATCODE_BASE_URL).strip().rstrip('/')
    effective_model = (model or os.environ.get("BHARATCODE_MODEL") or DEFAULT_BHARATCODE_MODEL).strip()

    headers = {
        "Authorization": f"Bearer {effective_api_key}",
        "Content-Type": "application/json",
        "User-Agent": "CodeAcharya-Backend/1.0"
    }

    # Determine endpoints to try
    # If caller specified full endpoint path (e.g. /chat/completions or /responses), use directly
    if effective_base_url.endswith("/chat/completions") or effective_base_url.endswith("/responses"):
        endpoints_to_try = [effective_base_url]
    else:
        # Try OpenAI-compatible chat/completions first, followed by /responses fallback
        endpoints_to_try = [
            f"{effective_base_url}/chat/completions",
            f"{effective_base_url}/responses"
        ]

    for endpoint_url in endpoints_to_try:
        is_chat_format = endpoint_url.endswith("/chat/completions")
        if is_chat_format:
            payload = {
                "model": effective_model,
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
        else:
            combined_input = f"{system_instruction}\n\n{prompt}".strip() if system_instruction else prompt.strip()
            payload = {
                "model": effective_model,
                "input": combined_input,
                "store": False
            }

        try:
            res = requests.post(
                endpoint_url,
                json=payload,
                headers=headers,
                timeout=timeout
            )

            if res.status_code == 200:
                try:
                    data = res.json()
                    text = extract_text_from_response(data)
                    if text and text.strip():
                        return text.strip()
                    logger.warning("[BharatCode] 200 OK received but response contained no extractable text.")
                    return None
                except json.JSONDecodeError as jde:
                    logger.warning(f"[BharatCode] Response body could not be decoded as JSON: {jde}")
                    return None

            elif res.status_code == 401:
                logger.warning("[BharatCode] Authentication failed (HTTP 401). Please verify BHARATCODE_API_KEY.")
                return None

            elif res.status_code == 429:
                logger.warning("[BharatCode] Rate limit / quota exceeded (HTTP 429).")
                return None

            elif res.status_code == 404:
                # If endpoint not found and multiple endpoints available, try next
                continue

            elif res.status_code >= 500:
                logger.warning(f"[BharatCode] Upstream server error (HTTP {res.status_code}).")
                return None

            else:
                logger.warning(f"[BharatCode] Request failed with HTTP {res.status_code}.")
                return None

        except requests.exceptions.Timeout:
            logger.warning(f"[BharatCode] Request timed out after {timeout} seconds.")
            return None

        except requests.exceptions.ConnectionError as ce:
            logger.warning(f"[BharatCode] Connection error: {ce.__class__.__name__}")
            return None

        except Exception as e:
            logger.warning(f"[BharatCode] Unexpected request error: {e.__class__.__name__}")
            return None

    return None

