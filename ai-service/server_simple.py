"""
信用解析 - 完整后端服务
OCR + AI分析 + 用户系统 + 支付订单
"""
import os
import json
import uuid
import hashlib
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta

from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Credit Analysis Service", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 配置 ==========
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_api_key_here")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

DB_PATH = Path(os.getenv("DB_PATH", "./credit_app.db"))

# ========== SQLite 数据库 ==========

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nickname TEXT DEFAULT '',
            avatar_url TEXT DEFAULT '',
            token TEXT UNIQUE,
            token_expires TEXT,
            balance REAL DEFAULT 0,
            free_queries INTEGER DEFAULT 3,
            is_vip INTEGER DEFAULT 0,
            vip_expires TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            order_type TEXT DEFAULT 'query',
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            task_id TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            paid_at TEXT
        );
        CREATE TABLE IF NOT EXISTS consume_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS invite_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inviter_id INTEGER NOT NULL,
            invitee_phone TEXT,
            commission REAL DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
    """)
    conn.commit()
    conn.close()

init_db()

# ========== 工具函数 ==========

def hash_password(phone: str, password: str) -> str:
    return hashlib.sha256(f"{phone}:{password}:credit_salt".encode()).hexdigest()

def generate_token(user_id: int) -> str:
    token = uuid.uuid4().hex
    expires = (datetime.now() + timedelta(days=30)).isoformat()
    conn = get_db()
    conn.execute("UPDATE users SET token=?, token_expires=? WHERE id=?", (token, expires, user_id))
    conn.commit()
    conn.close()
    return token

def verify_token(token: str):
    if not token:
        return None
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE token=?", (token,)).fetchone()
    conn.close()
    if row and row["token_expires"] and row["token_expires"] > datetime.now().isoformat():
        return dict(row)
    return None

def require_user(token: str = Header(None)):
    user = verify_token(token)
    if not user:
        raise HTTPException(401, "请先登录")
    return user

# ========== OCR 文字提取 ==========

def extract_pdf_text(filepath: str) -> str:
    text = ""
    try:
        import fitz
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        if text.strip(): return text.strip()
    except ImportError: pass
    
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: text += t + "\n"
        if text.strip(): return text.strip()
    except ImportError: pass
    
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(filepath)
        for page in reader.pages:
            t = page.extract_text()
            if t: text += t + "\n"
        if text.strip(): return text.strip()
    except ImportError: pass
    
    return text.strip()

def extract_image_text(filepath: str) -> str:
    text = ""
    try:
        from easyocr import Reader
        reader = Reader(['ch_sim', 'en'], gpu=False, verbose=False)
        result = reader.readtext(filepath)
        lines = [item[1] for item in result]
        text = "\n".join(lines)
        if text.strip(): return text.strip()
    except (ImportError, Exception): pass
    
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
        result = ocr.ocr(filepath, cls=True)
        if result and result[0]:
            lines = [line[1][0] for line in result[0] if line and len(line) >= 2]
            text = "\n".join(lines)
            if text.strip(): return text.strip()
    except (ImportError, Exception): pass
    
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        if text.strip(): return text.strip()
    except (ImportError, Exception): pass
    
    return text.strip()

# ========== DeepSeek AI 分析 ==========

def analyze_with_ai(raw_text: str) -> dict:
    if not raw_text or len(raw_text) < 20:
        return _mock_analysis("Text too short")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_BASE)
        prompt = f"""You are a professional credit report analyst. Extract key information from the following credit report OCR text and return as JSON.

Required fields:
1. personal: name (masked), id_number (masked last 4 digits), marriage, education
2. credit: credit_cards (count), loans (count), repayment_status
3. overdue: has_overdue (bool), details
4. credit_score: 0-950 score
5. risk_level: low/medium/high
6. risk_warnings: list of strings
7. suggestions: 2-3 optimization suggestions

=== Credit Report Text ===
{raw_text[:8000]}

