# CreditLens - 征信报告AI智能解析平台

[![GitHub Stars](https://img.shields.io/github/stars/jiangmingtao40-blip/CreditLens?style=social)](https://github.com/jiangmingtao40-blip/CreditLens)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

基于 **PaddleOCR + DeepSeek** 实现征信报告结构化提取与深度分析，采用 uni-app 前端 + Java CRMEB 后端 + Python AI 服务三层架构。

## 🎯 项目介绍

CreditLens 是一款智能征信报告分析工具，帮助用户快速解读征信报告，获取专业的信用评估和建议。

### 核心特性

- 📄 **智能OCR识别** - 支持PDF和图片格式的征信报告自动识别
- 🤖 **AI深度分析** - 基于DeepSeek智能解析信用数据
- 📊 **风险评估** - 自动生成信用评分和风险等级
- 💡 **优化建议** - 提供个性化的信用提升建议
- 📱 **多端支持** - 支持小程序、H5、APP多端使用

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
                  │ HTTP / REST API
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
│   └── package.json
│
├── crmeb_java/              # Java CRMEB 后端
│   └── crmeb/
│       └── crmeb-front/     # 征信业务接口
│
├── ai-service/              # Python AI 服务 ⭐ 核心
│   ├── server_simple.py      # FastAPI 主入口
│   ├── services/
│   │   ├── ai_service.py    # AI 分析服务
│   │   └── credit_agent.py  # Agent 架构
│   ├── utils/
│   │   └── cache_util.py    # 缓存工具
│   ├── config/              # 解析规则配置
│   └── requirements.txt     # Python 依赖
│
├── credit-report-ai/        # Web 原型演示
├── database/                # 数据库脚本
└── start-all.bat            # Windows 一键启动
```

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端框架** | uni-app (Vue 2) + SCSS | 跨端小程序/H5/APP |
| **UI组件** | Vant Weapp | 微信小程序组件库 |
| **后端框架** | Java Spring Boot (CRMEB) | 用户/订单/支付管理 |
| **AI服务** | Python FastAPI | OCR + NLP 智能解析 |
| **OCR引擎** | PaddleOCR | 高精度文字识别 |
| **AI模型** | DeepSeek API | 结构化数据提取 |
| **数据库** | MySQL | 业务数据持久化 |
| **缓存** | Redis | Token/会话管理 |

## 🚀 快速启动

### 前置要求

- Node.js ≥ 16
- Java JDK ≥ 8
- Python ≥ 3.10
- MySQL ≥ 5.7
- Redis（可选，有内存缓存降级）

### 环境配置

1. **克隆项目**
```bash
git clone https://github.com/jiangmingtao40-blip/CreditLens.git
cd CreditLens
```

2. **配置 AI 服务**
```bash
cd ai-service
cp .env.example .env  # 或手动创建 .env 文件
```

编辑 `.env` 文件：
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
SERVER_PORT=8081
```

3. **安装 Python 依赖**
```bash
cd ai-service
pip install -r requirements.txt
```

4. **安装前端依赖**
```bash
cd credit-app
npm install
```

### 启动服务

#### 一键启动 (Windows)
```bash
./start-all.bat
```

#### 手动启动

**1. 启动 AI 服务** (必需)
```bash
cd ai-service
python server_simple.py
# 服务地址：http://localhost:8081
```

**2. 启动 Java 后端** (可选，用户系统/VIP功能)
```bash
cd crmeb_java/crmeb
mvn clean package -DskipTests -pl crmeb-front -am
java -jar crmeb-front/target/Crmeb-front.jar --spring.profiles.active=dev
# 服务地址：http://localhost:20510
```

**3. 启动前端**
```bash
cd credit-app
npm run dev:h5    # H5 开发模式 → http://localhost:5173
npm run dev:mp-weixin  # 微信小程序模式
```

## 📖 使用说明

### API 接口

| 接口 | 方法 | 说明 | 必需 |
|------|------|------|------|
| `/api/ocr/upload` | POST | 上传征信报告 | ✅ |
| `/api/ocr/analyze/{task_id}` | POST | 异步分析报告 | ✅ |
| `/api/ocr/result/{task_id}` | GET | 查询分析结果 | ✅ |
| `/api/credit/quota` | GET | 查询用户额度 | ❌ |
| `/api/credit/commission` | GET | 查询佣金信息 | ❌ |

### 返回数据格式

```json
{
  "task_id": "xxx",
  "status": "completed",
  "credit_score": 782,
  "risk_level": "低",
  "personal_info": {
    "name": "张**",
    "id_number": "110***********1234",
    "marriage": "已婚",
    "education": "本科"
  },
  "credit_records": {
    "credit_cards": 3,
    "loans": 2,
    "repayment_status": "正常"
  },
  "overdue_records": {
    "has_overdue": false,
    "details": ""
  },
  "risk_warnings": [],
  "suggestions": [
    "建议保持良好的还款习惯",
    "信用卡数量适中，建议维持现状"
  ]
}
```

## ✨ 核心功能

### 1. 报告上传解析
- 支持 PDF 和图片格式（JPG/PNG）
- 自动 OCR 文字识别
- 异步处理，无需等待

### 2. AI 深度解读
- 智能提取个人信息
- 自动识别信贷记录
- 逾期记录分析
- 风险等级评估

### 3. 信用评分系统
- 基于多维度评分模型
- 750分以上：低风险
- 600-750分：中风险
- 600分以下：高风险

### 4. 历史记录管理
- 报告存档
- 历史对比分析
- 数据导出

### 5. VIP 会员体系 (需要Java后端)
- 月度/年度套餐
- 不同查询次数权益
- 邀请有礼

## ⚠️ 注意事项

### 安全提示
- `.env` 文件包含敏感信息，已加入 `.gitignore`
- 请勿将 API Key 提交到公共仓库
- 生产环境请使用环境变量或密钥管理服务

### 常见问题

**Q: 上传报告后没有响应？**
A: 检查 AI 服务是否启动，确保端口 8081 可用

**Q: 分析结果为空？**
A: 检查 DeepSeek API Key 是否配置正确

**Q: 前端显示连接被拒绝？**
A: 确认所有服务都已启动，可参考「启动服务」章节

## 📝 待配置项

| 配置项 | 文件位置 | 说明 |
|--------|----------|------|
| DeepSeek API Key | `ai-service/.env` | AI 解析服务必需 |
| 小程序 AppID | `credit-app/src/manifest.json` | 微信小程序必需 |
| 数据库连接 | `crmeb_java` 配置文件 | MySQL 连接信息 |
| Redis 连接 | `ai-service/.env` | 缓存服务（可选） |

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 License

本项目采用 Apache-2.0 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 高精度OCR引擎
- [DeepSeek](https://platform.deepseek.com/) - 强大的AI分析能力
- [uni-app](https://uniapp.dcloud.net.cn/) - 跨端开发框架
- [CRMEB](https://www.crmeb.com/) - Java电商系统

---

**如果这个项目对你有帮助，请给个 Star ⭐**
