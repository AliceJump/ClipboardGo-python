import os
import re
from config import load_config

def is_wildcard_format(fmt: str):
    return fmt.startswith("*.") and len(fmt) > 2

def match_and_extract(text: str, fmt: str):
    if is_wildcard_format(fmt):
        return os.path.splitext(text)[1].lower() == fmt[1:].lower(), text

    m = re.search(fmt, text)
    if not m:
        return False, None

    groups = m.groups()
    return True, groups[0] if groups else text

def find_software(text: str):
    for path, fmt, arg_fmt in load_config():
        ok, extracted = match_and_extract(text, fmt)
        if ok:
            return path, arg_fmt, extracted
    return None, None, None
