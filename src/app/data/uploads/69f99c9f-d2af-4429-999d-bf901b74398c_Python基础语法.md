下面这份可以当作你的 **Python 语法总纲 + 学习路线图**。
目标不是“罗列所有冷门语法”，而是覆盖你日常开发里 **95% 会接触到的 Python 语法与写法**，并说明：

* 它是什么
* 什么时候用
* 怎么写
* 和 JS 哪里像、哪里不一样

我会按由浅入深展开。

---

# 1. 先建立整体认知：Python 语法体系长什么样

你可以把 Python 语法分成 10 大块：

1. 基础语法：变量、注释、缩进、输入输出
2. 数据类型：数字、字符串、布尔、列表、元组、字典、集合
3. 运算与表达式：算术、比较、逻辑、成员、身份、三元表达式
4. 流程控制：if、for、while、break、continue、match
5. 函数：参数、返回值、作用域、匿名函数、闭包、装饰器
6. 异常处理：try / except / finally / raise
7. 模块与包：import、from import、自定义模块、包结构
8. 面向对象：class、继承、封装、多态、特殊方法
9. 迭代器与生成器：iter、next、yield、生成式
10. 高阶语法：上下文管理器、类型注解、异步、数据类、模式匹配

你可以简单理解为：

* **基础语法** = 会不会写
* **函数 / 类 / 模块** = 能不能组织代码
* **异常 / 上下文 / 异步** = 能不能写工程代码
* **生成器 / 装饰器 / 闭包** = 能不能看懂高级代码

---

# 2. Python 最基础的语法规则

## 2.1 缩进是语法的一部分

Python 不像 JS 用 `{}` 表示代码块，它用 **缩进**。

```python
if True:
    print("hello")
    print("world")
```

### 使用场景

任何代码块：if、for、while、函数、类、try 等。

### JS 对比

JS：

```javascript
if (true) {
  console.log("hello");
  console.log("world");
}
```

Python：

```python
if True:
    print("hello")
    print("world")
```

### 关键区别

* JS 靠 `{}` 分块
* Python 靠缩进分块
* Python 通常约定 4 个空格，不建议 tab 和空格混用

---

## 2.2 注释

### 单行注释

```python
# 这是注释
print("hello")
```

### 多行说明

Python没有真正独立的“多行注释语法”，常见是：

```python
"""
这是多行字符串，
常被当作文档说明来写
"""
```

更准确地说，这其实是字符串字面量，不是专门的注释符号。

### JS 对比

JS：

```javascript
// 单行注释
/*
多行注释
*/
```

Python：

```python
# 单行注释
"""
文档字符串 / 多行说明
"""
```

---

## 2.3 变量定义

Python 变量不需要 `let`、`const`、`var`。

```python
name = "Zilong"
age = 18
is_ok = True
```

### 使用场景

存储任意值。

### JS 对比

JS：

```javascript
let name = "Zilong";
const age = 18;
```

Python：

```python
name = "Zilong"
age = 18
```

### 关键区别

Python 变量是**名字绑定到对象**，不是传统意义的“固定类型盒子”。

---

## 2.4 输出

```python
print("hello")
print("name =", name)
```

### 使用场景

调试、命令行程序输出、快速验证逻辑。

### JS 对比

JS 常用：

```javascript
console.log("hello");
```

Python 常用：

```python
print("hello")
```

---

# 3. Python 的核心数据类型

---

## 3.1 数字类型

### 整数 int

```python
a = 10
```

### 浮点数 float

```python
b = 3.14
```

### 复数 complex

```python
c = 1 + 2j
```

复数平时业务开发很少用。

### 使用场景

* int：计数、索引、ID、循环
* float：价格、长度、比率、计算
* complex：科学计算

### JS 对比

JS 绝大多数数字都是 `number`，Python 区分 `int` 和 `float` 更明显。

---

## 3.2 布尔类型 bool

```python
is_login = True
is_admin = False
```

### 注意

Python 里首字母大写：

* `True`
* `False`
* `None`

不是 JS 的 `true false null`

---

## 3.3 字符串 str

```python
name = "python"
msg = 'hello'
text = """
这是多行字符串
第二行
"""
```

