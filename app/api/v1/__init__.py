"""API v1版本"""
from fastapi import APIRouter

from .agents import router as agents_router
from .models import router as models_router

# 创建API路由器
api_router = APIRouter()

# 注册子路由
api_router.include_router(agents_router, prefix="/agents", tags=["智能体"])
api_router.include_router(models_router, prefix="/models", tags=["模型"])

__all__ = ["api_router"]