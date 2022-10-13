from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QInputDialog,QFileDialog,QLineEdit
import game
import Hells
import sys
import time


# 游戏窗体设置需要的值
GAME_ROW = 40
GAME_COL = 28
OBS_WIDTH = GAME_COL // 4
SIDE = 13
SCREEN_WIDTH = SIDE*GAME_COL
SCREEN_HEIGHT = SIDE*GAME_ROW

class GameStartUi:

    def __init__(self):
        self.gamescore = 0              # 设置本类中需要给其他类传输数据的变量初始值
        self.hellfps = 60                         # 设置默认fps值（决定游戏）
        self.musicpath = "./music/01. I Want To See The Manager.mp3"

        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        
        qfile_stats = QFile('./ui/统计1.ui')                              # QFile 获取ui文件信息
        qfile_stats.open(QFile.ReadOnly)                              # 以只读方式打开文件，读取信息
        qfile_stats.close()                                   # 打开后需要关闭
        
        
        self.ui = QUiLoader().load(qfile_stats)                   # 读取数据后存入self.ui

        self.ui.button1.setIcon(QIcon('./ui/log.png'))         # 为button1 添加图片
        self.ui.button2.setIcon(QIcon('./ui/log.png'))
        self.ui.button3.setIcon(QIcon('./ui/log.png'))
        self.ui.button4.setIcon(QIcon('./ui/log.png'))

        self.ui.button1.clicked.connect(self.gameStart)                # 连接button1的点击操作到gameStart函数
        self.ui.button2.clicked.connect(self.gameContinue)                 # 连接 button2 的点击操作到gameContinue函数
        self.ui.button3.clicked.connect(self.chooseMusic)
        self.ui.button4.clicked.connect(self.gameQuit)

    def gameStart(self):                        # 游戏开始按键，点击后连接到此函数。选择难度后开始游戏
        items = ["简单", "一般", "困难"]                        # 下拉框包含选项
        item, ok = QInputDialog.getItem(None, "请选择", "难度:", items, 0, True)            # QInput函数，传入ui，框体文本，下拉框选项等，返回被选择的选项（str）

        if ok and item:                             # 若 ok与 item 不为空，运行下面的fps替换
            if item == "简单":
                self.hellfps = 50
            elif item == "一般":
                self.hellfps = 70
            else:
                self.hellfps = 90
        if ok:                  # 若 前面正常选择了难度，ok为True 否则Ok为False ，若有选择，则传入数据开始游戏
            hell = Hells.Hell("一百层", (SCREEN_WIDTH, SCREEN_HEIGHT),self.hellfps,self.musicpath,self.gamescore)              # 初始化游戏数据
            hell.run()                   # 游戏运行
        else:
            QMessageBox.critical(None,'错误','请选择游戏难度！')         # 未选择游戏难度，弹出提示框体              

        
    def gameContinue(self):             # 继续游戏按键，点击后连接到此函数，弹出文件选择框体，选择文件后读取文件数据，替换原本的gamescore，实现游戏读档
        file = QFileDialog.getOpenFileName(self.ui, "请选择存档文件", "", "txt(*.txt)")     # 读取文件框体，传入ui，框体提示文本，文件预设名，文件类型。选择后返回文件路径与传入的文件类型。

        if not file[0]:                      # file 为列表，储存文件路径与传入的文件类型。 file[0]即为文件路径，若传回路径为空，则弹出提示框
            QMessageBox.critical(None,'错误','请选择游戏存档！')
        else:             # 若不为空，则获取文件路径
            print(file)
            filepath = file[0]
            scoredict = self.getScore(filepath)        #连接到函数读取文件内存储的分数
            times = scoredict.keys()                    # 时间为分数字典的键值
            item, ok = QInputDialog.getItem(None, "请选择", "已存数据:", times, 0, True)      #下拉框选择，选择文件内按时间存储的数据
            if ok and item:
                self.gamescore = int(scoredict[item])                 # 若 正常选择文件，gamescore被选择的数据替换

    def chooseMusic(self):                      # 选择音乐按键，点击后连接到此函数，弹出文件选择框体，选择文件后替换预设音乐文件地址，更改游戏中播放的音乐
        file = QFileDialog.getOpenFileName(None, "请选择音乐文件", "",)       # 读取文件框体，传入ui，框体提示文本，文件预设名，文件类型。选择后返回文件路径与传入的文件类型。

        if not file[0]:             # file 为列表，储存文件路径与传入的文件类型。 file[0]即为文件路径，若传回路径为空，则弹出提示框 
            QMessageBox.critical(None,'错误','请选择游戏音乐文件！')
        else:                       # 若 文件路径不为空，替换预设音乐文件地址，完成音乐更改
            print(file)
            path = file[0]
            self.musicpath = path

    def gameQuit(self):              # 游戏退出按键，点击后利用exit()关闭
        sys.exit()

    def getScore(self,path):           # 读取文件内的分数 构成分数字典
        f = open(path,encoding="utf-8")     
        scoredict = {}                # 空的分数列表与空的读取数据
        allscore = []
        allscore = f.readlines()              # 按行读取，按行存储到列表
        for i in allscore:               
            templist1 = i.split("：")                    # 按分号分割 前面作为键值，后面作为数值，存入字典
            print(templist1)
            time1= templist1[0]
            oldscore = templist1[1][0:-1]
            scoredict[time1] = oldscore

        return scoredict          #返回分数字典

        

def mainWindows():                           # 弹出主窗体程序
    mainW = QApplication().instance()
    mainW.setWindowIcon(QIcon('./ui/log.png'))
    startui = GameStartUi()                        # 对象
    startui.ui.show()              # 对象方法
    mainW.exec_()                 # 无条件执行，保持框体存在

if __name__ == "__main__":         # 程序执行
   mainWindows()

