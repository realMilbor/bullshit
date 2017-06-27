import sys
import cx_Oracle
from typing import Optional, Any

from PyQt5 import QtCore, QtGui, QtWidgets
from Database import Database
from Model import *

from .UI import *
from .MainWindow import MainWindow
from .LoginDialog import LoginDialog
from .EditDialog import EditDialog
from .ListWidget import ListWidget
from .MasterRoleWidget import MasterRoleWidget
from .SupervisorRoleWidget import SupervisorRoleWidget


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
        widget = None
        user_role = user.role
        if user_role is User.Role.ADMIN:
            assert False
        elif user_role is User.Role.SUPERVISOR:
            widget = self._create_supervisor_role_widget()
        elif user_role is User.Role.MASTER:
            widget = self._create_master_role_widget(user)

        self.window.setWindowTitle('Ultimate Automatization Technology: logged in as ' + user.name + ' (' + str(user.role.name) + ') ')
        self.window.populate(widget)
        self.window.show()

    def _edit_mediator(self, connection: Database.Connection, table_name: str, model_class: MetaModel):
        class CustomMediator(EditDialog.Mediator):
            def __init__(self, id):
                self._id = id

            def read(self) -> Model:
                return self._select() if self._id is not None else model_class()

            def write(self, model: Model):
                self._update(model) if self._id is not None else self._insert(model)

            def _select(self) -> Model:
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

        return CustomMediator

    def _show_abstract_edit(self, id: Any, model_class: MetaModel, table_name: str):
        mediator_class = self._edit_mediator(connection=self._connection, table_name=table_name, model_class=model_class)
        dialog = EditDialog(mediator_class(id), self.window)
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
            return User(ADMIN_USERNAME, User.Role.ADMIN, 0)

        elif login == SUPERVISOR_USERNAME and password == SUPERVISOR_PASSWORD:
            return User(SUPERVISOR_USERNAME, User.Role.SUPERVISOR, 0)

        else:
            masters: List[Master] = self._connection.execute('''
            SELECT *
            FROM "MASTERS" MASTER
            WHERE MASTER.NAME = :login AND MASTER.NAME = :password
            ''', vars=None, model=Master, login=login, password=password).fetch_all()
            master = masters[0] if masters else None
            return User(master.NAME, User.Role.MASTER, master.ID) if master is not None else None

    def _create_master_role_widget(self, user):
        connection = self._connection
        show_abstract_edit = self._show_abstract_edit
        user_id = user.id

        class CarsListMediator(ListWidget.Mediator):
            def load(self) -> List[Model]:
                return connection.execute('''
                SELECT CAR.*
                FROM "CARS" CAR
                ORDER BY CAR.ID DESC
                ''', model=Car).fetch_all()

            def edit_available(self):
                return False

            def edit(self, item: Model):
                assert False, "You're not supposed to be able to do this"

            def delete_available(self):
                return False

            def delete(self, item: Model):
                assert False, "You're not supposed to be able to do this"

            def create_available(self):
                return False

            def create(self):
                assert False, "You're not supposed to be able to do this"

        class ServicesListMediator(ListWidget.Mediator):
            def load(self) -> List[Model]:
                return connection.execute('''
                SELECT SVC.*
                FROM "SERVICES" SVC
                ORDER BY SVC.ID DESC
                ''', model=Service).fetch_all()

            def edit_available(self):
                return False

            def edit(self, item: Model):
                assert False, "You're not supposed to be able to do this"

            def delete_available(self):
                return False

            def delete(self, item: Model):
                assert False, "You're not supposed to be able to do this"

            def create_available(self):
                return False

            def create(self):
                assert False, "You're not supposed to be able to do this"

        class RecentWorksListMediator(ListWidget.Mediator):
            def load(self) -> List[Model]:
                return connection.execute('''
                SELECT WORK.*
                FROM "WORKS" WORK
                WHERE WORK.MASTER_ID = :master_id AND WORK.DATE_WORK > ADD_MONTHS(CURRENT_DATE, -1)
                ORDER BY WORK.DATE_WORK DESC
                ''', model=Work, master_id=user_id).fetch_all()

            def edit(self, item: Work):
                assert isinstance(item, Work)
                show_abstract_edit(item.ID, Work, "WORKS")

            def delete(self, item: Work):
                assert isinstance(item, Work)
                connection.execute('''
                DELETE FROM "WORKS"
                WHERE ID = :work_id
                ''', work_id=item.ID)

            def create(self):
                show_abstract_edit(None, Work, "WORKS")

        class Mediator(MasterRoleWidget.Mediator):
            pass

        cars_widget = ListWidget(CarsListMediator(), "Available cars")
        services_widget = ListWidget(ServicesListMediator(), "Available services")
        works_widget = ListWidget(RecentWorksListMediator(), "Your recent works")
        return MasterRoleWidget(Mediator(), cars_widget, services_widget, works_widget)

    def _create_supervisor_role_widget(self):
        connection = self._connection
        show_abstract_edit = self._show_abstract_edit

        class CarsListMediator(ListWidget.Mediator):
            def load(self) -> List[Model]:
                return connection.execute('''
                SELECT CAR.*
                FROM "CARS" CAR
                ORDER BY CAR.ID DESC
                ''', model=Car).fetch_all()

            def edit(self, item: Car):
                assert isinstance(item, Car)
                show_abstract_edit(item.ID, Car, "CARS")

            def delete(self, item: Car):
                assert isinstance(item, Car)
                connection.execute('''
                DELETE FROM "CARS"
                WHERE ID = :id_
                ''', id_=item.ID)

            def create(self):
                show_abstract_edit(None, Car, "CARS")

        class ServicesListMediator(ListWidget.Mediator):
            def load(self) -> List[Model]:
                return connection.execute('''
                SELECT SVC.*
                FROM "SERVICES" SVC
                ORDER BY SVC.ID DESC
                ''', model=Service).fetch_all()

            def edit(self, item: Service):
                assert isinstance(item, Service)
                show_abstract_edit(item.ID, Service, "SERVICES")

            def delete(self, item: Service):
                assert isinstance(item, Service)
                connection.execute('''
                DELETE FROM SERVICES
                WHERE ID = :id_
                ''', id_=item.ID)

            def create(self):
                show_abstract_edit(None, Service, "SERVICES")

        class WorksListMediator(ListWidget.Mediator):
            def load(self) -> List[Model]:
                return connection.execute('''
                SELECT WORK.*
                FROM "WORKS" WORK
                ORDER BY WORK.DATE_WORK DESC
                ''', model=Work).fetch_all()

            def edit(self, item: Work):
                assert isinstance(item, Work)
                show_abstract_edit(item.ID, Work, "WORKS")

            def delete(self, item: Work):
                assert isinstance(item, Work)
                connection.execute('''
                DELETE FROM "WORKS"
                WHERE ID = :id_
                ''', id_=item.ID)

            def create(self):
                show_abstract_edit(None, Work, "WORKS")

        class MastersListMediator(ListWidget.Mediator):
            def load(self) -> List[Model]:
                items = connection.execute('''
                SELECT MASTER.*
                FROM MASTERS MASTER
                ''', model=Master).fetch_all()
                return items

            def edit(self, item: Master):
                assert isinstance(item, Master)
                show_abstract_edit(item.ID, Master, "MASTERS")

            def delete(self, item: Master):
                assert isinstance(item, Master)
                connection.execute('''
                DELETE FROM "MASTERS"
                WHERE ID = :id_
                ''', id_=item.ID)

            def create(self):
                show_abstract_edit(None, Master, "MASTERS")

        class Mediator(SupervisorRoleWidget.Mediator):
            def l1(self):
                return {record.IS_FOREIGN: record.COST for record in connection.execute('''
                SELECT CAR.IS_FOREIGN AS IS_FOREIGN, SUM(CASE WHEN CAR.IS_FOREIGN = 1 THEN SERVICE.COST_FOREIGN ELSE SERVICE.COST_OUR END) AS COST
                FROM "CARS" CAR
                INNER JOIN "WORKS" JOB ON JOB.CAR_ID = CAR.ID
                INNER JOIN "SERVICES" SERVICE ON JOB.SERVICE_ID = SERVICE.ID
                GROUP BY CAR.IS_FOREIGN
                ''').fetch_all()}

            def l2(self):
                return connection.execute('''
                SELECT MASTER.*, SUM(1) AS JOBSCOUNT
                FROM "MASTERS" MASTER
                INNER JOIN "WORKS" JOB ON JOB.MASTER_ID = MASTER.ID
                GROUP BY MASTER.ID, MASTER.NAME
                ORDER BY JOBSCOUNT DESC
                ''').fetch_all()

        masters_widget = ListWidget(MastersListMediator(), "Masters")
        services_widget = ListWidget(ServicesListMediator(), "Services")
        cars_widget = ListWidget(CarsListMediator(), "Cars")
        works_widget = ListWidget(WorksListMediator(), "Works")
        return SupervisorRoleWidget(Mediator(), (masters_widget, services_widget, cars_widget, works_widget))

