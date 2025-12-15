import os
import subprocess
from matcher import find_software

def open_with_software(text, item_type=None):
    if item_type == "files":
        os.startfile(text)
        print(">>> 打开详情")
        print("这是本地文件,直接本地打开")
        return

    soft, arg_fmt, extracted = find_software(text)
    if not soft:
        print("未找到匹配规则")
        return

    final_text = extracted or text
    args = [p.replace("{text}", final_text) for p in arg_fmt.split()]

    print(">>> 打开详情")
    print("软件:", soft)
    print("参数:", args)

    subprocess.Popen([soft] + args, creationflags=0x08000000)
