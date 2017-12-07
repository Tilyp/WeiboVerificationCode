＃WeiboVerificationCode

前言：
之前玩过微博爬虫，可以实现验证码的自动解锁和账号自动登录，最近朋友说也想玩玩微博，问我要代码，运行后发现无法自动登录， 之前的代码用的是九茶大神的， 搜了发现他没有更新，看很多网友也在求解决方法，那我就只能自己动手解决问题了。

先不废话，直接上代码：WeiboVerificationCode

解决问题的思路和九茶是一样的，只是修改了大神的两部分代码：

更新匹配模型， ims.py -> images.py，
更新匹配算法，利用欧氏距离计算相似度， getType(browser) -> getType_similirity(browser)
更新ims的原因是因为利用欧式距离计算后发现调换“2”和“3”的位置或者当“4”在第个三位置时“1”都在最前边或者最后边，因此这个模型已经不能很好的识别验证码，于是我就更新了这个模型，这样代码就简洁一些。

ims和images的区别是数据结构不一样， ims是由二维数组构成， 而images是由一维数组构成。
以下是计算相似度的代码：

def getType_similirity(browser):
    """ 识别图形路径 ，采用欧氏距离计算相似度"""
    time.sleep(3.5)
    im0 = Image.open(StringIO.StringIO(browser.get_screenshot_as_png()))
    box = browser.find_element_by_id('patternCaptchaHolder')
    im0 = im0.resize((1034, 708))
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

经过几十次的测试，成功率为百分之百，好了，废话不多说， 有什么问题加QQ群聊（526855734）
博客地址：http://blog.csdn.net/tilyp/article/details/78655045
