import sys
import threading

import pyaudio
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication

from App import App
from Video import Video
from loguru import logger
from moviepy.editor import VideoFileClip
from GUI import Window
import json
import ffms2
import cv2
import time

window = None


def read_file(path, encoding='utf-8'):
    with open(path, encoding=encoding) as f:
        return f.read()


class ThreadVideo(QThread):
    def __init__(self, _window):
        super().__init__()
        self.window = _window

    def run(self):
        # 线程相关代码
        self.play()

    def play(self):
        video = Video(r"C:\FFOutput\292585025-1-112.mp4")
        video.load_video()
        video.get_frame(0)
        start = time.time()
        for i in range(int(video.numberFrames)):
            while video.get_timestamps() > time.time() - start:
                time.sleep(0.001)
            frame = video.get_next_frame()
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_BGR888)
            self.window.controls.video.setPixmap(QPixmap(qImg))


def play_audio(audio):
    p = pyaudio.PyAudio()
    # 创建输出流
    stream = p.open(format=pyaudio.paFloat32,
                    channels=2,
                    rate=44100,
                    output=True)
    # 逐帧播放音频
    t = 0
    step = (1 / 44100)
    start = time.time()
    while time.time() - start < 100:
        t += step
        stream.write(audio.get_frame(t).astype('float32').tostring())
    p.terminate()


def onplay():
    global window
    video = VideoFileClip(r"C:\FFOutput\292585025-1-112.mp4")
    audio = video.audio
    thread = ThreadVideo(window)
    thread_audio = threading.Thread(target=play_audio, args=(audio,))
    thread.start()
    thread_audio.start()


def run_test():
    app = App("ObjectDetectionAPIMarker", "layout.json")
    app.create_window(sys.argv)
    app.Start()
    # global window
    # app = QApplication(sys.argv)
    # win = Window("ObjectDetectionAPIMarker")
    # window = win
    # win.listeners.onplay = onplay
    # win.loadUI(json.loads(read_file("layout.json")))
    #
    # win.show()
    # app.exec_()
    # sys.exit()

    # video = Video(r"C:\Users\Dusk\Downloads\330925181_nb2-1-112.flv")
    # video.load_video()
    # frame = video.get_next_frame()
    # logger.info(f"视频宽度: {video.width} 视频高度: {video.height} 视频总帧数量: {video.numberFrames}")
