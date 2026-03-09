AI Idea Generator for Startups

This is a small Flask app that generates multiple AI-style startup idea variations for a given domain.

Quick start (Windows PowerShell):

1. Create a virtual environment:

    python -m venv .venv
    ; .\.venv\Scripts\Activate.ps1

2. Install dependencies:

    pip install -r requirements.txt

3. Run the app:

    python app.py

4. Open http://127.0.0.1:5000 in your browser. Use the demo login:

    Email: admin@gmail.com
    Password: 1234

Notes:
- The app currently uses deterministic local templates and randomization to create varied outputs. If you want more advanced, truly AI-powered outputs, integrate an LLM (OpenAI, local models) and update `generate_ideas` to call the model with different prompts/strategies.
- To increase diversity, increase variation count or use different strategy selections.
