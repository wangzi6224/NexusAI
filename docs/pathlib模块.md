下面按你的当前阶段来讲：你已经有 **Python 工程基础、FastAPI、配置、日志、异常处理、Streaming/SSE** 这些基础，后面项目目录会逐步出现 `src/app/api`、`services/document`、`docs`、`eval`、`.env.example` 等结构；你的学习计划里也明确后续会做 **文档上传、解析文本、切分 chunk、保存 document/chunk**，并且第一版主要处理 `.md` / `.txt` 文件。`pathlib` 正好就是这些文件路径操作的核心工具。  

# 1. 先搞清楚：路径到底是什么？

路径就是“系统如何找到一个文件或目录”。

比如你的项目可能长这样：

```text
my_python_project/
├── src/
│   └── app/
│       ├── server.py
│       ├── core/
│       │   └── config.py
│       └── services/
│           └── document/
│               └── loader.py
├── docs/
│   └── dev-log.md
├── uploads/
│   └── frontend-style-guide.md
└── README.md
```

这里每一个文件都有一个“地址”：

```text
README.md
docs/dev-log.md
src/app/server.py
uploads/frontend-style-guide.md
```

这些就是路径。

---

# 2. 绝对路径 vs 相对路径

## 2.1 绝对路径

绝对路径是从系统根位置开始写的完整地址。

macOS / Linux：

```text
/Users/wangzilong/Projects/my_python_project/README.md
```

Windows：

```text
C:\Users\wangzilong\Projects\my_python_project\README.md
```

特点：

```text
从系统根位置开始
不依赖当前运行目录
路径很长
换机器后可能失效
```

---

## 2.2 相对路径

相对路径是相对于“当前工作目录”的路径。

比如你现在在：

```text
/Users/wangzilong/Projects/my_python_project
```

那么：

```text
README.md
```

实际指向：

```text
/Users/wangzilong/Projects/my_python_project/README.md
```

再比如：

```text
docs/dev-log.md
```

实际指向：

```text
/Users/wangzilong/Projects/my_python_project/docs/dev-log.md
```

特点：

```text
短
适合项目内部使用
但依赖当前工作目录 cwd
```

---

# 3. 一个初学者最容易混的点：当前工作目录 cwd

Python 里有一个非常重要的概念：

```python
Path.cwd()
```

它表示 **当前命令是从哪个目录执行的**。

注意：它不一定等于当前 `.py` 文件所在目录。

比如你有这个文件：

```text
my_python_project/
├── src/
│   └── app/
│       └── main.py
└── README.md
```

你在项目根目录执行：

```bash
python src/app/main.py
```

此时：

```python
from pathlib import Path

print(Path.cwd())
```

输出可能是：

```text
/Users/wangzilong/Projects/my_python_project
```

不是：

```text
/Users/wangzilong/Projects/my_python_project/src/app
```

所以：

```python
Path("README.md")
```

指的是：

```text
/Users/wangzilong/Projects/my_python_project/README.md
```

而不是：

```text
/Users/wangzilong/Projects/my_python_project/src/app/README.md
```

这点非常关键。

---

# 4. `pathlib` 是什么？

`pathlib` 是 Python 标准库里专门处理路径的模块。

传统写法通常用：

```python
import os

path = os.path.join("docs", "dev-log.md")
```

`pathlib` 的写法是：

```python
from pathlib import Path

path = Path("docs") / "dev-log.md"
```

你可以把 `Path` 理解成：

```text
一个“路径对象”
```

它不是普通字符串，而是一个带有很多路径操作能力的对象。

---

# 5. 最基础用法

## 5.1 创建一个路径对象

```python
from pathlib import Path

path = Path("README.md")
print(path)
```

输出：

```text
README.md
```

这里的 `path` 是一个 `Path` 对象。

你可以看类型：

```python
print(type(path))
```

macOS / Linux 上大概率是：

```text
<class 'pathlib.PosixPath'>
```

Windows 上大概率是：

```text
<class 'pathlib.WindowsPath'>
```

你不用太在意这个。通常直接用 `Path` 就行。

---

## 5.2 拼接路径

以前你可能会写：

```python
"docs" + "/" + "dev-log.md"
```

