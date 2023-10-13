from PyQt5.QtWidgets import QPushButton
import styles

class Button(QPushButton):
    def __init__(self, name: str):
        super(Button, self).__init__()
        self.setText(name)
        self.setStyleSheet(f"padding: {styles.Button.padding}px; font-size: {styles.Button.fontSize}px;")