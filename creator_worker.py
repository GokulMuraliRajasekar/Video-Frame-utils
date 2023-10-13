import cv2
import os
from glob import glob
import traceback

from PyQt5.QtCore import pyqtSignal, QThread

from utils.get_image_size import get_image_size
from utils.exceptions import ZeroImage, ResolutionMismatch, MultipleImageFormats


class Worker(QThread):

    resolution_mismatch = pyqtSignal()
    images_found = pyqtSignal(int)
    progress = pyqtSignal(int)
    incorrect_sequence = pyqtSignal()
    error = pyqtSignal(str)
    warning = pyqtSignal(str)
    completed = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(self, source, target, video_name, fps, image_format):
        super(Worker, self).__init__()
        self.source_dir = source
        self.target_dir = target
        self.video_name, _ = os.path.splitext(video_name)
        self.fps = fps
        self.clean = True
        self.image_format = image_format
        self.video_format = "mp4"
        self._codec = cv2.VideoWriter_fourcc(*'mp4v')
        self._video_path = os.path.join(
            target, f"{video_name}.{self.video_format}")

        self._start = 1
        self._end = 0
        self.custom_sequence = False
        self.detected_image_formats = {}

        self.images = []
        self.image_count = 0
        self.image_format = image_format

        self.run_flag = True

    def setCustomSequence(self, start=None, end=None):
        self.custom_sequence = True
        self._start = start or self._start
        self._end = end or 0

    def getImagesList(self):

        if self.image_format == 'auto':
            formats_to_search = ['jpg', 'png']
        else:
            formats_to_search = [self.image_format]

        for img_format in formats_to_search:
            images = glob(os.path.join(self.source_dir,
                          f"{self.video_name}*.{img_format}"))
            self.detected_image_formats[img_format] = len(images)
            self.images.extend(images)
            print(f"{img_format} : {len(images)} images")

        self.image_count = len(self.images)

        if self.image_count == 0:
            self.error.emit(f"no images found in {self.source_dir}")
            raise ZeroImage

    def autoDetectFormat(self):
        detected_img_format = None

        for fmt in self.detected_image_formats:
            if self.detected_image_formats[fmt] > 0:

                # set format
                if detected_img_format is None:
                    detected_img_format = fmt

                # multiple formats are detected. raise error
                else:
                    self.error.emit(
                        "multiple image formats detected, \nplease select an image format")

                    print("multiple image formats detected:",
                          self.detected_image_formats)

                    raise MultipleImageFormats

        self.image_format = detected_img_format
        print("detected image format", detected_img_format)

    def verifyImageResolutions(self):
        prev_w = prev_h = None

        for file in self.images:
            # print('checking...', file)
            w, h = get_image_size(os.path.join(self.source_dir, file))
            if prev_w != None:
                if prev_w != w and prev_h != h:
                    self.resolution_mismatch.emit()
                    self.clean = False

                    print("resolution mimatch")
                    print(f"{prev_w}x{prev_h}, {w}x{h}")
                    self.error.emit("multiple images resolutions are found")
                    raise ResolutionMismatch
                else:
                    prev_w, prev_h = w, h
                    # print(file, True)

        self.width = w
        self.height = h
        return

    def parseSequenceId(self, filename):
        name, _ = os.path.splitext(filename)
        seq_id = name.split('_')[-1]
        if seq_id.isnumeric():
            return int(seq_id)
        return -1

    def run(self):
        print("video writer started")
        try:

            # collect images for processing
            if self.run_flag:
                self.getImagesList()

            # Auto detect format
            if self.run_flag:
                if self.image_format == 'auto':
                    self.autoDetectFormat()

            # check image resolutions
            if self.run_flag:
                self.verifyImageResolutions()

            # sort images by seq id
            # if self.run_flag:
                # self.images.sort(key=self.parseSequenceId)

            # print("check complete", self.clean)

            if self.clean and self.run_flag:
                self.images_found.emit(self.image_count)
                # print(self.images)
                print("images found -", self.image_count)

                if self.custom_sequence:
                    if self._end == 0:
                        self._end = self._start + self.image_count + 1
                    else:
                        self._end += 1

                elif self._end == 0:
                    self._end = self.image_count + 1

                # video = cv2.VideoWriter()
                # video_format = cv2.VideoWriter_fourcc('M', 'P', 'V', '4')

                print(f"start:{self._start}, end: {self._end}")

                processed = 0
                writer = cv2.VideoWriter(
                    self._video_path, self._codec, self.fps, (self.width, self.height))

                print(f"saving video to {self._video_path}")

                for i, frame in enumerate(range(self._start, self._end)):
                    if not self.run_flag:
                        break

                    fp = os.path.join(
                        self.source_dir, f"{self.video_name}_{frame}.{self.image_format}")

                    if not os.path.isfile(fp):
                        continue

                    img = cv2.imread(fp)
                    writer.write(img)

                    processed += 1

                    self.progress.emit(processed)

                writer.release()

                if not self.run_flag:
                    self.cancelled.emit()
                elif processed == 0 and self.image_count > 0:
                    self.error.emit("no image found/ incorrect sequence")
                elif processed != self.image_count:
                    self.warning.emit(
                        "not all images were processed, check sequence")
                else:
                    self.completed.emit()

            else:
                print("file resolution check failed")

        except MultipleImageFormats:
            print("multiple image formats found")
        except ZeroImage:
            print(f"no images found in {self.source_dir}")
        except ResolutionMismatch:
            print("multiple image resolutions found")
        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)

    def stop(self):
        self.run_flag = False
