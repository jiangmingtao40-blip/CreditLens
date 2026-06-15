"""
征信报告AI解析服务 - FastAPI主入口（LangChain Agent 架构）
职责：文件上传、基于LangChain Agent的OCR识别+AI解析、结果缓存全链路
"""
import os
import json
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 加载环境变量
load_dotenv()

# ─── 日志配置 ───────────────────────────────────────────────
LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"

logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.getenv("LOG_FILE", "app.log"), encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# ─── 全局配置 ───────────────────────────────────────────────
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", 50)) * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
RESULT_TTL = int(os.getenv("CACHE_RESULT_TTL", 7200))
TASK_TTL = int(os.getenv("CACHE_TASK_TTL", 3600))

os.makedirs(UPLOAD_DIR, exist_ok=True)

# ─── 延迟导入 ──────────────────────────────────────────────
_credit_agent = None
_cache = None


def get_ai_service():
    """获取 AI 分析服务实例"""
    global _credit_agent
    if _credit_agent is None:
        from services.ai_service import AiAnalysisService
        _credit_agent = AiAnalysisService()
        logger.info("DeepSeek AI 分析服务初始化完成")
    return _credit_agent


def get_cache():
    """获取缓存实例"""
    global _cache
    if _cache is None:
        from utils.cache_util import cache
        _cache = cache
    return _cache


# ─── 生命周期管理 ───────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("征信报告AI解析服务启动中（LangChain Agent 架构）...")
    # 预热 Agent（延迟初始化在首次请求时触发）
    yield
    logger.info("服务已关闭")
    if _cache:
        _cache.close()


# ─── FastAPI 应用 ───────────────────────────────────────────
app = FastAPI(
    title="征信报告AI解析服务",
    description="基于 LangChain Agent + DeepSeek + PaddleOCR 的征信报告智能分析服务",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── 数据模型 ───────────────────────────────────────────────
class AnalysisResult(BaseModel):
    task_id: str
    status: str
    personal_info: Optional[dict] = None
    credit_records: Optional[dict] = None
    overdue_records: Optional[dict] = None
    query_records: Optional[dict] = None
    public_records: Optional[dict] = None
    credit_score: Optional[int] = None
    risk_tips: Optional[list] = None
    suggestions: Optional[list] = None
    error_message: Optional[str] = None


# ─── 工具函数 ───────────────────────────────────────────────
def validate_file(file: UploadFile) -> str:
    """验证上传文件"""
    file_ext = os.path.splitext(file.filename or "")[1].lower()

    if not file_ext:
        raise HTTPException(status_code=400, detail="文件缺少扩展名")
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式 '{file_ext}'，请上传PDF或图片文件"
        )

    return file_ext


def get_task_file_path(task_id: str) -> Optional[str]:
    """根据 task_id 查找已上传的文件"""
    for fname in os.listdir(UPLOAD_DIR):
        if fname.startswith(task_id):
            return os.path.join(UPLOAD_DIR, fname)
    return None


# ─── API 路由 ───────────────────────────────────────────────
@app.get("/", tags=["系统"])
async def root():
    """API 根路径"""
    return {
        "name": "征信报告AI解析服务（LangChain Agent）",
        "version": "2.0.0",
        "status": "running",
        "architecture": {
            "framework": "LangChain Agent + Tool Calling",
            "ocr_tools": ["ocr_extract_text", "ocr_extract_from_image", "ocr_extract_from_pdf"],
            "llm": "DeepSeek-V4-Pro (via OpenAI compatible API)",
            "ocr_engine": "PaddleOCR"
        },
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "upload": "/api/ocr/upload",
            "analyze": "/api/ocr/analyze/{task_id}",
            "result": "/api/ocr/result/{task_id}",
            "delete": "/api/ocr/task/{task_id}"
        }
    }


@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "credit-report-ai-langchain",
        "version": "2.0.0",
        "architecture": "LangChain Agent"
    }


