import threading
import time
import logging
from utils.GIautogui import GIautogui as pyautogui
from utils import OCR
import pydirectinput
import re
import os
import json
import config
from utils.Tools import read_config_value as rcv

path = config.get_config_directory()
# 更改工作目录为脚本所在目录
os.chdir(path)
# 打印当前工作目录
print("AutoFightConfig.py:当前工作目录：", os.getcwd())
# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
stop_event = threading.Event()

# 加载角色别名映射
with open('./AutoFight/combat_avatar.json', 'r', encoding='utf-8') as file:
    character_data = json.load(file)


def load_character_aliases(character_data):
    alias_mapping = {}
    for character in character_data:
        for alias in character["alias"]:
            alias_mapping[alias] = character["name"]
    return alias_mapping


alias_mapping = load_character_aliases(character_data)


# 解析配置文件
def parse_config(file_path):
    character_actions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split()
                character = parts[0]
                actions = parts[1].split(',')
                character_actions.append((character, actions))
    logger.info("解析配置文件：%s", character_actions)
    return character_actions


# 快速鼠标圆圈移动
def fast_mouse_circle(times):
    for _ in range(times):
        pydirectinput.moveRel(2000, 0, duration=0.1, relative=True)  # 向右移动


# 清洗OCR结果中的特殊符号并进行别名映射
def clean_ocr_result(ocr_results):
    clean_results = {}
    for character, coords in ocr_results.items():
        clean_character = re.sub(r'[^\u4e00-\u9fa5]', '', character)  # 仅保留汉字字符
        if clean_character in alias_mapping:
            clean_results[alias_mapping[clean_character]] = coords
        elif clean_character:
            clean_results[clean_character] = coords
    return clean_results


# 获取屏幕上的角色列表
def get_characters_from_screen():
    ocr_results = OCR.ppocr(1660, 235, 1764, 574, model='box and text')
    clean_results = clean_ocr_result(ocr_results)
    logger.info("OCR结果：%s", clean_results)

    character_positions = []
    for character, (x1, y1, x2, y2) in clean_results.items():
        character_positions.append((character, y1))
    character_positions.sort(key=lambda x: x[1])
    sorted_characters = [char for char, y in character_positions]
    logger.info("排序后的角色：%s", sorted_characters)
    return sorted_characters


# 寻找最匹配的配置文件
def find_best_matching_config(current_characters):
    config_directory = './AutoFight/AutoFightconfig'
    best_match_file = None
    best_match_count = 0

    for file_name in os.listdir(config_directory):
        if file_name.endswith('.txt'):
            file_path = os.path.join(config_directory, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                config_characters = [line.split()[0] for line in file if line.strip()]
                match_count = len(set(current_characters) & set(config_characters))
                if match_count > best_match_count:
                    best_match_count = match_count
                    best_match_file = file_path

    return best_match_file


# 执行动作
def perform_action(character, action):
    logger.info("开始执行动作：%s, %s", character, action)
    parts = action.split('(')
    action_name = parts[0]
    param = parts[1][:-1] if len(parts) > 1 else None

    if action_name == 'skill' or action_name == 'e':  # E技能配置--草神专配
        if param == 'hold':
            pyautogui.keyDown('e')
            if character == '纳西妲':
                time.sleep(1)
                fast_mouse_circle(5)
                time.sleep(1)
            else:
                time.sleep(1)
                pyautogui.keyUp('e')
                time.sleep(1)
        else:
            pyautogui.press('e')
            time.sleep(0.35)

    elif action_name == 'burst' or action_name == 'q':  # 大招配置
        pyautogui.press('q')
        time.sleep(2.2)

    elif action_name == 'attack':  # 普攻配置
        duration = float(param) if param else 0.2
        end_time = time.time() + duration
        while time.time() < end_time:
            pyautogui.click()
            time.sleep(0.3)

    elif action_name == 'charge':  # 重击配置--那位维莱特专配
        duration = float(param) if param else 0.2
        pyautogui.mouseDown()
        if character == '那维莱特':
            fast_mouse_circle(40)
            pyautogui.mouseUp()
            time.sleep(0.5)
        else:
            time.sleep(duration)
        pyautogui.mouseUp()
        time.sleep(0.5)

    elif action_name == 'wait':  # 等待 秒
        duration = float(param) if param else 0.5
        time.sleep(duration)

    elif action_name == 'dash':  # 闪避
        duration = float(param) if param else 0.5
        pyautogui.keyDown('shift')
        time.sleep(duration)
        pyautogui.keyUp('shift')
        time.sleep(0.45)

    elif action_name == 'jump' or action_name == 'j':
        pyautogui.press('space')

    elif action_name == 'walk':
        direction = param.split(',')[0]
        duration = float(param.split(',')[1])
        pyautogui.keyDown(direction)
        time.sleep(duration)
        pyautogui.keyUp(direction)

    elif action_name in ['w', 'a', 's', 'd']:
        duration = float(param) if param else 0.2
        pyautogui.keyDown(action_name)
        time.sleep(duration)
        pyautogui.keyUp(action_name)
    logger.info("完成动作：%s, %s", character, action)


# 获取战斗配置文件
def using_combat_file():
    config_file = rcv('./config.txt', 'AutoFight', 'using_combat_file')
    config_directory = './AutoFight/AutoFightconfig/'
    config_file = config_directory + config_file
    return config_file


# 主程序
def main(config_file=using_combat_file()):
    characters_on_screen = get_characters_from_screen()

    if config_file:
        character_actions = parse_config(config_file)
    else:
        best_match_file = find_best_matching_config(characters_on_screen)
        if best_match_file:
            logger.info("使用最匹配的配置文件：%s", best_match_file)
            character_actions = parse_config(best_match_file)
        else:
            logger.error("没有找到匹配的配置文件")
            return

    character_key_mapping = {character: str(i + 1) for i, character in enumerate(characters_on_screen)}
    while not stop_event.is_set():

        # 将角色按从上到下排序，分配按键1, 2, 3, 4
        logger.info("角色按键映射：%s", character_key_mapping)

        for character, actions in character_actions:
            if character in character_key_mapping and not stop_event.is_set():
                pyautogui.press(character_key_mapping[character])  # 切换角色
                logger.info("切换到角色：%s, 按键：%s", character, character_key_mapping[character])
                time.sleep(0.5)
                for action in actions:
                    perform_action(character, action)
                time.sleep(1)  # 每个角色动作完成后稍作停顿
    else:
        stop_event.clear()


# 停止线程：用于多线程调用
def stop():
    # 设置停止事件
    stop_event.set()


if __name__ == "__main__":
    time.sleep(3)
    main()