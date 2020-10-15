# coding:utf-8
"""
Created by 范嘉宁 on 2020.9.25
项目名称：疫情模拟游戏ESG(EpidemicSimulationGame, ESG, 直译流行病模拟游戏)
Version 1.0.0(Release)
使用环境： Anaconda 3(Python3.7)
IDE信息如下：
PyCharm 2020.1 (Professional Edition)
Build #PY-201.6668.115, built on April 7, 2020
Licensed to https://zhile.io
You have a perpetual fallback license for this version
Subscription is active until July 8, 2089
Runtime version: 11.0.6+8-b765.25 amd64
VM: OpenJDK 64-Bit Server VM by JetBrains s.r.o
Windows 10 10.0
GC: ParNew, ConcurrentMarkSweep
Memory: 733M
Cores: 2
开发时的操作系统：Windows 10.0.18362.1082
理论上可以运行于任意操作系统

我在github中开放了源代码， 详情见<https://github.com/Choctocatina/EpidemicSimulationGame/>
"""

# 导入依赖包
import pygame
import sys
import easygui
from pygame.locals import *
import random
import time
import music
import threading

pygame.init()

# 设置窗口
bgWidth = 480 * 3
bgHeight = 240 * 3
canvas = pygame.display.set_mode((bgWidth, bgHeight))
canvas.fill((255, 255, 255))
pygame.display.set_caption("疫情模拟游戏ESG")
bg_path = "..\\data\\images\\bg.png"
bg = pygame.image.load(bg_path)
one_day = 5


# 设置退出方式以及键鼠交互以及状态变化条件
def handleEvent():
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            judgment = easygui.boolbox("是否退出游戏?", "注意", ["确定退出", "算了，再玩会儿"])
            if judgment:
                pygame.quit()
                sys.exit()
            else:
                ...

        if event.type == MOUSEMOTION:
            if isMouseIn(event.pos[0], event.pos[1]):
                # print('MouseIn')
                if GameVar.state == GameVar.STATES['PAUSE']:
                    GameVar.state = GameVar.STATES['RUNNING']
            if isMouseOut(event.pos[0], event.pos[1]):
                # print('MouseOut')
                if GameVar.state == GameVar.STATES['RUNNING']:
                    GameVar.state = GameVar.STATES['PAUSE']

    if GameVar.state == GameVar.STATES["RUNNING"]:
        if len(GameVar.peoples) == 0:
            GameVar.state = GameVar.STATES["LOSE"]
        if len(GameVar.patients) == 0:
                GameVar.state = GameVar.STATES["WIN"]



def isMouseOut(x, y):
    if x >= (bgWidth - 20) or x <= 20 or y >= (bgHeight) or y <= 20:
        return True
    else:
        return False


def isMouseIn(x, y):
    if 1 < x < bgWidth and 1 < y < bgHeight:
        return True
    else:
        return False


def isActionTime(lastTime, interval):
    currentTime = time.time()
    return currentTime - lastTime >= interval


"""
def wait(interval):
    lastTime = time.time()
    while True:
        Now = time.time()
        if Now - lastTime >= interval:
            return True
"""


def write(text, pos, size, colour=(0, 0, 0), font="微软雅黑"):
    Fonts = pygame.font.SysFont(font, size)
    MyFont = Fonts.render(text, True, colour)
    canvas.blit(MyFont, pos)


# 游戏变量
class GameVar(object):
    STATES = {"START": 0, "LOGIN": 2, "RUNNING": 3, "PAUSE": 4, "WIN": 5, "LOSE": 6,
              "QUIT": 7}  # TODO：QUIT涉及到存储对象序列化，暂时没做
    state = STATES["START"]
    RO = 4
    peoples = []
    patients = []
    doctors = []
    symptoms = []
    asymptomatic = []
    for patient in patients:
        if patient.colour == 1: asymptomatic.append(1)
        if patient.colour == 2: symptoms.append(1)
    paintLastTime = 0
    paintInterval = 0.1
    hospitalResponsiveness = 2 * one_day
    hospitalQueue = []
    hospitalBeds = 12
    bg = bg