@app.post("/api/ocr/upload", tags=["OCR识别"], summary="上传征信报告文件")
async def upload_file(
        file: UploadFile = File(..., description="征信报告文件（PDF/JPG/PNG）"),
        background_tasks: BackgroundTasks = None
):
    """上传征信报告（PDF或图片），返回task_id用于后续分析"""
    file_ext = validate_file(file)
    task_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{task_id}{file_ext}")

    # 读取并保存文件
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制（最大{os.getenv('MAX_FILE_SIZE_MB', '50')}MB）"
        )

    with open(file_path, "wb") as f:
        f.write(content)

    # 设置任务状态
    cache = get_cache()
    cache.set_task_status(task_id, "uploaded", TASK_TTL)

    logger.info(f"文件上传成功: task_id={task_id}, filename={file.filename}, size={len(content)}")
    return {
        "task_id": task_id,
        "filename": file.filename,
        "file_size": len(content),
        "message": "文件上传成功，请调用 /api/ocr/analyze/{task_id} 开始分析"
    }


@app.post("/api/ocr/analyze/{task_id}", tags=["OCR识别"], summary="执行OCR识别和AI分析")
async def analyze_report(task_id: str):
    """
    执行完整分析流程：
    1. 使用 PaddleOCR 提取文字
    2. DeepSeek AI 结构化解析
    3. 信用评分计算（0-1000）
    4. 风险提示 + 优化建议生成
    """
    file_path = get_task_file_path(task_id)
    if not file_path:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 的文件不存在")

    cache = get_cache()
    cache.set_task_status(task_id, "processing", TASK_TTL)
    logger.info(f"[AI Service] 开始分析: task_id={task_id}, file={file_path}")

    try:
        # 步骤1: OCR识别提取文本
        from services.langchain_ocr import ocr_extract_text
        ocr_text = ocr_extract_text.invoke({"file_path": file_path})
        
        if not ocr_text or "错误" in ocr_text:
            raise ValueError(f"OCR识别失败: {ocr_text}")
        
        logger.info(f"[AI Service] OCR识别完成，文本长度: {len(ocr_text)}")

        # 步骤2: 使用 DeepSeek AI 进行结构化分析
        ai_service = get_ai_service()
        result = ai_service.analyze(ocr_text, task_id)

        # 缓存结果
        cache.set_result(task_id, result, RESULT_TTL)
        cache.set_task_status(task_id, "completed", RESULT_TTL)

        logger.info(f"[AI Service] 分析完成: task_id={task_id}, score={result.get('credit_score')}")
        logger.info(f"[AI Service] 返回数据结构: keys={list(result.keys())}")
        logger.info(f"[AI Service] personal_info: {result.get('personal_info', {})}")
        return result

    except ValueError as e:
        # 配置或参数错误
        cache.set_task_status(task_id, "failed", TASK_TTL)
        logger.error(f"[AI Service] 配置错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务配置异常: {str(e)}")
    except Exception as e:
        logger.error(f"[AI Service] 分析失败: {e}")
        cache.set_task_status(task_id, "failed", TASK_TTL)
        return {
            "task_id": task_id,
            "status": "failed",
            "error_message": f"分析处理异常: {str(e)}"
        }


@app.get("/api/ocr/result/{task_id}", tags=["OCR识别"], summary="获取分析结果")
async def get_result(task_id: str):
    """获取征信报告分析结果"""
    cache = get_cache()

    # 优先从缓存获取
    cached = cache.get_result(task_id)
    if cached:
        return cached

    # 查询任务状态
    status = cache.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")

    return {
        "task_id": task_id,
        "status": status,
        "message": "分析进行中" if status == "processing" else
        "等待处理" if status == "uploaded" else
        "分析失败" if status == "failed" else
        f"当前状态: {status}"
    }


@app.delete("/api/ocr/task/{task_id}", tags=["OCR识别"], summary="删除任务及文件")
async def delete_task(task_id: str):
    """删除任务记录、缓存和已上传文件"""
    # 删除缓存
    cache = get_cache()
    cache.delete(f"task:{task_id}", f"result:{task_id}")

    # 删除文件
    file_path = get_task_file_path(task_id)
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"已删除文件: {file_path}")

    logger.info(f"任务已删除: {task_id}")
    return {"message": f"任务 {task_id} 已删除", "task_id": task_id}


# ─── 启动入口 ───────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 8000))
    logger.info(f"启动 LangChain Agent 服务: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
