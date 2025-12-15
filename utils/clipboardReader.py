from io import BytesIO

import win32clipboard
import win32con
from PIL import Image
from bs4 import BeautifulSoup


def get_clipboard():
    """
    读取并解析当前剪贴板内容

    返回一个列表，每一项是一个字典：
    {
        "type": "text" | "files" | "image",
        "content": 对应内容
    }

    处理规则：
    - 文件、图片直接保留原始内容
    - 文本内容按优先级处理：HTML > 纯文本
    - HTML 文本会提取 StartFragment 并转换为纯文本
    """

    clipboard_data = []
    win32clipboard.OpenClipboard()

    try:
        text_item = None
        html_item = None

        # ---------- 纯文本 ----------
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            text_item = win32clipboard.GetClipboardData(
                win32con.CF_UNICODETEXT
            )

        # ---------- 文件列表 ----------
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
            files = win32clipboard.GetClipboardData(win32con.CF_HDROP)
            clipboard_data.append({
                "type": "files",
                "content": list(files)
            })

        # ---------- 图片 ----------
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB):
            dib = win32clipboard.GetClipboardData(win32con.CF_DIB)

            # 某些情况下 DIB 可能是字符串，需要转为 bytes
            if isinstance(dib, str):
                dib = dib.encode("latin1")

            image = Image.open(BytesIO(dib))
            clipboard_data.append({
                "type": "image",
                "content": image
            })

        # ---------- HTML ----------
        cf_html = win32clipboard.RegisterClipboardFormat("HTML Format")
        if win32clipboard.IsClipboardFormatAvailable(cf_html):
            html_item = win32clipboard.GetClipboardData(cf_html)

        # ---------- 文本优先级处理（HTML > Text） ----------
        final_text = None

        if html_item:
            if isinstance(html_item, bytes):
                html_str = html_item.decode("utf-8", errors="ignore")
            else:
                html_str = str(html_item)

            # 提取 HTML 片段（若存在）
            start = html_str.find("<!--StartFragment-->")
            end = html_str.find("<!--EndFragment-->")

            if start != -1 and end != -1:
                start += len("<!--StartFragment-->")
                fragment = html_str[start:end]
            else:
                fragment = html_str

            final_text = (
                BeautifulSoup(fragment, "html.parser")
                .get_text()
                .strip()
            )

        elif text_item:
            final_text = text_item.strip()

        if final_text:
            clipboard_data.append({
                "type": "text",
                "content": final_text
            })

        return clipboard_data

    finally:
        win32clipboard.CloseClipboard()


def choose_clipboard_item(items):
    """
    根据预设优先级选择一个剪贴板项目

    优先级：
    1. files
    2. image
    3. text

    :param items: 剪贴板项目列表
    :return: 选中的项目或 None
    """

    # 文件优先
    for item in items:
        if item["type"] == "files":
            return item

    # 其次图片
    for item in items:
        if item["type"] == "image":
            return item

    # 最后文本
    for item in items:
        if item["type"] == "text":
            return item

    return None
