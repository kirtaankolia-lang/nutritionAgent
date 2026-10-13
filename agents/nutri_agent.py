"""
NutriGuide Agent — Agentic AI Orchestrator
Phase: Agent Loop (Agentic AI SDLC - Orchestration Layer)

Implements the Perceive → Plan → Act → Reflect loop using IBM Granite LLM.
"""

import os
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

from .tools import (
    validate_user_profile,
    build_nutrition_prompt,
    apply_guardrails,
    save_plan_to_markdown,
)


# ──────────────────────────────────────────────────────────
# IBM Granite Model Configuration
# ──────────────────────────────────────────────────────────
WATSONX_API_KEY = os.environ.get("WATSONX_API_KEY", "")
WATSONX_URL = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT_ID = os.environ.get("WATSONX_PROJECT_ID", "")
GRANITE_MODEL_ID = "ibm/granite-13b-instruct-v2"


def _get_model() -> ModelInference:
    """Initialise and return the IBM Granite model inference client."""
    credentials = Credentials(
        url=WATSONX_URL,
        api_key=WATSONX_API_KEY,
    )
    client = APIClient(credentials=credentials, project_id=WATSONX_PROJECT_ID)
    params = {
        GenParams.MAX_NEW_TOKENS: 3000,
        GenParams.TEMPERATURE: 0.7,
        GenParams.TOP_P: 0.9,
        GenParams.REPETITION_PENALTY: 1.1,
        GenParams.STOP_SEQUENCES: ["<|endoftext|>"],
    }
    return ModelInference(
        model_id=GRANITE_MODEL_ID,
        credentials=credentials,
        project_id=WATSONX_PROJECT_ID,
        params=params,
    )


