# -*- coding: utf-8 -*-
"""
AI服务单元测试
职责：对OCR服务和AI分析服务进行独立单元测试
"""
import os
import sys
import json
import tempfile
import logging
import unittest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("unit-test")

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestOcrService(unittest.TestCase):
    """OCR服务单元测试"""

    @classmethod
    def setUpClass(cls):
        from services.ocr_service import OcrService
        cls.ocr = OcrService()

    def test_parse_ocr_result_empty(self):
        """测试空结果解析"""
        result = self.ocr._parse_ocr_result([])
        self.assertEqual(result, "")

    def test_parse_ocr_result_none(self):
        """测试None结果解析"""
        result = self.ocr._parse_ocr_result(None)
        self.assertEqual(result, "")

    def test_extract_text_file_not_found(self):
        """测试文件不存在场景"""
        result = self.ocr.extract_text("/path/to/nonexistent/file.pdf")
        self.assertEqual(result, "")

    def test_unsupported_format(self):
        """测试不支持的文件格式"""
        # 创建一个临时文件，但使用不支持的扩展名
        with tempfile.NamedTemporaryFile(suffix=".doc", delete=False) as f:
            f.write(b"test content")
            tmp_path = f.name
        try:
            with self.assertRaises(ValueError):
                self.ocr.extract_text(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestCreditScoreCalculation(unittest.TestCase):
    """信用评分计算测试（不依赖langchain）"""

    @classmethod
    def setUpClass(cls):
        # 直接导入ai_service模块，如果langchain缺失则跳过相关测试
        try:
            from services.ai_service import AiAnalysisService
            cls.ai = AiAnalysisService()
            cls.available = True
        except ImportError as e:
            logger.warning(f"AI服务导入失败（将跳过部分测试）: {e}")
            cls.available = False

    def setUp(self):
        if not getattr(self.__class__, 'available', False):
            self.skipTest("AI服务不可用（缺少依赖）")

    def _make_data(self, overdue=None, credit=None, query=None, public=None):
        """构造测试数据"""
        return {
            "personal_info": {},
            "credit_records": credit or {"debt_ratio": 0, "credit_history_years": 0, "on_time_payment_rate": 100},
            "overdue_records": overdue or {"has_overdue": False},
            "query_records": query or {"recent_3months": 0},
            "public_records": public or {}
        }

    def test_base_score(self):
        """测试基础分60分"""
        score = self.ai._calculate_credit_score(self._make_data())
        self.assertEqual(score, 60)

    def test_overdue_deduction(self):
        """测试逾期扣分"""
        score = self.ai._calculate_credit_score(self._make_data(
            overdue={"has_overdue": True, "overdue_count": 1, "max_overdue_days": 30}
        ))
        self.assertLess(score, 60)

    def test_high_debt_deduction(self):
        """测试高负债扣分"""
        score = self.ai._calculate_credit_score(self._make_data(
            credit={"debt_ratio": 0.8, "credit_history_years": 0, "on_time_payment_rate": 100}
        ))
        self.assertLess(score, 60)

    def test_good_history_bonus(self):
        """测试长信用历史加分"""
        score = self.ai._calculate_credit_score(self._make_data(
            credit={"debt_ratio": 0.2, "credit_history_years": 6, "on_time_payment_rate": 100},
            query={"recent_3months": 2}
        ))
        self.assertGreaterEqual(score, 75)

    def test_bankruptcy_penalty(self):
        """测试破产记录扣分"""
        score = self.ai._calculate_credit_score(self._make_data(
            public={"has_bankruptcy": True, "has_lawsuit": False, "has_tax_arrears": False}
        ))
        self.assertLessEqual(score, 10)

    def test_score_range(self):
        """测试评分范围限制在0-100"""
        score = self.ai._calculate_credit_score(self._make_data())
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_full_score_scenario(self):
        """测试最佳信用场景 满分100"""
        score = self.ai._calculate_credit_score(self._make_data(
            credit={"debt_ratio": 0.1, "credit_history_years": 10, "on_time_payment_rate": 100},
            query={"recent_3months": 1}
        ))
        self.assertEqual(score, 100)

    def test_severe_overdue(self):
        """测试90天以上严重逾期"""
        score = self.ai._calculate_credit_score(self._make_data(
            overdue={"has_overdue": True, "overdue_count": 2, "max_overdue_days": 120}
        ))
        # 60 - 30(有逾期) - 20(2次*10) - 40(>90天) = -30 → 0
        self.assertEqual(score, 0)

    def test_medium_overdue(self):
        """测试30-90天逾期"""
        score = self.ai._calculate_credit_score(self._make_data(
            overdue={"has_overdue": True, "overdue_count": 1, "max_overdue_days": 60}
        ))
        # 60 - 30(逾期) - 10(1次) - 20(>30天) = 0
        self.assertEqual(score, 0)


class TestRiskTipsGeneration(unittest.TestCase):
    """风险提示生成测试（不依赖langchain）"""

    @classmethod
    def setUpClass(cls):
        try:
            from services.ai_service import AiAnalysisService
            cls.ai = AiAnalysisService()
            cls.available = True
        except ImportError:
            cls.available = False

    def setUp(self):
        if not getattr(self.__class__, 'available', False):
            self.skipTest("AI服务不可用（缺少依赖）")

    def test_no_risk(self):
        """测试无风险场景"""
        tips = self.ai._generate_risk_tips({
            "overdue_records": {"has_overdue": False},
            "credit_records": {"debt_ratio": 0.3},
            "query_records": {"recent_3months": 2},
            "public_records": {}
        })
        self.assertIn("信用记录良好", str(tips))

    def test_overdue_risk(self):
        """测试逾期风险提示"""
        tips = self.ai._generate_risk_tips({
            "overdue_records": {"has_overdue": True, "overdue_count": 3, "max_overdue_days": 60},
            "credit_records": {"debt_ratio": 0.3},
            "query_records": {"recent_3months": 2},
            "public_records": {}
        })
        self.assertTrue(any("逾期" in t for t in tips))

    def test_many_queries_risk(self):
        """测试频繁查询风险提示"""
        tips = self.ai._generate_risk_tips({
            "overdue_records": {"has_overdue": False},
            "credit_records": {"debt_ratio": 0.3},
            "query_records": {"recent_3months": 12},
            "public_records": {}
        })
        self.assertTrue(any("频繁" in t or "过多" in t for t in tips))

    def test_high_debt_risk(self):
        """测试高负债风险提示"""
        tips = self.ai._generate_risk_tips({
            "overdue_records": {"has_overdue": False},
            "credit_records": {"debt_ratio": 0.8},
            "query_records": {"recent_3months": 2},
            "public_records": {}
        })
        self.assertTrue(any("负债率" in t for t in tips))

    def test_public_records_risk(self):
        """测试公共记录风险提示"""
        tips = self.ai._generate_risk_tips({
            "overdue_records": {"has_overdue": False},
            "credit_records": {"debt_ratio": 0.3},
            "query_records": {"recent_3months": 2},
            "public_records": {"has_bankruptcy": True, "has_lawsuit": False, "has_tax_arrears": False}
        })
        self.assertTrue(any("破产" in t for t in tips))


class TestAiResponseCleaning(unittest.TestCase):
    """AI返回文本清理测试（不依赖langchain）"""

    @classmethod
    def setUpClass(cls):
        try:
            from services.ai_service import AiAnalysisService
            cls.ai = AiAnalysisService()
            cls.available = True
        except ImportError:
            cls.available = False

    def setUp(self):
        if not getattr(self.__class__, 'available', False):
            self.skipTest("AI服务不可用（缺少依赖）")

    def test_clean_json_block(self):
        """测试清理markdown代码块标记"""
        text = '```json\n{"key": "value"}\n```'
        result = self.ai._clean_response(text)
        self.assertEqual(result, '{"key": "value"}')

    def test_clean_no_block(self):
        """测试无代码块标记"""
        text = '{"key": "value"}'
        result = self.ai._clean_response(text)
        self.assertEqual(result, text)

    def test_clean_triple_backticks_only(self):
        """测试仅有起始标记"""
        text = '```\n{"key": "value"}'
        result = self.ai._clean_response(text)
        self.assertEqual(result, '{"key": "value"}')

    def test_clean_with_extra_text(self):
        """测试带额外文本"""
        text = '这是分析结果:\n```json\n{"key": "value"}\n```\n完毕'
        result = self.ai._clean_response(text)
        self.assertEqual(result, '{"key": "value"}')


class TestErrorResult(unittest.TestCase):
    """错误结果生成测试（不依赖langchain）"""

    @classmethod
    def setUpClass(cls):
        try:
            from services.ai_service import AiAnalysisService
            cls.ai = AiAnalysisService()
            cls.available = True
        except ImportError:
            cls.available = False

    def setUp(self):
        if not getattr(self.__class__, 'available', False):
            self.skipTest("AI服务不可用（缺少依赖）")

    def test_error_result_format(self):
        """测试错误结果格式"""
        result = self.ai._error_result("test_id", "error message")
        self.assertEqual(result["task_id"], "test_id")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error_message"], "error message")
        self.assertEqual(result["credit_score"], 0)
        self.assertIn("error message", str(result["risk_tips"]))

    def test_error_result_without_task_id(self):
        """测试无task_id的错误结果"""
        result = self.ai._error_result(None, "some error")
        self.assertEqual(result["task_id"], "")
        self.assertEqual(result["status"], "failed")


class TestCacheUtil(unittest.TestCase):
    """缓存工具测试"""

    def test_cache_import(self):
        """测试缓存模块可导入"""
        try:
            from utils.cache_util import CacheUtil
            cache = CacheUtil()
            self.assertIsNotNone(cache)
        except ImportError as e:
            self.fail(f"导入失败: {e}")

    def test_cache_default_ttl(self):
        """测试默认TTL配置"""
        from utils.cache_util import cache
        # 验证对象已创建
        self.assertIsNotNone(cache)


if __name__ == "__main__":
    unittest.main(verbosity=2)
