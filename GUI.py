import math
import sys

import PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from loguru import logger


class Window(QWidget):
    def __init__(self, title, parent=None):
        super(Window, self).__init__(parent)
        self.controls = Controls()
        self.listeners = Listeners(self)
        self.mainGrid = None
        self.setWindowTitle(title)
        # self.setWindowIcon(QIcon("icon.png"))
        # self.UI()
        # layout = QVBoxLayout()
        # self.label = QLabel("Hello PyQt5")
        # self.label.setAlignment(Qt.AlignCenter)
        # layout.addWidget(self.label)
        # self.setLayout(layout)
        #
        # # 水平方向
        # self.s1 = QSlider(Qt.Horizontal)
        # # 设置最小值
        # self.s1.setMinimum(10)
        # # 设置最大值
        # self.s1.setMaximum(50)
        # # 设置步长
        # self.s1.setSingleStep(3)
        # # 设置当前值
        # self.s1.setValue(20)
        # # 刻度位置在下方
        # self.s1.setTickPosition(QSlider.TicksBelow)
        # # 设置刻度间隔
        # self.s1.setTickInterval(5)
        # layout.addWidget(self.s1)
        # # 连接信号槽
        # self.s1.valueChanged.connect(self.value_changed)

    def loadUI(self, configuration):
        mainGrid = QGridLayout()
        mainGrid.setAlignment(Qt.AlignTop)
        for layout in configuration["window"]:
            if layout["layoutType"] == "QGridLayout":
                grid = QGridLayout()
            if layout["layoutType"] == "QHBoxLayout":
                grid = QHBoxLayout()
            if layout["layoutType"] == "QVBoxLayout":
                grid = QVBoxLayout()
            grid.setObjectName(layout["name"])
            grid.setAlignment(getattr(Qt, layout["Align"]))
            for child in layout["children"]:
                (nameControl, positionControl, columnStretchControl, rowStretchControl, result) = self.createControl(
                    child)
                setattr(self.controls, nameControl, result)
                if "Align" in child.keys():
                    result.setAlignment(getattr(Qt, child["Align"]))
                if layout["layoutType"] == "QGridLayout":
                    if type(result) != PyQt5.QtWidgets.QVBoxLayout and type(result) != PyQt5.QtWidgets.QHBoxLayout:
                        grid.addWidget(result, *positionControl)
                    else:
                        grid.addLayout(result, *positionControl)
                    if columnStretchControl > 0:
                        grid.setColumnStretch(positionControl[1], positionControl[1] + columnStretchControl)
                    if rowStretchControl > 0:
                        grid.setRowStretch(positionControl[0], positionControl[0] + rowStretchControl)
                else:
                    if type(result) != PyQt5.QtWidgets.QVBoxLayout and type(result) != PyQt5.QtWidgets.QHBoxLayout:
                        grid.addWidget(result,
                                       positionControl[1] if layout["layoutType"] == "QHBoxLayout" else positionControl[
                                           0])
                    else:
                        grid.addLayout(result,
                                       positionControl[1] if layout["layoutType"] == "QHBoxLayout" else positionControl[
                                           0])
                    if columnStretchControl > 0 and layout["layoutType"] == "QHBoxLayout":
                        grid.setStretch(positionControl[1], positionControl[1] + columnStretchControl)
                    if rowStretchControl > 0 and layout["layoutType"] == "QVBoxLayout":
                        grid.setStretch(positionControl[0], positionControl[0] + rowStretchControl)
                    grid.setSpacing(0)
            setattr(self.controls, layout["name"], grid)
            mainGrid.addLayout(grid, *layout["position"])
            # if layout["ColumnStretch"] > 0:
            #     mainGrid.setColumnStretch(layout["position"][0], layout["position"][0] + layout["ColumnStretch"])
            # if layout["RowStretch"] > 0:
            #     mainGrid.setRowStretch(layout["position"][1], layout["position"][1] + layout["RowStretch"])
        self.setLayout(mainGrid)

        self.mainGrid = mainGrid

    def createControl(self, control):
        name = control["name"]
        _type = control["type"]
        position = control["position"]
        columnStretch = control["ColumnStretch"]
        rowStretch = control["RowStretch"]
        result = None
        if _type == "label":
            label = QLabel()
            label.setObjectName(name)
            if "MinimumSize" in control.keys():
                label.setMinimumSize(control["MinimumSize"]["width"], control["MinimumSize"]["height"])
            if "Text" in control.keys():
                label.setText(control["Text"])
            result = label
        if _type == "QSlider":
            slider = XQSlider(getattr(Qt, control["SliderType"]))
            slider.setObjectName(name)
            slider.setSingleStep(control["SingleStep"])  # 设置步长
            slider.setValue(control["Value"])  # 设置当前值
            slider.setTickInterval(control["TickInterval"])  # 设置刻度间隔
            slider.valueChanged.connect(getattr(self.listeners, control["eventFuncName"]))  # 绑定改变事件函数
            slider.addListener("onMousePress", getattr(self.listeners, control["eventMousedown"]))
            slider.addListener("onMouseRelease", getattr(self.listeners, control["eventMouseup"]))

            result = slider
        if _type == "Button":
            button = QPushButton(control["Text"])
            button.setObjectName(name)
            button.clicked.connect(getattr(self.listeners, control["eventFuncName"]))
            if "Icon" in control.keys():
                button.setIcon(QIcon(QPixmap(control["Icon"])))
                button.setText("")
            if "MaximumSize" in control.keys():
                button.setMaximumSize(control["MaximumSize"]["width"], control["MaximumSize"]["height"])
            result = button
        if _type == "ButtonVGroup" or _type == "ButtonHGroup":
            layoutGroup = QVBoxLayout() if _type == "ButtonVGroup" else QHBoxLayout()
            for buttonInfo in control["Elements"]:
                button = QPushButton(buttonInfo["Text"])
                button.setObjectName(name)
                button.clicked.connect(getattr(self.listeners, buttonInfo["eventFuncName"]))
                if "MaximumSize" in buttonInfo.keys():
                    button.setMaximumSize(buttonInfo["MaximumSize"]["width"], buttonInfo["MaximumSize"]["height"])
                if "Icon" in buttonInfo.keys():
                    button.setIcon(QIcon(QPixmap(buttonInfo["Icon"])))
                    button.setText("")
                setattr(self.controls, control["name"] + "_" + buttonInfo["name"], button)
                layoutGroup.addWidget(button)
            result = layoutGroup

        return name, position, columnStretch, rowStretch, result

    def value_changed(self):
        print("current slider value=%s" % self.s1.value())
        size = self.s1.value()
        self.label.setFont(QFont("Arial", size))

    # TODO: 记录笔记，修改滑动条时需要锁定信号
    def videoUpdate(self, image, frame, timestamps):
        self.controls.video.setPixmap(image)
        self.controls.progressBar.blockSignals(True)
        self.controls.progressBar.setValue(frame)
        self.controls.progressBar.blockSignals(False)
        self.controls.timeShow.setText(self.secondToString(timestamps))

    @staticmethod
    def secondToString(second):
        partHour = math.floor(second / 3600)
        partMin = math.floor((second - (partHour * 60)) / 60)
        partSecond = math.floor(second - (partHour * 3600) - (partMin * 60))
        return "%02d:%02d:%02d" % (partHour, partMin, partSecond)


class Controls:
    def __init__(self):
        """

        """


class Listeners:
    def __init__(self, father):
        self.father = father

    def onProgressChange(self):
        bar = self.father.controls.progressBar
        print("current slider value=%s" % bar.value())
        size = bar.value()
        # self.label.setFont(QFont("Arial", size))

    def onButtonCreateProjectClicked(self):
        return

    def onButtonLoadProjectClicked(self):
        return

    def onButtonCloseProjectClicked(self):
        return


class XQSlider(QSlider):
    def __init__(self, SliderType, parent=None):
        super(XQSlider, self).__init__(SliderType)
        self.listListener = []

    def addListener(self, name, func):
        self.listListener.append(name)
        setattr(self, name, func)

    def mousePressEvent(self, event):
        super(XQSlider, self).mousePressEvent(event)
        if "onMousePress" in self.listListener:
            self.onMousePress(event)

    def mouseReleaseEvent(self, event):
        super(XQSlider, self).mouseReleaseEvent(event)
        if "onMouseRelease" in self.listListener:
            self.onMouseRelease(event)