### 常见操作

```python
s = "hello"
print(len(s))       # 5
print(s[0])         # h
print(s[-1])        # o
print(s[1:4])       # ell
print(s.upper())    # HELLO
print(s.replace("h", "H"))  # Hello
```

### 使用场景

文本处理、日志、接口数据、文件内容。

### JS 对比

JS 字符串也支持索引和方法，但 Python 切片非常强：

```python
s[1:4]
```

JS 里更常见：

```javascript
s.slice(1, 4)
```

---

## 3.4 列表 list

Python 的列表，类似 JS 的数组。

```python
nums = [1, 2, 3]
names = ["a", "b", "c"]
mixed = [1, "hello", True]
```

### 常见操作

```python
nums.append(4)
nums.insert(0, 100)
nums.remove(2)
last = nums.pop()
print(nums[0])
print(nums[1:3])
```

### 使用场景

* 存一组有顺序的数据
* 遍历结果集
* 接口返回列表
* 批量处理

### JS 对比

JS：

```javascript
const arr = [1, 2, 3];
arr.push(4);
```

Python：

```python
nums = [1, 2, 3]
nums.append(4)
```

### 区别

* Python list 更像可变数组
* 支持切片、推导式，写数据处理时很强

---

## 3.5 元组 tuple

元组和列表很像，但**通常不可修改**。

```python
point = (10, 20)
person = ("Tom", 18)
```

### 使用场景

* 表示固定结构的数据
* 函数返回多个值
* 不希望被修改的轻量结构

### 例子

```python
def get_user():
    return ("Tom", 18)

name, age = get_user()
```

### JS 对比

JS 没有真正一模一样的 tuple 语法概念。TS 有 tuple 类型概念，但运行时还是数组。

---

## 3.6 字典 dict

Python 字典类似 JS 的对象 / Map 中的“键值对存储”。

```python
user = {
    "name": "Tom",
    "age": 18,
    "is_admin": True
}
```

### 常见操作

```python
print(user["name"])
print(user.get("age"))
user["city"] = "Shanghai"
del user["age"]
```

### 使用场景

* JSON 风格数据
* 配置项
* 按 key 查值
* 接口响应处理

### JS 对比

JS：

```javascript
const user = { name: "Tom", age: 18 };
console.log(user.name);
```

Python：

```python
user = {"name": "Tom", "age": 18}
print(user["name"])
```

### 区别

Python 更推荐显式地按 key 取值；复杂场景常配合类型注解、dataclass、Pydantic 使用。

---

## 3.7 集合 set

集合特点：**无序、去重**。

```python
s = {1, 2, 3}
```

### 常见操作

```python
s.add(4)
s.remove(2)
print(1 in s)
```

### 使用场景

* 去重
* 成员判断
* 交集、并集、差集

### 例子

```python
a = {1, 2, 3}
b = {3, 4, 5}
print(a & b)   # 交集 {3}
print(a | b)   # 并集
print(a - b)   # 差集
```

### JS 对比

JS 有 `Set`，概念比较接近。

---

## 3.8 None

```python
result = None
```

表示“空值 / 没有值”。

### JS 对比

接近 `null`，但也有点像 `undefined` 的一部分语义。

Python 里最常见的是判断：

```python
if result is None:
    print("没有结果")
```

---

# 4. 运算符与表达式

---

## 4.1 算术运算

```python
a = 10 + 2
b = 10 - 2
c = 10 * 2
d = 10 / 2
e = 10 // 3   # 整除
f = 10 % 3    # 取余
g = 2 ** 3    # 幂运算
```

### 使用场景

计数、分页、数学计算、索引计算。

### JS 对比

JS 没有 `**` 之前常用 `Math.pow()`，现在也支持 `**`。

---

## 4.2 比较运算

```python
print(1 == 1)
print(2 != 1)
print(3 > 2)
print(3 >= 3)
```

---

## 4.3 逻辑运算

```python
a = True and False
b = True or False
c = not True
```

### JS 对比

JS 是 `&& || !`
Python 是 `and or not`

---

## 4.4 成员运算

