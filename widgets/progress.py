from PyQt5 import QtGui
from PyQt5.QtWidgets import QProgressBar, QWidget, QVBoxLayout
from widgets.label import Label
from widgets.button import Button
import time


class ProgressBar(QWidget):
    def __init__(self):
        super(ProgressBar, self).__init__()

        self.setFixedWidth(300)
        self.message = Label("Starting extraction")

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.layout = QVBoxLayout(self)

        self.layout.addWidget(self.message)
        self.layout.addWidget(self.progress_bar)

        self.total_frames = 0
        self.cancel_cb = None

    def setCancelCallback(self, cb):
        self.cancel_cb = cb

    def setLimit(self, v):
        self.total_frames = v

    def update(self, v):
        progress = int((v/self.total_frames)*100)
        self.progress_bar.setValue(progress)
        self.message.setValue(f"{v}/{self.total_frames} frames processed")

    def updateCreation(self, v):
        progress = int((v/self.total_frames)*100)
        self.progress_bar.setValue(progress)
        self.message.setValue(f"{v}/{self.total_frames} frames processed")

    def setMessage(self, v: str):
        self.message.setValue(v)

    def completed(self):
        self.message.setValue(f"extracted {self.total_frames} frames")
        self.progress_bar.setValue(100)
        time.sleep(2)
        self.close()

    def closeEvent(self, a0) -> None:
        if self.cancel_cb is not None:
            self.cancel_cb()
        return super().closeEvent(a0)


if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication([])
    pbar = ProgressBar()
    pbar.show()
    sys.exit(app.exec_())
