from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import json
import os
from logging.handlers import RotatingFileHandler

class JSONFormatter(logging.Formatter):
    """结构化JSON日志格式"""
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "path": getattr(record, 'path', ''),
        }, ensure_ascii=False)

# 配置日志
os.makedirs("/data/logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加结构化JSON文件日志
file_handler = RotatingFileHandler(
    "/data/logs/app.log", maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
)
file_handler.setFormatter(JSONFormatter())
file_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(file_handler)

logger = logging.getLogger(__name__)

from app.database import init_db
from app.routers import files_router, auth_router, search_router, stats_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="AI知识库管理系统",
    description="AI驱动的文档解析、自动分类与语义检索API",
    version="1.0.0",
    lifespan=lifespan
)

# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": f"HTTP_{exc.status_code}", "message": exc.detail}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error_code": "INTERNAL_ERROR", "message": "服务器内部错误，请稍后重试"}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files_router)
app.include_router(auth_router)
app.include_router(search_router)
app.include_router(stats_router)

@app.get("/health", summary="健康检查", description="检查服务是否正常运行")
async def health():
    return {"status": "ok"}