不推荐。

因为 Windows 是反斜杠：

```text
docs\dev-log.md
```

macOS / Linux 是正斜杠：

```text
docs/dev-log.md
```

`pathlib` 推荐这样：

```python
from pathlib import Path

path = Path("docs") / "dev-log.md"
print(path)
```

输出：

```text
docs/dev-log.md
```

在 Windows 上，它会自动适配成 Windows 风格。

重点：

```python
Path("docs") / "dev-log.md"
```

这里的 `/` 不是数学除法，而是 `pathlib` 重载后的“路径拼接”。

---

# 6. 路径对象的常用属性

假设：

```python
from pathlib import Path

path = Path("src/app/services/document/loader.py")
```

## 6.1 文件名：`name`

```python
print(path.name)
```

输出：

```text
loader.py
```

---

## 6.2 不带后缀的文件名：`stem`

```python
print(path.stem)
```

输出：

```text
loader
```

---

## 6.3 后缀：`suffix`

```python
print(path.suffix)
```

输出：

```text
.py
```

如果是：

```python
Path("README.md").suffix
```

结果是：

```text
.md
```

如果是：

```python
Path("archive.tar.gz").suffix
```

结果是：

```text
.gz
```

如果你要所有后缀：

```python
print(Path("archive.tar.gz").suffixes)
```

输出：

```text
['.tar', '.gz']
```

---

## 6.4 父目录：`parent`

```python
print(path.parent)
```

输出：

```text
src/app/services/document
```

再往上：

```python
print(path.parent.parent)
```

输出：

```text
src/app/services
```

---

## 6.5 所有父级目录：`parents`

```python
for parent in path.parents:
    print(parent)
```

输出类似：

```text
src/app/services/document
src/app/services
src/app
src
.
```

---

# 7. 判断路径是否存在

```python
from pathlib import Path

path = Path("README.md")

print(path.exists())
```

如果文件存在：

```text
True
```

如果不存在：

```text
False
```

---

# 8. 判断是文件还是目录

```python
path = Path("README.md")

print(path.is_file())
print(path.is_dir())
```

如果 `README.md` 是文件：

```text
True
False
```

目录示例：

```python
path = Path("src")

print(path.is_file())
print(path.is_dir())
```

如果 `src` 是目录：

```text
False
True
```

---

# 9. 获取绝对路径

```python
from pathlib import Path

path = Path("README.md")

print(path.resolve())
```

可能输出：

```text
/Users/wangzilong/Projects/my_python_project/README.md
```

`resolve()` 的作用是：

```text
把相对路径转成绝对路径
顺便解析 . 和 ..
```

例如：

```python
path = Path("src/app/../app/server.py")
print(path.resolve())
```

实际会变成：

```text
/Users/wangzilong/Projects/my_python_project/src/app/server.py
```

---

# 10. `.` 和 `..` 是什么意思？

## 10.1 `.` 当前目录

```text
.
```

表示当前目录。

```python
Path(".")
```

表示当前工作目录。

```python
Path(".").resolve()
```

等价于：

```python
Path.cwd()
```

---

## 10.2 `..` 上一级目录

```text
..
```

表示上一级目录。

比如你在：

```text
my_python_project/src/app
```

那么：

```text
..
```

就是：

```text
my_python_project/src
```

示例：

```python
from pathlib import Path

print(Path("..").resolve())
```

---

# 11. 当前工作目录：`Path.cwd()`

```python
from pathlib import Path

print(Path.cwd())
```

这个很重要。

在你的 FastAPI 项目里，如果你从项目根目录启动：

```bash
python -m uvicorn src.app.server:app --reload
```

那么 `Path.cwd()` 通常就是项目根目录：

```text
/Users/wangzilong/Projects/my_python_project
```

所以：

```python
Path("uploads")
```

指向：

```text
/Users/wangzilong/Projects/my_python_project/uploads
```

---

# 12. 当前文件路径：`__file__`

`__file__` 表示当前 `.py` 文件自己的路径。

假设文件是：

```text
src/app/core/config.py
```

里面写：

```python
from pathlib import Path

print(__file__)
```

可能输出：

```text
/Users/wangzilong/Projects/my_python_project/src/app/core/config.py
```