"""
class Hospital(object):
    def __init__(self):
        self.responsiveness = 2 * one_day
        self.queue = []
        self.peoples = []
        self.doctors = GameVar.doctors

    def run(self):
        for doctor in GameVar.doctors:
            doctor.heal()

    def moreDoctor(self):
        dx = 50 - 20
        dy = random.randint(0, bgHeight - 20)
        GameVar.doctors.append(Doctor(dx, dy, 20, 20))


hospital = Hospital()
"""


# noinspection PyChainedComparisons
class CharacterObject(object):
    """所有人物的父类"""

    def __init__(self, x, y, width, height, colour):
        self.attributeDict = {"People": {"Health": 0, "Symptoms": 1, "Asymptomatic": 2, "Death": 5},
                              "Doctor": {"Health": 3, "Symptoms": 4}}
        self.x = x  # x坐标
        self.y = y  # y坐标
        self.width = width  # 宽
        self.height = height  # 高
        self.life = 3000  # 基础生命值
        self.immunity = random.randint(500, 1000)  # 免疫力
        self.defensive = self.life + self.immunity  # 总防御值
        self.can_infectOther = True  # 能否感染他人
        self.infectedPeoples = 0  # 被self感染的人数
        self.infectedTime = None  # 被感染时的时间
        self.attribute = self.attributeDict["People"]["Health"]  # 属性
        self.colourDict = {"green": 0, "yellow": 1, "red": 2, "dh": 3, "ds": 4, "death": 5}  # 储存不同颜色
        self.colour = self.colourDict[colour]  # 确定颜色
        self.init_colour = self.colour
        # 通过colour确定attribute以及image_path
        if colour == 0:
            self.attribute = self.attributeDict["People"]["Health"]
        if colour == 1:
            self.attribute = self.attributeDict["People"]["Asymptomatic"]
            self.infectedTime = time.time()
        if colour == 2:
            self.attribute = self.attributeDict["People"]["Symptoms"]
            self.infectedTime = time.time()
        if colour == 3:
            self.attribute = self.attributeDict["Doctor"]["Health"]
        if colour == 4:
            self.attribute = self.attributeDict["Doctor"]["Symptoms"]

        self.image_path = "..\\data\\images\\" + str(self.colour) + ".png"  # 图片路径
        self.load_image = pygame.image.load(self.image_path)  # 预加载图片

    def hit(self, component):  # 判断碰撞
        c = component
        return c.x > self.x - c.width and c.x < self.x + self.width and \
               c.y > self.y - c.height and c.y < self.y + self.height

    def paint(self):  # 绘制self
        canvas.blit(self.load_image, (self.x, self.y))

    def reset_pos(self):  # 重置坐标
        if self.x <= 70: self.x = random.randint(90, bgWidth - 50 - 20 - 20)
        if self.x >= bgWidth - 50 - 20: self.x = random.randint(90, bgWidth - 50 - 20 - 20)
        if self.y <= 20: self.y = random.randint(50, bgHeight - 50)
        if self.y >= bgHeight - 20: self.y = random.randint(50, bgHeight - 50)

    def CanInfectOther_qm(self):  # qm: question mark
        if self.infectedPeoples == GameVar.RO:
            self.can_infectOther = False

    def reloadImage(self):  # 重载图片
        self.image_path = self.image_path = "..\\data\\images\\" + str(self.colour) + ".png"
        self.load_image = pygame.image.load(self.image_path)

    def move(self, direction):  # 移动
        step = random.randint(0, 20)
        if direction == 0: self.x -= step  # left
        if direction == 1: self.x += step  # right
        if direction == 2: self.y -= step  # up
        if direction == 3: self.y += step  # down

    def Death(self):  # 判断死亡
        if self.defensive == 0:
            self.colour = self.colourDict["death"]
            self.reloadImage()