Return ONLY valid JSON, no other text:
{{"personal":{{"name":"Zhang**","id_number":"330***********1234","marriage":"married","education":"bachelor"}},"credit":{{"credit_cards":3,"loans":2,"repayment_status":"normal"}},"overdue":{{"has_overdue":false,"details":"no overdue"}},"credit_score":782,"risk_level":"low","risk_warnings":["recent inquiries: 3/month"],"suggestions":["maintain on-time payments","limit credit inquiries"]}}
"""
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL, messages=[{"role":"user","content":prompt}],
            temperature=0.3, max_tokens=2000
        )
        result_text = response.choices[0].message.content.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1]
            if result_text.endswith("```"): result_text = result_text[:-3]
        return json.loads(result_text)
    except Exception as e:
        print(f"AI analysis failed: {e}")
        return _mock_analysis(str(e)[:100])

def _mock_analysis(note: str = "") -> dict:
    return {
        "personal": {"name":"Zhang**","id_number":"330***********1234","marriage":"married","education":"bachelor"},
        "credit": {"credit_cards":3,"loans":2,"repayment_status":"normal"},
        "overdue": {"has_overdue":False,"details":"No overdue records"},
        "credit_score":782,"risk_level":"low",
        "risk_warnings":["Recent credit inquiries: 3/month"],
        "suggestions":["Maintain on-time payments","Control inquiry frequency","Use credit cards wisely"],
        "_note": f"Mock data (AI unavailable: {note})"
    }

def _calculate_score(result: dict) -> int:
    """当AI未返回credit_score时的兜底评分算法"""
    score = 700
    
    # 根据风险等级调整分数
    risk_level = result.get('risk_level', 'medium')
    if risk_level == 'low':
        score += 50
    elif risk_level == 'high':
        score -= 100
    
    # 根据逾期情况调整
    overdue = result.get('overdue', {})
    if overdue.get('has_overdue'):
        score -= 150
        details = overdue.get('details', '')
        if '90天' in details or '严重' in details:
            score -= 100
    
    # 根据风险警告数量调整
    warnings = result.get('risk_warnings', [])
    score -= len(warnings) * 20
    
    # 根据信贷记录调整
    credit = result.get('credit', {})
    cards = credit.get('credit_cards', 0)
    loans = credit.get('loans', 0)
    if cards > 0:
        score += 10
    if loans > 0:
        score += 10
    if cards >= 3 and loans >= 2:
        score += 20
    
    # 限制分数范围在300-900之间
    return max(300, min(900, score))

# ========== Pydantic Models ==========

class RegisterReq(BaseModel):
    phone: str
    password: str
    nickname: str = ""

class LoginReq(BaseModel):
    phone: str
    password: str

class PayReq(BaseModel):
    order_type: str = "query"

class RechargeReq(BaseModel):
    package_id: int = 1

class CreateOrderReq(BaseModel):
    order_type: str = "query"

# ========== 用户 API ==========

@app.post("/api/user/register")
def register(req: RegisterReq):
    if len(req.phone) != 11 or not req.phone.isdigit():
        raise HTTPException(400, "Invalid phone number")
    if len(req.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    
    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE phone=?", (req.phone,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(400, "Phone already registered")
    
    pw_hash = hash_password(req.phone, req.password)
    nick = req.nickname or f"User{req.phone[-4:]}"
    conn.execute(
        "INSERT INTO users (phone, password_hash, nickname, free_queries) VALUES (?,?,?,3)",
        (req.phone, pw_hash, nick)
    )
    conn.commit()
    user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    token = generate_token(user_id)
    user = dict(conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone())
    conn.close()
    
    return {"token": token, "user": {"id": user["id"], "phone": user["phone"],
            "nickname": user["nickname"], "balance": user["balance"],
            "free_queries": user["free_queries"], "is_vip": bool(user["is_vip"])}}

@app.post("/api/user/login")
def login(req: LoginReq):
    conn = get_db()
    pw_hash = hash_password(req.phone, req.password)
    user = conn.execute("SELECT * FROM users WHERE phone=? AND password_hash=?", 
                        (req.phone, pw_hash)).fetchone()
    if not user:
        conn.close()
        raise HTTPException(401, "Phone or password incorrect")
    token = generate_token(user["id"])
    user_dict = dict(user)
    conn.close()
    
    return {"token": token, "user": {"id": user_dict["id"], "phone": user_dict["phone"],
            "nickname": user_dict["nickname"], "balance": user_dict["balance"],
            "free_queries": user_dict["free_queries"], "is_vip": bool(user_dict["is_vip"])}}

@app.get("/api/user/info")
def get_user_info(user: dict = Depends(require_user)):
    return {"id": user["id"], "phone": user["phone"], "nickname": user["nickname"],
            "balance": user["balance"], "free_queries": user["free_queries"],
            "is_vip": bool(user["is_vip"]), "vip_expires": user["vip_expires"]}

@app.post("/api/user/logout")
def logout(token: str = Header(None)):
    if token:
        conn = get_db()
        conn.execute("UPDATE users SET token=NULL, token_expires=NULL WHERE token=?", (token,))
        conn.commit()
        conn.close()
    return {"message": "Logged out"}

# ========== 支付/订单 API ==========

@app.get("/api/pay/packages")
def get_packages():
    return {"packages": [
        {"id":1,"name":"Single Query","price":9.90,"queries":1,"desc":"1 credit report query"},
        {"id":2,"name":"3-Pack","price":29.70,"queries":3,"desc":"3 queries, save 0%"},
        {"id":3,"name":"5-Pack","price":59.00,"queries":5,"desc":"5 queries, best value"},
        {"id":4,"name":"VIP Monthly","price":29.90,"queries":-1,"desc":"Unlimited queries for 30 days"}
    ]}

@app.post("/api/pay/recharge")
def recharge(req: RechargeReq, user: dict = Depends(require_user)):
    packages = {1:(9.90,1),2:(29.70,3),3:(59.00,5),4:(29.90,-1)}
    if req.package_id not in packages:
        raise HTTPException(400, "Invalid package")
    
    amount, queries = packages[req.package_id]
    conn = get_db()
    
    if req.package_id == 4:  # VIP
        vip_expires = (datetime.now() + timedelta(days=30)).isoformat()
        conn.execute("UPDATE users SET is_vip=1, vip_expires=?, balance=balance+? WHERE id=?",
                     (vip_expires, amount, user["id"]))
    else:
        conn.execute("UPDATE users SET balance=balance+?, free_queries=free_queries+? WHERE id=?",
                     (amount, queries, user["id"]))
    
    # Order
    order_no = f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"
    conn.execute(
        "INSERT INTO orders (order_no,user_id,order_type,amount,status,paid_at) VALUES (?,?,?,?,?,datetime('now','localtime'))",
        (order_no, user["id"], "recharge", amount, "paid"))
    
    # Consume log
    conn.execute("INSERT INTO consume_log (user_id,type,name,amount) VALUES (?,?,?,?)",
                 (user["id"], "recharge", f"Package #{req.package_id}", amount))
    conn.commit()
    
    updated = dict(conn.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone())
    conn.close()
    
    return {"success": True, "order_no": order_no, "amount": amount,
            "balance": updated["balance"], "free_queries": updated["free_queries"],
            "is_vip": bool(updated["is_vip"])}

@app.post("/api/pay/create-order")
def create_order(req: CreateOrderReq, user: dict = Depends(require_user)):
    user_data = dict(user)
    is_vip = bool(user_data.get("is_vip", False))
    free = user_data.get("free_queries", 0)
    
    if not is_vip and free <= 0:
        raise HTTPException(400, "No free queries, please recharge")
    
    order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"
    amount = 0 if (is_vip or free > 0) else 9.90
    status = "paid" if amount == 0 else "pending"
    
    conn = get_db()
    conn.execute(
        "INSERT INTO orders (order_no,user_id,order_type,amount,status%s) VALUES (?,?,?,?,?)" % (",paid_at" if status=="paid" else ""),
        (order_no, user_data["id"], req.order_type, amount, status, *([datetime.now().isoformat()] if status=="paid" else [])))
    
    if is_vip:
        pass
    else:
        conn.execute("UPDATE users SET free_queries=free_queries-1 WHERE id=?", (user_data["id"],))
        conn.execute("INSERT INTO consume_log (user_id,type,name,amount) VALUES (?,?,?,?)",
                     (user_data["id"], "query", "Credit report query", -amount if amount > 0 else 0))
    conn.commit()
    conn.close()
    
    return {"order_no": order_no, "amount": amount, "status": status}

@app.get("/api/pay/orders")
def get_orders(user: dict = Depends(require_user)):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC LIMIT 50",
        (user["id"],)).fetchall()
    conn.close()
    return {"orders": [dict(r) for r in rows]}

@app.get("/api/pay/consume-log")
def get_consume_log(user: dict = Depends(require_user)):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM consume_log WHERE user_id=? ORDER BY created_at DESC LIMIT 50",
        (user["id"],)).fetchall()
    conn.close()
    return {"items": [dict(r) for r in rows]}

# ========== 邀请 API ==========

@app.get("/api/invite/stats")
def invite_stats(user: dict = Depends(require_user)):
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM invite_records WHERE inviter_id=?", 
                         (user["id"],)).fetchone()[0]
    total_commission = conn.execute(
        "SELECT COALESCE(SUM(commission),0) FROM invite_records WHERE inviter_id=?",
        (user["id"],)).fetchone()[0]
    conn.close()
    return {"invite_count": count, "total_commission": round(total_commission, 2),
            "invite_code": f"INV{user['id']:06d}"}

# ========== OCR/分析 API（保留原有） ==========

task_store = {}

@app.get("/")
def root():
    return {"service": "Credit Analysis Service", "version": "3.0", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/api/ocr/upload")
async def upload_report(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Filename required")
    ext = Path(file.filename).suffix.lower()
    if ext not in ['.pdf','.jpg','.jpeg','.png']:
        raise HTTPException(400, f"Unsupported format: {ext}")
    
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = UPLOAD_DIR / f"{timestamp}_{task_id}{ext}"
    
    content = await file.read()
    if len(content) > 50*1024*1024:
        raise HTTPException(400, "File exceeds 50MB")
    save_path.write_bytes(content)
    
    task_store[task_id] = {
        "task_id": task_id, "filename": file.filename,
        "filepath": str(save_path), "file_type": ext.lstrip('.'),
        "status": "uploaded", "created_at": datetime.now().isoformat(), "result": None
    }
    print(f"[Upload] {task_id} <- {file.filename} ({len(content)} bytes)")
    return {"task_id": task_id, "filename": file.filename, "status": "uploaded"}

async def do_analysis(task_id: str):
    """异步执行分析任务"""
    task = task_store.get(task_id)
    if not task:
        return
    
    fp, ext = task["filepath"], task["file_type"]
    print(f"[Analyze] {task_id} - Extracting...")
    
    raw_text = extract_pdf_text(fp) if ext == "pdf" else extract_image_text(fp)
    print(f"[Analyze] {task_id} - Text: {len(raw_text)} chars")
    
    if not raw_text or len(raw_text) < 20:
        print(f"[Analyze] {task_id} - Using mock data")
        result = _mock_analysis("Cannot extract sufficient text")
    else:
        print(f"[Analyze] {task_id} - Calling DeepSeek...")
        result = analyze_with_ai(raw_text)
        print(f"[Analyze] {task_id} - AI返回数据: {json.dumps(result)[:500]}")
        
        # 兜底：如果AI返回的credit_score无效（None或0），计算一个默认分数
        if result.get('credit_score') is None or result.get('credit_score') == 0:
            print(f"[Analyze] {task_id} - AI返回的credit_score无效({result.get('credit_score')})，使用兜底评分")
            result['credit_score'] = _calculate_score(result)
    
    task["result"] = result
    task["status"] = "completed"
    task["completed_at"] = datetime.now().isoformat()
    print(f"[Analyze] {task_id} - Done (score: {result.get('credit_score','N/A')})")

@app.post("/api/ocr/analyze/{task_id}")
async def analyze_report(task_id: str, background_tasks: BackgroundTasks):
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    
    task["status"] = "processing"
    
    # 使用后台任务异步执行分析
    background_tasks.add_task(do_analysis, task_id)
    
    # 立即返回processing状态，让前端轮询
    return {"task_id": task_id, "status": "processing"}

@app.get("/api/ocr/result/{task_id}")
async def get_result(task_id: str):
    task = task_store.get(task_id)
    if not task: raise HTTPException(404, "Task not found")
    if task["status"] != "completed":
        return {"task_id": task_id, "status": task["status"]}
    r = task["result"]
    return {
        "task_id": task_id, "status": "completed",
        "credit_score": r.get("credit_score", 0),
        "risk_level": r.get("risk_level", "unknown"),
        "personal_info": r.get("personal", {}),
        "credit_records": r.get("credit", {}),
        "overdue_records": r.get("overdue", {}),
        "risk_warnings": r.get("risk_warnings", []),
        "suggestions": r.get("suggestions", [])
    }

@app.delete("/api/ocr/task/{task_id}")
async def delete_task(task_id: str):
    task = task_store.pop(task_id, None)
    if not task: raise HTTPException(404, "Task not found")
    fp = task.get("filepath", "")
    if fp and os.path.exists(fp): os.remove(fp)
    return {"task_id": task_id, "deleted": True}

# ========== 启动 ==========

if __name__ == "__main__":
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8081"))
    print(f"[Server] Credit Analysis Service v3.0 starting...")
    print(f"    Address: http://{host}:{port}")
    print(f"    Docs: http://{host}:{port}/docs")
    print(f"    DB: {DB_PATH}")
    print(f"    DeepSeek: {'Configured' if DEEPSEEK_API_KEY.startswith('sk-') else 'Not configured'}")
    uvicorn.run(app, host=host, port=port, log_level="info")