常用写法：

```python
CURRENT_FILE = Path(__file__).resolve()
CURRENT_DIR = CURRENT_FILE.parent

print(CURRENT_FILE)
print(CURRENT_DIR)
```

输出：

```text
/Users/wangzilong/Projects/my_python_project/src/app/core/config.py
/Users/wangzilong/Projects/my_python_project/src/app/core
```

---

# 13. 项目根目录怎么找？

这个是工程里非常常见的问题。

假设你的文件在：

```text
src/app/core/config.py
```

项目根目录是：

```text
my_python_project/
```

从 `config.py` 往上数：

```text
config.py
所在目录：src/app/core
上一级：src/app
上一级：src
上一级：my_python_project
```

所以可以写：

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
```

解释：

```python
Path(__file__).resolve()
```

得到当前文件绝对路径：

```text
/Users/wangzilong/Projects/my_python_project/src/app/core/config.py
```

```python
.parents[0]
```

是：

```text
/Users/wangzilong/Projects/my_python_project/src/app/core
```

```python
.parents[1]
```

是：

```text
/Users/wangzilong/Projects/my_python_project/src/app
```

```python
.parents[2]
```

是：

```text
/Users/wangzilong/Projects/my_python_project/src
```

```python
.parents[3]
```

是：

```text
/Users/wangzilong/Projects/my_python_project
```

所以：

```python
BASE_DIR = Path(__file__).resolve().parents[3]
```

就是项目根目录。

---

# 14. 推荐你项目里的标准写法

你的项目可以在 `src/app/core/config.py` 或 `src/app/core/paths.py` 里统一定义路径。

例如：

```python
from pathlib import Path

# 当前文件：src/app/core/paths.py
BASE_DIR = Path(__file__).resolve().parents[3]

SRC_DIR = BASE_DIR / "src"
APP_DIR = SRC_DIR / "app"

DOCS_DIR = BASE_DIR / "docs"
UPLOADS_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

ENV_FILE = BASE_DIR / ".env"
README_FILE = BASE_DIR / "README.md"
```

以后其他地方不要乱写：

```python
Path("../../uploads")
```

而是统一用：

```python
from src.app.core.paths import UPLOADS_DIR

file_path = UPLOADS_DIR / "frontend-style-guide.md"
```

这样路径会更稳定。

---

# 15. 创建目录

比如你要确保 `uploads/` 存在：

```python
from pathlib import Path

uploads_dir = Path("uploads")

uploads_dir.mkdir(exist_ok=True)
```

含义：

```text
如果 uploads 不存在，就创建
如果已经存在，不报错
```

如果要创建多级目录：

```python
path = Path("data/documents/raw")
path.mkdir(parents=True, exist_ok=True)
```

参数解释：

```text
parents=True：中间目录不存在也一起创建
exist_ok=True：目录已存在时不报错
```

如果不加：

```python
path.mkdir()
```

目录已经存在时会报错。

---

# 16. 写文件

## 16.1 写文本文件

```python
from pathlib import Path

path = Path("docs/dev-log.md")

path.write_text("今天完成了 pathlib 学习。", encoding="utf-8")
```

注意：推荐加：

```python
encoding="utf-8"
```

否则在不同系统上可能出现编码问题。

---

## 16.2 追加内容

`write_text()` 会覆盖原文件。

如果要追加，使用普通 `open`：

```python
from pathlib import Path

path = Path("docs/dev-log.md")

with path.open("a", encoding="utf-8") as f:
    f.write("\n继续学习文件路径操作。")
```

模式说明：

```text
"w"：写入，覆盖原内容
"a"：追加
"r"：读取
```

---

# 17. 读文件

```python
from pathlib import Path

path = Path("docs/dev-log.md")

content = path.read_text(encoding="utf-8")

print(content)
```

读取 `.md` / `.txt` 文件时，这个非常常用。

在你后面做文档上传、解析、chunk 切分时，会经常写类似逻辑。

---

# 18. 读写二进制文件

文本文件用：

```python
read_text()
write_text()
```

图片、PDF、压缩包等二进制文件用：

```python
read_bytes()
write_bytes()
```

例子：

```python
from pathlib import Path

