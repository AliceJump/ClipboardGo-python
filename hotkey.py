import keyboard  # pip install keyboard
import time

def hotkey_listener(func):
    # 设置触发热键和停止热键
    trigger_hotkey = "ctrl+alt+v"
    stop_hotkey = "ctrl+alt+q"

    print(f"监听热键 {trigger_hotkey} 来调用功能...")
    print(f"按 {stop_hotkey} 停止监听。")

    # 注册主功能热键
    keyboard.add_hotkey(trigger_hotkey, func)

    # 注册停止热键，按下时会退出程序
    keyboard.wait(stop_hotkey)
    print("停止热键按下，退出监听。")
