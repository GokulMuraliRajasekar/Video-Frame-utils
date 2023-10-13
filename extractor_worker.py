from PyQt5.QtCore import QThread, pyqtSignal
import pathlib
import cv2
import os


class Worker(QThread):

    progress = pyqtSignal(int)
    completed = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, dest_path, video, prefix, sample_rate, start_frame=None, end_frame=None):
        super(Worker, self).__init__()
        pathlib.Path(dest_path).mkdir(parents=True, exist_ok=True)

        self.video = video
        self.sample_rate = sample_rate or 1
        self.prefix = prefix
        self.format = 'jpg'
        self.frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.dest = dest_path

        self.run_flag = True

    def run(self):

        for i in range(1, self.frame_count+1, self.sample_rate):

            # extraction in progress
            if self.run_flag:

                try:
                    ret, frame = self.video.read()

                    if ret:
                        file_name = f"{self.prefix}_{i}.{self.format}"
                        file_path = os.path.join(self.dest, file_name)
                        cv2.imwrite(file_path, frame)
                        progress = int(i/self.sample_rate)
                        self.progress.emit(progress)

                except:
                    self.error.emit("error extracting frames")

            # operation cancelled
            else:
                pass

        self.completed.emit()

    def stop(self):
        self.run_flag = False
