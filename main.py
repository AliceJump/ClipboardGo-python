from clipboardReader import get_clipboard, choose_clipboard_item
from opener import open_with_software
from config import ensure_config_exists
from hotkey import hotkey_listener
def main():
    ensure_config_exists()
    items = get_clipboard()
    item = choose_clipboard_item(items)

    if item["type"] == "files":
        for f in item["content"]:
            open_with_software(f, "files")
    else:
        open_with_software(item["content"], item["type"])

if __name__ == "__main__":
    hotkey_listener(main)


r'''
D:\items\project\python_project\ClipboardGo-python\origin.txt
发给test@example.com好么
看一下网页www.baidu.com
'''