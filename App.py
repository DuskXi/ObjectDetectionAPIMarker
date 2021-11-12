import json
import math
import threading
import time
from tkinter.filedialog import askopenfilename

import pyaudio
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, QMutex, QTimer
from PyQt5.QtWidgets import QApplication, QFileDialog
from loguru import logger
from moviepy.video.io.VideoFileClip import VideoFileClip

from GUI import Window
from Video import Video


def read_file(path, encoding='utf-8'):
    with open(path, encoding=encoding) as f:
        return f.read()


class App:
    def __init__(self, title, uiConfig):
        self.title = title
        self.qtApp = None
        self.window = None
        self.uiConfig = uiConfig
        self.VideoFileName = r"C:\Users\Dusk\Downloads\330925181_nb2-1-112.flv"
        self.videoPlayer = None
        self.isPlayButtonClickPushed = False
        self.sliderMouseDown = False

    def bindFunction(self):
        self.window.listeners.onplay = self.onplay
        self.window.listeners.onPlayButtonClick = self.onPlayButtonClick
        self.window.listeners.openFile = self.loadVideo
        self.window.listeners.onSliderMouseDown = self.onSliderMouseDown
        self.window.listeners.onSliderMouseUp = self.onSliderMouseUp
        self.window.listeners.onProgressChange = self.onProgressChange

    def create_window(self, argv):
        self.qtApp = QApplication(argv)
        self.window = Window("ObjectDetectionAPIMarker")
        self.bindFunction()
        self.window.loadUI(json.loads(read_file(self.uiConfig)))

    def Start(self):
        self.window.show()
        self.qtApp.exec_()

    def loadVideo(self):
        self.VideoFileName = QFileDialog.getOpenFileName(self.window, "打开视频文件", "./",
                                                         "Video Files (*.mp4 *.avi *flv);;All Files (*)")[0]
        self.videoPlayer = VideoPlayer(self.window, self.VideoFileName, self.videoExit)
        self.videoPlayer.move(frame=0)
        frame = self.videoPlayer.frame()
        height, width, channel = frame.shape  # 获取形状
        bytesPerLine = 3 * width  # 计算长度
        self.window.controls.video.setPixmap(
            QtGui.QPixmap(QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_BGR888)))
        self.window.controls.progressBar.setSingleStep(1)
        self.window.controls.progressBar.setValue(0)
        self.window.controls.progressBar.setTickInterval(int(self.videoPlayer.video.numberFrames / 50))
        self.window.controls.progressBar.setMinimum(0)
        self.window.controls.progressBar.setMaximum(int(self.videoPlayer.video.numberFrames))

    def onplay(self):
        self.videoPlayer = VideoPlayer(self.window, self.VideoFileName)
        self.videoPlayer.play()
        self.isPlayButtonClickPushed = True
        self.window.controls.playButtons_play.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/pause-outline.svg")))

    def onPlayButtonClick(self):
        if self.videoPlayer is not None:
            if not self.isPlayButtonClickPushed:
                self.isPlayButtonClickPushed = True
                self.window.controls.playButtons_play.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/pause-outline.svg")))
                if not self.videoPlayer.play():
                    self.isPlayButtonClickPushed = False
                    self.window.controls.playButtons_play.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/play-outline.svg")))
            else:
                self.isPlayButtonClickPushed = False
                self.window.controls.playButtons_play.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/play-outline.svg")))
                self.videoPlayer.pause()

    def onSliderMouseDown(self, event):
        self.sliderMouseDown = True
        if self.videoPlayer.isRun:
            self.videoPlayer.pause()
            self.isPlayButtonClickPushed = True

    def onSliderMouseUp(self, event):
        self.sliderMouseDown = False
        self.videoPlayer.move(frame=self.window.controls.progressBar.value())
        self.videoPlayer.frame()
        self.videoPlayer.current = self.videoPlayer.video.get_timestamps()
        self.videoPlayer.currentAudio = self.get_recent_time(self.videoPlayer.video.get_timestamps())
        if self.isPlayButtonClickPushed:
            self.videoPlayer.play()

    def onProgressChange(self):
        value = self.window.controls.progressBar.value()
        self.window.controls.timeShow.setText(
            self.window.secondToString(self.videoPlayer.video.timeLong * (value / self.videoPlayer.video.numberFrames)))
        index = int((value / self.videoPlayer.video.numberFrames) * 100)
        index = index if index >= 0 else 0
        index = index if index <= 99 else 99
        frame = self.videoPlayer.video.thumbnail[index]
        height, width, channel = frame.shape  # 获取形状
        bytesPerLine = 3 * width  # 计算长度
        self.window.controls.video.setPixmap(
            QtGui.QPixmap(QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_BGR888)))
        self.videoPlayer.current = self.videoPlayer.video.get_timestamps()
        self.videoPlayer.currentAudio = self.get_recent_time(self.videoPlayer.video.get_timestamps())

    def videoExit(self):
        if self.isPlayButtonClickPushed:
            self.isPlayButtonClickPushed = False
            self.window.controls.playButtons_play.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/play-outline.svg")))

    @staticmethod
    def get_recent_time(t, step=(1 / 44100)):
        t_result = 0
        while t_result < t:
            t_result += step
        return t_result


