from PyQt5 import QtCore, QtGui, QtWidgets, uic
from .LoginDialog import LoginDialog
from .UI import *


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._user = None
        uic.loadUi('./UI/MainWindow.ui', self)

    def populate(self, user: User):
        self._user = user
        self.setWindowTitle('Ultimate Automatization Technology: logged in as ' + self._user.name)
