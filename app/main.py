from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.api import api_router
from app.core.config import settings
from app.db.session import create_db_and_tables

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="雨林作业管理系统API",
    version="1.0.0",
)

# 设置CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "欢迎使用雨林作业管理系统API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.on_event("startup")
def on_startup():
    """应用启动时执行的函数"""
    # 创建数据库表
    create_db_and_tables()
    print("数据库表已创建")


if __name__ == "__main__":
    """
    直接运行此文件即可启动服务
    命令: python -m app.main
    """
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 