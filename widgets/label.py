from PyQt5.QtWidgets import QLabel
import styles


class Label(QLabel):
    def __init__(self, v: str = "-", width: int = None, color=None):
        super(Label, self).__init__()
        self.setText(v)

        self.setStyleSheet(
            f"font-size: {styles.Label.fontSize}px; padding: {styles.Label.padding}px")

        if width is not None:
            self.setFixedWidth(width)

    def setValue(self, v: str):
        self.setText(str(v))

    def value(self, v: str):
        return self.text()
