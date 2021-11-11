import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.controls = Controls()
        self.listeners = Listeners(self)
        self.mainGrid = None
        self.setWindowTitle("PyQt5 GUI")
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
        for layout in configuration["window"]:
            grid = QGridLayout()
            grid.setObjectName(layout["name"])

            for child in layout["children"]:
                (nameControl, positionControl, columnStretchControl, rowStretchControl, result) = self.createControl(
                    child)
                setattr(self.controls, nameControl, result)
                grid.addWidget(result, *positionControl)
                grid.setColumnStretch(positionControl[0], positionControl[0] + columnStretchControl)
                grid.setRowStretch(positionControl[1], positionControl[1] + rowStretchControl)
            # ...
            setattr(self.controls, layout["name"], grid)
            mainGrid.addLayout(grid, *layout["position"])
            mainGrid.setColumnStretch(layout["position"][0], layout["position"][0] + layout["ColumnStretch"])
            mainGrid.setRowStretch(layout["position"][1], layout["position"][1] + layout["RowStretch"])
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
            label.setMinimumSize(control["MinimumSize"]["width"], control["MinimumSize"]["height"])
            result = label
        if _type == "QSlider":
            slider = QSlider(getattr(Qt, control["SliderType"]))
            slider.setObjectName(name)
            slider.setSingleStep(control["SingleStep"])  # 设置步长
            slider.setValue(control["Value"])  # 设置当前值
            slider.setTickInterval(control["TickInterval"])  # 设置刻度间隔
            slider.valueChanged.connect(getattr(self.listeners, control["eventFuncName"]))  # 绑定改变事件函数
            result = slider

        return name, position, columnStretch, rowStretch, result

    def value_changed(self):
        print("current slider value=%s" % self.s1.value())
        size = self.s1.value()
        self.label.setFont(QFont("Arial", size))


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
