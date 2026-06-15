"""
LangChain OCR 工具集
基于 LangChain MCP 框架，将 PaddleOCR 封装为可被 Agent 调用的 Tool 组件
"""
import os
import logging
from typing import Optional, List

from langchain_core.tools import tool
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ─── 全局 PaddleOCR 延迟初始化 ─────────────────────────────
_paddle_ocr_instance: Optional[object] = None


def _get_paddle_ocr():
    """延迟初始化 PaddleOCR 引擎"""
    global _paddle_ocr_instance
    if _paddle_ocr_instance is None:
        try:
            from paddleocr import PaddleOCR
            _paddle_ocr_instance = PaddleOCR(
                use_angle_cls=True,
                lang='ch',
                use_gpu=False
            )
            logger.info("LangChain OCR Tool: PaddleOCR 初始化成功")
        except ImportError:
            logger.error("PaddleOCR 未安装，请执行: pip install paddleocr")
            raise
        except Exception as e:
            logger.error(f"PaddleOCR 初始化失败: {e}")
            raise
    return _paddle_ocr_instance


def _parse_ocr_result(result: List) -> str:
    """解析 PaddleOCR 返回结果为纯文本"""
    lines = []
    if result and result[0]:
        for line in result[0]:
            if line and len(line) >= 1:
                text = line[1][0] if len(line[1]) > 0 else ""
                confidence = line[1][1] if len(line[1]) > 1 else 0
                if text and text.strip() and confidence > 0.3:
                    lines.append(text.strip())
    return "\n".join(lines)


# ─── LangChain Tools ───────────────────────────────────────

class OcrImageInput(BaseModel):
    """图片 OCR 工具输入参数"""
    file_path: str = Field(description="图片文件的绝对路径，支持 jpg/jpeg/png/bmp/tiff 格式")


class OcrPdfInput(BaseModel):
    """PDF OCR 工具输入参数"""
    file_path: str = Field(description="PDF 文件的绝对路径")


@tool(args_schema=OcrImageInput)
def ocr_extract_from_image(file_path: str) -> str:
    """
    使用 PaddleOCR 从图片文件中提取文字。
    当用户上传了 JPG/PNG/BMP/TIFF 格式的征信报告图片时调用此工具。

    Args:
        file_path: 图片文件的绝对路径

    Returns:
        识别出的文本内容，每行一条
    """
    if not os.path.exists(file_path):
        return f"错误：文件不存在 - {file_path}"

    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in (".jpg", ".jpeg", ".png", ".bmp", ".tiff"):
        return f"错误：不支持的文件格式 {file_ext}，请使用 jpg/png/bmp/tiff"

    try:
        ocr = _get_paddle_ocr()
        logger.info(f"[OCR Tool] 开始识别图片: {file_path}")
        result = ocr.ocr(file_path, cls=True)
        text = _parse_ocr_result(result)
        logger.info(f"[OCR Tool] 图片识别完成，文本长度: {len(text)}")
        return text if text.strip() else "警告：未能从图片中识别出文字，请确认图片清晰度"
    except Exception as e:
        logger.error(f"[OCR Tool] 图片识别失败: {e}")
        return f"错误：OCR识别异常 - {str(e)}"


@tool(args_schema=OcrPdfInput)
def ocr_extract_from_pdf(file_path: str) -> str:
    """
    从PDF文件中提取文字。优先使用 pdfplumber 直接提取文本层（适用于文字版PDF），
    失败时自动使用 PaddleOCR 对每页进行扫描识别（适用于扫描版PDF）。

    Args:
        file_path: PDF 文件的绝对路径

    Returns:
        提取出的文本内容，包含页码标记
    """
    if not os.path.exists(file_path):
        return f"错误：文件不存在 - {file_path}"

    logger.info(f"[OCR Tool] 开始提取PDF: {file_path}")

    # 策略一：pdfplumber 直接提取文本层
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            pages_text = []
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    pages_text.append(f"--- 第{i + 1}页 ---\n{page_text.strip()}")
            if pages_text:
                text = "\n\n".join(pages_text)
                logger.info(f"[OCR Tool] PDF文本层提取成功，共{len(pages_text)}页")
                return text
    except ImportError:
        logger.warning("[OCR Tool] pdfplumber 未安装，跳过文本层提取")
    except Exception as e:
        logger.warning(f"[OCR Tool] pdfplumber 提取失败: {e}")

    # 策略二：PaddleOCR 逐页扫描识别
    try:
        import fitz
        doc = fitz.open(file_path)
        ocr = _get_paddle_ocr()
        pages_text = []

        for i in range(len(doc)):
            page = doc[i]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("png")

            temp_path = f"_langchain_ocr_page_{i}.png"
            with open(temp_path, "wb") as f:
                f.write(img_bytes)

            result = ocr.ocr(temp_path, cls=True)
            page_text = _parse_ocr_result(result)
            if page_text.strip():
                pages_text.append(f"--- 第{i + 1}页 ---\n{page_text.strip()}")

            if os.path.exists(temp_path):
                os.remove(temp_path)

        doc.close()
        text = "\n\n".join(pages_text)
        logger.info(f"[OCR Tool] 扫描版PDF识别完成，共{len(pages_text)}页")
        return text if text.strip() else "警告：PDF 所有页面均未识别出有效文字"

    except ImportError:
        logger.error("[OCR Tool] PyMuPDF (fitz) 未安装，无法处理扫描版PDF")
        return "错误：PDF 文本提取失败，请确认已安装 pdfplumber 和 PyMuPDF 依赖"
    except Exception as e:
        logger.error(f"[OCR Tool] PDF 扫描识别失败: {e}")
        return f"错误：PDF OCR识别异常 - {str(e)}"


@tool
def ocr_extract_text(file_path: str) -> str:
    """
    根据文件类型自动选择OCR方式提取文字。
    支持的格式：PDF（文字版+扫描版）、JPG、PNG、BMP、TIFF。

    此工具是 OCR 的统一入口，会根据文件扩展名自动路由到相应的处理引擎。

    Args:
        file_path: 征信报告文件的绝对路径

    Returns:
        从文件中提取的完整文本内容
    """
    if not os.path.exists(file_path):
        return f"错误：文件不存在 - {file_path}"

    file_ext = os.path.splitext(file_path)[1].lower()
    logger.info(f"[OCR Tool] 自动路由: {file_ext} -> {file_path}")

    if file_ext == ".pdf":
        return ocr_extract_from_pdf.invoke({"file_path": file_path})
    elif file_ext in (".jpg", ".jpeg", ".png", ".bmp", ".tiff"):
        return ocr_extract_from_image.invoke({"file_path": file_path})
    else:
        return f"错误：不支持的文件格式 '{file_ext}'，请使用 PDF 或图片（JPG/PNG/BMP/TIFF）格式"


def get_ocr_tools() -> List:
    """
    返回所有 OCR 相关的 LangChain Tools 列表，
    供 Agent 创建时注册使用。
    """
    return [
        ocr_extract_text,
        ocr_extract_from_image,
        ocr_extract_from_pdf,
    ]


logger.info("LangChain OCR 工具集模块加载完成")