# ──────────────────────────────────────────────────────────
# Agent State Machine
# ──────────────────────────────────────────────────────────
class NutriGuideAgent:
    """
    Agentic AI orchestrator for personalised nutrition planning.

    Agent Loop:
      PERCEIVE  → receive & validate user profile
      PLAN      → build context-aware prompt
      ACT       → invoke IBM Granite LLM
      GUARDRAIL → safety & ethics check on output
      REFLECT   → format, save, return
    """

    def __init__(self):
        self.state = "IDLE"
        self.trace = []  # Agentic reasoning trace

    def _log(self, phase: str, message: str):
        entry = {"phase": phase, "message": message}
        self.trace.append(entry)

    # ── PERCEIVE ────────────────────────────────────────────
    def perceive(self, raw_profile: dict) -> dict:
        self.state = "PERCEIVING"
        self._log("PERCEIVE", "Received user profile. Running validation tools.")
        result = validate_user_profile(raw_profile)
        if not result["valid"]:
            self._log("PERCEIVE", f"Validation failed: {result['errors']}")
            self.state = "ERROR"
        else:
            self._log("PERCEIVE", "Profile validated successfully.")
            self.state = "PLANNING"
        return result

    # ── PLAN ────────────────────────────────────────────────
    def plan(self, profile: dict) -> tuple:
        self._log("PLAN", "Building structured prompt for IBM Granite.")
        system_prompt, user_prompt = build_nutrition_prompt(profile)
        self._log("PLAN", "Prompt constructed with ethics guardrails embedded.")
        self.state = "ACTING"
        return system_prompt, user_prompt

    # ── ACT ─────────────────────────────────────────────────
    def act(self, system_prompt: str, user_prompt: str) -> str:
        self._log("ACT", f"Invoking IBM Granite model: {GRANITE_MODEL_ID}")
        model = _get_model()
        full_prompt = f"[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{user_prompt} [/INST]"
        response = model.generate_text(prompt=full_prompt)
        self._log("ACT", "Response received from IBM Granite.")
        self.state = "GUARDRAILING"
        return response

    # ── GUARDRAIL ───────────────────────────────────────────
    def guardrail(self, text: str) -> dict:
        self._log("GUARDRAIL", "Applying safety and ethics guardrails.")
        result = apply_guardrails(text)
        if result["safe"]:
            self._log("GUARDRAIL", "Content cleared. No harmful patterns detected.")
            self.state = "REFLECTING"
        else:
            self._log("GUARDRAIL", f"BLOCKED — harmful patterns: {result['flagged_terms']}")
            self.state = "BLOCKED"
        return result

    # ── REFLECT ─────────────────────────────────────────────
    def reflect(self, profile: dict, plan_text: str, plans_dir: str) -> dict:
        self._log("REFLECT", "Saving plan to Markdown file.")
        filepath = save_plan_to_markdown(profile, plan_text, output_dir=plans_dir)
        self._log("REFLECT", f"Plan saved: {filepath}")
        self.state = "DONE"
        return {"filepath": filepath, "trace": self.trace}

    # ── MAIN ENTRY POINT ────────────────────────────────────
    def run(self, raw_profile: dict, plans_dir: str = "plans") -> dict:
        """
        Full agentic loop. Returns a result dict with keys:
          success, plan, filepath, trace, errors
        """
        self.trace = []
        self.state = "IDLE"

        # 1. PERCEIVE
        validation = self.perceive(raw_profile)
        if not validation["valid"]:
            return {
                "success": False,
                "errors": validation["errors"],
                "plan": None,
                "filepath": None,
                "trace": self.trace,
            }

        profile = validation["sanitised"]

        # 2. PLAN
        system_prompt, user_prompt = self.plan(profile)

        # 3. ACT
        try:
            plan_text = self.act(system_prompt, user_prompt)
        except Exception as exc:
            self._log("ACT", f"LLM call failed: {exc}")
            return {
                "success": False,
                "errors": [f"IBM Granite API error: {str(exc)}"],
                "plan": None,
                "filepath": None,
                "trace": self.trace,
            }

        # 4. GUARDRAIL
        guard = self.guardrail(plan_text)
        if not guard["safe"]:
            return {
                "success": False,
                "errors": [guard["message"]],
                "plan": None,
                "filepath": None,
                "trace": self.trace,
            }

        # 5. REFLECT
        reflect_result = self.reflect(profile, plan_text, plans_dir)

        return {
            "success": True,
            "errors": [],
            "plan": plan_text,
            "filepath": reflect_result["filepath"],
            "trace": self.trace,
        }


# ──────────────────────────────────────────────────────────
# Q&A Agent — handles common nutrition queries
# ──────────────────────────────────────────────────────────
class NutriQAAgent:
    """
    Lightweight agentic Q&A resolver for common nutrition questions.
    Uses IBM Granite with a focused system prompt.
    """

    QA_SYSTEM_PROMPT = (
        "You are NutriGuide Q&A, a knowledgeable and responsible nutrition assistant. "
        "Answer the user's nutrition and diet question accurately, concisely, and safely. "
        "Always recommend consulting a healthcare professional for medical concerns. "
        "Keep answers under 200 words. Use a helpful, accurate, and mindful tone."
    )

    def answer(self, question: str) -> dict:
        """Answer a nutrition-related question using IBM Granite."""
        # Sanitise input
        question = question.strip()[:1000]
        if not question:
            return {"success": False, "answer": "Please provide a valid question."}

        try:
            model = _get_model()
            prompt = (
                f"[INST] <<SYS>>\n{self.QA_SYSTEM_PROMPT}\n<</SYS>>\n\n"
                f"Question: {question} [/INST]"
            )
            answer_text = model.generate_text(
                prompt=prompt,
                params={
                    GenParams.MAX_NEW_TOKENS: 400,
                    GenParams.TEMPERATURE: 0.5,
                }
            )
            guard = apply_guardrails(answer_text)
            if not guard["safe"]:
                return {
                    "success": False,
                    "answer": guard["message"],
                }
            return {"success": True, "answer": answer_text.strip()}
        except Exception as exc:
            return {"success": False, "answer": f"Error contacting IBM Granite: {str(exc)}"}
