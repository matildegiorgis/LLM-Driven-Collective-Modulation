# gemini_client.py — Gemini API wrapper with latency measurement

import json
import time
import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)
_model = genai.GenerativeModel(GEMINI_MODEL)

_SYSTEM_PROMPT = """
You are a Semantic Translator for a live musical performance.
Your role is to mediate between audience language, emotional perception, and sound synthesis parameters.

Your task is to convert audience comments into variations for 4 audio parameters:

1. PITCH (pitchshift~): Range 0.5 (deep, heavy, dark) to 2.0 (high, bright, thin).
2. FRAGMENTATION (gate~/rect~): Range 0.1 Hz (legato, smooth, continuous) to 20.0 Hz (granular, flickering, chaotic).
3. DYNAMICS (LFO phasor~): Range 0.1 Hz (slow, calm, distant) to 9.0 Hz (fast, energetic, tense).
4. TIMBRE (svf~ cutoff): Range 100 Hz (muffled, warm, intimate) to 8000 Hz (bright, sharp, open).

INTERPRETATION GUIDELINES:
- Translate perceptual and emotional language into parameter changes.
- Consider temporal evolution: "build" or "increase" imply gradual change.
- Prefer musically coherent transformations.
- Analyze comments as a group to find a dominant direction.

UPDATE RULES:
- Assign INTENT [-1, +1] and CONFIDENCE [0, 1] for each parameter.
- High agreement -> higher confidence.

OUTPUT FORMAT (JSON only):
{
  "pitch":         {"intent": float, "confidence": float},
  "fragmentation": {"intent": float, "confidence": float},
  "dynamics":      {"intent": float, "confidence": float},
  "timbre":        {"intent": float, "confidence": float}
}
"""


def call_gemini(messages: list[str], current_state: dict) -> tuple[dict | None, float]:
    """
    Send a batch of audience messages to Gemini and return
    (parsed_json | None, api_latency_ms).
    """
    prompt = f"Current State: {current_state}\nAudience Messages: {messages}"

    t0 = time.perf_counter()
    try:
        response = _model.generate_content(
            f"{_SYSTEM_PROMPT}\n\n{prompt}",
            generation_config={"response_mime_type": "application/json"},
        )
        api_ms = (time.perf_counter() - t0) * 1000
        return json.loads(response.text), api_ms
    except Exception as e:
        api_ms = (time.perf_counter() - t0) * 1000
        print(f"[Gemini ERROR] {e}  (after {api_ms:.0f} ms)")
        return None, api_ms
