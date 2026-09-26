"""
Pydantic schemas (Milestone 2, Activity 2.2 - Process User Input).

Used to validate the structure of form data and JSON API request bodies.
"""

from pydantic import BaseModel, Field


class UserInput(BaseModel):
    """All details collected by the index.html form."""

    username: str
    user_id: int
    age: int = Field(gt=0)
    weight: float = Field(gt=0)
    goal: str
    intensity: str


class FeedbackRequest(BaseModel):
    """JSON body for POST /update-plan/{user_id}."""

    feedback: str


class WorkoutRequest(BaseModel):
    """JSON body for POST /generate-workout/gemini."""

    goal: str
    intensity: str
