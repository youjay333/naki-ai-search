# naki-ai-search

基于 **FastAPI + LangChain + DeepSeek V4 + Vue 3** 的 AI 搜索引擎。用户输入自然语言问题，后端调用 [Tavily](https://tavily.com/) 获取最新网页结果，注入 DeepSeek V4 生成带引用标注的综合回答，前端通过 SSE 实时流式展示。

## 功能

- 实时联网搜索，保留完整搜索结果列表
- DeepSeek V4 流式生成回答（SSE 打字机效果）
- 回答内 `[1]`、`[2]` 形式引用来源
- 智能来源筛选：仅展示回答引用的结果
- 回答完成后自动生成 3-5 个相关问题
- 本地搜索历史（localStorage，最多 12 条）
- 响应式布局，支持深色/浅色模式

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.12+, FastAPI, LangChain, httpx |
| AI | DeepSeek V4（OpenAI 兼容接口）, Tavily Search API |
| 前端 | Vue 3 (Composition API), Vite, markdown-it, highlight.js |
| 测试 | pytest, pytest-asyncio, httpx.ASGITransport |

## 快速开始

### 1. 克隆

```bash
git clone https://github.com/youjay333/naki-ai-search.git
cd naki-ai-search
```

### 2. 配置后端

```powershell
cd backend
Copy-Item .env.example .env
```

编辑 `.env`，填入你的 API Key：

```env
TAVILY_API_KEY=tvly-your-key
DEEPSEEK_API_KEY=sk-your-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
```

### 3. 启动后端

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

健康检查：

```powershell
Invoke-RestMethod http://localhost:8000/health
# {"status":"ok"}
```

### 4. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173 即可使用。

> 如后端地址不是 `http://localhost:8000`，在 `frontend/.env` 中配置：
> ```env
> VITE_API_BASE_URL=http://localhost:8000
> ```

## 项目结构

```
naki-ai-search/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 应用入口，SSE 流式接口
│   │   ├── config.py        # pydantic-settings 配置
│   │   ├── models.py        # 请求/响应 Pydantic 模型
│   │   ├── search.py        # Tavily 搜索封装
│   │   ├── ai.py            # DeepSeek V4 流式回答 + 相关问题
│   │   └── sse.py           # SSE 事件格式化
│   ├── tests/
│   │   └── test_core.py     # pytest 测试
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 主页面（搜索/结果双视图）
│   │   ├── components/
│   │   │   ├── SearchBox.vue
│   │   │   └── MarkdownBlock.vue
│   │   └── utils/
│   │       ├── sse.js       # SSE 流式解析
│   │       └── history.js   # 本地搜索历史
│   ├── index.html
│   └── package.json
└── README.md
```

## SSE 事件流

`POST /api/search/stream` 按以下顺序推送事件：

| 事件 | 数据 | 说明 |
|------|------|------|
| `status` | `{"message": "正在联网搜索"}` | 状态指示 |
| `results` | `{"query": "...", "results": [...]}` | 搜索结果（含 id/title/url/content/score） |
| `token` | `{"text": "..."}` | AI 回答流式 token |
| `related` | `{"questions": ["q1", "q2", ...]}` | 3-5 个相关问题 |
| `done` | `{"answer": "..."}` | 完成（含最终清洗后的回答） |
| `error` | `{"message": "..."}` | 错误信息 |

## 引用系统

Tavily 返回的结果按顺序编号 `[1]`、`[2]`...，DeepSeek 的回答中引用格式为 `[1]` 或 `[2][4]`。`sanitize_citations()` 会剔除超出实际结果范围的无效引用。

前端根据回答内容自动计算 `citedSourceIds`，默认只展示被引用的来源；所有结果可在"完整结果"下查阅。

## 测试

```powershell
cd backend
pytest -v
```

测试覆盖：Tavily 数据归一化、上下文构建、SSE 格式化、引用清洗、健康检查。

```powershell
cd frontend
npm run build
```

前端构建作为冒烟测试。

## 许可证

MIT