class Doctor(CharacterObject):
    def __init__(self, x, y, width, weight):
        super().__init__(x, y, width, weight, "dh")
        self.attribute = self.attributeDict["Doctor"]["Health"]
        self.immunity = 500

        class HealLT:
            def __init__(self):
                self._h = time.time()
                self.can = False

            def read(self):
                return self._h

            def write(self, new):
                if self.can:
                    self._h = new

        self.healLT = HealLT()

    def move(self, step, direction=random.randint(0, 1)):
        if direction == 0: self.y -= step
        if direction == 1: self.y += step

    def reset_pos(self):
        if self.y <= 0: self.y = bgHeight / 2 - self.y
        if self.y >= bgHeight: self.y = bgHeight / 2 - self.y

    def heal(self):
        for patient in GameVar.patients:
            if isActionTime(self.healLT.read(), 10):
                self.healLT.can = True
                print("god")
                patient.life += 10
                if patient.defensive >= 3000:
                    patient.colour = 0
                    GameVar.patients.remove(patient)
                    GameVar.peoples.append(patient)
            self.healLT.write(time.time())

    def run(self):
        self.move(random.randint(0, 5))
        self.reset_pos()
        self.heal()


class Peoples(CharacterObject):
    def __init__(self, x, y, width, height, colour):
        super().__init__(x, y, width, height, colour)

        class InfectedTime(object):  # 这个类仅仅为了让infectedTime只能更改一次......
            def __init__(self):
                self._infectedTime = time.time()
                self.fre = 0

            def read(self):
                return self._infectedTime

            def write(self, new):
                if self.fre == 0:
                    self._infectedTime = new
                    self.fre = 1
                if self.fre != 0:
                    ...

        self.infectedTime = InfectedTime()

        class EruptionTime:
            def __init__(self):
                self._eruptionTime = time.time()
                self.fre = 0

            def read(self):
                return self._eruptionTime

            def write(self, new):
                # print(self.fre)
                if self.fre == 0:
                    self._eruptionTime = new
                    self.fre = 1
                if self.fre != 0:
                    ...

        self.eruptionTime = EruptionTime()

    def _pe_I_am_patient_qm(self):
        if self.colour == 1 or self.colour == 2 and self.init_colour == 0:
            self.infectedTime.write(time.time())
            self.init_colour = -1  # init_colour用不到了
            return True

    def pa_eruption(self):
        if self.colour == 1:
            if self.infectedTime.read() != 0:
                incubation_period = 7
                if isActionTime(self.infectedTime.read(), incubation_period * one_day):
                    # print(isActionTime(self.infectedTime.read(), incubation_period * one_day))
                    self.colour = 2
                    self.reloadImage()

    """
    def pa_goToHos(self):
        if self.colour == 2:
            self.eruptionTime.write(time.time())
            # print(self.eruptionTime.read())
            hospital.queue.append(self)
            if isActionTime(self.eruptionTime.read(), hospital.responsiveness + len(hospital.queue)):
                print("intro")
                hospital.peoples.append(self)
                GameVar.patients.remove(self)
                self.in_hospital = True
    """

    def pa_componentInfect(self):
        if self.colour == 1 or self.colour == 2:
            self.pa_eruption()
            if self.can_infectOther:
                for people in GameVar.peoples:
                    if self.hit(people):
                        infected_probability = random.random()
                        if infected_probability <= 0.6:
                            people.immunity -= random.randint(10, 100)
                            if people.immunity <= 0:
                                self.infectedPeoples += 1
                                people.colour = 1
                                people.reloadImage()
                                GameVar.patients.append(people)
                                GameVar.peoples.remove(people)
                            self.CanInfectOther_qm()

    def a_paint(self):
        canvas.blit(self.load_image, (self.x, self.y))

    """
    def run(self):
        if self.colour == 1: self.pa_eruption()
        if self.colour == 1 or self.colour == 2:
            if not self.in_hospital:
                directions = [0, 1, 2, 3]  # 0.left, 1.right, 2.up, 3.down
                direction = random.choice(directions)
                self.pa_componentInfect()
                self.move(direction)
                self.paint()
                if self.colour == 2:
                    self.pa_goToHos()
            if self.in_hospital:
                print(self.defensive)
                self._Changelife()

        if self.colour == 0:
            directions = [0, 1, 2, 3]  # 0.left, 1.right, 2.up, 3.down
            direction = random.choice(directions)
            self.move(direction)
            self.paint()
        """


class Keystrokes(object):
    def __init__(self, x, y, text, colour, function):
        self.x = x
        self.y = y
        self.width = len(text) * 16
        self.height = 22
        self.text = text
        self.colour = colour
        self.function = function

    def button(self):
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                if self.x <= event.pos[0] <= self.x + self.width:
                    if self.y <= event.pos[1] <= self.y + self.height:
                        self.function()

    def show(self):
        write(self.text, (self.x, self.y), 40, self.colour)

    def run(self):
        self.show()
        self.button()


