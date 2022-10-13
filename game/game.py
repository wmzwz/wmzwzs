import pygame
from pygame.locals import *
import sys
from PySide2.QtWidgets import QInputDialog,QMessageBox,QLineEdit
import datetime

FOUR_NEIGH = {"left": (0, -1), "right": (0, 1), "up": (-1, 0), "down": (1, 0)}
EIGHT_NEIGH = list(FOUR_NEIGH.values()) + [(1, 1), (1, -1), (-1, 1), (-1, -1)]
DIRECTION = {pygame.K_UP: "up", pygame.K_LEFT: "left", pygame.K_RIGHT: "right", pygame.K_DOWN: "down"}
FILEPATH = "./source"
 
 
def hex2rgb(color):                             #颜色设置
    b = color % 256
    color = color >> 8
    g = color % 256
    color = color >> 8
    r = color % 256
    return (r, g, b)
 
 
class Game(object):                                     # game类，游戏启动类 继承object类，可用其中的方法与内置变量
    def __init__(self, title, size, fps=60):               # 构造函数，完成整个类内置所有相关参数的传参
        self.size = size           # 内置传入size
        pygame.init()                        # pygame初始化
        self.screen = pygame.display.set_mode(size, 0, 32)         # 设置游戏框体，返回返回一个Surface对象（可刷新画布）储存在screen中
        pygame.display.set_caption(title)                 # 设置当前窗口标题
        self.keys = {}      # 按键按下
        self.keys_up = {}     # 按键提起 
        self.clicks = {}         # 点击操作
        self.timer = pygame.time.Clock()      # 创建一个对象来帮助跟踪时间
        self.fps = fps        # 预设fps
        self.score = 0                 # 预设分数
        self.end = False                                                 # 游戏结束条件
        self.fullscreen = False                                                   # 全屏设置条件
        self.last_time = pygame.time.get_ticks()  # 返回自 pygame_init() 调用以来的毫秒数    
        self.is_pause = False         # 暂停标注
        self.is_draw = True       # 是否绘制障碍物
        self.score_font = pygame.font.SysFont("Calibri", 130, True)            # 创建分数字体对象
 
    def bind_key(self, key, action):    # 对各个按键行为操作初始化（move or unmove）
        if isinstance(key, list):
            for k in key:
                self.keys[k] = action
        elif isinstance(key, int):
            self.keys[key] = action
 
    def bind_key_up(self, key, action):
        if isinstance(key, list):
            for k in key:
                self.keys_up[k] = action
        elif isinstance(key, int):
            self.keys_up[key] = action
 
    def bind_click(self, button, action):    # 鼠标点击
        self.clicks[button] = action
 
    def pause(self, key):
        if not self.is_pause:        # 若游戏暂停，音乐暂停，弹出选项框
            pygame.mixer.music.pause()                   # 音乐暂停
            choice = QMessageBox.question(None,'保存','是否保存游戏？')    # 保存选项框

            if choice == QMessageBox.Yes:                       # 选择yes传入当前score给保存函数
                    # 返回值分别是输入数据 和 是否点击了 OK 按钮（True/False）
                filename, okPressed = QInputDialog.getText(None, "输入存档文件名称","存档名称:",QLineEdit.Normal,"")

                if not okPressed:
                    print('你取消了输入')
                else:
                    self.save_score(filename)                          # 执行文件存储函数
                    print('你选择了yes')
            if choice == QMessageBox.No:                                # 选择no不做任何处理
                print('你选择了no')
        else:           # 结束暂停 音乐开始播放
            pygame.mixer.music.unpause()        # 音乐继续        
        self.is_pause = not self.is_pause      #  替换暂停状态指示
 
    def set_fps(self, fps):      # 函数用于更改内置fps的值
        self.fps = fps
 
    def handle_input(self, event):                                     # 检测输入
        if event.type == pygame.QUIT:                                  # 检测到退出操作，做出相应的退出
            pygame.quit()                              # 退出 pygame窗体
            sys.exit()                   # 结束整个程序。
   
        if event.type == pygame.KEYDOWN:             # 点击事件与按下按键连接，按下按键时执行下操作
            if event.key in self.keys.keys():       # 根据按键执行对应操作
                self.keys[event.key](event.key)
            if event.key == pygame.K_F11:                           # F11全屏       点击F11完成全屏判定条件的修改
                self.fullscreen = not self.fullscreen               # 替换原本的全屏判断条件
                if self.fullscreen:
                    self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN, 32)         # pygame 实现全屏
                else:
                    self.screen = pygame.display.set_mode(self.size, 0, 32)        # 设置屏幕任然为原屏幕
        if event.type == pygame.KEYUP:                           # 事件点击与松开按键连接，松开按键完成对应操作
            if event.key in self.keys_up.keys():
                self.keys_up[event.key](event.key)
        if event.type == pygame.MOUSEBUTTONDOWN:        # 鼠标点击，完成对应操作，获取鼠标点击位置信息
            
            if event.button in self.clicks.keys():
                self.clicks[event.button](*event.pos)
 
    def run(self):            # 游戏运行函数 
        while True:      # 死循环
            for event in pygame.event.get():       # pygame持续获取事件，分别按事件与其他的函数连接，获取相关信息
                self.handle_input(event)         # 
            self.timer.tick(self.fps)
 
            self.update(pygame.time.get_ticks())
            self.draw(pygame.time.get_ticks())
 
    def draw_score(self, color, rect=None):                     # 分数绘画，在背景绘画出分数，方便分数显示。
        score = self.score_font.render(str(self.score), True, color)        # 分数字体设置
        if rect is None:                     # rect  
            r = self.screen.get_rect()
            rect = score.get_rect(center=r.center)
        self.screen.blit(score, rect)

    def save_score(self,filename):          # 分数存储  
        days = datetime.date.today()       # 获取日期   
        filepath = FILEPATH+'/'+filename+f" {days}.txt"  # 确认文件存储路径与文件名
        f = open(filepath,'a',encoding = 'utf-8')            # f打开文件
        now_time = datetime.datetime.now()       # 获取当前时间
        now_time = str(now_time)               # 转换为srt
        savetime = now_time[11:19]         # 只获取时分秒
        f.write(f"{savetime}：{self.score}\n",)           # 将时分秒写入文件，中间用中文分号分割（便于后续分开分数与时间）
        f.close()      # 关闭文件

 
    def is_end(self):        # 返回游戏是否结束
        return self.end
 
    
 

 
 