class ThreadVideo(QThread):
    signal = QtCore.pyqtSignal(QtGui.QPixmap, int, float)

    def __init__(self, callback, signal):
        super().__init__()
        self.play = callback
        self.signal.connect(signal)

    def run(self):
        self.play(self.signal)


class VideoPlayer:
    def __init__(self, window, path, videoExit):
        self.window = window  # 赋值窗体
        self.video = Video(path)  # 实例化Video对象
        self.video.load_video()  # 加载视频
        video = VideoFileClip(path)  # 加载视频片段
        self.audio = video.audio  # 赋值audio
        self.start = -1  # 设置start时间初始值
        self.isRun = False  # 设置运行标志为false
        self.current = 0  # 初始化当前时间
        self.currentAudio = -1

        self.threadVideo = None  # 视频线程
        self.threadAudio = None  # 音频线程
        self.timer = None

        self.videoExit = videoExit

    def video_play(self, _signal):
        # self.video.get_frame(0)  # 设置初始值帧
        while self.video.currentFrame < self.video.numberFrames:
            # 遍历全部帧数
            while self.video.get_timestamps() > time.time() - self.start:  # 循环判断是否到达播放时间
                if not self.isRun:  # 判断是否暂停
                    break  # 结束循环
                time.sleep(0.001)
            if not self.isRun:  # 判断是否暂停
                break  # 结束循环
            self.current = time.time() - self.start  # 设置当前时间
            frame = self.video.get_next_frame()  # 获取下一帧
            if len(frame.shape) < 2:
                break
            height, width, channel = frame.shape  # 获取形状
            bytesPerLine = 3 * width  # 计算长度
            qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_BGR888)  # 转为QImage
            _signal.emit(QtGui.QPixmap(qImg), self.video.currentFrame, self.video.get_timestamps())  # 发送信号
            # if self.window.controls.video.isEnabled():
            #     self.window.controls.video.setPixmap(QtGui.QPixmap(qImg))  # 更新图像
        self.isRun = False  # 设置运行标志为false
        self.videoExit()

    def audio_play(self):
        p = pyaudio.PyAudio()  # 创建音频播放器
        stream = p.open(format=pyaudio.paFloat32, channels=2, rate=44100, output=True)  # 启动播放流
        t = 0 if self.currentAudio == -1 else self.currentAudio  # 时刻
        step = (1 / 44100)  # 步长
        while time.time() - self.start < self.audio.end:  # 循环，直到时间大于结束
            if not self.isRun:  # 判断是否暂停
                break  # 中断循环
            t += step  # 时刻加上步长
            self.currentAudio = t
            stream.write(self.audio.get_frame(t).astype('float32').tostring())  # 写入声音播放流
        p.terminate()  # 关闭
        # self.isRun = False  # 设置运行标志为false

    def play(self):
        if self.video.currentFrame < self.video.numberFrames - 1:
            self.isRun = True  # 设置运行标志为true
            self.start = time.time() if self.start == -1 else time.time() - self.current  # 获取当前时间戳
            self.threadVideo = ThreadVideo(self.video_play, self.window.videoUpdate)  # 初始化视频播放线程
            self.threadAudio = threading.Thread(target=self.audio_play)  # 初始化音频播放线程
            self.threadVideo.start()  # 启动视频播放线程
            self.threadAudio.start()  # 启动音频播放线程
            return True
        else:
            return False

    def pause(self):
        self.isRun = False  # 设置运行标志为false
        if self.threadVideo is not None:  # 如果视频线程不为空
            self.threadVideo.wait()  # 等待线程结束
        if self.threadAudio is not None:  # 如果音频线程不为空
            self.threadAudio.join()  # 等待线程结束

    def move(self, t: float = None, frame: int = None):
        if frame is not None:  # 如果frame不为空
            self.video.set_frame(frame)  # 以帧位设置视频播放位
        elif t is not None:  # 如果t不为空
            self.video.set_timestamps(t)  # 以时间戳设置视频播放位
        else:
            raise Exception("Error set video progress rate")  # 如果全为空则抛出错误

    def frame(self):
        return self.video.get_next_frame()