"""
green_path = image_path + "green.png"  # 12x13
yellow_path = image_path + "yellow.png"  # 12x12
red_path = image_path + "red.png"  # 11x12
"""


def starter():
    img_path = "..\\data\\images\\start.png"  # 486x188
    canvas.blit(pygame.image.load(img_path), (bgWidth / 2 - 486 / 2, bgHeight / 2 - 188 / 2))
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN and 511 <= event.pos[0] <= (511 + 486) and 366 <= event.pos[1] <= (366 + 188):
            return "RUNNING"
        else:
            return "START"


"""
def login():
    with open("..\\data\\user_data\\user_data.csv", mode="r", encoding="utf-8") as allUserData:
        # readlines[line1, line2, line3...]
        # readlines[[lin1/1, line1/2], [line2/1, line2/2]]
        # readlines[0]                [0]
        #          userdata(number)    0:username, 1:userpwd
        userDatas = allUserData.readlines()
        userDatas.pop(0)
        new_list = []
        for line_index in range(len(userDatas)):
            line = userDatas[line_index][:-1:]
            line = line.split(",")
            new_list.append(line)

        userDatas = new_list
        # print(userDatas)
    \"\"\"
    userName = easygui.enterbox("输入用户名", title="请登陆")
    for userData in userDatas:
        if userData[0] == userName:
            pwd = easygui.enterbox("输入密码", title="请输入密码")
            if userData[1] == pwd:
                easygui.msgbox("登录成功！")
                return "RUNNING"
        else:
            create_account = easygui.boolbox("请问你是要创建账户吗？", title="注意", choices=("是的", "不是"))
            if create_account:
                massage = "请按提示操作"
                title = "注册账户"
                fields = ["输入用户名", "输入密码", "确认密码"]
                account = list()
                account = easygui.multenterbox(massage, title, fields)
                print("account=={}".format(account))
                if account[1] == account[2]:
                    easygui.msgbox("用户创建成功！", title="提示")
    \"\"\"
    register = easygui.boolbox("请选择", choices=["注册", "登录"])
    over = False
    while not over:
        if register:
            massage = "请按提示操作"
            title = "注册账户"
            fields = ["输入用户名", "输入密码", "确认密码"]
            account = list()
            account = easygui.multenterbox(massage, title, fields)
            # print("account=={}".format(account))
            if account[1] == account[2]:
                over = True
                easygui.msgbox("用户创建成功！", title="提示")
                with open("..\\data\\user_data\\user_data.csv", mode="a", encoding="utf-8") as write_data:
                    write_data.write("\n" + str(account[0]) + "," + str(account[1]))
                GameVar.UserName = account[0]

        else:
            indata = easygui.multenterbox(msg="请输入", fields=["用户名", "密码"])
            for data in userDatas:
                if data[0] == indata[0]:
                    if data[1] == indata[1]:
                        easygui.msgbox("登录成功！")
                        GameVar.UserName = indata[0]
                        over = True
    return "RUNNING"
"""


def generate(number=1):
    """生成人物"""
    for num in range(number):
        x = random.randint(0 + 50, bgWidth - 20)  # TODO:左边留70做医院,  右边减去20是因为圆点大小
        y = random.randint(0 + 20, bgHeight - 20)  # TODO：上面20是数据区, 下面20放按键
        attribute = random.randint(0, 50)
        if attribute <= 48:
            attr = random.randint(0, 50)
            if attr <= 30:
                GameVar.peoples.append(Peoples(x, y, 20, 20, "green"))
            elif attr <= 45:
                GameVar.patients.append(Peoples(x, y, 20, 20, "yellow"))
            elif attr <= 50:
                GameVar.patients.append(Peoples(x, y, 20, 20, "red"))

        else:
            dx = 50 - 20
            dy = random.randint(0, bgHeight - 20)
            GameVar.doctors.append(Doctor(dx, dy, 20, 20))


