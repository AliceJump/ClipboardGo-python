from io import BytesIO

import win32clipboard
import win32con
from PIL import Image
from bs4 import BeautifulSoup


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
        cf_html = win32clipboard.RegisterClipboardFormat("HTML Format")
        if win32clipboard.IsClipboardFormatAvailable(cf_html):
            html = win32clipboard.GetClipboardData(cf_html)
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
        return clipboard_data

    finally:
        win32clipboard.CloseClipboard()

def choose_clipboard_item(items):
    # files 优先
    for item in items:
        if item["type"] == "files":
            return item

    # image 次之
    for item in items:
        if item["type"] == "image":
            return item

    # 最后 text
    for item in items:
        if item["type"] == "text":
            return item

    return None
