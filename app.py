"""
NutriGuide — Flask Web Application
Phase: Deployment Layer (Agentic AI SDLC)

Routes:
  GET  /             → Serve SPA frontend
  POST /api/plan     → Generate nutrition plan via agent
  POST /api/qa       → Answer nutrition query via Q&A agent
  GET  /api/download → Download generated .md plan file
"""

import os
from dotenv import load_dotenv
load_dotenv()  # load .env before any agent imports

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from agents.nutri_agent import NutriGuideAgent, NutriQAAgent

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

PLANS_DIR = os.path.join(os.path.dirname(__file__), "plans")
os.makedirs(PLANS_DIR, exist_ok=True)

nutri_agent = NutriGuideAgent()
qa_agent = NutriQAAgent()


# ──────────────────────────────────────────────────────────
# Serve SPA
# ──────────────────────────────────────────────────────────
@app.route("/")
def index():
    with open(os.path.join(os.path.dirname(__file__), "templates", "index.html"), encoding="utf-8") as f:
        return f.read()


# ──────────────────────────────────────────────────────────
# POST /api/plan  — Generate personalised nutrition plan
# ──────────────────────────────────────────────────────────
@app.route("/api/plan", methods=["POST"])
def generate_plan():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"success": False, "errors": ["Invalid JSON payload."]}), 400

    # Reinitialise agent for each request (fresh state)
    agent = NutriGuideAgent()
    result = agent.run(raw_profile=data, plans_dir=PLANS_DIR)

    if result["success"]:
        return jsonify({
            "success": True,
            "plan": result["plan"],
            "filename": os.path.basename(result["filepath"]),
            "trace": result["trace"],
        })
    else:
        return jsonify({
            "success": False,
            "errors": result["errors"],
            "trace": result["trace"],
        }), 422


# ──────────────────────────────────────────────────────────
# POST /api/qa  — Answer nutrition question
# ──────────────────────────────────────────────────────────
@app.route("/api/qa", methods=["POST"])
def answer_question():
    data = request.get_json(force=True, silent=True)
    if not data or "question" not in data:
        return jsonify({"success": False, "answer": "No question provided."}), 400

    result = qa_agent.answer(data["question"])
    return jsonify(result)


# ──────────────────────────────────────────────────────────
# GET /api/download/<filename>  — Download plan .md file
# ──────────────────────────────────────────────────────────
@app.route("/api/download/<filename>")
def download_plan(filename):
    # Security: only allow .md files within the plans directory
    if not filename.endswith(".md") or ".." in filename or "/" in filename:
        return jsonify({"error": "Invalid file request."}), 400
    filepath = os.path.join(PLANS_DIR, filename)
    if not os.path.isfile(filepath):
        return jsonify({"error": "File not found."}), 404
    return send_file(filepath, as_attachment=True, download_name=filename, mimetype="text/markdown")


# ──────────────────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────────────────
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "model": "ibm/granite-13b-instruct-v2"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
