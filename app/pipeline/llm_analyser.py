import os
import json
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def clean_json_string(text: str) -> str:
    """Strips markdown code blocks from a JSON response string if present."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def analyze_misconception_with_llm(
    code: str,
    error: str,
    misconception_name: str,
    misconception_description: str,
    example_fix: str
) -> dict:
    """
    Calls OpenRouter API to analyze the student's coding misconception.
    If the API call fails or returning data is invalid, falls back to a template explanation.
    """
    api_key = os.getenv("OPENROUTER_API_KEY", "your_key_here")
    model_name = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")
    max_tokens = int(os.getenv("MAX_TOKENS", "600"))

    # Fallback explanation details
    fallback_response = {
        "explanation": f"It looks like you're experiencing an issue related to: '{misconception_name}'. This happens because: {misconception_description}",
        "micro_exercise": f"Take a look at how this code pattern can be written correctly:\n\n{example_fix}"
    }

    # If the user hasn't set the key yet, skip network call and return fallback immediately
    if not api_key or api_key == "your_key_here":
        logger.warning("OPENROUTER_API_KEY is not set or is set to default. Returning fallback response.")
        return fallback_response

    # Prepare prompt
    prompt = f"""You are a CS education expert helping a beginner Python student understand their mistake.

Student code:
{code}

Error produced:
{error if error else 'No runtime error (Code runs but may have logic issues or anti-patterns)'}

Identified misconception: {misconception_name}
Misconception description: {misconception_description}

Respond ONLY in this JSON format with no extra text:
{{
  "explanation": "2-3 sentence plain English explanation of why the student thinking was wrong, friendly tone",
  "micro_exercise": "One small focused coding exercise to fix this specific misconception"
}}"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/internship-project",
        "X-Title": "Coding Misconception Detector"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=10.0)
        
        if response.status_code == 200:
            res_data = response.json()
            content = res_data["choices"][0]["message"]["content"]
            cleaned_content = clean_json_string(content)
            
            try:
                result = json.loads(cleaned_content)
                # Ensure it contains the required keys
                if "explanation" in result and "micro_exercise" in result:
                    return result
                else:
                    logger.error("LLM JSON response missing keys: explanation or micro_exercise")
            except json.JSONDecodeError:
                logger.error(f"Failed to parse LLM response as JSON: {cleaned_content}")
        else:
            logger.error(f"OpenRouter API returned error code {response.status_code}: {response.text}")
            
    except Exception as e:
        logger.error(f"OpenRouter API request failed: {str(e)}")

    return fallback_response
