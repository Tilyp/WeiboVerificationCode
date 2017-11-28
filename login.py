# encoding=utf-8
# ----------------------------------------
# 语言：Python2.7
# 日期：2017-05-01
# 作者：九茶<http://blog.csdn.net/bone_ace>
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

from ims import ims

PIXELS = []

ims_dict = {}
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

def getType(browser):
    """ 识别图形路径 """
    ttype = ''
    time.sleep(3.5)
    im0 = Image.open(StringIO.StringIO(browser.get_screenshot_as_png()))
    box = browser.find_element_by_id('patternCaptchaHolder')
    im = im0.crop((int(box.location['x']) + 10, int(box.location['y']) + 100, int(box.location['x']) + box.size['width'] - 10, int(box.location['y']) + box.size['height'] - 10)).convert('L')
    show_img(im, "jiepin")
    newBox = getExactly(im)
    im = im.crop(newBox)
    width = im.size[0]
    height = im.size[1]           
    for png in ims.keys():
        isGoingOn = True 
        for i in range(width):
            for j in range(height):  
                if ((im.load()[i, j] >= 245 and ims[png][i][j] < 245) or (im.load()[i, j] < 245 and ims[png][i][j] >= 245)) and abs(ims[png][i][j] - im.load()[i, j]) > 14: # 以245为临界值，大约245为空白，小于245为线条；两个像素之间的差大约10，是为了去除245边界上的误差
                    isGoingOn = False
                    break
            if isGoingOn is False:
                ttype = ''
                break
            else:
                ttype = png
        else:
            break
    px0_x = box.location['x'] + 40 + newBox[0]
    px1_y = box.location['y'] + 130 + newBox[1]
    PIXELS.append((px0_x, px1_y))
    PIXELS.append((px0_x + 100, px1_y))
    PIXELS.append((px0_x, px1_y + 100))
    PIXELS.append((px0_x + 100, px1_y + 100))
    return ttype

def show_img(im, title):
    import pylab as pl
    pl.gray()
    pl.matshow(im)
    pl.title(title)
    pl.show()

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
    """ 识别图形路径 """
    ttype = ''
    time.sleep(3.5)
    im0 = Image.open(StringIO.StringIO(browser.get_screenshot_as_png()))
    box = browser.find_element_by_id('patternCaptchaHolder')
    im = im0.crop((int(box.location['x']) + 10, int(box.location['y']) + 100,
                   int(box.location['x']) + box.size['width'] - 10,
                   int(box.location['y']) + box.size['height'] - 10)).convert('L')
    newBox = getExactly(im)
    im = im.crop(newBox)
    data = list(im.getdata())
    """保存图片灰度值"""
    save_pngs(data)
    data_vec = np.array(data)
    # pnglist = []
    # vectlist = []
    vectDict = {}
    for i, j in images.items():
        vect = euclidean_distances(data_vec, j)
        vectDict[i] = vect[0][0]
    sortDict = sorted(vectDict.iteritems(), key=lambda d: d[1], reverse=True)
    ttype = sortDict[-1][0]
    # listPng = list(sortDict[-1][0])
    # pos = {}
    # for index, val in enumerate(listPng):
    #     if val == "2":
    #         pos["n"] = index
    #     if val == "3":
    #         pos["p"] = index
    # for key, value in pos.items():
    #     if key == "n":
    #         listPng[value] = 3
    #     if key == "p":
    #         listPng[value] = 2
    # for sfg in listPng:
    #     ttype += str(sfg)
    px0_x = box.location['x'] + 40 + newBox[0]
    px1_y = box.location['y'] + 130 + newBox[1]
    PIXELS.append((px0_x, px1_y))
    PIXELS.append((px0_x + 100, px1_y))
    PIXELS.append((px0_x, px1_y + 100))
    PIXELS.append((px0_x + 100, px1_y + 100))
    return ttype
    # import pandas as pd
    # pdf = pd.DataFrame({"png": pnglist, "vec": vectlist})
    # print pdf.sort_values(by="vec")["png"].head(1)


def save_pngs(data):
    flag = input("sdfs:")
    if flag == 1:
        images["png"] = data
        with open("images.py", "w") as f:
            f.write('%s=%s' % ("images", images))
        time.sleep(20)


def loadims_to_matrix():
    for png in ims.keys():
        piclist = []
        #show_img(ims[png],""+str(png))
        for i in range(160):
            for j in range(160):
                piclist.append(ims[png][i][j])
        ims_dict[png] = np.array(piclist)

def main():
    loadims_to_matrix()
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
    # ttype = getType(browser)  # 识别图形路径
    draw(browser, ttype)  # 滑动破解
    time.sleep(20)
    browser.close()

if __name__ == '__main__':
    main()
