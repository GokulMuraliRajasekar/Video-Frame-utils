from PyQt5.QtWidgets import QFormLayout


def labelField(label, widget):
    layout = QFormLayout()
    layout.addRow(label, widget)
    return layout