source = Path("avatar.png")
target = Path("uploads/avatar.png")

data = source.read_bytes()
target.write_bytes(data)
```

---

# 19. 删除文件和目录

## 19.1 删除文件

```python
from pathlib import Path

path = Path("uploads/test.txt")

path.unlink()
```

如果文件不存在会报错。

更安全一点：

```python
if path.exists():
    path.unlink()
```

Python 新版本也支持：

```python
path.unlink(missing_ok=True)
```

---

## 19.2 删除空目录

```python
path = Path("uploads/temp")
path.rmdir()
```

注意：

```text
rmdir 只能删除空目录
```

如果目录里有文件，会报错。

---

# 20. 遍历目录

## 20.1 只遍历当前目录一层：`iterdir()`

```python
from pathlib import Path

docs_dir = Path("docs")

for item in docs_dir.iterdir():
    print(item)
```

可能输出：

```text
docs/architecture.md
docs/dev-log.md
docs/rag-design.md
```

可以判断文件还是目录：

```python
for item in docs_dir.iterdir():
    if item.is_file():
        print("文件:", item)
    elif item.is_dir():
        print("目录:", item)
```

---

## 20.2 匹配文件：`glob()`

查找当前目录下所有 `.md` 文件：

```python
from pathlib import Path

docs_dir = Path("docs")

for file in docs_dir.glob("*.md"):
    print(file)
```

只查当前层。

---

## 20.3 递归匹配文件：`rglob()`

查找整个项目下所有 `.py` 文件：

```python
from pathlib import Path

base_dir = Path.cwd()

for file in base_dir.rglob("*.py"):
    print(file)
```

`rglob()` 会递归子目录。

等价于：

```python
base_dir.glob("**/*.py")
```

---

# 21. 过滤 `.md` 和 `.txt` 文件

你后面做文档知识库第一版会处理 `.md` / `.txt`，可以这样写：

```python
from pathlib import Path

SUPPORTED_SUFFIXES = {".md", ".txt"}

docs_dir = Path("uploads")

for file_path in docs_dir.iterdir():
    if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_SUFFIXES:
        print("可处理文件:", file_path)
```

解释：

```python
file_path.suffix
```

获取后缀，比如：

```text
.md
.txt
.pdf
```

```python
.lower()
```

统一转小写，避免：

```text
README.MD
README.md
```

判断不一致。

---

# 22. 一个真实的文档加载器例子

你后面可能会有：

```text
src/app/services/document/loader.py
```

可以这样写：

```python
from pathlib import Path


class DocumentLoader:
    def __init__(self, supported_suffixes: set[str] | None = None) -> None:
        self.supported_suffixes = supported_suffixes or {".md", ".txt"}

    def load_text_file(self, file_path: Path) -> str:
        """
        加载单个文本文件内容。
        """
        file_path = file_path.resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"不是文件: {file_path}")

        if file_path.suffix.lower() not in self.supported_suffixes:
            raise ValueError(f"不支持的文件类型: {file_path.suffix}")

        return file_path.read_text(encoding="utf-8")

    def load_directory(self, directory: Path) -> list[tuple[Path, str]]:
        """
        加载目录下所有支持的文本文件。
        返回: [(文件路径, 文件内容), ...]
        """
        directory = directory.resolve()

        if not directory.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")

        if not directory.is_dir():
            raise ValueError(f"不是目录: {directory}")

        results: list[tuple[Path, str]] = []

        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in self.supported_suffixes:
                continue

            content = file_path.read_text(encoding="utf-8")
            results.append((file_path, content))

        return results
```

使用：

```python
from pathlib import Path

loader = DocumentLoader()

content = loader.load_text_file(Path("uploads/frontend-style-guide.md"))
print(content)
```

---

# 23. FastAPI 上传文件时的 pathlib 用法

假设你后面做：

```http
POST /documents/upload
```

FastAPI 里可能会有：

```python
from pathlib import Path
from fastapi import UploadFile


UPLOADS_DIR = Path("uploads")


async def save_upload_file(file: UploadFile) -> Path:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    target_path = UPLOADS_DIR / file.filename

    content = await file.read()
    target_path.write_bytes(content)

    return target_path
