"""
DeepSeek 结构化输出测试脚本
测试目的：
  - 验证 DeepSeek 对征信报告 OCR 文字的结构化提取能力
  - 测试流式输出（stream=True）与非流式输出的差异
  - 验证 JSON Schema 字段的完整性

使用方法：
  python tests/test_deepseek_structured.py
"""
import os
import sys
import json
import time

# 确保能导入项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# ─── 配置 ───────────────────────────────────────────────────
API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

if not API_KEY or API_KEY == "your_deepseek_api_key_here":
    print("❌ 请先配置 DEEPSEEK_API_KEY 环境变量")
    sys.exit(1)

print(f"🔧 配置: model={MODEL}, base={API_BASE}")
print(f"🔑 API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
print()

# ─── 模拟征信报告 OCR 数据 ─────────────────────────────────
MOCK_OCR_TEXT = """
个人信用报告
（本人查询）

被查询者信息：
姓名：张三
身份证号码：310115199003152578
婚姻状况：已婚
手机号码：13812345678
通讯地址：上海市浦东新区陆家嘴金融城100号

────────────────────────────────────────
信贷记录汇总：
共有账户数：8 个（其中激活账户数：6 个，结清账户数：2 个）
首次信贷记录时间：2015年3月
授信总额度：850,000.00 元
已使用额度：320,000.00 元

────────────────────────────────────────
信用卡明细：
1. 招商银行 贷记卡
   授信额度：100,000.00 元
   已使用额度：45,200.00 元
   账户状态：正常
   逾期记录：0次

2. 建设银行 贷记卡
   授信额度：80,000.00 元
   已使用额度：12,000.00 元
   账户状态：正常
   逾期记录：0次

3. 交通银行 准贷记卡
   授信额度：50,000.00 元
   已使用额度：50,000.00 元
   账户状态：逾期
   逾期记录：2次

────────────────────────────────────────
贷款明细：
一、住房贷款：
1. 中国工商银行 个人住房贷款
   贷款金额：2,000,000.00 元
   贷款余额：1,520,000.00 元
   月还款额：12,500.00 元
   账户状态：正常
   逾期记录：0次

二、汽车贷款：
1. 上汽通用汽车金融 汽车贷款
   贷款金额：180,000.00 元
   贷款余额：60,000.00 元
   账户状态：正常
   逾期记录：0次

三、其他贷款：
1. 蚂蚁集团 消费贷款
   贷款金额：50,000.00 元
   贷款余额：25,000.00 元
   账户状态：正常
   逾期记录：0次

────────────────────────────────────────
逾期记录：
1. 2025年3月 交通银行信用卡逾期
   逾期金额：12,500.00 元
   逾期天数：35 天
   当前状态：已结清

2. 2025年8月 交通银行信用卡逾期
   逾期金额：8,200.00 元
   逾期天数：15 天
   当前状态：未结清

────────────────────────────────────────
查询记录（近6个月）：
1. 2026-05-15  招商银行         信用卡审批
2. 2026-04-20  中国工商银行     贷款审批
3. 2026-03-10  中国建设银行     信用卡审批
4. 2026-02-28  蚂蚁集团         贷款审批
5. 2026-01-15  中国银行         信用卡审批
6. 2025-12-20  上海浦东发展银行 信用卡审批
7. 2025-12-05  本人查询

────────────────────────────────────────
公共记录：
无破产记录
无诉讼记录
无税务欠款记录
无强制执行记录
"""

# ─── System Prompt（v2 版本，来自 ai_service.py） ─────────────
SYSTEM_PROMPT = """你是一个专业的征信报告分析专家。请根据以下 OCR 识别出的征信报告文字内容，提取并结构化输出以下字段。

## 需要提取的字段

### 1. 个人信息
- name: 姓名
- id_card: 身份证号（脱敏显示仅保留后4位，其余用 **** 替代，未识别填null）
- gender: 性别（男/女，未识别填null）
- marital_status: 婚姻状况（已婚/未婚/离异/丧偶/未知）
- address: 居住地址

### 2. 信贷记录汇总 credit_summary
- credit_cards: 信用卡列表，每项含 issuing_institution, credit_limit, used_amount, avg_6month_usage_rate
- mortgages: 住房贷款列表，每项含 institution, loan_amount, balance, status
- other_loans: 其他贷款列表，每项含 type, amount, balance, status

### 3. 逾期记录 overdue_records
- overdue_count: 逾期笔数（整数）
- max_overdue_months: 最长逾期月数（整数）
- max_monthly_amount: 单月最高逾期金额（元）

### 4. 查询记录 query_records
- recent_1month: 近1个月查询次数（排除本人查询和贷后管理）
- recent_6months: 近6个月查询次数（排除本人查询和贷后管理）
- query_reasons: [{reason, count}] 查询原因分类

### 5. 公共记录 public_records
- has_enforcement, has_administrative_penalty, has_tax_arrears

### 6. 信用评估（AI 直接输出）
- credit_score: 0-1000（整数）
- risk_level: 低/中/高
- risk_warnings: 风险提示字符串数组（无风险时 [])）

## 输出格式（纯JSON，不要```json```标记）
{
  "personal_info": {"name": null, "id_card": null, "gender": null, "marital_status": "未知", "address": null},
  "credit_summary": {"credit_cards": [], "mortgages": [], "other_loans": []},
  "overdue_records": {"overdue_count": 0, "max_overdue_months": 0, "max_monthly_amount": 0},
  "query_records": {"recent_1month": 0, "recent_6months": 0, "query_reasons": []},
  "public_records": {"has_enforcement": false, "has_administrative_penalty": false, "has_tax_arrears": false},
  "credit_score": 600,
  "risk_level": "低",
  "risk_warnings": []
}

## 规则
1. 身份证号只保留后4位，前14位用 **** 替代
2. 金额纯数字，单位"元"
3. 空数组用 []，字符串未识别用 null"""


# ─── 测试 1: 非流式请求 ─────────────────────────────────────
def test_non_streaming():
    """测试非流式（一次返回完整 JSON）"""
    print("=" * 60)
    print("📋 测试 1: 非流式请求 (stream=False)")
    print("=" * 60)

    from openai import OpenAI

    client = OpenAI(api_key=API_KEY, base_url=API_BASE)
    start = time.time()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": MOCK_OCR_TEXT}
            ],
            temperature=0.1,
            max_tokens=4096,
            stream=False
        )

        elapsed = time.time() - start
        content = response.choices[0].message.content
        usage = response.usage

        print(f"⏱️ 耗时: {elapsed:.2f}s")
        print(f"📊 Token: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}")
        print(f"📏 返回文本长度: {len(content)}")
        print()

        # 解析 JSON
        cleaned = content.strip()
        if cleaned.startswith("```"):
            import re
            cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned)
            cleaned = re.sub(r'\n?```\s*$', '', cleaned)

        try:
            parsed = json.loads(cleaned)
            print("✅ JSON 解析成功")
            print()

            # 验证关键字段
            _validate_fields(parsed)

            # 美化输出
            print("── 个人信息 ──")
            pi = parsed.get("personal_info", {})
            print(f"  姓名: {pi.get('name')}")
            print(f"  身份证(后4位): {pi.get('id_card')}")
            print(f"  性别: {pi.get('gender')}")
            print(f"  婚姻: {pi.get('marital_status')}")
            print(f"  地址: {pi.get('address')}")

            print("── 信贷汇总 ──")
            cs = parsed.get("credit_summary", {})
            print(f"  信用卡: {len(cs.get('credit_cards', []))} 张")
            for c in cs.get("credit_cards", []):
                print(f"    {c.get('issuing_institution')}: 额度{c.get('credit_limit')}元, 已用{c.get('used_amount')}元, 使用率{c.get('avg_6month_usage_rate')}")
            print(f"  房贷: {len(cs.get('mortgages', []))} 笔")
            for m in cs.get("mortgages", []):
                print(f"    {m.get('institution')}: 金额{m.get('loan_amount')}元, 余额{m.get('balance')}元, {m.get('status')}")
            print(f"  其他贷款: {len(cs.get('other_loans', []))} 笔")

            print("── 逾期记录 ──")
            od = parsed.get("overdue_records", {})
            print(f"  笔数: {od.get('overdue_count')}, 最长: {od.get('max_overdue_months')}个月, 最高金额: {od.get('max_monthly_amount')}元")

            print("── 查询记录 ──")
            qr = parsed.get("query_records", {})
            print(f"  近1月: {qr.get('recent_1month')} 次, 近6月: {qr.get('recent_6months')} 次")

            print("── AI 信用评估 ──")
            print(f"  评分: {parsed.get('credit_score')}, 风险等级: {parsed.get('risk_level')}")
            rw = parsed.get('risk_warnings', [])
            if rw: print(f"  风险提示: {', '.join(rw)}")

            # 保存完整结果
            return True, parsed

        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")
            print(f"原始返回:\n{content[:500]}")
            return False, None

    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False, None