```python
print("a" in "abc")
print(2 in [1, 2, 3])
print("name" in {"name": "Tom"})
```

### 使用场景

检查元素是否存在。

---

## 4.5 身份运算 is

```python
x = None
print(x is None)
```

### 这个很重要

`is` 比较的是 **是不是同一个对象**
`==` 比较的是 **值是否相等**

### 推荐记忆

判断 `None` 时，优先用：

```python
if x is None:
    ...
```

而不是：

```python
if x == None:
    ...
```

### JS 对比

JS 的 `===` 是严格相等，但本质也不是 Python 的 `is`。

---

## 4.6 三元表达式

```python
age = 18
status = "adult" if age >= 18 else "child"
```

### JS 对比

JS：

```javascript
const status = age >= 18 ? "adult" : "child";
```

Python：

```python
status = "adult" if age >= 18 else "child"
```

---

# 5. 流程控制

---

## 5.1 if / elif / else

```python
score = 85

if score >= 90:
    print("A")
elif score >= 80:
    print("B")
else:
    print("C")
```

### 使用场景

分支判断、校验、状态流转。

### JS 对比

JS 是 `else if`，Python 是 `elif`。

---

## 5.2 while 循环

```python
i = 0
while i < 5:
    print(i)
    i += 1
```

### 使用场景

不确定循环次数、持续读取、重试逻辑。

### JS 对比

概念一样。

---

## 5.3 for 循环

Python 的 `for` 不是传统 C 风格的三段式循环，
它本质是 **遍历可迭代对象**。

```python
for x in [1, 2, 3]:
    print(x)
```

### 使用场景

遍历列表、字典、字符串、文件、生成器。

### JS 对比

更接近 JS 的：

```javascript
for (const x of arr) {
  console.log(x);
}
```

不是传统的：

```javascript
for (let i = 0; i < arr.length; i++) {}
```

---

## 5.4 range()

```python
for i in range(5):
    print(i)
```

输出 0 到 4。

### 常见形式

```python
range(5)        # 0,1,2,3,4
range(1, 5)     # 1,2,3,4
range(1, 10, 2) # 1,3,5,7,9
```

### 使用场景

按次数循环、带索引迭代。

### JS 对比

Python 没有原生 `for (let i = 0; i < 5; i++)` 这种形式，通常用 `range()`。

---

## 5.5 break / continue / pass

### break

终止循环

```python
for i in range(10):
    if i == 5:
        break
    print(i)
```

### continue

跳过本次循环

```python
for i in range(5):
    if i == 2:
        continue
    print(i)
```

### pass

占位，不做任何事

```python
if True:
    pass
```

### 使用场景

* `break`：找到目标就结束
* `continue`：跳过不合法数据
* `pass`：先把结构写出来，后面再补实现

---

## 5.6 for-else / while-else

这个是 Python 比较有特色的语法。

```python
for x in [1, 2, 3]:
    if x == 5:
        break
else:
    print("没有找到")
```

### 含义

`else` 在**循环正常结束且没有 break** 时执行。

### 使用场景

查找场景挺适合。

---

## 5.7 match-case（模式匹配）

Python 3.10+。

```python
status = 200

match status:
    case 200:
        print("success")
    case 404:
        print("not found")
    case _:
        print("unknown")
```

### 使用场景

多分支匹配，比一长串 `if elif` 更清晰。

### JS 对比

有点像 `switch`，但比 `switch` 更强。

JS：

```javascript
switch (status) {
  case 200:
    console.log("success");
    break;
  default:
    console.log("unknown");
}
```

Python：

```python
match status:
    case 200:
        print("success")
    case _:
        print("unknown")
```

---

# 6. 函数：Python 开发的核心

---

## 6.1 定义函数

```python
def greet():
    print("hello")
```

### 调用

```python
greet()
```

### 使用场景

封装逻辑、复用代码、拆分职责。

---

## 6.2 参数与返回值

```python
def add(a, b):
    return a + b

result = add(1, 2)
```

### JS 对比

JS：

```javascript
function add(a, b) {
  return a + b;
}
```

Python：

```python
def add(a, b):
    return a + b
```

---

## 6.3 默认参数

```python
def greet(name="World"):
    print("Hello,", name)
```

