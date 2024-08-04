import time
import utils.ScreenCompare as Sc
from utils.GIautogui import GIautogui as pyautogui_Mo
import pyautogui
import config
import os
import cv2
import numpy as np
import Package.CalibrateMap
import AutoEnigma
from Package.log_config import logger
import threading
from AutoFight import AutoFightConfig
from utils.OCR import ppocr
path = config.get_config_directory()
# 更改工作目录为脚本所在目录
os.chdir(path)
stop_event = threading.Event()

# 打印当前工作目录
print("Lock_East_Angle.py:当前工作目录：", os.getcwd())
def is_grayscale_region_present(x1, y1, x2, y2, saturation_threshold=0.1, area_threshold=0.2):
    # 截取屏幕指定区域
    screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # 将图像转换为HSV颜色空间
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 提取S通道（饱和度）
    saturation = hsv_image[:, :, 1]

    # 计算饱和度低于阈值的像素数量
    low_saturation_pixels = np.sum(saturation < (saturation_threshold * 255))

    # 计算总像素数量
    total_pixels = saturation.size

    # 计算低饱和度像素占总像素的比例
    low_saturation_ratio = low_saturation_pixels / total_pixels

    # 如果低饱和度像素比例大于指定阈值，返回True，否则返回False
    if low_saturation_ratio > area_threshold:
        return True
    else:
        return False
def autofight():
    AutoFightConfig.main()

def wait_screen(path_to_img,timesmax = 200):
    x, y = Sc.CompareWithin_Continue(path_to_img, timesmax=timesmax)
    return x, y


def go_into_enigma():
    time.sleep(1)
    pyautogui_Mo.press('f')  # 点击秘境
    x, y = wait_screen('./img/true.png')  # 单人挑战
    if x != 0:
        time.sleep(0.5)
        pyautogui_Mo.click(x, y)
    time.sleep(1)
    x, y = wait_screen('./img/true.png')  # 开始挑战
    if x != 0:
        time.sleep(0.5)
        pyautogui_Mo.click(x, y)
    a, b = Sc.CompareWithin('./img/true.png')  # 可能出现的额外的确认
    if a != 0:
        time.sleep(0.5)
        pyautogui_Mo.click(a, b)


def recognition_dead():
    dead1 = is_grayscale_region_present(1768, 217, 1837, 594)
    dead2 = is_grayscale_region_present(1768, 217, 1837, 594)
    dead3 = is_grayscale_region_present(1768, 217, 1837, 594)
    if not dead1 or not dead2 or not dead3:
        dead = False
    else:
        dead = True
    if dead:
        logger.warning('存在角色死亡')
        Package.CalibrateMap.newlife()
        AutoEnigma.start()
        go_into_enigma()
        x, y = wait_screen('./img/Enigma_close.png')  # 秘境提示点击
        if x != 0:
            time.sleep(0.5)
            pyautogui_Mo.click(x, y)

def fight_in_Enigma(times):
    x, y = wait_screen('./img/Enigma_close.png')  # 秘境提示点击
    if x != 0:
        time.sleep(0.5)
        pyautogui_Mo.click(x, y)
    time.sleep(1)
    recognition_dead()
    time.sleep(0.5)
    pyautogui_Mo.keyDown('w')
    x, y = wait_screen('./img/jiaohu.png')
    logger.info('检测到交互键')
    if x != 0:
        pyautogui_Mo.press('f')
    if x != 0:
        pyautogui_Mo.press('f')
        pyautogui_Mo.keyUp('w')
        main_thread = threading.Thread(target=autofight)
        main_thread.start()
        # 等待结束停止AutoFight线程
        from AutoFight import FindTreeMain  # 我劝你别在10秒内打完！！！！！
        x, y = wait_screen('./img/successful.png', timesmax=2000)
        logger.info('检测到挑战成功')
        if x != 0:
            AutoFightConfig.stop()


        # 等待主线程结束
        main_thread.join()
        stop_event.clear()
        logger.info("自动战斗已停止")
        pyautogui_Mo.click(button='MIDDLE')
        FindTreeMain.main_threading()

        # 走到古化石树
        pyautogui_Mo.keyDown('w')
        time.sleep(0.35)
        pyautogui_Mo.keyDown('shift')
        x, y = wait_screen('./img/reward2.png')
        if x != 0:
            pyautogui_Mo.press('f')
            pyautogui_Mo.keyUp('shift')
        time.sleep(1)
        a, b = Sc.CompareWithin('./img/shuzhi.png')
        if a != 0:
            pyautogui_Mo.click(a, b)
            time.sleep(1)
        else:
            logger.info('没有浓缩树脂了！')
        for _ in range(10):
            pyautogui_Mo.click(1847, 36)
            time.sleep(0.25)
        x1, y1 = wait_screen('./img/true.png')
        time.sleep(1)
        result = ppocr(1195, 916, 1244, 950, model='int')
        try:
            result_num = result[0]
        except IndexError:
            result_num = 0
        if result_num > 20:
            pyautogui_Mo.click(x1, y1)
            finish = False
        else:
            a, b = Sc.CompareWithin('./img/cancel.png')
            logger.info('没有体力了！自动秘境结束')
            pyautogui_Mo.click(a, b)
            finish = True
        return finish

def main():
    dead = is_grayscale_region_present(1768, 217, 1837, 594)
    if dead:
        logger.warning('存在角色死亡')  # TODO：返回神像后返回
        Package.CalibrateMap.newlife()
        AutoEnigma.start()
    go_into_enigma()
    times = 1
    finish = fight_in_Enigma(times)
    while not finish:
        times = times + 1
        finish = fight_in_Enigma(times)
        logger.info('自动秘境结束')


time.sleep(2)
if __name__ == '__main__':
    main()
