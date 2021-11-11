import json
import threading
import time
from tkinter.filedialog import askopenfilename

import pyaudio
from PyQt5 import QtGui
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
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
        self.filename = r"C:\Users\Dusk\Downloads\330925181_nb2-1-112.flv"
        self.videoPlayer = None

    def bindFunction(self):
        self.window.listeners.onplay = self.onplay

    def create_window(self, argv):
        self.qtApp = QApplication(argv)
        self.window = Window("ObjectDetectionAPIMarker")
        self.bindFunction()
        self.window.loadUI(json.loads(read_file(self.uiConfig)))

    def Start(self):
        self.window.show()
        self.qtApp.exec_()

    def loadVideo(self):
        self.filename = askopenfilename(title='打开视频文件',
                                        filetypes=[('视频', '*.mp4 *.avi *flv')])

    def onplay(self):
        self.videoPlayer = VideoPlayer(self.window, self.filename)
        self.videoPlayer.play()


class ThreadVideo(QThread):
    def __init__(self, callback):
        super().__init__()
        self.play = callback

    def run(self):
        self.play()


class VideoPlayer:
    def __init__(self, window, path):
        self.window = window  # 赋值窗体
        self.video = Video(path)  # 实例化Video对象
        self.video.load_video()  # 加载视频
        video = VideoFileClip(path)  # 加载视频片段
        self.audio = video.audio  # 赋值audio
        self.start = -1  # 设置start时间初始值
        self.isRun = False  # 设置运行标志为false
        self.current = 0  # 初始化当前时间

        self.threadVideo = None  # 视频线程
        self.threadAudio = None  # 音频线程

    def video_play(self):
        self.video.get_frame(0)  # 设置初始值帧
        for i in range(int(self.video.numberFrames)):  # 遍历全部帧数
            t = time.time() - self.start
            while self.video.get_timestamps() > time.time() - self.start:  # 循环判断是否到达播放时间
                if not self.isRun:  # 判断是否暂停
                    break  # 结束循环
                time.sleep(0.001)
            if not self.isRun:  # 判断是否暂停
                break  # 结束循环
            self.current = time.time() - self.start  # 设置当前时间
            frame = self.video.get_next_frame()  # 获取下一帧
            height, width, channel = frame.shape  # 获取形状
            bytesPerLine = 3 * width  # 计算长度
            qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_BGR888)  # 转为QImage
            if self.window.controls.video.isEnabled():
                self.window.controls.video.setPixmap(QtGui.QPixmap(qImg))  # 更新图像
        self.isRun = False  # 设置运行标志为false

    def audio_play(self):
        p = pyaudio.PyAudio()  # 创建音频播放器
        stream = p.open(format=pyaudio.paFloat32, channels=2, rate=44100, output=True)  # 启动播放流
        t = 0  # 时刻
        step = (1 / 44100)  # 步长
        while time.time() - self.start < self.audio.end:  # 循环，直到时间大于结束
            if not self.isRun:  # 判断是否暂停
                break  # 中断循环
            t += step  # 时刻加上步长
            stream.write(self.audio.get_frame(t).astype('float32').tostring())  # 写入声音播放流
        p.terminate()  # 关闭
        self.isRun = False  # 设置运行标志为false

    def start_play(self):
        self.isRun = True  # 设置运行标志为true
        self.start = time.time()  # 获取当前时间戳
        self.threadVideo = ThreadVideo(self.video_play)  # 初始化视频播放线程
        self.threadAudio = threading.Thread(target=self.audio_play)  # 初始化音频播放线程
        self.threadVideo.start()  # 启动视频播放线程
        self.threadAudio.start()  # 启动音频播放线程

    def pause(self):
        self.isRun = False  # 设置运行标志为false
        if self.threadVideo is not None:  # 如果视频线程不为空
            self.threadVideo.join()  # 等待线程结束
        if self.threadAudio is not None:  # 如果音频线程不为空
            self.threadAudio.join()  # 等待线程结束

    def continue_play(self):
        self.isRun = True  # 设置运行标志为true
        self.threadVideo = ThreadVideo(self.video_play)  # 初始化视频播放线程
        self.threadAudio = threading.Thread(target=self.audio_play)  # 初始化音频播放线程
        self.threadVideo.start()  # 启动视频播放线程
        self.threadAudio.start()  # 启动音频播放线程

    def play(self):
        if self.start == -1:  # 如果start时间戳为负数则代表从来没有启动过视频
            self.start_play()  # 使用初始化方式启动视频
        else:
            self.continue_play()  # 就行视频播放

    def move(self, t: float = None, frame: int = None):
        if frame is not None:  # 如果frame不为空
            self.video.set_frame(frame)  # 以帧位设置视频播放位
        elif t is not None:  # 如果t不为空
            self.video.set_timestamps(t)  # 以时间戳设置视频播放位
        else:
            raise Exception("Error set video progress rate")  # 如果全为空则抛出错误
