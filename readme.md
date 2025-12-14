# ClipboardGo – 工作流程与规则说明

本文档基于当前最新代码实现，说明 **ClipboardGo** 从读取剪贴板到打开目标程序的完整流程、匹配规则设计，以及参数传递机制。

---

## 一、整体工作流程（总览）

```text
启动程序
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
匹配配置规则并提取关键文本
  ↓
构造启动参数
  ↓
静默启动外部程序
```

---

## 二、剪贴板读取逻辑

### 支持的剪贴板类型

| 类型    | 说明                     |
|-------|------------------------|
| files | Windows 文件列表（CF_HDROP） |
| image | 图片（CF_DIB → PIL Image） |
| text  | 文本 / HTML 解析后的纯文本      |

### 文本优先级规则

1. HTML（提取 StartFragment → 转纯文本）
2. 普通 Unicode 文本

HTML 与文本只会保留 **一个最终 text** 项。

---

## 三、剪贴板内容选择策略

程序不会同时处理多个类型，而是按以下顺序 **只选择一个最合适的内容**：

```text
files  → image → text
```

对应代码逻辑：

```
files 优先
image 次之
最后才是 text
```

---

## 四、内容类型对应的处理方式

### 1️⃣ files（文件路径）

* 认为是 **系统已确认的本地文件**
* 直接调用：

```
os.startfile(path)
```

* 不参与 config.json 匹配

---

### 2️⃣ image（图片）

* 已在剪贴板读取阶段转换为 `PIL.Image`
* 仅展示，不参与自动打开逻辑

---

### 3️⃣ text（文本 / HTML 提取结果）

* 进入 **规则匹配 + 提取流程**
* 是本项目最核心的智能逻辑

---

## 五、配置文件（config.json）结构

### 基本结构

```
[
  [软件路径, 匹配规则, 参数格式],
  ...
]
```

### 当前默认配置示例

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

## 六、匹配与提取规则（核心设计）

### 1️⃣ 通配符规则（文件扩展名）

```text
*.txt
```

* 使用文件后缀匹配
* `{text}` = 原始文本

---

### 2️⃣ 正则规则（提取型）

#### 关键设计原则

* 使用 `re.search`
* **最多只允许 1 个捕获组**
* 该捕获组的内容将作为 `{text}`

```text
无分组 → {text} = 原始文本
1 个分组 → {text} = 分组内容
>1 分组 → 视为配置错误
```

---

### 示例：邮箱提取

```regex
([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)
```

可匹配：

* `test@example.com`
* `帮我发给 test@example.com`
* `请帮忙发给 test@example.com 谢谢`

最终 `{text}`：

```text
test@example.com
```

---

### 示例：URL 提取（只允许 1 个捕获组）

```regex
((?:https?://)?[\w.-]+\.[a-zA-Z]{2,}(?:/\S*)?)
```

说明：

* 所有内部结构使用 `(?:...)` 非捕获组
* 外层仅保留一个捕获组

---

## 七、参数格式化与启动机制

### 参数格式 `{text}`

* `{text}` 会被替换为：

  * 捕获组内容（若存在）
  * 否则为原始文本

### 参数构造方式

```
for part in arg_fmt.split():
    args.append(part.replace("{text}", final_text))
```

⚠️ 注意：

* 当前实现以 **空格拆分参数**
* 参数中若包含空格，需由目标程序自行容错

---

## 八、外部程序启动方式

```
subprocess.Popen(
    [soft] + args,
    creationflags=0x08000000
)
```

* `CREATE_NO_WINDOW`：不弹出命令行窗口
* 程序为一次性执行，不驻留后台

---

## 九、典型使用场景

| 剪贴板内容                 | 行为           |
|-----------------------|--------------|
| `D:\\a.txt`           | 记事本打开文件      |
| `发给 test@example.com` | Outlook 新建邮件 |
| `https://example.com` | Edge 打开网页    |
| 复制图片                  | 弹出图片预览       |

---
## 使用方式

```
pip install requirements.txt
```
```
python main.py
```

