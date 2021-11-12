import os

import cv2
import time
import numpy as np
from loguru import logger

import numba
from numba import jit


class Video:
    def __init__(self, path):
        self.path = path
        self.width = -1
        self.height = -1
        self.fps = -1
        self.duration = None
        self.cap = None
        self.numberFrames = None
        self.currentFrame = 0
        self.frameInterval = -1
        self.timeLong = -1
        self.thumbnail = []

    def load_video(self):
        self.cap = cv2.VideoCapture(self.path)
        self.get_video_info()
        start = time.time()
        self.generateThumbnail()
        logger.info(f"耗时:{(time.time() - start) * 1000}ms")

    def get_video_info(self):
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.numberFrames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.timeLong = self.numberFrames / self.fps

    def generateThumbnail(self):
        for i in range(100):
            self.thumbnail.append(self.get_frame(int(i * (self.numberFrames / 100))))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def get_frame(self, index):
        if self.cap.get(cv2.CAP_PROP_POS_FRAMES) != index:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = self.cap.read()
        return np.array(frame)

    def get_next_frame(self):
        self.currentFrame += 1
        ret, frame = self.cap.read()
        return np.array(frame)

    def get_timestamps(self):
        return self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

    def set_frame(self, index):
        self.currentFrame = index
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)

    def set_timestamps(self, timestamps: float):
        self.cap.set(cv2.CAP_PROP_POS_MSEC, int(timestamps * 1000))