def componentPaint():
    """绘制小圆点＆背景"""
    if not isActionTime(GameVar.paintLastTime, GameVar.paintInterval):
        return
    GameVar.paintLastTime = time.time()
    canvas.blit(GameVar.bg, (0, 0))
    for people in GameVar.peoples:
        people.reset_pos()
        people.paint()
    for patient in GameVar.patients:
        patient.reset_pos()
        patient.paint()
    for doctor in GameVar.doctors:
        doctor.reset_pos()
        doctor.paint()
    pygame.display.update()


def componentMove():
    """随机移动"""
    for people in GameVar.peoples:
        directions = [0, 1, 2, 3]  # 0.left, 1.right, 2.up, 3.down
        direction = random.choice(directions)
        people.move(direction)
    for patient in GameVar.patients:
        directions = [0, 1, 2, 3]  # 0.left, 1.right, 2.up, 3.down
        direction = random.choice(directions)
        patient.move(direction)
    for doctor in GameVar.doctors:
        directions = [0, 1]
        doctor.move(random.randint(0, 10), random.choice(directions))


def showData():
    symptoms = []
    asymptomatic = []
    for patient in GameVar.patients:
        if patient.colour == 1: asymptomatic.append(1)
        if patient.colour == 2: symptoms.append(1)
    write("health:{}".format(len(GameVar.peoples)), (70, 0), 40, (0, 255, 0))
    write("patients:{}".format(len(GameVar.patients)), (200, 0), 40, (130, 130, 0))
    write("symptoms:{}".format(len(symptoms)), (400, 0), 40, (255, 0, 0))
    write("asymptomatic:{}".format(len(asymptomatic)), (600, 0), 40, (127, 127, 0))
    write("doctors:{}".format(len(GameVar.doctors)), (850, 0), 40, (0, 0, 255))


def moreDoctor():
    dx = 50 - 20
    dy = random.randint(0, bgHeight - 20)
    GameVar.doctors.append(Doctor(dx, dy, 20, 20))


def buttons():
    button_MoreDoctor = Keystrokes(50, bgHeight - 22, "More Doctor", (0, 255, 255), moreDoctor)
    button_MoreDoctor.run()


def ChangingProperties():
    canvas.blit(bg, (0, 0))
    showData()
    buttons()
    for patient in GameVar.patients:
        patient.pa_componentInfect()
        patient.pa_eruption()
        patient.reloadImage()
    for people in GameVar.peoples:
        people.reloadImage()
    for doctor in GameVar.doctors:
        doctor.heal()


def controlState():
    if GameVar.state == GameVar.STATES["START"]:
        key = starter()
        if type(key) == str:
            GameVar.state = GameVar.STATES[key]
            # print(key)
        handleEvent()
    """
    if GameVar.state == GameVar.STATES["LOGIN"]:
        key = login()
        if type(key) == str:
            GameVar.state = GameVar.STATES[key]
            # print(key)
        handleEvent()
    """

    if GameVar.state == GameVar.STATES["RUNNING"]:
        handleEvent()
        componentPaint()
        componentMove()
        ChangingProperties()

    if GameVar.state == GameVar.STATES["PAUSE"]:
        componentPaint()
        showData()
        buttons()

    if GameVar.state == GameVar.STATES["LOSE"]:
        handleEvent()
        canvas.blit(bg, (0, 0))
        _path = "..\\data\\images\\LOSE.png"
        img = pygame.image.load(_path)
        write("YOU LOSE!\nMouse click to exit", (0, 0), 40, (0, 0, 0))
        canvas.blit(img, (200, 200))
        del _path
        del img
        """
        play = threading.Thread(target=music.play, args=("LOSE",))
        play.start()
        play.join()
        """
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                pygame.quit()
                sys.exit()

    if GameVar.state == GameVar.STATES["WIN"]:
        handleEvent()
        canvas.blit(bg, (0, 0))
        _path = "..\\data\\images\\WIN.png"
        img = pygame.image.load(_path)
        write("YOU WIN!\nMouse click to exit", (0, 0), 40, (0, 0, 0))
        canvas.blit(img, (200, 200))
        del _path
        del img
        """
        play = threading.Thread(target=music.play, args=("WIN", ))
        play.start()
        play.join()
        """
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    generate(50)
    while True:
        pygame.display.update()
        controlState()
        handleEvent()
