"""
征信报告分析 Agent
基于 LangChain Agent + Tool Calling 框架，编排 OCR 识别 + DeepSeek AI 分析全链路（v2 提示词）
"""
import os
import json
import re
import logging
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_tools_agent
from langchain.agents import AgentExecutor
from langchain_core.output_parsers import StrOutputParser

from .langchain_ocr import get_ocr_tools

logger = logging.getLogger(__name__)

# ─── Agent 系统提示词 ───────────────────────────────────────
AGENT_SYSTEM_PROMPT = """你是一个专业的征信报告分析系统。你的任务是协助用户完成征信报告的OCR识别和结构化分析。

## 可用工具
- `ocr_extract_text`: 自动识别 PDF 或图片中的文字内容（统一入口）

## 工作流程
1. 用户提供文件路径后，先调用 `ocr_extract_text` 工具提取文字
2. 获取 OCR 文本后，按照下方 JSON Schema 进行结构化分析
3. 直接输出最终的 JSON 分析结果

## 输出格式
{
  "personal_info": {
    "name": null,
    "id_card": null,
    "gender": null,
    "marital_status": "未知",
    "address": null
  },
  "credit_summary": {
    "credit_cards": [],
    "mortgages": [],
    "other_loans": []
  },
  "overdue_records": {
    "overdue_count": 0,
    "max_overdue_months": 0,
    "max_monthly_amount": 0
  },
  "query_records": {
    "recent_1month": 0,
    "recent_6months": 0,
    "query_reasons": []
  },
  "public_records": {
    "has_enforcement": false,
    "has_administrative_penalty": false,
    "has_tax_arrears": false
  },
  "credit_score": 600,
  "risk_level": "低",
  "risk_warnings": []
}

## 字段说明
- credit_cards[]: issuing_institution, credit_limit, used_amount, avg_6month_usage_rate
- mortgages[]: institution, loan_amount, balance, status
- other_loans[]: type, amount, balance, status
- overdue_records: overdue_count(笔数), max_overdue_months(最长逾期月数), max_monthly_amount(最高金额)
- query_records: recent_1month, recent_6months(排除本人查询/贷后管理), query_reasons[{reason, count}]
- public_records: has_enforcement, has_administrative_penalty, has_tax_arrears
- credit_score: 0-1000, 750+低风险, 600-750中, <600高
- risk_warnings: 字符串数组，无风险则为空数组 []

## 分析规则
1. 身份证号脱敏仅保留后4位
2. 金额单位为"元"，纯数字
3. avg_6month_usage_rate = 近6月月均已用 / 授信额度
4. 空数组用 []，字符串空值用 null
5. 输出纯 JSON，不要 markdown 代码块标记
6. 输出 JSON 后不要附加任何说明"""


