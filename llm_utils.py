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

    def simple_similarity(a: str, b: str) -> float:
        # Token overlap similarity (case-insensitive, ignores punctuation)
        import re
        tokens_a = set(re.findall(r"\w+", a.lower()))
        tokens_b = set(re.findall(r"\w+", b.lower()))
        if not tokens_a or not tokens_b:
            return 0.0
        return len(tokens_a & tokens_b) / max(len(tokens_a), len(tokens_b))

    sim = simple_similarity(customer_desc, submission)
    similarity_warning = (
        "\n\nWARNING: The engineer's summary appears too similar to the customer description. Penalize copying and require the summary to be in the engineer's own words."
        if sim > 0.8 else ""
    )

    return f"""
You are an expert writing coach for technical support case handoffs. Your job is to evaluate the engineer's summary for a customer case, focusing on how well it prepares the next shift to take over. Grade the summary on the following criteria:

Clarity: Is the summary easy to understand and free of ambiguity?
Completeness: Does it cover all key facts and context needed for the next engineer?
Actionability: Are next steps and unresolved issues clearly stated?
Tone: Is the language professional and appropriate for internal handoff?
Conciseness: Is the summary brief but thorough, avoiding unnecessary detail?

Output JSON only. Do not include any explanation outside the JSON.

Case (customer description):
<<<{customer_desc}>>>

Case (analysis notes):
- {notes_bulleted}

Engineer’s summary (to grade):
<<<{submission}>>>{similarity_warning}

Score each 0–5: clarity, completeness, actionability, tone, conciseness.
Provide 2–5 fixes with 'aspect','issue','fix'.
Return JSON exactly:
{{
  "scores": {{"clarity":0,"completeness":0,"actionability":0,"tone":0,"conciseness":0}},
  "feedback": [{{"aspect":"","issue":"","fix":""}}]
}}
"""

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