### 使用场景

给参数提供默认值，减少调用负担。

### 注意坑

不要把可变对象当默认参数：

```python
def foo(items=[]):   # 不推荐
    items.append(1)
    return items
```

应该写：

```python
def foo(items=None):
    if items is None:
        items = []
    items.append(1)
    return items
```

这个是 Python 很经典的面试 / 工程坑。

---

## 6.4 关键字参数

```python
def create_user(name, age):
    print(name, age)

create_user(age=18, name="Tom")
```

### 使用场景

参数很多时，提高可读性。

### JS 对比

有点像 JS 里传对象参数，但 Python 是直接按参数名传。

---

## 6.5 可变参数

### `*args`

接收位置参数的可变数量。

```python
def total(*args):
    return sum(args)

print(total(1, 2, 3))
```

### `**kwargs`

接收关键字参数的可变数量。

```python
def print_info(**kwargs):
    print(kwargs)

print_info(name="Tom", age=18)
```

### 使用场景

* 包装函数
* 转发参数
* 写通用工具
* 写装饰器

### JS 对比

有点像剩余参数和对象展开。

JS：

```javascript
function total(...args) {}
```

Python：

```python
def total(*args):
    ...
```

---

## 6.6 返回多个值

```python
def get_user():
    return "Tom", 18
```

调用：

```python
name, age = get_user()
```

本质上是返回了一个元组。

### 使用场景

函数返回多个结果。

### JS 对比

有点像：

```javascript
return [name, age];
```

然后解构。

---

## 6.7 作用域：局部变量、全局变量

```python
x = 10

def foo():
    y = 20
    print(x)
    print(y)
```

### 修改全局变量

```python
count = 0

def inc():
    global count
    count += 1
```

### 使用场景

一般能不用 `global` 就别用，工程里不推荐大量依赖全局状态。

---

## 6.8 匿名函数 lambda

```python
add = lambda a, b: a + b
print(add(1, 2))
```

### 使用场景

简单函数，常用于排序、map、filter。

```python
users = [{"age": 20}, {"age": 18}]
users.sort(key=lambda x: x["age"])
```

### JS 对比

很像箭头函数，但 Python 的 lambda 只能写**单表达式**，不能写多行逻辑。

---

## 6.9 闭包

```python
def outer(x):
    def inner(y):
        return x + y
    return inner

f = outer(10)
print(f(5))  # 15
```

### 含义

内部函数记住了外部函数的变量。

### 使用场景

* 函数工厂
* 装饰器
* 封装部分状态

### JS 对比

和 JS 闭包概念很像。

---

## 6.10 装饰器

这是 Python 很重要的高级语法。

```python
def log_decorator(func):
    def wrapper():
        print("before")
        func()
        print("after")
    return wrapper

@log_decorator
def say_hi():
    print("hi")

say_hi()
```

### `@xxx` 是什么

相当于：

```python
say_hi = log_decorator(say_hi)
```

### 使用场景

* 日志
* 权限校验
* 计时
* 缓存
* 路由注册
* 框架能力扩展

### 你作为前端转 Python，需要特别理解

这类写法在 Flask、FastAPI、Django、测试框架里非常常见。

JS 里也有 decorator 提案 / TS 装饰器概念，但 Python 装饰器在实际工程中的存在感更强。

---

# 7. 常见内置数据处理语法

---

## 7.1 列表推导式

```python
nums = [1, 2, 3, 4]
squares = [x * x for x in nums]
```

### 带条件

```python
evens = [x for x in nums if x % 2 == 0]
```

### 使用场景

简洁地生成新列表。

### JS 对比

类似：

```javascript
const squares = nums.map(x => x * x);
const evens = nums.filter(x => x % 2 === 0);
```

Python 一条推导式经常能同时表达 map + filter。

---

## 7.2 字典推导式

```python
nums = [1, 2, 3]
d = {x: x * x for x in nums}
```

### 使用场景

快速构造映射表。

---

## 7.3 集合推导式

```python
s = {x * 2 for x in [1, 2, 2, 3]}
```

会自动去重。

---

## 7.4 生成器表达式

