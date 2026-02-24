from fastapi import APIRouter

from app.models import (
    Goal,
    GoalCreate,
    GoalWithProjection,
    compute_projection,
)
from app.storage import append_goal, load_data

router = APIRouter(prefix="/goals", tags=["goals"])


def _goal_with_projection(goal: Goal) -> GoalWithProjection:
    projection = compute_projection(goal)
    return GoalWithProjection(**goal.model_dump(), projection=projection)


@router.get("", response_model=list[GoalWithProjection])
def list_goals() -> list[GoalWithProjection]:
    data = load_data()
    goals = [Goal.model_validate(g) for g in data["goals"]]
    return [_goal_with_projection(g) for g in goals]


@router.post("", status_code=201, response_model=GoalWithProjection)
def create_goal(body: GoalCreate) -> GoalWithProjection:
    goal = Goal(**body.model_dump())
    append_goal(goal)
    return _goal_with_projection(goal)
