# CreditLens - 征信报告AI智能解析平台

基于 PaddleOCR + DeepSeek 实现征信报告结构化提取与深度分析，采用 uni-app 前端 + Java CRMEB 后端 + Python AI 服务三层架构。

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────┐
│                   用户层                          │
│   uni-app小程序 / H5 / APP (Vue 2 + SCSS)        │
└─────────────────┬───────────────────────────────┘
                  │ HTTP / REST API
┌─────────────────▼───────────────────────────────┐
│                Java 业务层                        │
│         CRMEB后端 (Spring Boot)                   │
│    用户/订单/VIP/支付/报告管理                    │
└─────────────────┬───────────────────────────────┘
                  │ HTTP / gRPC
┌─────────────────▼───────────────────────────────┐
│              Python AI 服务层                     │
│        FastAPI (端口 8081)                        │
│   PaddleOCR 文字识别 + DeepSeek 结构化解析        │
└─────────────────────────────────────────────────┘
```

## 📁 项目结构

```
CreditLens/
├── credit-app/              # uni-app 前端 (Vue 2 + SCSS)
│   ├── src/
│   │   ├── pages/           # 10个核心页面
│   │   │   ├── index/       # 首页
│   │   │   ├── upload/      # 报告上传
│   │   │   ├── progress/    # 分析进度
│   │   │   ├── result/      # 分析结果
│   │   │   ├── records/     # 历史记录
│   │   │   ├── profile/     # 个人中心
│   │   │   ├── login/       # 登录页
│   │   │   ├── settings/    # 设置页
│   │   │   ├── about/       # 关于我们
│   │   │   └── vip-center/  # 会员中心
│   │   ├── api/             # API 接口层
│   │   ├── components/      # 公共组件
│   │   └── pages.json       # 路由配置
│   ├── package.json
│   └── vite.config.ts
│
├── crmeb_java/              # Java CRMEB 后端
│   └── Controller/Service/  # 征信业务模块
├── ai-service/              # Python AI 服务
│   ├── app.py               # FastAPI 主入口 (端口 8081)
│   ├── services/
│   │   ├── ocr_service.py   # PaddleOCR 识别
│   │   ├── credit_agent.py  # DeepSeek 代理
│   │   └── ai_service.py    # AI 综合分析
│   └── config/              # 解析规则配置
│
├── database/                # 数据库脚本
│   ├── schema.sql           # 表结构
│   └── create_tables.sql    # 建表语句
│
├── credit-report-ai/        # AI 解析前端原型
├── docs/                    # 项目文档
└── start-all.bat            # Windows 一键启动
```

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | uni-app (Vue 2) + SCSS | 跨端小程序/H5/APP |
| 后端 | Java Spring Boot (CRMEB) | 用户/订单/支付管理 |
| AI服务 | Python FastAPI | OCR + NLP 智能解析 |
| OCR引擎 | PaddleOCR | 高精度文字识别 |
| AI模型 | DeepSeek API | 结构化数据提取 |
| 数据库 | MySQL | 业务数据持久化 |
| 缓存 | Redis | Token/会话管理 |

## 🚀 快速启动

### 前置要求

- Node.js ≥ 16
- Java JDK ≥ 8
- Python ≥ 3.10
- MySQL ≥ 5.7
- Redis

### 一键启动 (Windows)

```bash
./start-all.bat
```

### 手动启动

```bash
# 1. AI 服务
cd ai-service
pip install -r requirements.txt
python app.py                    # http://localhost:8081

# 2. Java 后端
cd crmeb_java
mvn spring-boot:run              # http://localhost:20510

# 3. 前端
cd credit-app
npm install
npm run dev:h5                   # 打开浏览器调试
npm run dev:mp-weixin            # 微信开发者工具
```

## ✨ 核心功能

- **报告上传解析** — 支持PDF/图片格式征信报告上传，自动OCR识别
- **AI深度解读** — DeepSeek 智能分析借贷记录、逾期风险、信用评分
- **历史记录管理** — 报告存档、对比分析、导出分享
- **VIP会员体系** — 月度/年度套餐，不同查询次数权益
- **微信授权登录** — 小程序/H5双端支持

## ⚠️ 待配置

| 配置项 | 文件 | 说明 |
|--------|------|------|
| 小程序AppID | `credit-app/src/manifest.json` | 微信小程序AppID |
| 公众号AppID | `credit-app/src/pages/login/login.vue` | H5端OAuth |
| DeepSeek API Key | `ai-service/.env` | AI解析服务 |
| 数据库连接 | `crmeb_java` 配置文件 | MySQL + Redis |

## 📄 License

Apache-2.0