```python
g = (x * x for x in range(5))
```

和列表推导式很像，但不是一次性把全部数据放进内存。

### 使用场景

大数据量、惰性计算、节省内存。

---

# 8. 异常处理

---

## 8.1 try / except

```python
try:
    x = 1 / 0
except ZeroDivisionError:
    print("除零错误")
```

### 使用场景

文件读取、网络请求、类型转换、数据库、外部依赖调用。

---

## 8.2 捕获多个异常

```python
try:
    ...
except (ValueError, TypeError) as e:
    print(e)
```

---

## 8.3 else / finally

```python
try:
    print("try")
except Exception:
    print("except")
else:
    print("没有异常时执行")
finally:
    print("一定执行")
```

### 使用场景

* `else`：成功路径逻辑
* `finally`：资源释放、收尾动作

---

## 8.4 主动抛出异常 raise

```python
def divide(a, b):
    if b == 0:
        raise ValueError("b 不能为 0")
    return a / b
```

### 使用场景

参数校验、业务规则失败、封装底层错误。

---

## 8.5 自定义异常

```python
class UserNotFoundError(Exception):
    pass
```

### 使用场景

让错误语义更清晰，便于业务层处理。

### 这是你前面问过的重点

这表示“定义了一个新的异常类型”。

---

## 8.6 异常链 raise ... from ...

```python
try:
    int("abc")
except ValueError as e:
    raise RuntimeError("解析用户输入失败") from e
```

### 含义

新异常是基于旧异常产生的，保留因果链。

### 使用场景

底层错误转换为业务错误，但不丢原始原因。

---

# 9. 模块与包

---

## 9.1 import

```python
import math
print(math.sqrt(16))
```

---

## 9.2 from ... import ...

```python
from math import sqrt
print(sqrt(16))
```

---

## 9.3 起别名

```python
import numpy as np
from math import sqrt as s
```

### 使用场景

简化命名、避免冲突。

---

## 9.4 自定义模块

假设 `utils.py`：

```python
def add(a, b):
    return a + b
```

另一个文件：

```python
import utils
print(utils.add(1, 2))
```

---

## 9.5 包

目录里有 `__init__.py`，通常表示一个包。

```python
project/
  main.py
  utils/
    __init__.py
    math_utils.py
```

导入：

```python
from utils.math_utils import add
```

### 使用场景

组织大项目代码。

### JS 对比

有点像模块目录，但 Python 的包概念更体系化。

---

# 10. 面向对象编程

---

## 10.1 定义类

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def say_hi(self):
        print(f"Hi, I am {self.name}")
```

创建对象：

```python
u = User("Tom", 18)
u.say_hi()
```

### 使用场景

封装状态和行为。

### JS 对比

JS：

```javascript
class User {
  constructor(name, age) {
    this.name = name;
    this.age = age;
  }
}
```

Python：

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

---

## 10.2 self

`self` 表示“当前实例对象”。

```python
self.name = name
```

### 你可以理解成

JS 里的 `this`，但 Python 需要你显式写出来。

---

## 10.3 类属性和实例属性

```python
class User:
    species = "human"   # 类属性

    def __init__(self, name):
        self.name = name  # 实例属性
```

### 使用场景

* 类属性：所有实例共享
* 实例属性：每个对象独有

---

## 10.4 继承

```python
class Animal:
    def speak(self):
        print("...")

class Dog(Animal):
    def speak(self):
        print("wang")
```

### 使用场景

复用父类逻辑，扩展子类行为。

---

## 10.5 super()

```python
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed
```

### 使用场景

调用父类构造或方法。

### JS 对比

和 JS class 里的 `super()` 很像。

---

## 10.6 特殊方法（魔术方法）

### `__str__`

```python
class User:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"User({self.name})"
```

### `__len__`

```python
class Box:
    def __len__(self):
        return 10
```

### `__getitem__`

```python
class MyList:
    def __getitem__(self, index):
        return index * 10
```

### 使用场景

让对象表现得像字符串、容器、可比较对象等。

这是 Python 非常强大的地方：**你可以通过协议让自己的对象像内置类型一样工作**。

---

## 10.7 封装与“私有”

Python 没有 Java 那种严格私有字段机制，但有约定：

```python
class User:
    def __init__(self):
        self._internal = 1
        self.__secret = 2
