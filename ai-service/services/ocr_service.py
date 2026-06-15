"""
OCR识别服务模块
职责：PDF/图片文件解析，使用PaddleOCR进行文字识别
"""
import os
import logging
from typing import List

logger = logging.getLogger(__name__)


class OcrService:
    """PaddleOCR 识别服务"""

    def __init__(self):
        self._ocr = None

    def _get_ocr(self):
        """延迟初始化 PaddleOCR"""
        if self._ocr is None:
            try:
                from paddleocr import PaddleOCR
                self._ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False)
                logger.info("PaddleOCR 初始化成功")
            except Exception as e:
                logger.error(f"PaddleOCR 初始化失败: {e}")
                raise
        return self._ocr

    def extract_text(self, file_path: str) -> str:
        """
        从PDF或图片中提取文本（入口方法）
        Args:
            file_path: 文件路径
        Returns:
            提取的文本内容
        """
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return ""

        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == ".pdf":
            return self._extract_from_pdf(file_path)
        elif file_ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
            return self._extract_from_image(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")

    def _extract_from_pdf(self, file_path: str) -> str:
        """从PDF提取文本（优先pdfplumber，兜底PaddleOCR）"""
        text = ""

        # 方法一：直接提取文本（针对文字版PDF）
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
                    logger.info(f"PDF文本提取成功，共{len(pages_text)}页")
                    return text
        except Exception as e:
            logger.warning(f"pdfplumber提取失败，切换到OCR模式: {e}")

        # 方法二：扫描版PDF使用PaddleOCR逐页识别
        try:
            import fitz
            doc = fitz.open(file_path)
            ocr = self._get_ocr()
            pages_text = []

            for i in range(len(doc)):
                page = doc[i]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x 提高分辨率
                img_bytes = pix.tobytes("png")

                temp_path = f"_temp_page_{i}.png"
                with open(temp_path, "wb") as f:
                    f.write(img_bytes)

                result = ocr.ocr(temp_path, cls=True)
                page_text = self._parse_ocr_result(result)
                if page_text.strip():
                    pages_text.append(f"--- 第{i + 1}页 ---\n{page_text.strip()}")

                if os.path.exists(temp_path):
                    os.remove(temp_path)

            doc.close()
            text = "\n\n".join(pages_text)
            logger.info(f"扫描版PDF OCR识别完成，共{len(pages_text)}页")
            return text

        except Exception as e:
            logger.error(f"PDF OCR识别失败: {e}")
            return ""

    def _extract_from_image(self, file_path: str) -> str:
        """从图片提取文本（PaddleOCR）"""
        try:
            ocr = self._get_ocr()
            result = ocr.ocr(file_path, cls=True)
            text = self._parse_ocr_result(result)
            logger.info(f"图片OCR识别完成，文本长度: {len(text)}")
            return text
        except Exception as e:
            logger.error(f"图片OCR识别失败: {e}")
            return ""

    def _parse_ocr_result(self, result: List) -> str:
        """
        解析PaddleOCR返回结果
        Args:
            result: PaddleOCR返回的嵌套列表
        Returns:
            拼接后的文本
        """
        lines = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 1:
                    text = line[1][0] if len(line[1]) > 0 else ""
                    confidence = line[1][1] if len(line[1]) > 1 else 0
                    if text and text.strip() and confidence > 0.3:  # 置信度阈值
                        lines.append(text.strip())
        return "\n".join(lines)

    def extract_text_multi(self, file_paths: List[str]) -> str:
        """批量处理多个文件"""
        all_text = []
        for path in file_paths:
            text = self.extract_text(path)
            if text.strip():
                all_text.append(text)
        return "\n\n==========\n\n".join(all_text)


# 全局实例
ocr_service = OcrService()

# 兼容旧接口
extract_text = ocr_service.extract_text
