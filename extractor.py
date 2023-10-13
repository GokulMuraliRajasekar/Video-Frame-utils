import os
import cv2
import math

from PyQt5.QtWidgets import QLineEdit, QWidget, QSpinBox, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt5.QtCore import Qt
from widgets.button import Button
from widgets.label import Label
from widgets.video_info import VideoInfo
from widgets.progress import ProgressBar

from extractor_worker import Worker


class Extractor(QWidget):
    def __init__(self):
        super(Extractor, self).__init__()
        self.initControls()
        self.initLayouts()
        self.pbar = ProgressBar()
        self.video_file_name = None
        self.destination_path = None
        self.frame_count = 0

    def initControls(self):
        self.button_select_video = Button("open video")
        self.button_extract_frames = Button("extract frames")
        self.button_save_path = Button("save path")

        self.button_extract_frames.clicked.connect(self.extractFrames)
        self.button_save_path.clicked.connect(self.browseSavePath)

        self.le_selected_file = QLineEdit()
        self.le_save_path = QLineEdit()
        self.le_save_path.setStyleSheet("padding: 5px;")
        self.le_selected_file.setStyleSheet("padding: 5px;")
        self.le_selected_file.setReadOnly(True)

        self.le_save_path.setReadOnly(True)
        self.le_selected_file.setReadOnly(True)

        self.label_sampling_rate = Label("sampling rate")
        self.sampling_rate = QSpinBox()
        self.sampling_rate.setRange(1, 10000)
        self.sampling_rate.setStyleSheet("padding: 5px; font-size: 13px;")
        self.sampling_rate.valueChanged.connect(self.refreshSampledFrames)

        self.video = None
        self.video_info = VideoInfo()

        self.button_select_video.clicked.connect(self.displayFileBrowser)

    def initLayouts(self):
        self.layout = QVBoxLayout(self)
        self.layout_browser = QHBoxLayout()
        self.layout_save_dir = QHBoxLayout()
        self.layout_actions = QHBoxLayout()
        self.layout_sampling = QHBoxLayout()

        self.layout_browser.addWidget(self.button_select_video)
        self.layout_browser.addWidget(self.le_selected_file)
        self.layout_browser.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.layout_save_dir.addWidget(self.button_save_path)
        self.layout_save_dir.addWidget(self.le_save_path)

        self.layout_sampling.addWidget(Label("sampling rate"))
        self.layout_sampling.addWidget(self.sampling_rate)

        self.layout_actions.addWidget(
            self.button_extract_frames, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout.addLayout(self.layout_browser)
        self.layout.addWidget(self.video_info)
        self.layout.addLayout(self.layout_sampling)
        self.layout.addLayout(self.layout_save_dir)
        self.layout.addStretch()
        self.layout.addLayout(self.layout_actions)
        self.layout.setSpacing(10)

    def getSampleRate(self):
        return self.sampling_rate.value()

    def getSavePath(self):
        return self.le_save_path.text()

    def refreshSampledFrames(self, sample_rate):
        if self.frame_count:
            if sample_rate:
                if sample_rate > self.frame_count:
                    sampled_frames = self.frame_count
                else:
                    sampled_frames = math.floor(self.frame_count/sample_rate)
            else:
                sampled_frames = self.frame_count
            self.sampled_frames = sampled_frames
            self.video_info.setSampledFrameCount(sampled_frames)

    def displayFileBrowser(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "select a video file", "./", "Videos (*.mp4 *.avi)")
        if filename:
            print('selected file', filename)
            path, video_name = os.path.split(filename)

            self.video_file_name, _ = os.path.splitext(video_name)
            self.destination_path = os.path.join(path, self.video_file_name)

            self.le_selected_file.setText(filename)
            self.le_save_path.setText(self.destination_path)

            width, height, self.frame_count = self.getVideoInfo(filename)
            self.video_info.setValue(
                video_name, width, height, self.frame_count)

            self.refreshSampledFrames(self.getSampleRate())

    def browseSavePath(self):
        folder = QFileDialog.getExistingDirectory(
            caption="select save directory")
        if folder:
            self.le_save_path.setText(folder)

    # @timeit

    def getVideoInfo(self, video):
        self.video = cv2.VideoCapture(video)
        width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"width: {width}, height: {height}, frames: {frame_count}")
        return width, height, frame_count

    def extractFrames(self):
        if self.video is None:
            return

        self.extractor = Worker(
            self.getSavePath(), self.video, self.video_file_name, self.getSampleRate())
        self.extractor.completed.connect(self.pbar.completed)
        self.extractor.progress.connect(self.pbar.update)

        self.pbar.setLimit(self.sampled_frames)
        self.pbar.setCancelCallback(self.extractor.stop)

        self.extractor.start()

        self.pbar.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.pbar.show()
