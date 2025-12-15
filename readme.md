# ClipboardGo – 工作流程与热键控制完整说明

本文档基于当前 **最新代码实现**，说明 **ClipboardGo** 从剪贴板读取 → 内容判定 → 规则匹配 → 启动外部程序的完整流程，并补充 **热键控制模块** 的设计与行为。

---

## 一、整体工作流程（总览）

```text
程序启动
  ↓
注册全局热键（hotkey_listener）
  ↓
用户按下触发热键
  ↓
执行 main()
  ↓
读取 / 创建 config.json
  ↓
读取 Windows 剪贴板
  ↓
对剪贴板内容进行分类（files / image / text）
  ↓
按优先级选择一个内容项
  ↓
根据内容类型决定处理方式
  ↓
（text）匹配配置规则并提取关键文本
  ↓
构造启动参数
  ↓
静默启动外部程序
```

ClipboardGo 是 **热键驱动的被动工具**，不会主动监听剪贴板变化，仅在用户明确触发时执行。

---

## 二、热键控制机制（新增）

### 热键定义

| 热键               | 行为                         |
|------------------|----------------------------|
| `Ctrl + Alt + V` | 对当前剪贴板内容执行 ClipboardGo 主逻辑 |
| `Ctrl + Alt + Q` | 停止监听并退出程序                  |

### 设计目标

* 明确用户意图，避免误触发
* 允许程序长期常驻
* 保证异常不会导致监听失效
* 防止高频连按导致重复启动

---

## 三、热键监听实现逻辑

```python
import keyboard
import time

_last_trigger = 0

def safe_call(func):
    def wrapper():
        try:
            func()
        except Exception as e:
            print("ClipboardGo 执行出错：", e)
    return wrapper


def debounce_call(func, delay=0.3):
    def wrapper():
        global _last_trigger
        now = time.time()
        if now - _last_trigger < delay:
            return
        _last_trigger = now
        func()
    return wrapper


def hotkey_listener(func):
    trigger_hotkey = "ctrl+alt+v"
    stop_hotkey = "ctrl+alt+q"

    print(f"监听热键 {trigger_hotkey} 来调用功能...")
    print(f"按 {stop_hotkey} 停止监听。")

    wrapped_func = debounce_call(safe_call(func))

    keyboard.add_hotkey(trigger_hotkey, wrapped_func)

    try:
        keyboard.wait(stop_hotkey)
    finally:
        keyboard.unhook_all_hotkeys()
        print("停止热键按下，退出监听。")
```

### 关键特性说明

* **异常隔离**：任何异常不会终止热键监听
* **防抖机制**：默认 300ms 内重复触发会被忽略
* **干净退出**：退出时解除所有系统级热键钩子

---

## 四、剪贴板读取逻辑

### 支持的剪贴板类型

| 类型    | 说明                     |
|-------|------------------------|
| files | Windows 文件列表（CF_HDROP） |
| image | 图片（CF_DIB → PIL.Image） |
| text  | 文本 / HTML 提取后的纯文本      |

### 文本优先级规则

1. HTML（提取 StartFragment → 转纯文本）
2. 普通 Unicode 文本

HTML 与 text 最终只保留 **一个 text 项**。

---

## 五、剪贴板内容选择策略

程序 **只会选择一个最合适的内容**，优先级如下：

```text
files → image → text
```

此逻辑集中在 `choose_clipboard_item()` 中，后续流程无需再关心剪贴板的复杂性。

---

## 六、内容类型对应处理方式

### 1️⃣ files（文件路径）

* 认为是系统已确认的本地文件
* 不参与 config.json 匹配
* 直接调用：

```
os.startfile(path)
```

支持多文件批量打开。

---

### 2️⃣ image（图片）

* 剪贴板阶段已转换为 `PIL.Image`
* 当前行为：仅展示
* 不参与自动打开逻辑

（后续可扩展 OCR / 保存 / 打开图像软件）

---

### 3️⃣ text（文本）

* ClipboardGo 的核心智能处理路径
* 进入 **规则匹配 + 提取流程**

---

## 七、配置文件（config.json）结构

### 基本结构

```
[
  [软件路径, 匹配规则, 参数格式],
  ...
]
```

### 默认配置示例

```json
[
  ["notepad", "*.txt", "{text}"],
  [
    "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE",
    "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+)",
    "/c ipm.note /m {text}"
  ],
  [
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "((?:https?://)?[\\w.-]+\\.[a-zA-Z]{2,}(?:/[^\\s]*)?)",
    "{text}"
  ]
]
```

---

## 八、匹配与提取规则（核心设计）

### 1️⃣ 通配符规则（文件扩展名）

```text
*.txt
```

* 使用文件后缀匹配
* `{text}` = 原始文本

---

### 2️⃣ 正则规则（提取型）

#### 规则约束

* 使用 `re.search`
* **最多允许 1 个捕获组**

| 正则情况  | `{text}` 值 |
|-------|------------|
| 无分组   | 原始文本       |
| 1 个分组 | 分组内容       |
| 多个分组  | 视为配置错误     |

---

### 示例：邮箱提取

```regex
([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)
```

剪贴板内容：

```text
请帮我发给 test@example.com 谢谢
```

最终 `{text}`：

```text
test@example.com
```

---

### 示例：URL 提取（单捕获组）

```regex
((?:https?://)?[\w.-]+\.[a-zA-Z]{2,}(?:/\S*)?)
```

---

## 九、参数格式化与启动机制

### `{text}` 占位符

* 替换为：

  * 捕获组内容（若存在）
  * 否则为原始文本

### 参数构造方式

```
for part in arg_fmt.split():
    args.append(part.replace("{text}", final_text))
```

⚠️ 当前以 **空格拆分参数**，复杂参数需目标程序自行处理。

---

## 十、外部程序启动方式

```
subprocess.Popen(
    [soft] + args,
    creationflags=0x08000000
)
```

* 使用 `CREATE_NO_WINDOW`
* 程序一次性启动，不驻留后台

---

## 十一、典型使用场景

| 剪贴板内容                 | 行为           |
|-----------------------|--------------|
| `D:\\a.txt`           | 记事本打开文件      |
| `发给 test@example.com` | Outlook 新建邮件 |
| `https://example.com` | Edge 打开网页    |
| 复制图片                  | 图片预览         |

---

## 十二、运行方式

```
pip install -r requirements.txt
```

```
python main.py
```

---

**ClipboardGo 是一个以“用户意图”为核心的热键工具框架，规则简单、结构清晰、可持续扩展。**
