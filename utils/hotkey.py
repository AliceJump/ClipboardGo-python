import keyboard
import time


def safe_call(func):
    """
    为函数增加异常保护，防止热键回调中断监听

    :param func: 需要安全执行的函数
    :return: 包装后的函数
    """
    def wrapper():
        try:
            func()
        except Exception as e:
            print("ClipboardGo 执行出错：", e)
    return wrapper


# 上一次触发时间（用于防抖）
_last_trigger = 0


def debounce_call(func, delay=0.3):
    """
    为函数增加防抖逻辑，避免短时间内重复触发

    :param func: 需要防抖的函数
    :param delay: 最小触发间隔（秒）
    :return: 包装后的函数
    """
    def wrapper():
        global _last_trigger
        now = time.time()

        # 若触发间隔小于 delay，则忽略本次调用
        if now - _last_trigger < delay:
            return

        _last_trigger = now
        func()

    return wrapper


def hotkey_listener(func):
    """
    注册并监听全局热键

    - 触发热键：执行指定函数
    - 停止热键：退出监听并清理所有热键

    :param func: 热键触发时要执行的函数
    """

    trigger_hotkey = "ctrl+alt+v"
    stop_hotkey = "ctrl+alt+q"

    print(f"监听热键 {trigger_hotkey} 来调用功能...")
    print(f"按 {stop_hotkey} 停止监听。")

    # 为回调函数增加异常保护与防抖
    wrapped_func = debounce_call(safe_call(func))

    # 注册触发热键
    keyboard.add_hotkey(trigger_hotkey, wrapped_func)

    try:
        # 阻塞等待停止热键
        keyboard.wait(stop_hotkey)
    finally:
        # 清理所有已注册的热键
        keyboard.unhook_all_hotkeys()
        print("停止热键按下，退出监听。")
