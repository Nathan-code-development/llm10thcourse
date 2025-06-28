from fastapi import APIRouter

from app.api.v1.endpoints import (
    assignments,
    auth,
    classes,
    courses,
    gradings,
    notifications,
    statistics,
    submissions,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(classes.router, prefix="/classes", tags=["班级"])
api_router.include_router(courses.router, prefix="/courses", tags=["课程"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["作业"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["提交"])
api_router.include_router(gradings.router, prefix="/gradings", tags=["批改"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["通知"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["统计"]) 