# ─── 测试 2: 流式请求 ───────────────────────────────────────
def test_streaming():
    """测试流式输出（逐 token 返回）"""
    print()
    print("=" * 60)
    print("📋 测试 2: 流式请求 (stream=True)")
    print("=" * 60)

    from openai import OpenAI

    client = OpenAI(api_key=API_KEY, base_url=API_BASE)
    start = time.time()

    full_content = ""
    chunk_count = 0
    last_print_len = 0

    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": MOCK_OCR_TEXT}
            ],
            temperature=0.1,
            max_tokens=4096,
            stream=True,
            stream_options={"include_usage": True}  # 获取最终 usage
        )

        usage = None
        for chunk in stream:
            chunk_count += 1
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    full_content += delta.content
                    # 每 100 字符打印一次进度
                    if len(full_content) - last_print_len >= 100:
                        last_print_len = len(full_content)
                        print(f"  ...已接收 {len(full_content)} 字符")

            # 最后一个 chunk 可能包含 usage
            if hasattr(chunk, 'usage') and chunk.usage:
                usage = chunk.usage

        elapsed = time.time() - start
        print(f"⏱️ 耗时: {elapsed:.2f}s")
        print(f"📦 接收 chunk 数: {chunk_count}")
        if usage:
            print(f"📊 Token: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}")
        print(f"📏 最终文本长度: {len(full_content)}")
        print()

        # 解析 JSON
        cleaned = full_content.strip()
        if cleaned.startswith("```"):
            import re
            cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned)
            cleaned = re.sub(r'\n?```\s*$', '', cleaned)

        try:
            parsed = json.loads(cleaned)
            print("✅ 流式 JSON 解析成功")
            return True, parsed
        except json.JSONDecodeError as e:
            print(f"❌ 流式 JSON 解析失败: {e}")
            print(f"原始返回前500字符:\n{full_content[:500]}")
            return False, None

    except Exception as e:
        print(f"❌ 流式请求失败: {e}")
        return False, None


