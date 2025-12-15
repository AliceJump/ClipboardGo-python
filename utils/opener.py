import os
import subprocess
from utils.matcher import find_software


def open_with_software(text, item_type=None):
    """
    根据内容类型使用对应的软件打开内容

    :param text: 要打开的文本或文件路径
    :param item_type: 内容类型（如 files）
    """

    # 如果是文件类型，直接使用系统默认方式打开
    if item_type == "files":
        os.startfile(text)
        print(">>> 打开详情")
        print("这是本地文件，已使用系统默认方式打开")
        return

    # 根据文本内容匹配可用的软件及参数格式
    soft, arg_fmt, extracted = find_software(text)
    if not soft:
        print("未找到匹配规则")
        return

    # 优先使用从文本中提取的内容，否则使用原始文本
    final_text = extracted or text

    # 构造启动参数，将占位符替换为实际文本
    args = [
        p.replace("{text}", final_text)
        for p in arg_fmt.split()
    ]

    # 输出调试信息
    print(">>> 打开详情")
    print("软件:", soft)
    print("参数:", args)

    # 启动外部程序（隐藏控制台窗口）
    subprocess.Popen(
        [soft] + args,
        creationflags=0x08000000
    )