```

### 约定

* `_name`：约定为“内部使用”
* `__name`：名称改写，避免直接访问

Python 更强调“约定优于强限制”。

---

## 10.8 类方法与静态方法

### 类方法

```python
class User:
    count = 0

    @classmethod
    def get_count(cls):
        return cls.count
```

### 静态方法

```python
class MathUtil:
    @staticmethod
    def add(a, b):
        return a + b
```

### 使用场景

* `@classmethod`：和类本身相关
* `@staticmethod`：逻辑上放在类里，但不依赖实例和类状态

---

# 11. 迭代器、生成器、yield

---

## 11.1 可迭代对象

能被 `for` 遍历的，一般就是可迭代对象。

```python
for x in [1, 2, 3]:
    print(x)
```

列表、元组、字典、字符串、集合、文件对象等都可以。

---

## 11.2 迭代器

```python
nums = [1, 2, 3]
it = iter(nums)
print(next(it))
print(next(it))
```

### 含义

* `iter()` 生成迭代器
* `next()` 每次取下一个值

### 使用场景

理解 Python 遍历本质、手动控制迭代流程。

---

## 11.3 生成器函数

```python
def gen():
    yield 1
    yield 2
    yield 3
```

调用：

```python
g = gen()
print(next(g))
print(next(g))
```

### yield 是什么

函数执行到 `yield` 时，先返回一个值，并暂停状态；下次继续从暂停处往下执行。

### 使用场景

* 流式处理
* 大数据逐步生成
* 惰性计算
* 协程基础理解

### 这个语法非常重要

很多高级框架、异步思想、流式输出都和它相关。

### JS 对比

JS 也有 generator：

```javascript
function* gen() {
  yield 1;
}
```

概念相似。

---

# 12. 文件操作

---

## 12.1 打开文件

```python
f = open("test.txt", "r", encoding="utf-8")
content = f.read()
f.close()
```

### 模式

* `r` 读
* `w` 写，覆盖
* `a` 追加
* `b` 二进制
* `x` 新建

---

## 12.2 推荐写法：with

```python
with open("test.txt", "r", encoding="utf-8") as f:
    content = f.read()
```

### 使用场景

自动关闭文件，避免资源泄漏。

### 这是工程代码标准写法

以后你读文件、写文件，优先都用 `with`。

---

# 13. 上下文管理器

`with` 背后是上下文管理协议。

```python
with open("a.txt", "r") as f:
    data = f.read()
```

### 含义

进入代码块前做准备，离开时自动清理。

### 使用场景

* 文件
* 数据库连接
* 锁
* 临时资源
* 网络连接

### 高阶理解

如果一个对象实现了 `__enter__` 和 `__exit__`，就可以配合 `with` 使用。

---

# 14. 常见内置函数

这些非常常用，属于你必须熟的“基础工具箱”。

---

## 14.1 len()

```python
len([1, 2, 3])
len("hello")
```

---

## 14.2 type()

```python
print(type(123))
```

---

## 14.3 isinstance()

```python
print(isinstance(123, int))
```

### 使用场景

判断对象类型，通常比 `type(x) == int` 更灵活。

---

## 14.4 enumerate()

```python
names = ["a", "b", "c"]
for i, name in enumerate(names):
    print(i, name)
```

### 使用场景

遍历时同时拿索引和元素。

### JS 对比

类似：

```javascript
arr.entries()
```

或 `forEach((item, index) => ...)`

---

## 14.5 zip()

```python
names = ["Tom", "Jerry"]
ages = [18, 20]

for name, age in zip(names, ages):
    print(name, age)
```

### 使用场景

并行遍历多个序列。

---

## 14.6 sorted()

```python
nums = [3, 1, 2]
print(sorted(nums))
```

### 带 key

```python
users = [{"age": 20}, {"age": 18}]
print(sorted(users, key=lambda x: x["age"]))
```

### 使用场景

排序数据。

---

## 14.7 map / filter / sum / min / max / any / all

```python
nums = [1, 2, 3]

