"""
Database layer (Milestone 2, Activity 2.1 - User & Plan Storage).

SQLite + SQLAlchemy ORM. Stores user details and AI-generated workout plans.
Feedback-based updates are saved in a separate column so both the original
and the updated plan are preserved.
"""

import os

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# fitbuddy.db lives in the project root (one level above the app/ package)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(PROJECT_ROOT, 'fitbuddy.db')}"

# check_same_thread=False lets FastAPI's worker threads share the SQLite connection
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class User(Base):
    """A FitBuddy user. `id` is the user-supplied User ID from the form."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String, nullable=False)
    intensity = Column(String, nullable=False)
    schedule = Column(Integer, default=7)  # number of days in the plan

    plans = relationship("WorkoutPlan", back_populates="user")


class WorkoutPlan(Base):
    """A user's workout plan: the original AI plan and the feedback-updated one."""

    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)

    user = relationship("User", back_populates="plans")


def init_db():
    """Create all tables (runs once at app startup)."""
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# Helper functions used by routes.py
# ---------------------------------------------------------------------------

def save_user(user_id: int, name: str, age: int, weight: float, goal: str, intensity: str):
    """Upsert a user: update the row if the User ID exists, otherwise create it."""
    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(id=user_id).first()
        if existing:
            # Update existing user info
            existing.name = name
            existing.age = age
            existing.weight = weight
            existing.goal = goal
            existing.intensity = intensity
        else:
            # Create a new user
            user = User(
                id=user_id,
                name=name,
                age=age,
                weight=weight,
                goal=goal,
                intensity=intensity,
                schedule=7,  # default 7-day schedule
            )
            db.add(user)
        db.commit()
    finally:
        db.close()


def save_plan(user_id: int, plan: str):
    """
    Store a newly generated plan as the user's original_plan.

    If the user already has a plan row (they regenerated with the same User ID),
    that row is replaced and its old updated_plan is cleared, so each user has
    exactly one current plan and feedback always applies to the latest one.
    """
    db = SessionLocal()
    try:
        workout = db.query(WorkoutPlan).filter_by(user_id=user_id).first()
        if workout:
            workout.original_plan = plan
            workout.updated_plan = None
        else:
            workout = WorkoutPlan(user_id=user_id, original_plan=plan)
            db.add(workout)
        db.commit()
    finally:
        db.close()


def update_plan(user_id: int, updated_text: str):
    """Save the feedback-based revision in the user's updated_plan column."""
    db = SessionLocal()
    try:
        workout = db.query(WorkoutPlan).filter_by(user_id=user_id).first()
        if workout:
            workout.updated_plan = updated_text
            db.commit()
    finally:
        db.close()


def get_original_plan(user_id: int):
    """Return the user's original plan text, or None if they have no plan."""
    db = SessionLocal()
    try:
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        return plan.original_plan if plan else None
    finally:
        db.close()


def get_user(user_id: int):
    """Return the User row for this ID, or None."""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


def get_all_users():
    """Return every user (used by the admin dashboard)."""
    db = SessionLocal()
    try:
        return db.query(User).order_by(User.id).all()
    finally:
        db.close()


def get_all_plans():
    """Return every workout plan (used by the admin dashboard)."""
    db = SessionLocal()
    try:
        return db.query(WorkoutPlan).all()
    finally:
        db.close()
