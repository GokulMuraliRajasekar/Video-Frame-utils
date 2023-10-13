from PyQt5.QtWidgets import QMessageBox


class MessageBox(QMessageBox):
    def __init__(self):
        super(MessageBox, self).__init__()
        self.setWindowTitle("")
        self.setStandardButtons(QMessageBox.StandardButton.Ok)

    def showErrorMessage(self, message: str):
        self.setText(message)
        self.setIcon(QMessageBox.Icon.Critical)
        self.exec()

    def showSuccessMessage(self, message: str):
        self.setText(message)
        self.setIcon(QMessageBox.Icon.Information)
        self.exec()

    def showWarningMessage(self, message: str):
        self.setText(message)
        self.setIcon(QMessageBox.Icon.Warning)
        self.exec()