print(sum(nums))
print(min(nums))
print(max(nums))
print(any([False, True, False]))
print(all([True, True, False]))
```

### 使用场景

聚合、判断、函数式处理。

不过在 Python 里，很多时候 **列表推导式比 map/filter 更直观**。

---

# 15. 解包语法

---

## 15.1 序列解包

```python
a, b = 1, 2
name, age = ("Tom", 18)
```

---

## 15.2 星号解包

```python
first, *middle, last = [1, 2, 3, 4, 5]
```

结果：

* `first = 1`
* `middle = [2, 3, 4]`
* `last = 5`

### 使用场景

处理不定长数据、拆分列表。

---

## 15.3 参数展开

```python
def add(a, b, c):
    return a + b + c

nums = [1, 2, 3]
print(add(*nums))
```

字典展开：

```python
def greet(name, age):
    print(name, age)

data = {"name": "Tom", "age": 18}
greet(**data)
```

### JS 对比

类似 spread：

```javascript
fn(...arr)
const obj2 = { ...obj1 }
```

---

# 16. 类型注解

Python 是动态类型，但支持类型提示。

```python
def add(a: int, b: int) -> int:
    return a + b
```

### 使用场景

* 提升可读性
* IDE 智能提示
* 静态检查
* 大型工程协作

### 常见写法

```python
name: str = "Tom"
age: int = 18
items: list[int] = [1, 2, 3]
user: dict[str, str] = {"name": "Tom"}
```

### JS / TS 对比

如果你有 TS 基础，这个很好理解。
但注意：**Python 类型注解默认不会在运行时强制拦截错误**，它主要是提示和检查用途。

---

# 17. dataclass

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
```

### 它解决什么问题

如果一个类主要是存数据，自己手写 `__init__` 很烦，`@dataclass` 可以自动帮你生成。

### 使用场景

* DTO
* 配置对象
* 简单数据实体
* 内部结构体

### 对比 JS

有点像“定义一个纯数据对象结构”，但 Python dataclass 更正式、更工程化。

---

# 18. 异步语法 async / await

---

## 18.1 定义异步函数

```python
async def main():
    print("hello")
```

---

## 18.2 await

```python
import asyncio

async def say_hi():
    await asyncio.sleep(1)
    print("hi")

asyncio.run(say_hi())
```

### 使用场景

* 网络请求
* 并发 IO
* Web 服务
* 爬虫
* 消息系统

### JS 对比

和 JS 的 `async / await` 很像。

JS：

```javascript
async function main() {
  await fetchData();
}
```

Python：

```python
async def main():
    await fetch_data()
```

### 但底层生态不同

Python 异步通常围绕 `asyncio`，JS 围绕事件循环和 Promise。

---

## 18.3 async for / async with

更高阶一点：

```python
async for item in async_iterable:
    ...
```

```python
async with resource:
    ...
```

### 使用场景

异步流、异步资源管理。

---

# 19. 高阶但常见的工程语法

---

## 19.1 property

```python
class User:
    def __init__(self, age):
        self._age = age

    @property
    def age(self):
        return self._age
```

### 使用场景

把方法伪装成属性访问，便于封装校验逻辑。

---

## 19.2 断言 assert

```python
assert 1 + 1 == 2
```

### 使用场景

调试、单元测试、前置条件验证。

### 注意

生产逻辑里不能把它当严格业务校验机制。

---

## 19.3 文档字符串 docstring

```python
def add(a, b):
    """返回两个数字之和"""
    return a + b
```

### 使用场景

函数说明、自动文档、IDE 提示。

---

## 19.4 **name** == "**main**"

```python
def main():
    print("run")

if __name__ == "__main__":
    main()
```

### 含义

当前文件被直接运行时执行，不是被 import 时执行。

### 使用场景

脚本入口。

### JS 对比

有点像 Node 里的：

```javascript
if (require.main === module) {}
```

---

# 20. 你真正开发时最常用的语法子集

如果从“实战频率”看，下面这些是最高频：

## 入门必会

* 变量
* 字符串
* list / dict
* if / for / while
* 函数
* import
* try / except
* 文件读写
* 类的基础用法

## 工程必会

