from PyQt5 import QtCore, QtGui, QtWidgets, uic
from typing import Optional


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._user = None
        uic.loadUi('./UI/MainWindow.ui', self)

    def populate(self, widget: Optional[QtWidgets.QWidget]):
        if widget is not None:
            self.centralWidget().layout().addWidget(widget)
