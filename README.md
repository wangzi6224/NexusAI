# my_python_project

一个从零开始创建的 Python 工程。

## 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Week 1：FastAPI + Ollama 模型调用服务

### 目标

完成一个最小 AI Chat Backend：

```text
用户请求 -> FastAPI -> LLMProvider -> Ollama -> 返回回答