* 默认参数
* `*args` / `**kwargs`
* 列表推导式
* lambda
* with
* 自定义异常
* 装饰器基础
* 类型注解
* dataclass

## 看源码必会

* 闭包
* 装饰器
* yield / generator
* 魔术方法
* classmethod / staticmethod
* async / await

---

# 21. Python 和 JS 的核心差异，建议你重点建立这些认知

---

## 21.1 Python 更强调“可读性优先”

JS 很多时候偏灵活、生态驱动。
Python 很多语法设计目标就是：**让人读着像自然语言**。

例如：

```python
if x in items:
    ...
```

```python
for name, age in zip(names, ages):
    ...
```

---

## 21.2 Python 的 for 本质是遍历，不是传统计数循环

你要从 JS 的“三段式 for”思维切换到“遍历 iterable”。

---

## 21.3 Python 对数据处理特别强

* 切片
* 推导式
* zip
* enumerate
* sorted(key=...)
* dict / set 操作

这套东西做后端、脚本、AI 数据处理时非常顺手。

---

## 21.4 Python 的高级语法在框架里存在感很强

例如：

* `@decorator`
* `yield`
* `with`
* `async def`
* `@property`
* dataclass
* 类型注解

你如果学 FastAPI、Django、机器学习框架，会频繁看到。

---

## 21.5 Python 更像“协议驱动”

很多能力不是靠“硬编码继承某个类”，而是对象实现某种协议：

* 可迭代协议
* 上下文管理协议
* 魔术方法协议
* 异步协议

这点和 JS 的对象模型思路不太一样。

---

# 22. 给你一份推荐学习顺序

按你现在的情况，我建议按这个顺序学：

## 第一阶段：先把基本语法打通

1. 变量、缩进、注释
2. 数字、字符串、布尔
3. list / tuple / dict / set
4. 运算符
5. if / for / while
6. 函数
7. import
8. try / except

## 第二阶段：进入工程开发

9. 文件读写
10. with
11. 类与对象
12. 继承
13. 列表推导式
14. lambda
15. 类型注解
16. dataclass

## 第三阶段：开始能看中高级代码

17. 闭包
18. 装饰器
19. yield / generator
20. 魔术方法
21. async / await
22. property / classmethod / staticmethod

---

# 23. 一个完整的小例子，把前面语法串起来

```python
from dataclasses import dataclass
from typing import Optional


class UserNotFoundError(Exception):
    pass


@dataclass
class User:
    name: str
    age: int


def find_user(users: list[User], name: str) -> Optional[User]:
    for user in users:
        if user.name == name:
            return user
    return None


def main():
    users = [
        User("Tom", 18),
        User("Jerry", 20),
    ]

    try:
        target = find_user(users, "Tom")
        if target is None:
            raise UserNotFoundError("用户不存在")

        status = "adult" if target.age >= 18 else "child"
        print(f"name={target.name}, age={target.age}, status={status}")

    except UserNotFoundError as e:
        print(f"业务错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")


if __name__ == "__main__":
    main()
```

这个例子里已经包含了：

* import
* dataclass
* 自定义异常
* 类型注解
* list
* for
* if
* return
* None
* raise
* try / except
* 三元表达式
* f-string
* main 入口

这就是很典型的 Python 工程基础代码风格。

---

# 24. 最后给你一个结论

如果你想把 Python 语法学到“能开发、能看框架、能做 AI 工程”的程度，核心不是死记所有冷门语法，而是先把这几层吃透：

## 第一层：会写

* 变量
* 数据类型
* 条件
* 循环
* 函数

## 第二层：会组织代码

* 模块
* 类
* 异常
* 文件操作
* with

## 第三层：会看工程代码

* 装饰器
* 闭包
* 生成器
* 类型注解
* 异步

你把这三层打通，Python 语法基本就真的覆盖到 95% 了。

如果你要，我下一步可以继续直接给你整理一份：

**《Python 语法覆盖 95% 的系统学习清单（表格版）》**

我会按下面字段输出，适合你保存和反复查：

* 语法点
* 作用
* 使用场景
* 示例
* 常见坑
* JS 对比
* 学习优先级