class CreditAnalysisAgent:
    """征信报告分析 Agent —— v2 提示词"""

    def __init__(self):
        self._llm = None
        self._agent_executor = None

    def _get_llm(self) -> ChatOpenAI:
        if self._llm is None:
            api_key = os.getenv("DEEPSEEK_API_KEY", "")
            api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
            model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            if not api_key or api_key == "your_deepseek_api_key_here":
                raise ValueError("请先配置 DEEPSEEK_API_KEY 环境变量")
            self._llm = ChatOpenAI(
                model_name=model, openai_api_key=api_key,
                openai_api_base=api_base, temperature=0.1,
                max_tokens=4096, request_timeout=180
            )
            logger.info(f"[Agent] LLM 初始化: model={model}")
        return self._llm

    def _get_agent_executor(self) -> AgentExecutor:
        if self._agent_executor is None:
            llm = self._get_llm()
            tools = get_ocr_tools()
            prompt = ChatPromptTemplate.from_messages([
                ("system", AGENT_SYSTEM_PROMPT),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            agent = create_openai_tools_agent(llm, tools, prompt)
            self._agent_executor = AgentExecutor(
                agent=agent, tools=tools, verbose=True,
                handle_parsing_errors=True, max_iterations=6,
                return_intermediate_steps=False,
            )
            logger.info("[Agent] Agent 构建完成")
        return self._agent_executor

    # ─── 主分析入口 ─────────────────────────────────────────

    def analyze(self, file_path: str, task_id: Optional[str] = None) -> dict:
        if not os.path.exists(file_path):
            return self._error_result(task_id, f"文件不存在: {file_path}")
        logger.info(f"[Agent] 开始分析: task_id={task_id}")
        try:
            result = self._run_agent_pipeline(file_path)
            credit_score = _first_int(result.get("credit_score"), self._calc_score(result))
            risk_level = result.get("risk_level") or self._get_risk_level(credit_score)
            risk_warnings = result.get("risk_warnings") or self._gen_risk_warnings(result, credit_score)
            suggestions = self._gen_suggestions(result, credit_score)
            return {
                "task_id": task_id or "", "status": "completed",
                "personal_info": result.get("personal_info", {}),
                "credit_summary": result.get("credit_summary", {}),
                "overdue_records": result.get("overdue_records", {}),
                "query_records": result.get("query_records", {}),
                "public_records": result.get("public_records", {}),
                "credit_score": credit_score, "risk_level": risk_level,
                "risk_warnings": risk_warnings, "suggestions": suggestions,
            }
        except json.JSONDecodeError as e:
            return self._error_result(task_id, f"AI返回格式异常: {str(e)}")
        except Exception as e:
            return self._error_result(task_id, f"分析异常: {str(e)}")

    def _run_agent_pipeline(self, file_path: str) -> dict:
        executor = self._get_agent_executor()
        input_text = (
            f"请帮我对以下征信报告文件进行OCR识别和结构化分析。\n\n"
            f"文件路径: {file_path}\n\n"
            f"请：1.调 ocr_extract_text 提取文字 2.按 JSON Schema 输出分析结果"
        )
        response = executor.invoke({"input": input_text})
        output = response.get("output", "")
        return self._parse_output(output)

    @staticmethod
    def _parse_output(output: str) -> dict:
        output = output.strip()
        output = re.sub(r'^```(?:json)?\s*\n?', '', output)
        output = re.sub(r'\n?```\s*$', '', output)
        m = re.search(r'\{[\s\S]*\}', output)
        return json.loads(m.group(0) if m else output)

    # ─── 兜底逻辑 ───────────────────────────────────────────

    @staticmethod
    def _calc_score(data: dict) -> int:
        score = 600
        try:
            od = data.get("overdue_records", {})
            cnt = od.get("overdue_count", 0)
            if cnt > 0:
                score -= 80
                if cnt >= 10: score -= 100
                elif cnt >= 5: score -= 60
                elif cnt >= 2: score -= 30
                m = od.get("max_overdue_months", 0)
                if m > 6: score -= 100
                elif m > 3: score -= 60
                elif m > 1: score -= 30
                amt = od.get("max_monthly_amount", 0)
                if amt > 100000: score -= 60
                elif amt > 50000: score -= 40
                elif amt > 10000: score -= 20
            cs = data.get("credit_summary", {})
            cards = cs.get("credit_cards", [])
            mrtgs = cs.get("mortgages", [])
            if len(cards) > 0 and len(mrtgs) > 0: score += 20
            if len(cards) + len(mrtgs) + len(cs.get("other_loans", [])) >= 5: score += 30
            qr = data.get("query_records", {})
            q6 = qr.get("recent_6months", 0)
            if q6 > 15: score -= 100
            elif q6 > 10: score -= 70
            elif q6 > 5: score -= 30
            pr = data.get("public_records", {})
            if pr.get("has_enforcement"): score -= 100
            if pr.get("has_administrative_penalty"): score -= 60
            if pr.get("has_tax_arrears"): score -= 50
        except Exception:
            pass
        return max(0, min(1000, score))

    @staticmethod
    def _get_risk_level(score: int) -> str:
        if score >= 750: return "低"
        if score >= 600: return "中"
        return "高"

    @staticmethod
    def _gen_risk_warnings(data: dict, score: int) -> list:
        w = []
        od = data.get("overdue_records", {})
        if od.get("overdue_count", 0) > 0:
            w.append(f"存在{od['overdue_count']}笔逾期，最长{od.get('max_overdue_months',0)}个月")
        qr = data.get("query_records", {})
        if qr.get("recent_6months", 0) > 10:
            w.append("近6月机构查询频繁")
        pr = data.get("public_records", {})
        if pr.get("has_enforcement"): w.append("存在强制执行记录")
        if pr.get("has_tax_arrears"): w.append("存在欠税记录")
        if score < 400: w.append("综合评分较低")
        if not w: w.append("未发现明显风险点")
        return w

    @staticmethod
    def _gen_suggestions(data: dict, score: int) -> list:
        s = []
        if data.get("overdue_records", {}).get("overdue_count", 0) > 0:
            s.append("立即结清逾期欠款，逾期记录将在结清后5年消除")
        cs = data.get("credit_summary", {})
        if any((c.get("avg_6month_usage_rate") or 0) > 0.7 for c in cs.get("credit_cards", [])):
            s.append("将信用卡使用率控制在70%以下")
        if data.get("query_records", {}).get("recent_6months", 0) > 5:
            s.append("减少不必要的信贷申请")
        pr = data.get("public_records", {})
        if pr.get("has_enforcement") or pr.get("has_administrative_penalty") or pr.get("has_tax_arrears"):
            s.append("尽快处理公共记录中的负面信息")
        if score >= 750: s.append("评分较高，继续保持")
        return s

    def _error_result(self, task_id: Optional[str], msg: str) -> dict:
        return {
            "task_id": task_id or "", "status": "failed",
            "personal_info": {}, "credit_summary": {},
            "overdue_records": {}, "query_records": {}, "public_records": {},
            "credit_score": 0, "risk_level": "未知",
            "risk_warnings": [msg], "suggestions": ["请重试"],
            "error_message": msg
        }


def _first_int(val, fallback: int) -> int:
    try: return int(val)
    except (TypeError, ValueError): return fallback


credit_agent = CreditAnalysisAgent()
