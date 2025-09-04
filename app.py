"""
app.py
@ken.chen
"""
import os, datetime
from flask import Flask, request, redirect, url_for, render_template, render_template_string, abort
from pymongo import MongoClient
from dotenv import load_dotenv
from llm_utils import ollama_generate, extract_first_json, build_prompt, total_score, set_llm_config

# Load variables from .env into os.environ
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/training")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "mistral:7b-instruct")
set_llm_config(OLLAMA_URL, MODEL_NAME)

client = MongoClient(MONGO_URI)
db = client.get_database()  # uses DB in URI; else 'edu'
cases = db["cases"]
submissions = db["submissions"]
reviews = db["reviews"]

app = Flask(__name__)

@app.get("/")
def index():
    all_cases = list(cases.find({}, {"_id": 1, "title": 1}))
    return render_template("index.html", cases=all_cases)

@app.get("/case")
def redirect_case():
    cid = request.args.get("id")
    if not cid:
        return redirect(url_for("index"))
    return redirect(url_for("show_case", case_id=cid))


@app.get("/case/<case_id>")
def show_case(case_id):
    doc = cases.find_one({"_id": case_id})
    if not doc:
        abort(404)
    return render_template("page1.html", case=doc)

@app.post("/case/<case_id>")
def submit_case(case_id):
    doc = cases.find_one({"_id": case_id})
    if not doc:
        abort(404)
    text = (request.form.get("text") or "").strip()
    author = (request.form.get("author") or "").strip()
    if len(text) < 60:
        return "Please write at least ~120 words for a meaningful review.", 400

    sub = {
        "case_id": case_id,
        "author": author or None,
        "text": text,
        "created_at": datetime.datetime.utcnow()
    }
    sub_id = submissions.insert_one(sub).inserted_id

    # Grade with mistral
    prompt = build_prompt(doc["customer_desc"], doc.get("analysis_notes", []), text)
    raw = ollama_generate(MODEL_NAME, prompt)
    parsed = extract_first_json(raw)
    scores = parsed.get("scores", {})
    feedback = parsed.get("feedback", [])

    rev = {
        "submission_id": sub_id,
        "model": MODEL_NAME,
        "scores": {
            "clarity": scores.get("clarity", 0),
            "completeness": scores.get("completeness", 0),
            "actionability": scores.get("actionability", 0),
            "tone": scores.get("tone", 0),
            "conciseness": scores.get("conciseness", 0),
        },
        "total": total_score(scores),
        "feedback": feedback,
        "created_at": datetime.datetime.utcnow()
    }
    reviews.insert_one(rev)
    return redirect(url_for("review_submission", submission_id=str(sub_id)))

@app.get("/review/<submission_id>")
def review_submission(submission_id):
    from bson import ObjectId
    sub = submissions.find_one({"_id": ObjectId(submission_id)})
    if not sub:
        abort(404)
    case = cases.find_one({"_id": sub["case_id"]})
    rev = reviews.find_one({"submission_id": sub["_id"]}, sort=[("_id", -1)])
    if not rev:
        abort(404)
    # make dicts attribute-like for Jinja
    class O(dict):
        __getattr__ = dict.get
    return render_template(
        "page2.html",
        case=O(case),
        submission=O({**sub, "created_at": sub["created_at"].strftime("%Y-%m-%d %H:%M UTC")}),
        review=O({**rev, "scores": O(rev["scores"])})
    )

if __name__ == "__main__":
    app.run(port=1314, debug=True)
