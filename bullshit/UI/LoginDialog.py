from PyQt5 import QtCore, QtGui, QtWidgets, uic


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        uic.loadUi('./UI/LoginDialog.ui', self)
        
    def login(self) -> str:
        return self.loginEdit.text()

    def password(self) -> str:
        return self.passwordEdit.text()
