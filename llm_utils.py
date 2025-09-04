"""
llm_utils.py
@ken.chen
Utility functions for LLM integration (Ollama, etc.)
"""
import re
import json
import requests

OLLAMA_URL = None  # Set from app.py or via setter
MODEL_NAME = None

def set_llm_config(url, model):
    global OLLAMA_URL, MODEL_NAME
    OLLAMA_URL = url
    MODEL_NAME = model

def ollama_generate(model: str, prompt: str) -> str:
    r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=120)
    r.raise_for_status()
    return r.json().get("response", "")

def extract_first_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m: return {}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {}

def build_prompt(customer_desc: str, notes: list[str], submission: str) -> str:
    notes_bulleted = "\n- ".join(notes)
    return f"""You are a writing coach for MongoDB Technical Services handoffs. Output JSON only.

Case (customer description):
<<<{customer_desc}>>>

Case (analysis notes):
- {notes_bulleted}

Engineer’s summary (to grade):
<<<{submission}>>>

Score each 0–5: clarity, completeness, actionability, tone, conciseness.
Provide 2–5 fixes with 'aspect','issue','fix'.
Return JSON exactly:
{{
  "scores": {{"clarity":0,"completeness":0,"actionability":0,"tone":0,"conciseness":0}},
  "feedback": [{{"aspect":"","issue":"","fix":""}}]
}}"""

def total_score(scores: dict) -> int:
    try:
        c = scores.get("clarity", 0)
        comp = scores.get("completeness", 0)
        act = scores.get("actionability", 0)
        tone = scores.get("tone", 0)
        conc = scores.get("conciseness", 0)
        return int((c + comp + act) * 2 + tone + conc)
    except Exception:
        return 0