```

但是这个版本有安全隐患。

如果用户上传的文件名是：

```text
../../evil.py
```

那么：

```python
UPLOADS_DIR / file.filename
```

可能变成危险路径。

更安全写法：

```python
from pathlib import Path
from fastapi import UploadFile
from uuid import uuid4


UPLOADS_DIR = Path("uploads")


async def save_upload_file(file: UploadFile) -> Path:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    original_name = Path(file.filename or "unknown").name
    suffix = Path(original_name).suffix.lower()

    safe_filename = f"{uuid4().hex}{suffix}"
    target_path = UPLOADS_DIR / safe_filename

    content = await file.read()
    target_path.write_bytes(content)

    return target_path
```

关键点：

```python
Path(file.filename).name
```

只取文件名，不保留用户传进来的目录路径。

比如：

```python
Path("../../evil.py").name
```

结果是：

```text
evil.py
```

---

# 24. `relative_to()`：获取相对路径

假设：

```python
from pathlib import Path

base_dir = Path("/Users/wangzilong/Projects/my_python_project")
file_path = Path("/Users/wangzilong/Projects/my_python_project/docs/dev-log.md")
```

你想得到项目内相对路径：

```text
docs/dev-log.md
```

可以：

```python
relative_path = file_path.relative_to(base_dir)
print(relative_path)
```

输出：

```text
docs/dev-log.md
```

这个在返回 API 时很有用。

比如数据库里可以保存：

```json
{
  "file_path": "docs/dev-log.md"
}
```

而不是保存：

```text
/Users/wangzilong/Projects/my_python_project/docs/dev-log.md
```

因为绝对路径换机器就没用了。

---

# 25. `with_suffix()`：改文件后缀

```python
from pathlib import Path

path = Path("README.md")

new_path = path.with_suffix(".txt")

print(new_path)
```

输出：

```text
README.txt
```

这个在生成缓存文件、解析结果文件时很有用：

```python
source = Path("uploads/frontend-style-guide.md")
parsed = source.with_suffix(".json")

print(parsed)
```

输出：

```text
uploads/frontend-style-guide.json
```

---

# 26. `with_name()`：改文件名

```python
from pathlib import Path

path = Path("uploads/frontend-style-guide.md")

new_path = path.with_name("new-file.md")

print(new_path)
```

输出：

```text
uploads/new-file.md
```

---

# 27. `rename()`：重命名或移动文件

```python
from pathlib import Path

old_path = Path("uploads/old.md")
new_path = Path("uploads/new.md")

old_path.rename(new_path)
```

也可以移动：

```python
old_path = Path("uploads/file.md")
new_path = Path("data/documents/file.md")

new_path.parent.mkdir(parents=True, exist_ok=True)
old_path.rename(new_path)
```

注意：

```text
rename 会真实移动文件
```

---

# 28. `Path` 和字符串的关系

很多库接受字符串路径，比如：

```python
open("README.md")
```

但 `Path` 也能直接传进去：

```python
from pathlib import Path

