# encoding=utf-8
# ----------------------------------------
# 语言：Python2.7.13
# 日期：2017-11-28
# 作者：Tilyp<http://blog.csdn.net/tilyp>
# 功能：破解四宫格图形验证码，登录m.weibo.cn
# ----------------------------------------

import StringIO
import random
import time
from math import sqrt
import numpy as np
from PIL import Image
from images import images
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.command import Command
from sklearn.metrics import euclidean_distances

PIXELS = []

def getExactly(im):
    """ 精确剪切"""
    imin = -1
    imax = -1
    jmin = -1
    jmax = -1
    row = im.size[0]
    col = im.size[1]
    for i in range(row):
        for j in range(col):
            if im.load()[i, j] != 255:
                imax = i
                break
        if imax == -1:
            imin = i

    for j in range(col):
        for i in range(row):
            if im.load()[i, j] != 255:
                jmax = j
                break
        if jmax == -1:
            jmin = j
    return (imin + 1, jmin + 1, imax + 1, jmax + 1)

def move(browser, coordinate, coordinate0):
    """ 从坐标coordinate0，移动到坐标coordinate """
    time.sleep(0.05)
    length = sqrt((coordinate[0] - coordinate0[0]) ** 2 + (coordinate[1] - coordinate0[1]) ** 2)  # 两点直线距离
    if length < 4:  # 如果两点之间距离小于4px，直接划过去
        ActionChains(browser).move_by_offset(coordinate[0] - coordinate0[0], coordinate[1] - coordinate0[1]).perform()
        return
    else:  # 递归，不断向着终点滑动
        step = random.randint(3, 5)
        x = int(step * (coordinate[0] - coordinate0[0]) / length)  # 按比例
        y = int(step * (coordinate[1] - coordinate0[1]) / length)
        ActionChains(browser).move_by_offset(x, y).perform()
        move(browser, coordinate, (coordinate0[0] + x, coordinate0[1] + y))

def draw(browser, ttype):
    """ 滑动 """
    if len(ttype) == 4:
        px0 = PIXELS[int(ttype[0]) - 1]
        login = browser.find_element_by_id('loginAction')
        ActionChains(browser).move_to_element(login).move_by_offset(px0[0] - login.location['x'] - int(login.size['width'] / 2), px0[1] - login.location['y'] - int(login.size['height'] / 2)).perform()
        browser.execute(Command.MOUSE_DOWN, {})

        px1 = PIXELS[int(ttype[1]) - 1]
        move(browser, (px1[0], px1[1]), px0)

        px2 = PIXELS[int(ttype[2]) - 1]
        move(browser, (px2[0], px2[1]), px1)

        px3 = PIXELS[int(ttype[3]) - 1]
        move(browser, (px3[0], px3[1]), px2)
        browser.execute(Command.MOUSE_UP, {})
    else:
        print 'Sorry! Failed! Maybe you need to update the code.'

def getType_similirity(browser):

    """ 识别图形路径 ，采用欧氏距离计算相似度"""

    time.sleep(3.5)
    im0 = Image.open(StringIO.StringIO(browser.get_screenshot_as_png()))
    box = browser.find_element_by_id('patternCaptchaHolder')
    im = im0.crop((int(box.location['x']) + 10, int(box.location['y']) + 100,
                   int(box.location['x']) + box.size['width'] - 10,
                   int(box.location['y']) + box.size['height'] - 10)).convert('L')
    newBox = getExactly(im)
    im = im.crop(newBox)
    data = list(im.getdata())
    data_vec = np.array(data)
    vectDict = {}
    for i, j in images.items():
        vect = euclidean_distances(data_vec, j)
        vectDict[i] = vect[0][0]
    """对欧氏距离计算结果排序，取最小值"""
    sortDict = sorted(vectDict.iteritems(), key=lambda d: d[1], reverse=True)
    ttype = sortDict[-1][0]
    px0_x = box.location['x'] + 40 + newBox[0]
    px1_y = box.location['y'] + 130 + newBox[1]
    PIXELS.append((px0_x, px1_y))
    PIXELS.append((px0_x + 100, px1_y))
    PIXELS.append((px0_x, px1_y + 100))
    PIXELS.append((px0_x + 100, px1_y + 100))
    return ttype


def main():
    browser = webdriver.Chrome()
    browser.set_window_size(1050, 840)
    browser.get('https://passport.weibo.cn/signin/login?entry=mweibo&r=https://weibo.cn/')
    time.sleep(1)
    name = browser.find_element_by_id('loginName')
    psw = browser.find_element_by_id('loginPassword')
    login = browser.find_element_by_id('loginAction')
    name.send_keys('15504043442')  # 测试账号
    psw.send_keys('puybgk4834l')
    login.click()
    ttype = getType_similirity(browser)
    draw(browser, ttype)  # 滑动破解
    time.sleep(20)
    browser.close()

if __name__ == '__main__':
    main()
