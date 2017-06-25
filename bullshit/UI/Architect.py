import sys
import cx_Oracle
from typing import Optional

from PyQt5 import QtCore, QtGui, QtWidgets
from Database import Database
from Model import *

from .UI import *
from .MainWindow import MainWindow
from .LoginDialog import LoginDialog
from .EditDialog import EditDialog


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
        self._show_main_edit(self._connection, "CARS", None, Car)

    def _show_main_edit(self, connection: Database.Connection, table_name: str, id, model_class: MetaModel):
        class CustomMediator(EditDialog.Mediator):
            def __init__(self, id):
                self._id = id

            def read(self) -> Model:
                return self._selet() if self._id is not None else model_class()

            def write(self, model: Model):
                self._update(model) if self._id is not None else self._insert(model)

            def _selet(self) -> Model:
                return connection.execute('''
                SELECT *
                FROM {table} TBL
                WHERE TBL.ID = :id
                '''.format(table=table_name), id=self._id, model=model_class).fetch_one()

            def _update(self, model: Model):
                object: OrderedDict = model.serialize()
                del object['ID']
                val_name = lambda x: str(x) + '_val'
                object_string = ', '.join([str(key) + ' = ' + ':' + val_name(key) for key in object.keys()])
                object_vals = {val_name(key): val for key, val in object.items()}
                cursor: Database.DatabaseCursor = connection.execute('''
                UPDATE {table} TBL
                SET {object}
                WHERE TBL.ID = :id
                '''.format(object=object_string, table=table_name), id=self._id, **object_vals)
                connection.commit_transaction()

            def _insert(self, model: Model):
                object: OrderedDict = model.serialize()
                del object['ID']
                keys = object.keys()
                variables = {'ID': cx_Oracle.NUMBER}
                query = '''
                INSERT INTO {table} ({keys})
                VALUES ({values})
                RETURNING "ID" INTO :ID
                '''.format(table=table_name, keys=', '.join(keys), values=', '.join([':' + key for key in keys]))

                cursor: Database.DatabaseCursor = connection.execute(query, vars=variables, **object)
                connection.commit_transaction()
                self._id = cursor.variables['ID'].getvalue()

        dialog = EditDialog(CustomMediator(id), self.window)
        dialog.show()

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
