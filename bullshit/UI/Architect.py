import sys
from typing import Optional

from PyQt5 import QtCore, QtGui, QtWidgets
from Database import Database
from Model import *

from .UI import *
from .MainWindow import MainWindow
from .LoginDialog import LoginDialog


class Architect(QtCore.QObject):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)

        self._app = QtWidgets.QApplication(sys.argv)

        self._db: Database = db
        self._connection: Database.Connection = db.connect()
        self._connection.open()

        self.window = MainWindow()

        self._show_login_dialog()

    def __del__(self):
        self._connection.close()

    def run(self):
        return self._app.exec()

    def _show_main_window(self, user: User):
        self.window.populate(user)
        self.window.show()

    def _show_login_dialog(self):
        login_dialog = LoginDialog(self.window)
        login_dialog.modal = True
        login_dialog.accepted.connect(self._slot_login_accepted)
        login_dialog.show()
        self._login_dialog = login_dialog

    def _slot_login_accepted(self):
        user = self._get_user(self.sender().login(), self.sender().password())
        if user is not None:
            self._show_main_window(user)
        else:
            qmb = QtWidgets.QMessageBox
            answer = qmb.critical(self.window, "Login failed", "Username or login incorrect", qmb.Cancel | qmb.Retry, qmb.Retry)
            if answer == qmb.Retry:
                self._show_login_dialog()

    def _get_user(self, login: str, password: str) -> Optional[User]:
        ADMIN_USERNAME = "admin"
        ADMIN_PASSWORD = "root"
        SUPERVISOR_USERNAME = "super"
        SUPERVISOR_PASSWORD = "pooper"

        if login is None or password is None:
            return None

        elif login == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return User(ADMIN_USERNAME, User.Role.ADMIN)

        elif login == SUPERVISOR_USERNAME and password == SUPERVISOR_PASSWORD:
            return User(SUPERVISOR_USERNAME, User.Role.SUPERVISOR)

        else:
            masters: List[Master] = self._connection.execute('''
            SELECT *
            FROM "MASTERS" MASTER
            WHERE MASTER.NAME = :login AND MASTER.ID = :password
            ''', vars=None, model=Master, login=login, password=password).fetch_all()
            master = masters[0] if masters else None
            return User(master.NAME, User.Role.MASTER) if master is not None else None


