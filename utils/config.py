import json
import os

# 配置文件路径
CONFIG_FILE = "../config.json"

# 默认配置规则
# 每一项格式为：
# [软件路径, 匹配规则(通配符或正则), 启动参数模板]
DEFAULT_CONFIG = [
    ["notepad", "*.txt", "{text}"],
    [
        "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE",
        "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+)",
        "/c ipm.note /m {text}"
    ],
    [
        "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        r"((?:https?://)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)",
        "{text}"
    ]
]


def ensure_config_exists():
    """
    确保配置文件存在

    若配置文件不存在，则使用 DEFAULT_CONFIG 创建
    """
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(
                DEFAULT_CONFIG,
                f,
                ensure_ascii=False,
                indent=4
            )


def load_config():
    """
    加载配置文件内容

    - 若配置文件不存在：自动创建并返回默认配置
    - 若配置文件格式损坏：重置为默认配置

    :return: 配置列表
    """
    ensure_config_exists()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except json.decoder.JSONDecodeError:
        # 配置文件损坏时自动恢复默认配置
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(
                DEFAULT_CONFIG,
                f,
                ensure_ascii=False,
                indent=4
            )
        return DEFAULT_CONFIG
