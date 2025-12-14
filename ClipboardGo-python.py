import json
import os
import subprocess
import re
import win32clipboard
import win32con
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = [
    ["notepad", "*.txt", "{text}"],
    ["C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE",
     r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", "/c ipm.note /m {text}"],
    ["C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
     r"^(https?://)?([\w.-]+)\.([a-zA-Z]{2,})(/[^\s]*)?$", "{text}"]
]

# ---------------- 配置相关 ----------------
def ensure_config_exists():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)
        print(">>> 配置文件不存在，已自动创建默认 config.json\n")


def load_config():
    ensure_config_exists()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        conf = json.load(f)
    if not isinstance(conf, list) or not all(
            isinstance(i, list) and len(i) == 3 for i in conf):
        raise ValueError("config.json 格式错误，应为 [[软件路径, 匹配格式, 参数格式], ...]")
    return conf


def is_wildcard_format(fmt: str):
    return fmt.startswith("*.") and len(fmt) > 2


def match_format(text: str, fmt: str) -> bool:
    if is_wildcard_format(fmt):
        ext = os.path.splitext(text)[1].lower()
        return ext == fmt[1:].lower()
    try:
        return re.fullmatch(fmt, text) is not None
    except re.error:
        return False


def find_software_for_file(text: str):
    conf = load_config()
    for path, fmt, arg_fmt in conf:
        if match_format(text, fmt):
            return path, arg_fmt
    return None, None


def open_with_software(filename):
    soft, arg_fmt = find_software_for_file(filename)
    if not soft:
        print("未找到匹配的软件")
        print(f"内容: {filename}")
        return

    # 参数格式化，使用列表保证路径带空格不会拆开
    args = []
    for part in arg_fmt.split():
        if "{text}" in part:
            args.append(part.replace("{text}", filename))
        else:
            args.append(part)

    print(f"静默打开文件：{filename}")
    print(f"使用软件：{soft}")
    print(f"参数：{args}")

    CREATE_NO_WINDOW = 0x08000000
    subprocess.Popen([soft] + args, creationflags=CREATE_NO_WINDOW)


def get_clipboard():
    """
    返回剪贴板内容列表，每一项是一个字典：
    {
        "type": "text" / "files" / "image",
        "content": 对应内容
    }

    处理逻辑：
    - 如果存在 HTML 内容，则渲染 HTML 提取文本并 strip
    - 否则使用纯文本 strip
    - 文件和图片保持原样
    """
    clipboard_data = []
    win32clipboard.OpenClipboard()
    try:
        text_item = None
        html_item = None

        # 文本
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            text_item = text  # 先保存，等优先级判断

        # 文件列表
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
            files = win32clipboard.GetClipboardData(win32con.CF_HDROP)
            clipboard_data.append({"type": "files", "content": list(files)})

        # 图片
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB):
            dib = win32clipboard.GetClipboardData(win32con.CF_DIB)
            if isinstance(dib, str):
                dib = dib.encode('latin1')
            image = Image.open(BytesIO(dib))
            clipboard_data.append({"type": "image", "content": image})

        # HTML
        CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")
        if win32clipboard.IsClipboardFormatAvailable(CF_HTML):
            html = win32clipboard.GetClipboardData(CF_HTML)
            html_item = html  # 保存 HTML，优先处理

        # 处理文本优先级：HTML > Text
        final_text = None
        if html_item:
            if isinstance(html_item, bytes):
                html_str = html_item.decode('utf-8', errors='ignore')
            else:
                html_str = str(html_item)
            start_idx = html_str.find("<!--StartFragment-->")
            end_idx = html_str.find("<!--EndFragment-->")
            if start_idx != -1 and end_idx != -1:
                start_idx += len("<!--StartFragment-->")
                fragment = html_str[start_idx:end_idx]
            else:
                fragment = html_str
            final_text = BeautifulSoup(fragment, "html.parser").get_text().strip()
        elif text_item:
            final_text = text_item.strip()

        if final_text:
            clipboard_data.append({"type": "text", "content": final_text})

    finally:
        win32clipboard.CloseClipboard()

    return clipboard_data

# ---------------- 主流程 ----------------
if __name__ == "__main__":
    ensure_config_exists()

    print("当前配置：")
    for s, f, a in load_config():
        print(f"  软件: {s}   格式: {f}   参数格式: {a}")
    print("\n检测剪贴板内容...\n")

    clipboard_items = get_clipboard()
    for item in clipboard_items:
        print(f"类型: {item['type']}")
        if item['type'] == "image":
            print("剪贴板包含图片，可用PIL处理。")
            item['content'].show()
        elif item['type'] == "files":
            for f in item['content']:
                open_with_software(f)
        else:  # text 或 html
            open_with_software(item['content'])
        print("-" * 40)