# ─── 测试 3: JSON Mode 结构化输出 ───────────────────────────
def test_json_mode():
    """测试 response_format=json_object（DeepSeek 的 JSON Mode）"""
    print()
    print("=" * 60)
    print("📋 测试 3: JSON Mode (response_format=json_object)")
    print("=" * 60)

    from openai import OpenAI

    # JSON Mode 要求 prompt 中必须包含 "json" 关键字
    json_system = SYSTEM_PROMPT + "\n\n你必须输出合法的 JSON 对象。"

    client = OpenAI(api_key=API_KEY, base_url=API_BASE)
    start = time.time()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": json_system},
                {"role": "user", "content": MOCK_OCR_TEXT}
            ],
            temperature=0.1,
            max_tokens=4096,
            stream=False,
            response_format={"type": "json_object"}  # JSON Mode
        )

        elapsed = time.time() - start
        content = response.choices[0].message.content
        usage = response.usage

        print(f"⏱️ 耗时: {elapsed:.2f}s")
        print(f"📊 Token: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}")
        print(f"📏 返回文本长度: {len(content)}")
        print()

        try:
            parsed = json.loads(content)
            print("✅ JSON Mode 解析成功（无需清理 markdown）")

            # 对比：JSON Mode 不会带 ```json 标记
            print(f"  返回文本是否以 '{{' 开头: {content.strip().startswith('{')}")
            print(f"  返回文本是否以 '}}' 结尾: {content.strip().endswith('}')}")

            return True, parsed
        except json.JSONDecodeError as e:
            print(f"❌ JSON Mode 解析失败: {e}")
            return False, None

    except Exception as e:
        print(f"❌ JSON Mode 请求失败（可能模型不支持）: {e}")
        return False, None


# ─── 字段校验 ───────────────────────────────────────────────
def _validate_fields(data: dict):
    """校验必填字段是否存在（v2 结构）"""
    required_top = [
        "personal_info", "credit_summary", "overdue_records",
        "query_records", "public_records", "credit_score", "risk_level", "risk_warnings"
    ]
    required_personal = ["name", "id_card", "gender", "marital_status", "address"]
    required_overdue = ["overdue_count", "max_overdue_months", "max_monthly_amount"]
    required_query = ["recent_1month", "recent_6months"]
    errors = []
    for f in required_top:
        if f not in data:
            errors.append(f"  缺少顶层字段: {f}")
    for f in required_personal:
        if f not in data.get("personal_info", {}):
            errors.append(f"  缺少 personal_info.{f}")
    for f in required_overdue:
        if f not in data.get("overdue_records", {}):
            errors.append(f"  缺少 overdue_records.{f}")
    for f in required_query:
        if f not in data.get("query_records", {}):
            errors.append(f"  缺少 query_records.{f}")
    if errors:
        print("⚠️ 字段缺失:")
        for e in errors: print(e)
    else:
        print("✅ 所有必填字段完整")
    print()


# ─── 主函数 ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 DeepSeek 结构化输出测试")
    print(f"  模型: {MODEL}")
    print(f"  API: {API_BASE}")
    print()

    results = {}

    # 测试 1: 非流式
    ok1, data1 = test_non_streaming()
    results["non_streaming"] = ok1

    # 测试 2: 流式
    ok2, data2 = test_streaming()
    results["streaming"] = ok2

    # 测试 3: JSON Mode
    ok3, data3 = test_json_mode()
    results["json_mode"] = ok3

    # ─── 汇总 ──────────────────────────────────────────────
    print()
    print("=" * 60)
    print("📊 测试汇总")
    print("=" * 60)
    for name, ok in results.items():
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {name}: {status}")

    # 保存完整结果到文件
    if data1 or data2 or data3:
        combined = {
            "non_streaming": data1 if data1 else None,
            "streaming": data2 if data2 else None,
            "json_mode": data3 if data3 else None,
        }
        output_path = os.path.join(os.path.dirname(__file__), "test_output.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)
        print(f"\n📁 完整结果已保存到: {output_path}")
