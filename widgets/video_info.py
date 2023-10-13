from PyQt5.QtWidgets import QWidget, QLabel, QFormLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from widgets.label import Label
from styles import Color

class VideoInfo(QWidget):
    def __init__(self):
        super(VideoInfo, self).__init__()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet("background-color: LightGray; border-radius: 5px")
        
        self._width = Label()
        self._height = Label()
        self._frame_count = Label()
        self._sampled_frames = Label(width = 50)
        self._name = Label()

        self._layout = QHBoxLayout(self)
        self._layout_col_1 = QFormLayout()
        self._layout_col_2 = QFormLayout()

        self._layout_col_1.addRow(Label("Video"), self._name)
        self._layout_col_1.addRow(Label("Width"), self._width)
        self._layout_col_1.addRow(Label("Height"), self._height)
        self._layout_col_1.addRow(Label("Frames"), self._frame_count)

        self._layout_col_2.addRow(Label("sampled frames"), self._sampled_frames)
        self._layout_col_2.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._layout.addLayout(self._layout_col_1)
        self._layout.addStretch()
        self._layout.addLayout(self._layout_col_2)

        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.setSpacing(5)
    
    def setValue(self, name, width, height, frame_count):
        self._width.setValue(width)
        self._height.setValue(height)
        self._frame_count.setValue(frame_count)
        self._name.setValue(name)
    
    def setSampledFrameCount(self, v):
        self._sampled_frames.setValue(v)