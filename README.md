# Say It Right: Effective Communication Trainer
@ken.chen

This project is a training tool for engineers to practice writing clear and effective case handoffs for the next shift.  
It provides a simple web interface built with Flask, stores cases and submissions in MongoDB, and uses Ollama (Mistral) to grade responses against a communication effectiveness rubric.

## Features
- Case bank stored in MongoDB (seeded with 5 sample cases).  
- Page 1: Displays customer description + analysis notes, with a text area for the engineer’s summary.  
- Page 2: Shows the submission, AI rubric grades, weighted total, and feedback.  
- Grading rubric evaluates clarity, completeness, actionability, tone, and conciseness.  
- Weighted scoring: maximum 40 points, displayed as `34/40 (85%)`.  

## Requirements
- Python 3.9+
- MongoDB (local or remote)
- Ollama installed locally
- Pulled Mistral model:
```bash
ollama pull mistral:7b-instruct
```

## Installation
- Clone this repo and cd into the folder.
- Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
- Install dependencies:
```bash
pip install -r requirements.txt
```
- Set up .env (already included in repo):
```bash
MONGO_URI=mongodb://localhost:27017/edu
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral:7b-instruct
```

## Seed the Case Bank
Run the seeder to populate MongoDB with 5 sample cases:
```bash
python seed_cases.py
```

## Run the App
Start Flask:
```bash
python app.py
```
By default it runs at http://localhost:1314

## Usage
- Open the index page → select a case.
- Read customer description + analysis notes.
- Write your next-shift briefing summary (120–180 words).
- Submit → AI grades it (scores + total out of 40, plus suggestions).

## Example Output
### Total: 34 / 40 (85%)
### Feedback:
- Missing explicit SLA timeline.
- Consider breaking long sentences.
- Good clarity and actionable next steps.

## Notes
- You can add/edit cases directly in the cases collection.
- The app extracts only the first JSON block from AI output to keep it clean.
- Modify total_score() if you want different weighting logic.