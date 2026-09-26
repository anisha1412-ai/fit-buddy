"""
Workout Plan Generation (Milestone 2, Activity 2.1).

Uses the Gemini "Pro" model setting to generate a structured, day-wise
7-day workout plan from the user's goal and intensity.
"""

from app.gemini_client import generate_with_fallback, model_list

# Model(s) for the long, structured workout plan (see GEMINI_PRO_MODEL in .env)
PRO_MODELS = model_list("GEMINI_PRO_MODEL", "gemini-1.5-pro")
PRO_MODEL_NAME = PRO_MODELS[0]


def generate_workout_gemini(user_input: dict) -> str:
    """
    Generate a personalized 7-day workout plan.

    Args:
        user_input (dict): must contain 'goal' and 'intensity';
                           'age' and 'weight' are used when present.

    Returns:
        str: The plan text, or a readable "Error: ..." message on failure.
    """
    # Optional profile details make the plan more personal
    profile = ""
    if user_input.get("age"):
        profile += f"\nThe person is {user_input['age']} years old."
    if user_input.get("weight"):
        profile += f"\nThe person weighs {user_input['weight']} kg."

    prompt = f"""
You are a professional fitness trainer.

Create a personalized, structured 7-day workout plan for someone with the goal of **{user_input['goal']}**, and prefers **{user_input['intensity']} intensity** workouts.{profile}

Each day must include:
- A warm-up (5-10 mins)
- Main workout (targeted exercises, sets & reps)
- Cooldown or recovery tip

Format:
Day 1:
Warm-up: ...
Main Workout: ...
Cooldown: ...
(Repeat for Day 2-7)
"""
    try:
        return generate_with_fallback(PRO_MODELS, prompt)
    except Exception as e:
        return f"Error: {e}"
