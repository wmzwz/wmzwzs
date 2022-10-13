import pygame
import game
from random import choice, randint
from PySide2.QtWidgets import QInputDialog,QMessageBox
import sys
 
SCORE = 0   #分数，可设置文件提取，保存游戏进度
SOLID = 1                 # 障碍物类型
FRAGILE = 2
DEADLY = 3
BELT_LEFT = 4
BELT_RIGHT = 5
BODY = 6
 
GAME_ROW = 40
GAME_COL = 28
OBS_WIDTH = GAME_COL // 4
SIDE = 13
SCREEN_WIDTH = SIDE*GAME_COL
SCREEN_HEIGHT = SIDE*GAME_ROW
COLOR = {SOLID: 0x00ffff, FRAGILE: 0xff5500, DEADLY: 0xff2222, SCORE: 0xcccccc,
        BELT_LEFT: 0xffff44, BELT_RIGHT: 0xff99ff, BODY: 0x00ff00}
CHOICE = [SOLID, SOLID, SOLID, FRAGILE, FRAGILE, BELT_LEFT, BELT_RIGHT, DEADLY]  # 全局列表 solid为普通障碍，
                           #frgile为可消失障碍， BELT为接触会运动的障碍，deadly接触后会死亡    
 
 
class Barrier(object):                                       # 障碍物的上升操作
    def __init__(self, screen, opt=None):                        
        self.screen = screen                  # 接收screen数据
        if opt is None:                      # 非特殊障碍时，设置方块的种类 （普通，运动，可消失，接触死亡）
            self.type = choice(CHOICE)      
        else:
            self.type = opt
        self.frag_touch = False             # 接触后是否消失
        self.frag_time = 10             # 接触后消失前停顿事件
        self.score = False                 # 得分计算
        self.belt_dire = 0
        self.belt_dire = pygame.K_LEFT if self.type == BELT_LEFT else pygame.K_RIGHT         # 若障碍物种类为向左就赋左按键效果，否则为右按键效果
        left = randint(0, SCREEN_WIDTH - 7 * SIDE - 1)           # 障碍物宽度
        top = SCREEN_HEIGHT - SIDE - 1               # 障碍物长度
        self.rect = pygame.Rect(left, top, 7*SIDE, SIDE)          # 初始化障碍物
 
    def rise(self):            # 上升操作
        if self.frag_touch:         # 若接触后消失，时间每毫秒-1
            self.frag_time -= 1
        if self.frag_time == 0:       # 为0时结束，返回false障碍物消失
            return False
        self.rect.top -= 2
        return self.rect.top >= 0
 
    def draw_side(self, x, y):             # 绘画障碍物
        if self.type == SOLID:
            rect = pygame.Rect(x, y, SIDE, SIDE)     #  初始化一个矩形          
            self.screen.fill(COLOR[SOLID], rect)       # 使用纯色填充 返回值是一个 Rect 对象，表示实际绘制的矩形区域
        elif self.type == FRAGILE:
            rect = pygame.Rect(x+2, y, SIDE-4, SIDE)
            self.screen.fill(COLOR[FRAGILE], rect)
        elif self.type == BELT_LEFT or self.type == BELT_RIGHT:
            rect = pygame.Rect(x, y, SIDE, SIDE)
            pygame.draw.circle(self.screen, COLOR[self.type], rect.center, SIDE // 2 + 1)
        elif self.type == DEADLY:
            p1 = (x + SIDE//2 + 1, y)
            p2 = (x, y + SIDE)
            p3 = (x + SIDE, y + SIDE)
            points = [p1, p2, p3]
            pygame.draw.polygon(self.screen, COLOR[DEADLY], points)
 
    def draw(self):                                # 随机绘制障碍物
        for i in range(7):
            self.draw_side(i*SIDE+self.rect.left, self.rect.top)
 
 
class Hell(game.Game):                                                      # hell 继承 Game类
    def __init__(self, title, size, fps,musicpath,gamescore):
        super(Hell, self).__init__(title, size, fps)              # 调用game的构造函数
        self.fps = fps                        # 设定fps值
        self.last = 6 * SIDE                      #  初始障碍物之间间隔
        self.dire = 0                       # 初始运动方向
        self.barrier = [Barrier(self.screen, SOLID)]            # 设置初始时的障碍物
        self.body = pygame.Rect(self.barrier[0].rect.center[0], 200, SIDE, SIDE)      # 初始方块
        self.score = gamescore         # 传入游戏分数

        self.musicpath = musicpath # 音乐地址传入
        pygame.mixer.init()
        pygame.mixer.music.load(self.musicpath)
        pygame.mixer.music.play()  #  无参数默认从开头开始无限循环
        pygame.mixer.music.set_volume(0.5)  # 控制声音的大小（0~1），声音大于1按照1即最大音进行处理


        self.bind_key([pygame.K_LEFT, pygame.K_RIGHT], self.move)         # 按下按键操作
        self.bind_key_up([pygame.K_LEFT, pygame.K_RIGHT], self.unmove)        # 松开按键操作
        self.bind_key(pygame.K_SPACE, self.pause)                 # 按下空格游戏暂停
 
    def move(self, key):           # 开始运动        
        self.dire = key

    def unmove(self, key):      # 停止运动
        self.dire = 0
 
    def show_end(self):              # 游戏结束
        self.draw(0, end=True)
        self.end = True
 
    def move_man(self, dire):           # 方块运动
        if dire == 0:
            return True
        rect = self.body.copy()           # 复制方块
        if dire == pygame.K_LEFT:      # 若按键为左
            rect.left -= 2              # 方块每帧左移2单位
        else:
            rect.left += 2           # 否则右移2单位
        if rect.left < 0 or rect.left + SIDE >= SCREEN_WIDTH:   # 当移动到边缘时，不能再向左右移动
            return False
        for ba in self.barrier:                  
            if rect.colliderect(ba.rect):               # 检测与障碍物的碰撞，若发生接触，不能再向左右移动
                return False
        self.body = rect
        return True
 
    def get_score(self, ba):                      # 当方块超过障碍物，加分
        if self.body.top > ba.rect.top and not ba.score:
            self.score += 1
            ba.score = True
 
    def to_hell(self):                                 # 方块向下运动
        self.body.top += 2
        for ba in self.barrier:                      # 若检测到与障碍物碰撞，不能再向下运动
            if not self.body.colliderect(ba.rect):
                self.get_score(ba)                    # 若未碰撞，计算是否加分
                continue
            if ba.type == DEADLY:                 # 若方块接触障碍物死亡，显示死亡
                self.show_end()
                return
            self.body.top = ba.rect.top - SIDE - 2
            if ba.type == FRAGILE:        # 障碍物可消失
                ba.frag_touch = True
            elif ba.type == BELT_LEFT or ba.type == BELT_RIGHT:                # 障碍物造成的方块左右移动效果              
                # self.body.left += ba.belt_dire
                self.move_man(ba.belt_dire)
            break
 
        top = self.body.top
        if top < 0 or top+SIDE >= SCREEN_HEIGHT:             # 接触到最底面游戏结束
            self.show_end()
 
    def create_barrier(self):             # 创造障碍物对象
        solid = list(filter(lambda ba: ba.type == SOLID, self.barrier))   #  普通障碍物
        if len(solid) < 1:                            # 普通障碍物少于一个，添加新的普通障碍物进入
            self.barrier.append(Barrier(self.screen, SOLID))
        else:
            self.barrier.append(Barrier(self.screen))        # 否则随机加入障碍物
        self.last = randint(3, 5) * SIDE    # 随机障碍物出现间隔
 
    def update(self, current_time):                   # 界面刷新
        if self.end or self.is_pause:               # 游戏暂停或结束停止刷新
            return
        self.last -= 1                # 游戏障碍物刷新间隔
        if self.last == 0:             # 刷新间隔结束刷新障碍物
            self.create_barrier()
 
        for ba in self.barrier:      
            if not ba.rise():
                if ba.type == FRAGILE and ba.rect.top > 0:              # 消失障碍物消失后，分数加一
                    self.score += 1
                self.barrier.remove(ba)        # 消失后移除这个障碍物
 
        self.move_man(self.dire)           # 获取方块运动方向
        self.move_man(self.dire)
        self.to_hell()               # 方块向下运动
 
    def draw(self, current_time, end=False):                    # 绘制障碍
        if self.end:
            pygame.mixer.music.pause()
            choice = QMessageBox.question(None,'你输了！','是否重新开始？')
            if choice == QMessageBox.Yes:                                           # 选择yes 游戏重新开始
                hell = Hell("一百层", (SCREEN_WIDTH, SCREEN_HEIGHT),self.fps,self.musicpath,0)           # 直接套娃
                hell.run()
            if choice == QMessageBox.No:            # 选择no，sys关闭所有程序
                sys.exit()
            return
        elif self.is_pause:
            return
        self.screen.fill(0x000000)         # 画面填充
        self.draw_score((0x3c, 0x3c, 0x3c))            # 分数背景显示
        for ba in self.barrier:                       # 分别绘制已存储的障碍物
            ba.draw()
        if not end:                                   # 未结束，绘制未死亡方块
            self.screen.fill(COLOR[BODY], self.body)
        else:
            self.screen.fill(COLOR[DEADLY], self.body)   # 死亡绘制死亡方块
        pygame.display.update()            # 无参数，更新整个surface对象
 
 

