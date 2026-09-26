"""
Nutrition Tip Generation (Milestone 2, Activity 2.1).

Uses the lightweight Gemini Flash model setting to return a quick, practical
nutrition or recovery tip for the user's goal.
"""

from app.gemini_client import generate_with_fallback, model_list

# Flash model(s) are fast and cheap - ideal for short tips (see GEMINI_FLASH_MODEL in .env)
FLASH_MODELS = model_list("GEMINI_FLASH_MODEL", "gemini-1.5-flash")


def generate_nutrition_tip_with_flash(goal: str) -> str:
    """
    Generate a nutrition or recovery tip using Gemini Flash based on the user's fitness goal.

    Args:
        goal (str): User's fitness goal - "weight loss", "muscle gain", or "general fitness".

    Returns:
        str: Generated tip, or a readable error message on failure.
    """
    prompt = (
        f"Give one clear, helpful nutrition or recovery tip for someone focused on '{goal}'. "
        "The tip should be practical, friendly, and easy to understand."
    )

    try:
        return generate_with_fallback(FLASH_MODELS, prompt).strip()
    except Exception as e:
        return f"Error generating tip: {str(e)}"
