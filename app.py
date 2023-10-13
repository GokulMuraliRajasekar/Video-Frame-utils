from PyQt5.QtWidgets import QWidget, QMainWindow
from PyQt5.QtWidgets import QApplication, QTabWidget
# from PyQt5.QtCore import Qt

# from widgets.video_info import VideoInfo
# from widgets.label import Label
# from widgets.button import Button
from widgets.progress import ProgressBar

from extractor import Extractor
from creator import Creator

import time
import sys
from functools import partial

# timeit decorator


def timeit(func):

    def wrapper(*args):
        start_time = time.time()
        res = func(*args)
        time_elapsed = time.time() - start_time
        print(f"{func.__name__} executed in {round(time_elapsed, 2)}'s")
        return res

    return wrapper


class VideoUtils(QMainWindow):
    def __init__(self):
        super(VideoUtils, self).__init__()

        self.setWindowTitle("VidEx")

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("font-size: 13px; padding: 5px")
        # self.tabs.setFixedWidth(500)

        self.widget = QWidget()
        # self.widget.setFixedSize(500, 300)
        self.widget.setMinimumSize(500, 300)
        self.setCentralWidget(self.tabs)

        self.creator = Creator()
        self.extractor = Extractor()

        self.tabs.addTab(self.extractor, "Extract Video")
        self.tabs.addTab(self.creator, "Create Video")


if __name__ == '__main__':
    app = QApplication([])
    video_utils = VideoUtils()
    video_utils.show()
    sys.exit(app.exec_())
