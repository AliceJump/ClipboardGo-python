import pyperclip

from utils.clipboardReader import get_clipboard, choose_clipboard_item
from utils.opener import open_with_software
from utils.config import ensure_config_exists
from utils.hotkey import hotkey_listener
from utils.image import open_img_with_func
from utils.scan import decode_qr


def main():
    """
    剪贴板处理主流程：
    1. 确保配置文件存在
    2. 读取剪贴板内容
    3. 让用户选择要处理的项目
    4. 根据内容类型调用对应的软件打开
    """

    # 确保配置文件存在（不存在则创建）
    ensure_config_exists()

    # 获取剪贴板中的所有项目
    items = get_clipboard()

    # 让用户从剪贴板项目中选择一个
    item = choose_clipboard_item(items)

    # 根据选中项目的类型进行处理
    if item["type"] == "files":
        # 文件类型：逐个文件使用对应软件打开
        for f in item["content"]:
            open_with_software(f, "files")
    elif item['type'] == "image":
        print("剪贴板包含图片，可扫描处理。")
        str1=open_img_with_func(item["content"],decode_qr)
        if str1:
            pyperclip.copy(str1)
            print("识别结果:",str1)
        else:
            print("识别失败，直接展示")
            item["content"].show()
    else:
        # 其他类型：直接打开内容
        open_with_software(item["content"], item["type"])


if __name__ == "__main__":
    # 启动热键监听，触发 main 函数
    hotkey_listener(main)



r'''
D:\items\project\python_project\ClipboardGo-python\origin.txt
发给test@example.com好么
看一下网页www.baidu.com
'''