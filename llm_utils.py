"""
llm_utils.py
@ken.chen
Utility functions for LLM integration (Ollama, etc.)
"""
import re, os, time
import json
import logging
import requests
from openai.lib.azure import AzureOpenAI

LLM_BACKEND = None  # 'ollama', 'openai', 'azure', etc.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def llm_generate(prompt: str, llm_backend: str = None) -> str:
    """
    Unified LLM call. Selects backend based on LLM_BACKEND.
    """
    if llm_backend == 'ollama':
        start = time.time()
        url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        model = os.getenv("OLLAMA_MODEL", "mistral:7b-instruct")
        r = requests.post(url, json={"model": model, "prompt": prompt, "stream": False}, timeout=120)
        r.raise_for_status()
        elapsed = time.time() - start
        logger.info(f"LLM call, model {model} took {elapsed:.2f} seconds")
        return r.json().get("response", "")
    elif llm_backend == 'openai':
        # Example stub: implement OpenAI API call here
        # import openai
        # openai.api_key = LLM_CONFIG['api_key']
        # response = openai.ChatCompletion.create(...)
        # return response['choices'][0]['message']['content']
        raise NotImplementedError("OpenAI backend not implemented yet.")
    elif llm_backend == 'azure':
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        model = os.getenv("AZURE_OPENAI_MODEL")
        az_client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        response = az_client.chat.completions.create(
                messages=messages,
                max_tokens=2048,
                temperature=0.0,
                top_p=1.0,
                model=model
            )
        return response.choices[0].message.content
    else:
        raise ValueError(f"Unknown LLM backend: {llm_backend}")
    
def get_model(llm_backend):
    if llm_backend == 'ollama':
        return os.getenv("OLLAMA_MODEL", "mistral:7b-instruct")
    elif llm_backend == 'openai':
        return os.getenv("OPENAI_MODEL", "gpt-4")
    elif llm_backend == 'azure':
        return os.getenv("AZURE_OPENAI_MODEL", "gpt-4")
    else:
        raise ValueError(f"Unknown LLM backend: {llm_backend}")

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
