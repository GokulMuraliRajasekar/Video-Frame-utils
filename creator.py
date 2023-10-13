from PyQt5.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QFileDialog, QCheckBox, QSpinBox, QFormLayout, QErrorMessage, QComboBox
from PyQt5.QtCore import Qt

from widgets.button import Button
from widgets.label import Label
from widgets.frame_info import FrameInfo
from widgets.layout import labelField
from widgets.progress import ProgressBar
from widgets.popup import MessageBox

from creator_worker import Worker
import os


image_formats = ['auto', 'jpg', 'png']


class Creator(QWidget):
    def __init__(self):
        super(Creator, self).__init__()
        self.initControls()
        self.initLayouts()
        self.msg_box = MessageBox()

    def initControls(self):
        self.label_video_name = Label("video name")
        self.video_name = QLineEdit()

        self.button_save_dir = Button("save dir")
        self.save_path = QLineEdit()
        self.save_path.setReadOnly(True)
        self.button_save_dir.clicked.connect(self.getSaveDir)

        self.button_source_dir = Button("source dir")
        self.source_path = QLineEdit()
        self.source_path.setReadOnly(True)
        self.button_source_dir.clicked.connect(self.getSourceDir)

        self.video_name = QLineEdit()
        self.fps = QSpinBox()
        self.fps.setRange(1, 60)

        self.image_format = QComboBox()
        self.image_format.addItems(image_formats)

        self.frame_info = FrameInfo()

        # custom frame sequence
        self.custom_sequence = QCheckBox("custom frame sequence")
        self.custom_sequence_start = QSpinBox()
        self.custom_sequence_end = QSpinBox()
        self.custom_sequence_start.setMaximum(1000000)
        self.custom_sequence_end.setMaximum(1000000)

        self.disable(self.custom_sequence_start)
        self.disable(self.custom_sequence_end)

        self.custom_sequence.clicked.connect(self.toggleCustomSequence)

        self.button_create_video = Button("create video")
        self.button_create_video.clicked.connect(self.createVideo)

    def initLayouts(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.layout_source = QHBoxLayout()
        self.layout_target = QHBoxLayout()
        self.layout_video_info = QHBoxLayout()
        self.layout_custom_sequence = QHBoxLayout()
        self.layout_cs_start = QFormLayout()
        self.layout_cs_end = QFormLayout()

        self.layout_source.addWidget(self.button_source_dir)
        self.layout_source.addWidget(self.source_path)
        self.layout_source.addLayout(
            labelField('image format', self.image_format))

        self.layout_target.addWidget(self.button_save_dir)
        self.layout_target.addWidget(self.save_path)

        self.layout_custom_sequence.addWidget(self.custom_sequence)
        self.layout_custom_sequence.addStretch()
        self.layout_cs_start.addRow('start', self.custom_sequence_start)
        self.layout_cs_end.addRow('end', self.custom_sequence_end)
        self.layout_custom_sequence.addLayout(self.layout_cs_start)
        self.layout_custom_sequence.addLayout(self.layout_cs_end)

        self.layout_video_info.addLayout(labelField(
            "video name", self.video_name), stretch=2)
        self.layout_video_info.addLayout(labelField("fps", self.fps))

        self.layout.addLayout(self.layout_source)
        self.layout.addLayout(self.layout_video_info)
        # self.layout.addWidget(self.frame_info)
        self.layout.addLayout(self.layout_custom_sequence)
        self.layout.addLayout(self.layout_target)
        self.layout.addStretch()
        self.layout.addWidget(self.button_create_video,
                              alignment=Qt.AlignmentFlag.AlignRight)

    def getSaveDir(self):
        folder = self.getFolder()
        if folder:
            self.save_path.setText(folder)
        elif self.save_path.text():
            pass
        else:
            self.save_path.setText("./")

    def getSourceDir(self):
        folder = self.getFolder()
        self.source_path.setText(folder)
        if folder != "":
            video_name = folder.split(os.path.altsep)[-1]
            self.video_name.setText(video_name)
            self.save_path.setText(folder)
        else:
            self.video_name.setText("")

    def getFolder(self, caption="select a folder"):
        folder = QFileDialog.getExistingDirectory(
            self, caption="select a  folder")
        return folder

    def disable(self, item):
        item.setEnabled(False)

    def enable(self, item):
        item.setEnabled(True)

    def toggleCustomSequence(self, v: bool):
        self.custom_sequence_start.setEnabled(v)
        self.custom_sequence_end.setEnabled(v)

    def createVideo(self):
        source = self.source_path.text()
        target = self.save_path.text()
        video_name = self.video_name.text()
        fps = self.fps.value()
        image_format = self.image_format.currentText()

        self.writer = Worker(
            source, target, video_name, fps, image_format)

        self.pbar = ProgressBar()
        self.pbar.setMessage("checking for images")
        self.pbar.setCancelCallback(self.writer.stop)

        if self.custom_sequence.isChecked():
            self.writer.setCustomSequence(
                self.custom_sequence_start.value(), self.custom_sequence_end.value())

        self.writer.images_found.connect(self.pbar.setLimit)
        self.writer.progress.connect(self.pbar.update)
        self.writer.error.connect(self.showErrorMessage)
        self.writer.warning.connect(self.showWarningMessage)
        self.writer.completed.connect(self.finalize)
        self.writer.cancelled.connect(lambda: self.pbar.close())
        self.writer.start()

        self.pbar.show()

    def showErrorMessage(self, message):
        self.pbar.close()
        self.msg_box.showErrorMessage(message)

    def showWarningMessage(self, message):
        self.msg_box.showWarningMessage(message)
        self.pbar.close()

    def finalize(self):
        self.msg_box.showSuccessMessage("Video created")
        self.pbar.close()