path = Path("README.md")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()
```

大部分现代 Python 库都支持 `Path` 对象。

如果某个库不支持，你可以转成字符串：

```python
str(path)
```

例如：

```python
some_library.load(str(path))
```

---

# 29. pathlib 和 os.path 对比

| 操作    | os.path 写法                     | pathlib 写法              |
| ----- | ------------------------------ | ----------------------- |
| 拼接路径  | `os.path.join("docs", "a.md")` | `Path("docs") / "a.md"` |
| 判断存在  | `os.path.exists(path)`         | `path.exists()`         |
| 判断文件  | `os.path.isfile(path)`         | `path.is_file()`        |
| 判断目录  | `os.path.isdir(path)`          | `path.is_dir()`         |
| 获取文件名 | `os.path.basename(path)`       | `path.name`             |
| 获取父目录 | `os.path.dirname(path)`        | `path.parent`           |
| 获取后缀  | `os.path.splitext(path)[1]`    | `path.suffix`           |
| 绝对路径  | `os.path.abspath(path)`        | `path.resolve()`        |

推荐你以后优先用 `pathlib`。

---

# 30. 你最应该掌握的 15 个 API

| API                        | 用途         |
| -------------------------- | ---------- |
| `Path("xxx")`              | 创建路径对象     |
| `Path.cwd()`               | 获取当前工作目录   |
| `Path(__file__).resolve()` | 获取当前文件绝对路径 |
| `path / "child"`           | 拼接路径       |
| `path.exists()`            | 判断是否存在     |
| `path.is_file()`           | 判断是否文件     |
| `path.is_dir()`            | 判断是否目录     |
| `path.mkdir()`             | 创建目录       |
| `path.read_text()`         | 读文本        |
| `path.write_text()`        | 写文本        |
| `path.read_bytes()`        | 读二进制       |
| `path.write_bytes()`       | 写二进制       |
| `path.iterdir()`           | 遍历当前目录     |
| `path.glob("*.md")`        | 匹配文件       |
| `path.rglob("*.py")`       | 递归匹配文件     |

---

# 31. 你现在最容易踩的坑

## 坑 1：以为相对路径是相对于当前文件

错误理解：

```text
Path("README.md") 是相对于当前 py 文件
```

真实情况：

```text
Path("README.md") 是相对于当前工作目录 cwd
```

所以要经常检查：

```python
print(Path.cwd())
```

---

## 坑 2：到处写 `../../`

不推荐：

```python
Path("../../uploads")
```

因为文件位置一变，路径就坏。

推荐：

```python
BASE_DIR = Path(__file__).resolve().parents[3]
UPLOADS_DIR = BASE_DIR / "uploads"
```

---

## 坑 3：忘记创建目录

错误：

```python
path = Path("uploads/test.md")
path.write_text("hello", encoding="utf-8")
```

如果 `uploads` 不存在，会报错。

正确：

```python
path = Path("uploads/test.md")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text("hello", encoding="utf-8")
```

---

## 坑 4：不指定编码

不推荐：

```python
content = path.read_text()
```

推荐：

```python
content = path.read_text(encoding="utf-8")
```

尤其你会处理中文文档。

---

## 坑 5：直接相信上传文件名

危险：

```python
target_path = UPLOADS_DIR / file.filename
```

更安全：

```python
original_name = Path(file.filename or "unknown").name
```

只取文件名，不接受用户传来的目录路径。

---

# 32. 给你一个可直接放进项目的 `paths.py`

建议新建：

```text
src/app/core/paths.py
```

内容：

```python
from pathlib import Path


# 当前文件路径:
# my_python_project/src/app/core/paths.py
CURRENT_FILE = Path(__file__).resolve()

# 当前文件所在目录:
# my_python_project/src/app/core
CURRENT_DIR = CURRENT_FILE.parent

# 项目根目录:
# my_python_project
BASE_DIR = CURRENT_FILE.parents[3]

# 常用目录
SRC_DIR = BASE_DIR / "src"
APP_DIR = SRC_DIR / "app"
DOCS_DIR = BASE_DIR / "docs"
UPLOADS_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# 常用文件
ENV_FILE = BASE_DIR / ".env"
README_FILE = BASE_DIR / "README.md"


def ensure_runtime_dirs() -> None:
    """
    确保运行时需要的目录存在。
    例如: uploads、data、logs。
    """
    for directory in [UPLOADS_DIR, DATA_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
```

在启动时调用：

```python
from src.app.core.paths import ensure_runtime_dirs

ensure_runtime_dirs()
```

这样项目启动后会自动确保目录存在。

---

# 33. 一个更完整的文档读取工具

可以放到：

```text
src/app/services/document/loader.py
```

代码：

```python
from pathlib import Path

from src.app.core.paths import UPLOADS_DIR


class UnsupportedFileTypeError(ValueError):
    pass


class DocumentLoader:
    """
    文档加载器。

    第一版只支持 .md 和 .txt。
    后续可以扩展 PDF、DOCX 等。
    """

    def __init__(self, base_dir: Path = UPLOADS_DIR) -> None:
        self.base_dir = base_dir
        self.supported_suffixes = {".md", ".txt"}

    def load(self, relative_path: str) -> str:
        """
        根据相对路径读取文档内容。

        参数:
            relative_path: 相对于 uploads 目录的路径。
                          例如: "frontend-style-guide.md"

        返回:
            文件文本内容。
        """
        file_path = (self.base_dir / relative_path).resolve()

        self._validate_file_path(file_path)

        return file_path.read_text(encoding="utf-8")

    def _validate_file_path(self, file_path: Path) -> None:
        """
        校验文件路径是否合法。
        """
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"路径不是文件: {file_path}")

        if file_path.suffix.lower() not in self.supported_suffixes:
            raise UnsupportedFileTypeError(f"不支持的文件类型: {file_path.suffix}")
