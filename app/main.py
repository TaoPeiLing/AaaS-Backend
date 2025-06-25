"""
FastAPI应用主入口
基于LangChain专家建议使用LangServe部署智能体服务
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .api.v1 import api_router
from .core.config import get_settings
from .core.exceptions import BaseAppException, handle_exception
from .core.logging import setup_logging, get_logger, audit_logger
from .database.connection import init_database, close_database
from .models.manager import model_manager
from .agents.factory import get_agent_manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    logger = get_logger("startup")
    
    try:
        # 启动时初始化
        logger.info("开始初始化应用")
        
        # 初始化数据库
        await init_database()
        logger.info("数据库初始化完成")
        
        # 初始化模型管理器
        await model_manager.initialize()
        logger.info("模型管理器初始化完成")
        
        # 初始化智能体管理器
        agent_manager = await get_agent_manager()
        logger.info("智能体管理器初始化完成")
        
        logger.info("应用初始化完成")
        
        yield
        
    except Exception as e:
        logger.error(f"应用初始化失败: {str(e)}")
        raise
    finally:
        # 关闭时清理
        logger.info("开始清理应用资源")
        
        try:
            await close_database()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {str(e)}")
        
        logger.info("应用资源清理完成")


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    # 初始化日志系统
    setup_logging()
    
    settings = get_settings()
    
    # 创建FastAPI应用
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="基于LangChain的智能体服务平台",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
        lifespan=lifespan
    )
    
    # 配置中间件
    setup_middleware(app)
    
    # 配置异常处理
    setup_exception_handlers(app)
    
    # 注册路由
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    
    return app


def setup_middleware(app: FastAPI) -> None:
    """配置中间件"""
    settings = get_settings()
    
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_debug else ["https://yourdomain.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 可信主机中间件（生产环境）
    if not settings.is_debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
        )
    
    # 请求日志中间件
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger = get_logger("http")
        
        # 记录请求开始
        start_time = asyncio.get_event_loop().time()
        
        # 生成请求ID
        request_id = f"req_{int(start_time * 1000000) % 1000000:06d}"
        
        logger.info(
            "HTTP请求开始",
            method=request.method,
            url=str(request.url),
            request_id=request_id,
            client_ip=request.client.host if request.client else "unknown"
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = asyncio.get_event_loop().time() - start_time
            
            # 记录请求完成
            logger.info(
                "HTTP请求完成",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time=process_time,
                request_id=request_id
            )
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 计算处理时间
            process_time = asyncio.get_event_loop().time() - start_time
            
            # 记录请求异常
            logger.error(
                "HTTP请求异常",
                method=request.method,
                url=str(request.url),
                error=str(e),
                process_time=process_time,
                request_id=request_id
            )
            
            raise


def setup_exception_handlers(app: FastAPI) -> None:
    """配置异常处理器"""
    
    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request: Request, exc: BaseAppException):
        """应用异常处理器"""
        # 记录异常
        audit_logger.log_error(
            error=exc,
            request_id=request.headers.get("X-Request-ID")
        )
        
        # 返回错误响应
        return JSONResponse(
            status_code=400 if exc.error_code.startswith("1") else 500,
            content=exc.to_dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理器"""
        # 转换为应用异常
        app_exc = handle_exception(exc)
        
        # 记录异常
        audit_logger.log_error(
            error=app_exc,
            request_id=request.headers.get("X-Request-ID")
        )
        
        # 返回错误响应
        return JSONResponse(
            status_code=500,
            content=app_exc.to_dict()
        )


# 创建应用实例
app = create_app()


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查数据库
        from .database.connection import db_manager
        db_healthy = await db_manager.health_check()
        
        # 检查模型服务
        model_health = await model_manager.health_check()
        
        # 整体健康状态
        healthy = db_healthy and any(model_health.values())
        
        return {
            "status": "healthy" if healthy else "unhealthy",
            "database": "healthy" if db_healthy else "unhealthy",
            "models": model_health,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
        )


# 根路径
@app.get("/")
async def root():
    """根路径"""
    settings = get_settings()
    return {
        "message": f"欢迎使用{settings.app_name}",
        "version": settings.version,
        "docs_url": f"{settings.api_v1_prefix}/docs",
        "health_url": "/health"
    }


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )