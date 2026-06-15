"""
AI解析服务模块
职责：接入DeepSeek-V4-Pro，对OCR结果进行结构化解析、信用评分、风险提示生成
"""
import os
import json
import re
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

# ─── DeepSeek 提示词模板 ────────────────────────────────────
SYSTEM_PROMPT = """你是一个专业的征信报告分析专家。请根据以下 OCR 识别出的征信报告文字内容，提取并结构化输出以下字段。

## 需要提取的字段

### 1. 个人信息
- name: 姓名
- id_card: 身份证号（脱敏显示仅保留后4位，其余用 **** 替代，未识别填null）
- gender: 性别（男/女，未识别填null）
- marital_status: 婚姻状况（已婚/未婚/离异/丧偶/未知）
- address: 居住地址

### 2. 信贷记录汇总 credit_summary
- credit_cards: 信用卡列表，每项包含：
  - issuing_institution: 发卡机构
  - credit_limit: 授信额度（元，数字）
  - used_amount: 已用额度（元，数字）
  - avg_6month_usage_rate: 最近6个月平均使用率（0.0~1.0，数字）
- mortgages: 住房贷款列表，每项包含：
  - institution: 贷款机构
  - loan_amount: 贷款金额（元）
  - balance: 贷款余额（元）
  - status: 还款状态（正常/逾期/结清）
- other_loans: 其他贷款列表，每项包含：
  - type: 贷款类型
  - amount: 金额（元）
  - balance: 余额（元）
  - status: 还款状态（正常/逾期/结清）

### 3. 逾期记录 overdue_records
- overdue_count: 逾期笔数（整数）
- max_overdue_months: 最长逾期月数（整数）
- max_monthly_amount: 单月最高逾期金额（元，数字）

### 4. 查询记录 query_records
- recent_1month: 近1个月查询次数（整数）
- recent_6months: 近6个月查询次数（整数，排除本人查询和贷后管理）
- query_reasons: 查询原因分类数组，每项包含 reason（原因名称）和 count（次数）

### 5. 公共记录 public_records
- has_enforcement: 是否有强制执行记录（布尔）
- has_administrative_penalty: 是否有行政处罚记录（布尔）
- has_tax_arrears: 是否有欠税记录（布尔）

### 6. 信用评估（请直接计算并输出）
- credit_score: 信用评分 0-1000（整数）—— 基于逾期次数、逾期月数、负债率、查询频率、公共负面记录等因素综合打分
- risk_level: 风险等级 —— 750分以上→"低"，600-750→"中"，600以下→"高"
- risk_warnings: 风险提示字符串数组，列出所有值得关注的风险点，无风险时返回空数组 []

## 输出格式要求
请直接输出有效的 JSON 格式，不要添加任何额外的解释文字，不要包含代码块标记。
JSON 结构包含以下顶级字段：
- personal_info: 包含 name, id_card, gender, marital_status, address
- credit_summary: 包含 credit_cards[], mortgages[], other_loans[]
- overdue_records: 包含 overdue_count, max_overdue_months, max_monthly_amount
- query_records: 包含 recent_1month, recent_6months, query_reasons[]
- public_records: 包含 has_enforcement, has_administrative_penalty, has_tax_arrears
- credit_score: 0-1000 的整数
- risk_level: "低"、"中" 或 "高"
- risk_warnings: 风险提示字符串数组，无风险时返回空数组

## 重要规则
1. 身份证号只保留后4位，前14位用 **** 替代，如 **** **** **** 2578
2. 金额统一为"元"，纯数字不带单位，从OCR文本解析时去除"万元"并换算
3. 最近6个月平均使用率 = 近6个月月均已用额度 / 授信额度
4. 查询记录需排除"本人查询"和"贷后管理"
5. 未识别到的字段：字符串填 null，数字填 0，布尔填 false，数组填 []（空数组，不是 null）
6. 逾期笔数=0 时表示无逾期，credit_score 不应因此扣分

## 以下是 OCR 识别出来的征信报告文字：
"""

# ─── 优化建议模板 ──────────────────────────────────────────
OPTIMIZATION_TEMPLATES = {
    "overdue": [
        "立即结清所有逾期欠款，逾期记录将在结清后5年自动消除",
        "对于非恶意逾期，可联系金融机构协商出具《非恶意逾期证明》",
        "设置自动还款提醒，避免因遗忘导致的逾期"
    ],
    "high_debt": [
        "建议将信用卡使用率控制在70%以下，降低个人负债率",
        "优先偿还高利率债务（如信用卡循环利息），减轻还款压力",
        "避免短期内频繁申请新的信贷产品"
    ],
    "frequent_query": [
        "减少不必要的信贷申请，每次硬查询都会留下记录",
        "未来3-6个月内控制新增信贷申请频率",
        "建议通过预审批了解额度，而非正式提交申请"
    ],
    "short_history": [
        "保持现有信用账户正常使用，逐步积累信用记录时长",
        "建议保留最早开立的信用卡，不要轻易销户"
    ],
    "public_negative": [
        "尽快处理诉讼、欠税等公共记录中的负面信息",
        "已结清的公共记录可申请异议处理，要求更新征信状态"
    ],
    "no_credit": [
        "建议申请一张信用卡并按时还款，开始建立个人信用记录",
        "可通过银行流水、社保缴纳记录等辅助材料证明信用状况"
    ]
}


class AiAnalysisService:
    """DeepSeek AI 分析服务 —— 适配 v2 提示词模板"""

    def __init__(self):
        self._api_key = None
        self._api_base = None
        self._model = None

    def _init_api(self):
        if self._api_key is None:
            self._api_key = os.getenv("DEEPSEEK_API_KEY", "")
            self._api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
            self._model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            if not self._api_key or self._api_key == "your_deepseek_api_key_here":
                raise ValueError("请先配置 DEEPSEEK_API_KEY 环境变量")
            logger.info(f"DeepSeek API 初始化完成: model={self._model}")

    # ─── 主分析入口 ────────────────────────────────────────

    def analyze(self, ocr_text: str, task_id: Optional[str] = None) -> dict:
        if not ocr_text or not ocr_text.strip():
            return self._empty_result(task_id, "OCR文本为空，无法分析")
        try:
            parsed = self._call_deepseek_parse(ocr_text)
            logger.info(f"[{task_id}] DeepSeek返回数据: {json.dumps(parsed, ensure_ascii=False)[:500]}")
            credit_score = _first_int(parsed.get("credit_score"), self._calc_score(parsed))
            risk_level = parsed.get("risk_level") or self._get_risk_level(credit_score)
            risk_warnings = parsed.get("risk_warnings") or self._gen_risk_warnings(parsed, credit_score)
            suggestions = self._generate_suggestions(parsed, credit_score)
            logger.info(f"[{task_id}] 分析完成: score={credit_score}, level={risk_level}")
            result = {
                "task_id": task_id or "", "status": "completed",
                "personal_info": parsed.get("personal_info", {}),
                "credit_summary": parsed.get("credit_summary", {}),
                "overdue_records": parsed.get("overdue_records", {}),
                "query_records": parsed.get("query_records", {}),
                "public_records": parsed.get("public_records", {}),
                "credit_score": credit_score, "risk_level": risk_level,
                "risk_warnings": risk_warnings, "suggestions": suggestions
            }
            logger.info(f"[{task_id}] 最终结果: keys={list(result.keys())}, personal_info={result.get('personal_info', {})}")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return self._empty_result(task_id, f"AI返回格式异常: {str(e)}")
        except Exception as e:
            logger.error(f"AI分析请求失败: {e}")
            return self._empty_result(task_id, f"AI分析失败: {str(e)}")

    # ─── DeepSeek 调用 ──────────────────────────────────────

    def _call_deepseek_parse(self, ocr_text: str) -> dict:
        self._init_api()
        logger.info(f"调用DeepSeek解析，文本长度: {len(ocr_text)}")
        max_chars = 15000
        if len(ocr_text) > max_chars:
            ocr_text = ocr_text[:max_chars] + "\n\n[文本过长已截断...]"
        
        # 使用原生requests调用DeepSeek API
        url = f"{self._api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ocr_text}
            ],
            "temperature": 0.1,
            "max_tokens": 4096
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        result_text = result["choices"][0]["message"]["content"]
        return json.loads(self._clean_response(result_text))

    @staticmethod
    def _clean_response(text: str) -> str:
        text = text.strip()
        text = re.sub(r'^```(?:json)?\s*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)
        return text.lstrip('\ufeff')

    # ─── 后端兜底评分算法 ─────────────────────────────────

    @staticmethod
    def _calc_score(data: dict) -> int:
        """后端兜底 0-1000 评分（当 AI 未返回时使用）"""
        score = 600
        try:
            od = data.get("overdue_records", {})
            count = od.get("overdue_count", 0)
            months = od.get("max_overdue_months", 0)
            amount = od.get("max_monthly_amount", 0)
            if count > 0:
                score -= 80
                if count >= 10:      score -= 100
                elif count >= 5:     score -= 60
                elif count >= 2:     score -= 30
                if months > 6:       score -= 100
                elif months > 3:     score -= 60
                elif months > 1:     score -= 30
                if amount > 100000:  score -= 60
                elif amount > 50000: score -= 40
                elif amount > 10000: score -= 20

            cs = data.get("credit_summary", {})
            cards = cs.get("credit_cards", [])
            mrtgs = cs.get("mortgages", [])
            others = cs.get("other_loans", [])
            all_loans = cards + mrtgs + others
            if len(cards) > 0 and len(mrtgs) > 0: score += 20
            if len(all_loans) >= 5: score += 30

            qr = data.get("query_records", {})
            q6 = qr.get("recent_6months", 0)
            if q6 > 15:         score -= 100
            elif q6 > 10:       score -= 70
            elif q6 > 5:        score -= 30
            elif q6 <= 2:       score += 10

            pr = data.get("public_records", {})
            if pr.get("has_enforcement"):           score -= 100
            if pr.get("has_administrative_penalty"): score -= 60
            if pr.get("has_tax_arrears"):           score -= 50
        except Exception as e:
            logger.warning(f"评分计算异常: {e}")
        return max(0, min(1000, score))

    @staticmethod
    def _get_risk_level(score: int) -> str:
        if score >= 750: return "低"
        if score >= 600: return "中"
        return "高"

    @staticmethod
    def _gen_risk_warnings(data: dict, score: int) -> list:
        """后端兜底风险提示生成"""
        w = []
        od = data.get("overdue_records", {})
        cnt = od.get("overdue_count", 0)
        if cnt > 0:
            w.append(f"存在{cnt}笔逾期记录，最长逾期{od.get('max_overdue_months',0)}个月")
            if od.get("max_overdue_months", 0) > 3:
                w.append("存在较长时间逾期，信贷审批将受重大影响")
        qr = data.get("query_records", {})
        if qr.get("recent_6months", 0) > 10:
            w.append("近6个月机构查询过于频繁")
        pr = data.get("public_records", {})
        if pr.get("has_enforcement"):
            w.append("存在强制执行记录，信用评估受影响")
        if pr.get("has_tax_arrears"):
            w.append("存在欠税记录，影响信用评级")
        if score < 400:
            w.append("综合评分较低，建议联系金融机构了解信用修复方案")
        if not w:
            w.append("未发现明显风险点，信用状况良好")
        return w

    # ─── 优化建议 ───────────────────────────────────────────

    def _generate_suggestions(self, data: dict, score: int) -> list:
        s = []
        od = data.get("overdue_records", {})
        if od.get("overdue_count", 0) > 0:
            s.extend(OPTIMIZATION_TEMPLATES["overdue"])
        cs = data.get("credit_summary", {})
        cards = cs.get("credit_cards", [])
        has_high_usage = any((c.get("avg_6month_usage_rate") or 0) > 0.7 for c in cards)
        if has_high_usage:
            s.extend(OPTIMIZATION_TEMPLATES["high_debt"])
        qr = data.get("query_records", {})
        if qr.get("recent_6months", 0) > 5:
            s.extend(OPTIMIZATION_TEMPLATES["frequent_query"])
        pr = data.get("public_records", {})
        if pr.get("has_enforcement") or pr.get("has_administrative_penalty") or pr.get("has_tax_arrears"):
            s.extend(OPTIMIZATION_TEMPLATES["public_negative"])
        if len(cards) + len(cs.get("mortgages", [])) + len(cs.get("other_loans", [])) == 0:
            s.extend(OPTIMIZATION_TEMPLATES["no_credit"])
        seen = set()
        unique = []
        for x in s:
            if x not in seen:
                seen.add(x)
                unique.append(x)
        if score >= 750:
            unique.append("当前信用评分较高，建议继续保持良好的还款习惯")
        return unique

    # ─── 降级方案：正则提取 ────────────────────────────────

    @staticmethod
    def extract_fields_by_regex(ocr_text: str) -> dict:
        return {
            "personal_info": {
                "name": _rx_first(ocr_text, [r'姓名[：:\s]*([\u4e00-\u9fa5]{2,4})']),
                "id_card": _mask_id(_rx_first(ocr_text, [r'身份证号码[：:\s]*(\d{17}[\dXx])'])),
                "gender": _rx_first(ocr_text, [r'性别[：:\s]*(男|女)']),
                "marital_status": _rx_first(ocr_text, [r'婚姻[：:\s]*(已婚|未婚|离异|丧偶)']) or "未知",
                "address": _rx_first(ocr_text, [r'(?:通讯|居住|户籍)地址[：:\s]*([\u4e00-\u9fa5\d\s\-]+?)(?:\n|$)']),
            },
            "credit_summary": {"credit_cards": [], "mortgages": [], "other_loans": []},
            "overdue_records": {"overdue_count": 0, "max_overdue_months": 0, "max_monthly_amount": 0},
            "query_records": {"recent_1month": 0, "recent_6months": 0, "query_reasons": []},
            "public_records": {"has_enforcement": False, "has_administrative_penalty": False, "has_tax_arrears": False},
            "credit_score": 600, "risk_level": "低", "risk_warnings": []
        }

    def _empty_result(self, task_id: Optional[str], msg: str) -> dict:
        return {
            "task_id": task_id or "", "status": "failed",
            "personal_info": {"name": None, "id_card": None, "gender": None, "marital_status": "未知", "address": None},
            "credit_summary": {"credit_cards": [], "mortgages": [], "other_loans": []},
            "overdue_records": {"overdue_count": 0, "max_overdue_months": 0, "max_monthly_amount": 0},
            "query_records": {"recent_1month": 0, "recent_6months": 0, "query_reasons": []},
            "public_records": {"has_enforcement": False, "has_administrative_penalty": False, "has_tax_arrears": False},
            "credit_score": 0, "risk_level": "未知",
            "risk_warnings": [msg], "suggestions": ["请重试或联系客服"],
            "error_message": msg
        }


def _rx_first(text: str, patterns: list) -> Optional[str]:
    for p in patterns:
        m = re.search(p, text)
        if m: return m.group(1).strip()
    return None


def _mask_id(id_str: Optional[str]) -> Optional[str]:
    if not id_str or len(id_str) < 8: return id_str
    return id_str[-4:]


def _first_int(val, fallback: int) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return fallback


# 全局实例
ai_service = AiAnalysisService()
