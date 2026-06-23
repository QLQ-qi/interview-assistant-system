# 面试辅助系统 (Interview Assistant System)

一个基于腾讯会议开放平台API + 本地LLM的**实时面试辅助系统**。

## 核心功能

- 🎙️ **实时转写**：腾讯会议语音 → 实时文字转写
- 🔍 **知识库检索**：标准话术、历史案例、岗位资料的多维匹配
- 🤖 **本地LLM推理**：基于上下文生成面试官实时提醒
- 📊 **实时看板**：面试官看到建议话术、关键点提示
- 💾 **知识库沉淀**：新录音自动归档，持续优化知识库

## 系统架构

```
腾讯会议 → 实时转写API → Webhook推送 → 本地系统
                                    ↓
                          ┌─────────┼─────────┐
                          ↓         ↓         ↓
                      实时记录   知识库检索  本地LLM
                          ↓         ↓         ↓
                          └─────────┼─────────┘
                                    ↓
                          WebSocket推送 → 前端看板
```

## 快速开始

### 环境要求
- Python 3.10+
- PostgreSQL 13+
- Redis 6.0+
- CUDA 11.8+ (GPU推荐，用于LLM推理)

### 本地开发

1. **克隆仓库**
   ```bash
   git clone https://github.com/QLQ-qi/interview-assistant-system.git
   cd interview-assistant-system
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量** (.env)
   ```
   TENCENT_MEETING_APP_ID=your_app_id
   TENCENT_MEETING_APP_SECRET=your_app_secret
   DATABASE_URL=postgresql://user:password@localhost/interview_db
   REDIS_URL=redis://localhost:6379
   LLM_MODEL=qwen:latest
   LLM_API_URL=http://localhost:11434
   ```

4. **启动服务**
   ```bash
   # 方式1：Docker Compose (推荐)
   docker-compose up -d
   
   # 方式2：本地启动
   python -m uvicorn app.main:app --reload
   ```

5. **验证服务**
   ```bash
   curl http://localhost:8000/health
   ```

## 项目结构

```
interview-assistant-system/
├── README.md                      # 项目说明
├── docs/
│   ├── ARCHITECTURE.md           # 详细架构设计
│   ├── API.md                    # API文档
│   ├── DEPLOYMENT.md             # 部署指南
│   └── KNOWLEDGE_BASE.md          # 知识库管理指南
├── app/
│   ├── main.py                   # FastAPI入口
│   ├── config.py                 # 配置管理
│   ├── webhooks/                 # Webhook处理
│   │   ├── __init__.py
│   │   ├── handler.py            # Webhook处理器
│   │   └── models.py             # Webhook数据模型
│   ├── transcription/            # 转写处理
│   │   ├── __init__.py
│   │   ├── processor.py          # 转写处理逻辑
│   │   ├── models.py             # 数据模型
│   │   └── service.py            # 业务逻辑
│   ├── knowledge_base/           # 知识库服务
│   │   ├── __init__.py
│   │   ├── retriever.py          # 检索服务
│   │   ├── embeddings.py         # 向量化服务
│   │   └── manager.py            # 知识库管理
│   ├── llm/                      # LLM推理
│   │   ├── __init__.py
│   │   ├── service.py            # LLM服务
│   │   ├── prompts.py            # Prompt模板
│   │   └── models.py             # LLM相关模型
│   ├── realtime/                 # 实时通信
│   │   ├── __init__.py
│   │   ├── websocket_manager.py  # WebSocket连接管理
│   │   └── push_service.py       # 推送服务
│   ├── database/                 # 数据库
│   │   ├── __init__.py
│   │   ├── models.py             # SQLAlchemy ORM模型
│   │   ├── init_db.py            # 数据库初始化
│   │   └── session.py            # 数据库会话
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # 日志工具
│       └── security.py           # 安全工具
├── tests/                        # 测试
│   ├── __init__.py
│   ├── test_webhook.py           # Webhook单元测试
│   ├── test_transcription.py     # 转写处理测试
│   ├── test_knowledge_base.py    # 知识库检索测试
│   └── test_llm.py               # LLM服务测试
├── docker-compose.yml            # Docker编排
├── Dockerfile                    # Docker镜像
├── requirements.txt              # Python依赖
├── .env.example                  # 环境变量示例
└── LICENSE                       # MIT License
```

## 核心模块

### 1. Webhook处理 (`app/webhooks/`)
- 腾讯会议事件推送接收
- HMAC-SHA256签名验证
- 事件类型识别和分发

### 2. 转写处理 (`app/transcription/`)
- 实时转写文本存储
- 会话状态管理
- 知识库查询触发

### 3. 知识库服务 (`app/knowledge_base/`)
- 多维检索（关键词 + 向量）
- 标准话术库、案例库、岗位资料库
- 向量化和相似度搜索

### 4. LLM推理 (`app/llm/`)
- 本地LLM集成 (Ollama / vLLM)
- Prompt工程和优化
- 流式生成提醒

### 5. 实时推送 (`app/realtime/`)
- WebSocket连接管理
- 转写内容和提醒的实时推送
- 消息广播

## 腾讯会议集成

### Webhook配置
1. 登录腾讯会议开放平台
2. 创建应用
3. 配置Webhook URL：`https://your-domain/webhooks/tencent-meeting`
4. 订阅事件：
   - `meeting.started` - 会议开始
   - `transcription.received` - 实时转写
   - `recording.completed` - 录制完成
5. 获取Token和Secret

### 环境变量
```
TENCENT_MEETING_APP_ID=<your_app_id>
TENCENT_MEETING_APP_SECRET=<your_app_secret>
TENCENT_MEETING_WEBHOOK_TOKEN=<webhook_token>
TENCENT_MEETING_WEBHOOK_ENCODING_AES_KEY=<aes_key>
```

## 前端接入

### WebSocket连接
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/meeting/<session_id>');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'transcription') {
    // 实时显示转写文本
    displayTranscription(message.text);
  } else if (message.type === 'hint') {
    // 显示提醒建议
    displayHint(message.hint);
  }
};
```

## 知识库管理

### 导入标准话术
```bash
curl -X POST http://localhost:8000/api/knowledge-base/import-talks \
  -F "file=@standard_talks.csv"
```

### 导入历史案例
```bash
curl -X POST http://localhost:8000/api/knowledge-base/import-cases \
  -F "recording=@interview_001.mp3" \
  -F "metadata={\"position_id\":\"pos_123\",\"outcome\":\"pass\"}"
```

## 部署

详见 [DEPLOYMENT.md](docs/DEPLOYMENT.md)

### 快速部署（Docker）
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 技术栈

- **后端**：FastAPI, Python 3.10+
- **数据库**：PostgreSQL, Redis
- **向量存储**：Milvus / FAISS
- **LLM**：Ollama / vLLM (本地部署)
- **实时通信**：WebSocket
- **前端**：React / Vue 3 (待实现)
- **部署**：Docker, Kubernetes

## 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 📧 Email: your-email@example.com
- 💬 Issues: [GitHub Issues](https://github.com/QLQ-qi/interview-assistant-system/issues)

## 致谢

- 腾讯会议开放平台
- Ollama / vLLM 团队
- 开源社区贡献者
