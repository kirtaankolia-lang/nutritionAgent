"""
Agentic Tools for Nutrition AI
Phase: Tool Definition (Agentic AI SDLC - Tool Layer)

Each tool is a discrete, composable action the agent can invoke.
"""

import re
from datetime import datetime


# ─────────────────────────────────────────────
# TOOL 1 — Validate & sanitise user profile
# ─────────────────────────────────────────────
def validate_user_profile(profile: dict) -> dict:
    """
    Validates the collected user profile for completeness and safety.
    Returns {valid: bool, errors: list[str], sanitised: dict}
    """
    errors = []
    sanitised = {}

    # Name
    name = str(profile.get("name", "")).strip()
    if not name or len(name) < 2:
        errors.append("Name must be at least 2 characters.")
    sanitised["name"] = name[:80]

    # Age
    try:
        age = int(profile.get("age", 0))
        if age < 1 or age > 120:
            errors.append("Age must be between 1 and 120.")
        sanitised["age"] = age
    except (ValueError, TypeError):
        errors.append("Age must be a valid number.")
        sanitised["age"] = None

    # Diet preference
    diet = str(profile.get("diet_preference", "")).strip().lower()
    if diet not in ("veg", "non-veg", "vegan", "pescatarian"):
        errors.append("Diet preference must be one of: veg, non-veg, vegan, pescatarian.")
    sanitised["diet_preference"] = diet

    # Medical history (free text — scrub script injections)
    medical = str(profile.get("medical_history", "none")).strip()
    medical = re.sub(r"[<>{};]", "", medical)[:500]
    sanitised["medical_history"] = medical or "none"

    # Location
    city = str(profile.get("city", "")).strip()[:100]
    country = str(profile.get("country", "")).strip()[:100]
    if not city or not country:
        errors.append("City and country are required.")
    sanitised["city"] = city
    sanitised["country"] = country

    return {"valid": len(errors) == 0, "errors": errors, "sanitised": sanitised}


# ─────────────────────────────────────────────
# TOOL 2 — Build the structured prompt
# ─────────────────────────────────────────────
def build_nutrition_prompt(profile: dict) -> tuple:
    """
    Constructs a detailed, ethics-aware prompt for IBM Granite.
    Implements HAM (Helpful, Accurate, Mindful) tone guidelines.
    """
    age = profile["age"]
    name = profile["name"]
    diet = profile["diet_preference"]
    medical = profile["medical_history"]
    city = profile["city"]
    country = profile["country"]

    # Determine life stage
    if age < 13:
        life_stage = "child"
    elif age < 18:
        life_stage = "adolescent"
    elif age < 60:
        life_stage = "adult"
    else:
        life_stage = "senior"

    system_prompt = (
        "You are NutriGuide, a responsible and empathetic AI nutrition assistant powered by IBM Granite. "
        "Your role is to provide evidence-based, personalised nutrition guidance. "
        "Follow these ethics guardrails strictly:\n"
        "1. Never recommend extreme calorie restriction or dangerous diets.\n"
        "2. Always defer serious medical concerns to a qualified healthcare professional.\n"
        "3. Be culturally sensitive to the user's location.\n"
        "4. Use a helpful, accurate, and mindful (HAM) tone throughout.\n"
        "5. Do not provide specific medication advice.\n"
        "6. Flag any high-risk conditions (e.g., eating disorders, severe diabetes complications) with extra care.\n"
    )

    user_prompt = f"""
Create a comprehensive, personalised 7-day nutrition plan for the following individual:

**Personal Details:**
- Name: {name}
- Age: {age} years ({life_stage})
- Dietary Preference: {diet}
- Medical History: {medical}
- Location: {city}, {country}

**Please structure your response with the following sections:**

## 1. Nutritional Assessment Summary
Briefly assess the individual's nutritional needs based on their profile.

## 2. Key Nutritional Goals
List 3–5 specific, measurable nutrition goals tailored to their age, diet, and medical conditions.

## 3. Foods to Embrace
List nutrient-dense foods appropriate for their diet preference and medical conditions, with brief reasons.

## 4. Foods to Limit or Avoid
List foods that may negatively impact their health given their medical history.

## 5. 7-Day Meal Plan
For each day (Day 1 through Day 7), provide:
- Breakfast
- Mid-Morning Snack
- Lunch
- Afternoon Snack
- Dinner
- Hydration tip

Keep meals practical and use locally available ingredients from {city}, {country}.

## 6. Supplement Recommendations
Suggest any vitamins or minerals that may benefit this individual (with a note to consult a doctor before use).

## 7. Lifestyle Tips
Provide 3 complementary lifestyle habits (sleep, stress, movement) that support the nutrition plan.

## 8. Progress Tracking
Suggest simple ways to track progress over 4 weeks.

End with a **Medical Disclaimer** reminding the user that this plan is AI-generated for informational purposes only and does not replace professional medical or dietetic advice.
"""
    return system_prompt, user_prompt


# ─────────────────────────────────────────────
# TOOL 3 — Guardrail checker
# ─────────────────────────────────────────────
HARMFUL_PATTERNS = [
    r"\bstarv(e|ing|ation)\b",
    r"\bextreme\s+(fast|diet|restrict)\b",
    r"\b(laxative|diuretic)\s+abuse\b",
    r"\bsuicid\b",
    r"\bself.harm\b",
    r"eat\s+nothing",
    r"skip\s+all\s+meals",
]


def apply_guardrails(text: str) -> dict:
    """
    Scans LLM output for harmful patterns.
    Returns {safe: bool, flagged_terms: list, message: str}
    """
    flagged = []
    lower = text.lower()
    for pattern in HARMFUL_PATTERNS:
        if re.search(pattern, lower):
            flagged.append(pattern)

    if flagged:
        return {
            "safe": False,
            "flagged_terms": flagged,
            "message": (
                "[BLOCKED] The generated response contained potentially harmful content and was blocked. "
                "Please consult a registered dietitian or healthcare professional directly."
            ),
        }
    return {"safe": True, "flagged_terms": [], "message": "Content passed safety checks."}


# ─────────────────────────────────────────────
# TOOL 4 — Save plan to Markdown file
# ─────────────────────────────────────────────
def save_plan_to_markdown(profile: dict, plan_text: str, output_dir: str = "plans") -> str:
    """
    Persists the generated nutrition plan as a Markdown file.
    Returns the file path.
    """
    import os

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r"[^\w]", "_", profile["name"].lower())
    filename = f"{safe_name}_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)

    header = f"""# Personalised Nutrition Plan
**Generated by:** NutriGuide — IBM Granite AI  
**Date:** {datetime.now().strftime("%B %d, %Y at %H:%M")}  
**For:** {profile['name']} | Age: {profile['age']} | Diet: {profile['diet_preference']}  
**Location:** {profile['city']}, {profile['country']}  
**Medical History:** {profile['medical_history']}  

---

"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header + plan_text)

    return filepath
