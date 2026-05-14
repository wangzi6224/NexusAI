import json
from src.app.services.chunk_splitter import ChunkSplitter

text = """# FastAPI 异常处理

1.FastAPI 可以通过 exception_handler 注册全局异常处理器。
2.FastAPI 可以通过 exception_handler 注册全局异常处理器。
3.FastAPI 可以通过 exception_handler 注册全局异常处理器。
4.FastAPI 可以通过 exception_handler 注册全局异常处理器。

## AppError

5.AppError 是我们自定义的业务异常基类。

## JSONResponse

6.JSONResponse 可以自定义异常返回的 JSON 结构。

## RequestValidationError

7.RequestValidationError 用来处理请求参数验证失败。
"""

splitter = ChunkSplitter()
chunks = splitter.split(text, "md")

print(json.dumps(chunks, ensure_ascii=False, indent=2))
