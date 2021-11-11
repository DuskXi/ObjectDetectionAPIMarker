import os

import cv2
import time
import numpy as np
from loguru import logger


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

    def load_video(self):
        self.cap = cv2.VideoCapture(self.path)
        self.get_video_info()

    def get_video_info(self):
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.numberFrames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

    def get_frame(self, index):
        if self.cap.get(cv2.CAP_PROP_POS_FRAMES) != index:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = self.cap.read()
        return np.array(frame)

    def get_next_frame(self):
        self.currentFrame += 1
        return self.get_frame(self.currentFrame)

    def get_timestamps(self):
        return self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

    def set_frame(self, index):
        self.currentFrame = index
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)

    def set_timestamps(self, timestamps: float):
        self.cap.set(cv2.CAP_PROP_POS_MSEC, int(timestamps * 1000))
