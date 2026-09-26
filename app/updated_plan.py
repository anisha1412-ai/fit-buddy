"""
Feedback-Based Plan Updating (Milestone 2, Activity 2.1).

Sends the original 7-day plan plus the user's feedback (e.g. "Add yoga",
"Include more cardio") to the Gemini "Pro" model setting and returns the revised plan.
"""

from app.gemini_client import generate_with_fallback, model_list

PRO_MODELS = model_list("GEMINI_PRO_MODEL", "gemini-1.5-pro")


def update_workout_plan(original_plan: str, user_feedback: str) -> str:
    """
    Use Gemini to update the workout plan based on user feedback.

    Returns:
        str: The revised plan, or a readable error message on failure.
    """
    prompt = f"""
You are a professional fitness trainer assistant.

Here's the original 7-day workout plan:
{original_plan}

User Feedback:
"{user_feedback}"

Based on the feedback, revise the relevant parts of the workout plan. Keep the format and rest of the plan unchanged if not needed.
"""
    try:
        return generate_with_fallback(PRO_MODELS, prompt).strip()
    except Exception as e:
        return f"Error updating plan: {e}"
