# 🥗 NutriGuide — IBM Granite AI Nutrition Planner

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask&logoColor=white)
![IBM Granite](https://img.shields.io/badge/IBM%20Granite-13B-0062ff?logo=ibm&logoColor=white)
![watsonx.ai](https://img.shields.io/badge/watsonx.ai-Powered-6929c4?logo=ibm&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)
![AI Ethics](https://img.shields.io/badge/AI%20Ethics-HAM%20Guardrails-009d9a)

**A fully agentic, web-based Nutrition Planner powered by IBM Granite LLM**

[Features](#features) • [Architecture](#architecture) • [Quick Start](#quick-start) • [API Reference](#api-reference) • [Deployment](#deployment) • [Ethics & Safety](#ai-ethics--safety)

</div>

---

## Overview

**NutriGuide** is a production-ready **Agentic AI web application** that generates personalised 7-day nutrition plans using the **IBM Granite 13B Instruct** language model via IBM watsonx.ai. It implements the complete **Agentic AI SDLC** with multi-step tool orchestration, AI ethics guardrails, HAM (Helpful, Accurate, Mindful) tone enforcement, and Markdown plan export.

### What it does

1. **Collects** user details — name, age, diet preference, medical history, city, country
2. **Validates** all inputs through an agentic perception layer
3. **Generates** a comprehensive 7-day meal plan personalised to the user's profile
4. **Guards** output with safety filters that block harmful diet advice
5. **Exports** the plan as a downloadable `.md` file
6. **Answers** common nutrition questions via a dedicated Q&A agent

---

## Features

| Feature | Description |
|---------|-------------|
| 🤖 **IBM Granite LLM** | `ibm/granite-13b-instruct-v2` via watsonx.ai SDK |
| 🔄 **Agentic Loop** | PERCEIVE → PLAN → ACT → GUARDRAIL → REFLECT |
| 🛡️ **AI Ethics Guardrails** | Regex-based harmful content detection, input sanitisation |
| ✅ **HAM Tone** | Helpful, Accurate, Mindful response style |
| 📥 **Markdown Export** | Timestamped `.md` plan saved to `plans/` directory |
| 💬 **Q&A Agent** | Real-time nutrition question answering |
| 🔍 **Reasoning Trace** | Full agent step log returned with every plan |
| 🌍 **Location-Aware** | Meals use locally available ingredients |
| ⚕️ **Medical Disclaimer** | Prominently displayed on every plan |
| 🖥️ **Web UI** | Responsive SPA — no framework dependencies |
| 🪟 **Windows Launcher** | One-click `run.bat` setup and start |

---

## Architecture

```
nutrition_ai/
├── app.py                  # Flask web server — 5 REST endpoints
├── requirements.txt        # Python dependencies
├── .env.example            # IBM watsonx.ai credentials template
├── .gitignore              # Git ignore rules
├── run.bat                 # Windows one-click setup & launcher
├── README.md               # This file
├── agents/
│   ├── __init__.py
│   ├── nutri_agent.py      # NutriGuideAgent + NutriQAAgent (orchestration)
│   └── tools.py            # 4 agentic tools (tool layer)
├── plans/                  # Auto-created — stores generated .md plans
└── templates/
    └── index.html          # Single-page application (SPA)
```

### Agentic AI SDLC Phases

```
Phase 1 — Requirements   : Nutrition goals, user profile schema, ethics constraints
Phase 2 — Tool Design    : validate_user_profile, build_nutrition_prompt,
                           apply_guardrails, save_plan_to_markdown
Phase 3 — Agent Loop     : PERCEIVE → PLAN → ACT → GUARDRAIL → REFLECT
Phase 4 — Guardrails     : Harmful content detection + ethics in system prompt
Phase 5 — Deployment     : Flask REST API + SPA on localhost:5000
Phase 6 — Monitoring     : Per-request reasoning trace logged and returned
```

### Agent Loop Flow

```
User Profile Input
      │
      ▼
┌─────────────────────────────────┐
│  PERCEIVE                       │
│  validate_user_profile()        │ ← sanitise + validate all fields
└────────────────┬────────────────┘
                 │ ✓
                 ▼
┌─────────────────────────────────┐
│  PLAN                           │
│  build_nutrition_prompt()       │ ← embed HAM tone + 6 ethics rules
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  ACT                            │
│  IBM Granite LLM (watsonx.ai)   │ ← generate 7-day nutrition plan
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  GUARDRAIL                      │
│  apply_guardrails()             │ ← block harmful content patterns
└────────────────┬────────────────┘
                 │ ✓
                 ▼
┌─────────────────────────────────┐
│  REFLECT                        │
│  save_plan_to_markdown()        │ ← export to plans/<name>_<ts>.md
└────────────────┬────────────────┘
                 │
                 ▼
          Return plan + trace
          to frontend
```

---

## Prerequisites

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Git** — [Download](https://git-scm.com/downloads)
- **IBM watsonx.ai account** — [Sign up free](https://cloud.ibm.com/registration)
- **IBM API Key** — [Create here](https://cloud.ibm.com/iam/apikeys)
- **IBM watsonx.ai Project ID** — [Create project](https://dataplatform.cloud.ibm.com/projects)

---

## Quick Start

### Option A — Windows One-Click (Recommended)

```
Double-click  run.bat
```

The script automatically:
1. Checks Python is installed
2. Creates a Python virtual environment (`venv/`)
3. Installs all dependencies from `requirements.txt`
4. Copies `.env.example` → `.env` and prompts you to add credentials
5. Starts the Flask server on port 5000
6. Opens `http://localhost:5000` in your default browser

### Option B — Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/kirtaankolia-lang/nutritionAgent.git
cd nutritionAgent

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure IBM watsonx.ai credentials
cp .env.example .env
# Edit .env with your credentials (see Configuration section below)

# 5. Run the application
python app.py
```

Then open **http://localhost:5000** in your browser.

---

## Configuration

Create a `.env` file in the project root (copy from `.env.example`):

```env
WATSONX_API_KEY=your_ibm_watsonx_api_key_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_PROJECT_ID=your_project_id_here
```

| Variable | Description | Where to get it |
|----------|-------------|-----------------|
| `WATSONX_API_KEY` | IBM Cloud API key | [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys) |
| `WATSONX_URL` | Regional endpoint | Keep default unless using a different region |
| `WATSONX_PROJECT_ID` | watsonx.ai project ID | [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com/projects) |

> ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore` by default.

---

## API Reference

### `POST /api/plan` — Generate Nutrition Plan

**Request Body:**
```json
{
  "name": "Priya Sharma",
  "age": 35,
  "diet_preference": "veg",
  "medical_history": "Type 2 diabetes, hypertension",
  "city": "Mumbai",
  "country": "India"
}
```

**Diet preference values:** `veg` | `non-veg` | `vegan` | `pescatarian`

**Response (success):**
```json
{
  "success": true,
  "plan": "## 1. Nutritional Assessment Summary\n...",
  "filename": "priya_sharma_20241201_143022.md",
  "trace": [
    {"phase": "PERCEIVE", "message": "Profile validated successfully."},
    {"phase": "PLAN",    "message": "Prompt constructed with ethics guardrails embedded."},
    {"phase": "ACT",     "message": "Response received from IBM Granite."},
    {"phase": "GUARDRAIL","message": "Content cleared. No harmful patterns detected."},
    {"phase": "REFLECT", "message": "Plan saved: plans/priya_sharma_20241201_143022.md"}
  ]
}
```

---

### `POST /api/qa` — Nutrition Q&A

**Request Body:**
```json
{ "question": "What foods help lower blood pressure naturally?" }
```

**Response:**
```json
{
  "success": true,
  "answer": "Foods rich in potassium, magnesium, and nitrates..."
}
```

---

### `GET /api/download/<filename>` — Download Plan

Downloads the generated `.md` file. Replace `<filename>` with the value returned by `/api/plan`.

---

### `GET /api/health` — Health Check

```json
{ "status": "ok", "model": "ibm/granite-13b-instruct-v2" }
```

---

## Generated Nutrition Plan Structure

Each `.md` file exported to `plans/` contains:

```markdown
# Personalised Nutrition Plan
Generated by: NutriGuide — IBM Granite AI
Date: December 01, 2024 at 14:30

## 1. Nutritional Assessment Summary
## 2. Key Nutritional Goals
## 3. Foods to Embrace
## 4. Foods to Limit or Avoid
## 5. 7-Day Meal Plan
   Day 1–7: Breakfast, Snack, Lunch, Snack, Dinner, Hydration tip
## 6. Supplement Recommendations
## 7. Lifestyle Tips
## 8. Progress Tracking

--- Medical Disclaimer ---
```

---

## AI Ethics & Safety

NutriGuide applies the following safety layers:

| Layer | Implementation |
|-------|---------------|
| **Input Validation** | Name, age, diet, location validated; script injection characters stripped |
| **Prompt Ethics** | System prompt embeds 6 explicit guardrail rules for IBM Granite |
| **HAM Tone** | Helpful, Accurate, Mindful enforced in every LLM call |
| **Output Scanning** | Regex patterns detect harmful advice (starvation, extreme restriction, etc.) |
| **Medical Disclaimer** | Shown prominently on every generated plan |
| **File Security** | Download endpoint prevents path traversal attacks |
| **Input Length Limits** | All user inputs capped to safe lengths |

---

## Deployment

### Run locally

```bash
python app.py
# Server starts on http://0.0.0.0:5000
```

### Deploy to a cloud server (optional)

For production deployment on a Linux server:

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | IBM Granite 13B Instruct v2 |
| AI Platform | IBM watsonx.ai |
| Backend | Python 3.10+ · Flask 3.x |
| Frontend | Vanilla HTML5 · CSS3 · JavaScript (ES2020) |
| CORS | flask-cors |
| Config | python-dotenv |
| Export | Python stdlib (os, re, datetime) |

---

## Medical Disclaimer

> **NutriGuide is an AI-powered tool for informational and educational purposes only.** The nutrition plans and advice generated by this application are **not a substitute for professional medical, dietary, or health advice**. Always consult a qualified healthcare provider, registered dietitian, or nutritionist before making significant changes to your diet — especially if you have existing medical conditions such as diabetes, hypertension, kidney disease, or are pregnant or nursing. IBM Granite AI generates content based solely on the information you provide and does not have access to your complete medical history.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with ❤️ using <strong>IBM Granite</strong> · Agentic AI SDLC · AI Ethics Compliant
</div>
