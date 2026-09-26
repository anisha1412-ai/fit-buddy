"""
Route handlers (Milestone 3, Activity 3.1).

Bridges the Jinja2 templates, the Gemini AI modules and the SQLite database.

HTML routes:
    GET  /                 -> input form (index.html)
    POST /generate-workout -> generate + save plan, show result.html
    POST /submit-feedback  -> update plan from feedback, show result.html
    GET  /view-all-users   -> admin dashboard (all_users.html)

JSON API routes (testable from /docs):
    POST /generate-workout/gemini
    GET  /nutrition-tip
    POST /update-plan/{user_id}
"""

import os

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.database import (
    get_all_plans,
    get_all_users,
    get_original_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
)
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.gemini_generator import PRO_MODEL_NAME, generate_workout_gemini
from app.schemas import FeedbackRequest, UserInput, WorkoutRequest
from app.updated_plan import update_workout_plan

router = APIRouter()

# Jinja2 template setup (Milestone 4, Activity 4.2)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)


def _is_error(text: str) -> bool:
    """The Gemini helpers return messages starting with 'Error' when a call fails."""
    return text.startswith("Error")


# ---------------------------------------------------------------------------
# HTML routes
# ---------------------------------------------------------------------------

# 1. Home: show the input form
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


# 2. Web: generate a workout plan from the form
@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: int = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    # Validate the form data with the UserInput Pydantic model
    try:
        user_data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
    except ValidationError:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"error": "Please enter a valid age and weight (both must be greater than 0)."},
        )

    # Gemini Pro -> 7-day plan, Gemini Flash -> nutrition tip
    plan = generate_workout_gemini(user_data.model_dump())
    nutrition_tip = generate_nutrition_tip_with_flash(user_data.goal)

    # Persist the user, and the plan only if generation succeeded
    save_user(
        user_id=user_data.user_id,
        name=user_data.username,
        age=user_data.age,
        weight=user_data.weight,
        goal=user_data.goal,
        intensity=user_data.intensity,
    )
    error = None
    if _is_error(plan):
        error = "We couldn't generate your plan right now. Details are shown below."
    else:
        save_plan(user_data.user_id, plan)

    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "username": user_data.username,
            "user_id": user_data.user_id,
            "age": user_data.age,
            "weight": user_data.weight,
            "goal": user_data.goal,
            "intensity": user_data.intensity,
            "workout_plan": plan,
            "nutrition_tip": nutrition_tip,
            "error": error,
        },
    )


# 3. Web: update the plan based on user feedback
@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: int = Form(...),
    feedback: str = Form(...),
):
    user = get_user(user_id)
    original = get_original_plan(user_id)

    # No plan saved for this User ID -> friendly message instead of a 500
    if not user or not original:
        return templates.TemplateResponse(
            request,
            "result.html",
            {
                "user_id": user_id,
                "error": f"No workout plan found for User ID {user_id}. "
                         "Please generate a plan first using the same User ID.",
            },
        )

    # Gemini Pro revises the original plan using the feedback
    updated = update_workout_plan(original, feedback)
    nutrition_tip = generate_nutrition_tip_with_flash(user.goal)

    context = {
        "username": user.name,
        "user_id": user.id,
        "age": user.age,
        "weight": user.weight,
        "goal": user.goal,
        "intensity": user.intensity,
        "workout_plan": updated,
        "nutrition_tip": nutrition_tip,
    }

    if _is_error(updated):
        context["error"] = "We couldn't update your plan right now. Details are shown below."
    else:
        update_plan(user_id, updated)
        context["updated_plan"] = updated  # triggers the confirmation banner

    return templates.TemplateResponse(request, "result.html", context)


# 4. Web: admin dashboard - all users & their plans
@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    users = get_all_users()
    # Map user_id -> plan so each user is joined with their WorkoutPlan row
    plans_by_user = {plan.user_id: plan for plan in get_all_plans()}

    user_data = []
    for user in users:
        plan = plans_by_user.get(user.id)
        user_data.append({
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "original_plan": plan.original_plan if plan else "N/A",
            "updated_plan": plan.updated_plan if plan and plan.updated_plan else "Not updated",
        })

    return templates.TemplateResponse(request, "all_users.html", {"users": user_data})


# ---------------------------------------------------------------------------
# JSON API routes (try them at /docs)
# ---------------------------------------------------------------------------

# 5. API: generate workout using Gemini Pro
@router.post("/generate-workout/gemini")
def generate_gemini_workout(request: WorkoutRequest):
    try:
        result = generate_workout_gemini({
            "goal": request.goal,
            "intensity": request.intensity,
        })
        if _is_error(result):
            raise HTTPException(status_code=500, detail=result)
        return {"model": PRO_MODEL_NAME, "workout_plan": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 6. API: generate nutrition tip using Gemini Flash
@router.get("/nutrition-tip")
def get_flash_tip(goal: str):
    tip = generate_nutrition_tip_with_flash(goal)
    return {"goal": goal, "nutrition_tip": tip}


# 7. API: update workout plan based on user feedback
@router.post("/update-plan/{user_id}", response_model=dict)
def update_user_plan(user_id: int, data: FeedbackRequest):
    original = get_original_plan(user_id)
    if not original:
        return {"error": "Original plan not found for this user."}
    updated = update_workout_plan(original, data.feedback)
    if _is_error(updated):
        return {"error": updated}
    update_plan(user_id, updated)
    return {"updated_plan": updated}
