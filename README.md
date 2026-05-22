# naki-ai-search

一个 Python FastAPI + LangChain + Vue 3 的 AI 搜索引擎示例。用户输入自然语言问题后，后端调用 Tavily 获取最新网页结果，再把编号后的搜索结果注入 DeepSeek V4，前端用 SSE 实时展示 AI 回答、引用来源、完整搜索结果、搜索历史和相关问题。

## 功能

- 居中搜索主页和高密度结果页
- Tavily 联网搜索，保留完整结果列表
- DeepSeek V4 OpenAI 兼容接口流式生成回答
- 回答内使用 `[1]`、`[2]` 形式标注来源
- SSE 打字机输出
- 本地搜索历史
- 回答完成后生成 3-5 个相关问题

## 环境变量

复制后端示例配置：

```powershell
Copy-Item backend\.env.example backend\.env
```

填写：

```env
TAVILY_API_KEY=tvly-your-key
DEEPSEEK_API_KEY=sk-your-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
```

## 后端启动

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

健康检查：

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## 前端启动

```powershell
cd frontend
npm install
npm run dev
```

默认访问：

```text
http://localhost:5173
```

如后端地址不是 `http://localhost:8000`，在 `frontend/.env` 中配置：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 测试

```powershell
cd backend
pytest
```

```powershell
cd frontend
npm run build
```
