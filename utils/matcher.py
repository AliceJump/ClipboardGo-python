import os
import re
from .config import load_config


def is_wildcard_format(fmt: str):
    """
    判断是否为通配符格式（如 *.txt、*.png）

    :param fmt: 匹配格式字符串
    :return: 是否为通配符格式
    """
    return fmt.startswith("*.") and len(fmt) > 2


def match_and_extract(text: str, fmt: str):
    """
    根据给定格式匹配文本，并提取可用内容

    支持两种格式：
    1. 通配符格式（*.ext）：用于文件扩展名匹配
    2. 正则表达式：用于复杂文本匹配与提取

    :param text: 待匹配的文本
    :param fmt: 匹配格式（通配符或正则）
    :return: (是否匹配, 提取的内容)
    """

    # 通配符匹配：仅比较文件扩展名
    if is_wildcard_format(fmt):
        matched = os.path.splitext(text)[1].lower() == fmt[1:].lower()
        return matched, text

    # 正则表达式匹配
    m = re.search(fmt, text)
    if not m:
        return False, None

    # 若正则包含分组，则优先返回第一个分组内容
    groups = m.groups()
    return True, groups[0] if groups else text


def find_software(text: str):
    """
    根据配置规则查找可用于打开文本的软件

    配置项格式：
    (软件路径, 匹配格式, 参数模板)

    :param text: 输入的文本内容
    :return: (软件路径, 参数格式, 提取后的文本)
    """

    # 遍历配置文件中的所有匹配规则
    for path, fmt, arg_fmt in load_config():
        ok, extracted = match_and_extract(text, fmt)
        if ok:
            return path, arg_fmt, extracted

    # 未找到任何匹配规则
    return None, None, None