```

使用：

```python
loader = DocumentLoader()
content = loader.load("frontend-style-guide.md")
print(content)
```

---

# 34. 但上面还有一个安全问题

这一行：

```python
file_path = (self.base_dir / relative_path).resolve()
```

如果用户传：

```text
../../README.md
```

它可能逃出 `uploads` 目录。

所以更安全的版本要加：

```python
if not file_path.is_relative_to(self.base_dir.resolve()):
    raise ValueError("非法文件路径")
```

完整版本：

```python
from pathlib import Path

from src.app.core.paths import UPLOADS_DIR


class UnsupportedFileTypeError(ValueError):
    pass


class DocumentLoader:
    def __init__(self, base_dir: Path = UPLOADS_DIR) -> None:
        self.base_dir = base_dir.resolve()
        self.supported_suffixes = {".md", ".txt"}

    def load(self, relative_path: str) -> str:
        file_path = (self.base_dir / relative_path).resolve()

        self._validate_file_path(file_path)

        return file_path.read_text(encoding="utf-8")

    def _validate_file_path(self, file_path: Path) -> None:
        if not file_path.is_relative_to(self.base_dir):
            raise ValueError(f"非法文件路径，不能访问 uploads 之外的文件: {file_path}")

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"路径不是文件: {file_path}")

        if file_path.suffix.lower() not in self.supported_suffixes:
            raise UnsupportedFileTypeError(f"不支持的文件类型: {file_path.suffix}")
```

这个细节对后端项目很重要。

---

# 35. 最后给你一套学习顺序

你不用一下子记住全部。按这个顺序练：

## 第一阶段：路径对象

掌握：

```python
Path("README.md")
Path("docs") / "dev-log.md"
Path.cwd()
Path(__file__).resolve()
```

目标：

```text
知道路径对象是什么
知道相对路径依赖 cwd
知道怎么拼接路径
```

---

## 第二阶段：路径信息

掌握：

```python
path.name
path.stem
path.suffix
path.parent
path.parents
```

目标：

```text
能拆解一个文件路径
```

---

## 第三阶段：文件判断

掌握：

```python
path.exists()
path.is_file()
path.is_dir()
```

目标：

```text
读写文件前先校验
```

---

## 第四阶段：文件读写

掌握：

```python
path.read_text(encoding="utf-8")
path.write_text("内容", encoding="utf-8")
path.read_bytes()
path.write_bytes()
```

目标：

```text
能处理 md、txt、上传文件
```

---

## 第五阶段：目录操作

掌握：

```python
path.mkdir(parents=True, exist_ok=True)
path.iterdir()
path.glob("*.md")
path.rglob("*.py")
```

目标：

```text
能扫描文档目录，找到所有可处理文件
```

---

# 36. 你现在可以这样理解 pathlib

一句话：

```text
pathlib 就是把“路径字符串”升级成“路径对象”，让你用对象方法安全、清晰、跨平台地操作文件和目录。
```

对你当前 Python / FastAPI / RAG 项目来说，它主要用于：

```text
定位项目根目录
读取 .env / README / docs
创建 uploads / logs / data
保存上传文件
读取 md / txt 文档
扫描文档目录
过滤文件后缀
生成解析结果路径
避免路径穿越安全问题
```

你现在最应该熟练掌握的是这套组合：

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
UPLOADS_DIR = BASE_DIR / "uploads"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

file_path = UPLOADS_DIR / "frontend-style-guide.md"

if file_path.exists() and file_path.is_file():
    content = file_path.read_text(encoding="utf-8")
    print(content)
```

这段代码基本覆盖了你后续做文档上传、知识库、RAG 时最常见的路径操作。
