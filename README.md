# Say It Right: Effective Communication Trainer
This project is a training tool for engineers to practice writing clear and effective case handoffs for the next shift. It provides a simple web interface built with Flask, stores cases and submissions in MongoDB, and uses Ollama (Mistral) to grade responses against a communication effectiveness rubric.

## Features
- Case bank stored in MongoDB (seeded with 5 sample cases).
- **Practice Page:** Shows a real-world customer description and analysis notes. Users write and submit a shift briefing summary for grading.
- **Review Page:** Displays your submission, detailed AI rubric scores (clarity, completeness, actionability, tone, conciseness), total score, and actionable feedback for improvement.
- Grading rubric evaluates clarity, completeness, actionability, tone, and conciseness.
- Weighted scoring: maximum 40 points, displayed as `34/40 (85%)`.

## Quick Start
1. Clone this repo and enter the folder:
	```bash
	git clone https://github.com/simagix/say-it-right.git
	cd say-it-right
	```
2. Create and activate a virtual environment:
	```bash
	python3 -m venv venv
	source venv/bin/activate
	```
3. Install dependencies:
	```bash
	pip install -r requirements.txt
	```
4. Install MongoDB and start it locally (see [MongoDB installation](https://www.mongodb.com/docs/manual/installation/)).
5. Install Ollama (see below) and pull the Mistral model.
6. Seed the database (see below).
7. Run the app (see below).

## What is Ollama?
Ollama is a local LLM (large language model) server that lets you run and interact with models like Mistral on your own machine. This project uses Ollama to grade your shift briefings using AI. Learn more at [ollama.com](https://ollama.com/).

## Requirements
- Python 3.9+
- MongoDB (local or remote)
- Ollama installed locally ([installation guide](https://ollama.com/download))
- On macOS, you can install via Homebrew:
	```bash
	brew install ollama
	```
- Pulled Mistral model:
	```bash
	ollama pull mistral:7b-instruct
	```

## Installation
1. Clone this repo and cd into the folder.
   ```bash
   git clone https://github.com/simagix/say-it-right.git
   cd say-it-right
   ```
2. Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Set up .env (already included in repo):
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
1. Open the index page → select a case.
2. Read customer description + analysis notes.
3. Write your next-shift briefing summary (120–180 words).
4. Submit → AI grades it (scores + total out of 40, plus suggestions).

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