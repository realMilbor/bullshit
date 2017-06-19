import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Model import *
import cx_Oracle

from Database import *
from UITable import UITable


class LAB:
    def __init__(self, db: Database, window: QWidget):
        self.db = db
        self.window = window


class LAB0(LAB):
    """Утилиты"""

    def display_all_cars(self):
        self._do('''SELECT * FROM "DB_USER_1"."CARS"''', 'Cars')

    def display_all_services(self):
        self._do('''SELECT * FROM "DB_USER_1"."SERVICES"''', "Services")

    def display_all_masters(self):
        self._do('''SELECT * FROM "DB_USER_1"."MASTERS"''', "Masters")

    def display_all_works(self):
        self._do('''SELECT * FROM "DB_USER_1"."WORKS"''', "Works")

    def display_all_tables(self):
        self._do('''SELECT * FROM all_objects WHERE object_type IN ('TABLE','VIEW') AND OWNER = 'DB_USER_1' ''')

    def setup(self):
        with open('export.sql') as file:
            script = file.read()
            # TODO: more reliable way to extract statements
            for statement in script.split(';'):
                self.lab.db.execute(statement)

    def run(self):
        self.display_all_masters()
        self.display_all_services()
        self.display_all_cars()
        self.display_all_works()

    def _do(self, query: str, title: str = None):
        table = UITable(self.db.execute(query), self.window)
        table.setWindowTitle(title or query)
        table.show()


class LAB1(LAB):
    """Выборка данных"""

    class A:
        """однотабличная выборка"""

        def __init__(self, lab):
            self.lab = lab

        def l1(self):
            """Вычислить общее услуг и общую сумму стоимости для отечественных и импортных автомобилей"""
            self.lab._do('''
            SELECT COUNT(1) AS COUNT, SUM(COST_OUR) AS TOTAL_OUR, SUM(COST_FOREIGN) AS TOTAL_FOREIGN
            FROM "DB_USER_1"."SERVICES"
            ''', str(self.l1.__doc__))

        def l2(self):
            """Вывести все работы за последний месяц"""
            self.lab._do('''
            SELECT *
            FROM "DB_USER_1"."WORKS"
            WHERE "DATE_WORK" < CURRENT_DATE AND "DATE_WORK" > ADD_MONTHS(CURRENT_DATE, -1)
            ''', str(self.l2.__doc__))

    class B:
        """соединение таблиц (join)"""

        def __init__(self, lab):
            self.lab = lab

        def l1(self):
            """Вывести все иностранные автомобили, которые обслуживались за последний месяц больше двух раз"""
            self.lab._do('''
            SELECT CAR.*
            FROM "DB_USER_1"."CARS" CAR
            WHERE CAR.IS_FOREIGN = 1 AND 2 < (SELECT COUNT(1) FROM "DB_USER_1"."WORKS" JOB WHERE JOB.CAR_ID = CAR.ID)
            ''', str(self.l1.__doc__))

        def l2(self):
            """Вывести стоимость обслуживания каждого автомобиля за последний год,
            включая автомобили, которые не обслуживались, упорядочив по убыванию стоимости"""
            self.lab._do('''
            SELECT CAR.ID AS CAR_ID, SUM(CASE WHEN CAR.IS_FOREIGN = 1 THEN SERVICE.COST_OUR ELSE SERVICE.COST_FOREIGN END) AS COST
            FROM "DB_USER_1"."CARS" CAR
            LEFT OUTER JOIN "DB_USER_1"."WORKS" JOB ON JOB.CAR_ID = CAR.ID
            INNER JOIN "DB_USER_1"."SERVICES" SERVICE ON JOB.SERVICE_ID = SERVICE.ID
            WHERE JOB.DATE_WORK < CURRENT_DATE AND JOB.DATE_WORK > ADD_MONTHS(CURRENT_DATE, -1)
            GROUP BY CAR.ID
            ''', str(self.l2.__doc__))

    class C:
        """для реализации проекта"""

        def __init__(self, lab):
            self.lab = lab

        def l1(self):
            """Вычислить общую стоимость обслуживания отечественных и импортных автомобилей
            за все время существования сервиса"""
            self.lab._do('''
            SELECT CAR.IS_FOREIGN AS IS_FOREIGN, SUM(CASE WHEN CAR.IS_FOREIGN = 1 THEN SERVICE.COST_OUR ELSE SERVICE.COST_FOREIGN END) AS COST
            FROM "DB_USER_1"."CARS" CAR
            INNER JOIN "DB_USER_1"."WORKS" JOB ON JOB.CAR_ID = CAR.ID
            INNER JOIN "DB_USER_1"."SERVICES" SERVICE ON JOB.SERVICE_ID = SERVICE.ID
            GROUP BY CAR.IS_FOREIGN
            ''', str(self.l1.__doc__))

        def l2(self):
            """Пять мастеров, которые за последний месяц сделали большего всего машин (разных)"""
            self.lab._do('''
            SELECT MASTER.ID, SUM(1) AS JOBSCOUNT
            FROM "DB_USER_1"."MASTERS" MASTER
            INNER JOIN "DB_USER_1"."WORKS" JOB ON JOB.MASTER_ID = MASTER.ID
            GROUP BY MASTER.ID
            ORDER BY JOBSCOUNT DESC
            ''', str(self.l2.__doc__))

    def run(self):
        a = __class__.A(self)
        a.l1()
        a.l2()

        b = __class__.B(self)
        b.l1()
        b.l2()

        c = __class__.C(self)
        c.l1()
        c.l2()

    def _do(self, query: str, title: str = None):
        table = UITable(self.db.execute(query), self.window)
        table.setWindowTitle(title or query)
        table.show()


class LAB2(LAB):
    """Вставка данных"""

    class A:
        """однотабличная вставка"""

        def __init__(self, lab):
            self.lab = lab

        def l1(self, service: Service):
            """Добавить новую услугу"""
            assert isinstance(service, Service)
            id = self.lab._do_insert('''"DB_USER_1"."SERVICES"''', service)
            service.ID = id

        def l2(self, work: Work):
            """Добавить работу по новой услуге из {lab_2_a_1}"""
            assert isinstance(work, Work)
            id = self.lab._do_insert('''"DB_USER_1"."WORKS"''', work)
            work.ID = id

        def run(self):
            service = Service(ID=0, NAME="TEST SERVICE LAB2_A_1", COST_OUR=11, COST_FOREIGN=22)
            self.l1(service)
            print("LAB2_A_1 Inserted new service: " + str(service))
            work = Work(ID=0, DATE_WORK=datetime.now(), MASTER_ID=1, CAR_ID=1, SERVICE_ID=service.ID)
            self.l2(work)
            print("LAB2_A_1 Inserted new work: " + str(work))

    class B:
        """многотабличная вставка в рамках транзакции"""

        def __init__(self, lab):
            self.lab = lab

        def l1(self, car: Car, service: Service, work: Work):
            """Добавить в рамках транзакции новый автомобиль и услугу
            и провести работу для этого автомобиля по новой услуге."""
            assert isinstance(car, Car) and isinstance(service, Service) and isinstance(work, Work)

            def chunk():
                car.ID = self.lab._do_insert('''"DB_USER_1"."CARS"''', car)
                service.ID = self.lab._do_insert('''"DB_USER_1"."SERVICES"''', service)
                work.CAR_ID = car.ID
                work.SERVICE_ID = service.ID
                work.ID = self.lab._do_insert('''"DB_USER_1"."WORKS"''', work)

            self.lab.db.perform_in_transaction(chunk)

        def l2(self, work: Work):
            """Добавить в рамках транзакции работу, в случае, если для мастера уже была работа за день,
            транзакцию откатить."""
            assert isinstance(work, Work)

            def chunk():
                work.ID = self.lab._do_insert('''"DB_USER_1"."WORKS"''', work)
                cursor = self.lab._do('''
                SELECT COUNT(1) AS WORKS_COUNT
                FROM "DB_USER_1"."WORKS" WORK
                WHERE WORK.MASTER_ID = :masterid AND WORK.DATE_WORK > (CURRENT_DATE - 1)
                ''', masterid=work.MASTER_ID)
                works_counts = [x.WORKS_COUNT for x in cursor]
                assert works_counts[0] == 1

            return self.lab.db.perform_in_transaction(chunk)

        def run(self):
            car = Car(ID=0, NUM="t000tt", COLOR=0, MARK="TEST CAR LAB2_B_1", IS_FOREIGN=1)
            service = Service(ID=0, NAME="TEST SERVICE LAB2_B_1", COST_OUR=11, COST_FOREIGN=22)
            work = Work(ID=0, DATE_WORK=datetime.now(), MASTER_ID=1, CAR_ID=0, SERVICE_ID=0)
            self.l1(car, service, work)
            print("Inserted new\ncar: {car}\nservice: {service}\nwork: {work}".format(car=str(car), work=str(work), service=str(service)))

            work2 = Work(ID=0, DATE_WORK=datetime.now(), MASTER_ID=1, CAR_ID=car.ID, SERVICE_ID=service.ID)
            if self.l2(work2):
                print("Inserted new work: {work}".format(work=str(work2)))

    def run(self):
        a = __class__.A(self)
        a.run()
        b = __class__.B(self)
        b.run()

    def _do(self, query: str, *args, **kwargs):
        return self.db.execute(query, *args, **kwargs)

    def _do_insert(self, table: str, model: Model):
        object: OrderedDict = model.serialize()
        id_key = "ID"
        del object[id_key]
        keys = object.keys()

        variables = {
            id_key: cx_Oracle.NUMBER
        }

        query = '''
        INSERT INTO {table} ({keys})
        VALUES ({values})
        RETURNING "{ID}" INTO :{ID}
        '''.format(table=table, keys=', '.join(keys), values=', '.join([':' + key for key in keys]), ID=id_key)

        cursor: Database.DatabaseCursor = self.db.execute(query, vars=variables, **object)

        return cursor.variables[id_key].getvalue()


class LAB3(LAB):
    """Удаление данных"""

    class A:
        """удаление по фильтру и удаление из связанных таблиц"""

        def __init__(self, lab):
            self.lab = lab

        def l1(self, car_id: Number):
            """Удалить статью автомобиль и все работы по нему"""
            self.lab._do('''
            DELETE FROM "DB_USER_1"."CARS"
            WHERE ID = :car_id
            ''', car_id=car_id)

        def run(self):
            self.l1(60)

    class B:
        """удаление в рамках транзакции"""

        def __init__(self, lab):
            self.lab = lab

        def l1(self, master_id: Number):
            """Удалить в рамках транзакции услуги, которые оказывались только заданным мастером.
            Удалить работы по таким услугам этого мастера."""
            def chunk():
                self.lab._do('''
                DELETE FROM "DB_USER_1"."SERVICES" SVC
                WHERE SVC.ID IN (
                SELECT 1
                FROM (SELECT WORK."SERVICE_ID" AS SVCID, SUM(1) AS COUNT
                FROM "DB_USER_1"."WORKS" WORK
                WHERE WORK.MASTER_ID = :master_id
                GROUP BY  WORK."SERVICE_ID") SVC
                WHERE SVC.COUNT = 1)
                ''', master_id=master_id)

            self.lab.db.perform_in_transaction(chunk)

        def l2(self, master_id: Number):
            """то же, что и п1, но еще удалить мастера и транзакцию откатить"""
            def chunk():
                self.lab._do('''
                DELETE FROM "DB_USER_1"."SERVICES" SVC
                WHERE SVC.ID IN (
                SELECT 1
                FROM (SELECT WORK."SERVICE_ID" AS SVCID, SUM(1) AS COUNT
                FROM "DB_USER_1"."WORKS" WORK
                WHERE WORK.MASTER_ID = :master_id
                GROUP BY  WORK."SERVICE_ID") SVC
                WHERE SVC.COUNT = 1)
                ''', master_id=master_id)
                self.lab._do('''
                DELETE FROM "DB_USER_1"."MASTERS" MASTER
                WHERE MASTER.ID = :master_id
                ''', master_id=master_id)
                raise Exception()

            self.lab.db.perform_in_transaction(chunk)

        def run(self):
            self.l1(1)
            self.l2(2)

    def run(self):
        a = __class__.A(self)
        a.run()
        b = __class__.B(self)
        b.run()

    def _do(self, query: str, *args, **kwargs):
        return self.db.execute(query, *args, **kwargs)


class LAB4(LAB):
    """Модификация данных"""

    class A:
        """модификация по фильтру"""

        def __init__(self, lab):
            self.lab = lab

        def l1(self):
            """Увеличить стоимость всех услуг на 15%"""
            self.lab._do('''
            UPDATE "DB_USER_1"."SERVICES"
            SET COST_OUR = COST_OUR * 1.15, COST_FOREIGN = COST_FOREIGN * 1.15
            ''')
            self.lab.db.commit_transaction()

        def run(self):
            self.l1()

    class B:
        """модификация в рамках транзакции"""

        def __init__(self, lab):
            self.lab = lab

        def l1(self):
            """В рамках транзакции в таблице услуг увеличить цену услуги, оказанной последней, на 10.00"""
            def chunk():
                self.lab._do('''
                UPDATE "DB_USER_1"."SERVICES" SERVICE
                SET COST_OUR = COST_OUR + 10.00, COST_FOREIGN = COST_FOREIGN + 10.00
                WHERE SERVICE.ID IN (
                SELECT WORK."SERVICE_ID"
                FROM "DB_USER_1"."WORKS" WORK
                ORDER BY WORK."DATE_WORK" DESC
                FETCH FIRST 1 ROW ONLY
                )
                ''')

            self.lab.db.perform_in_transaction(chunk)

        def l2(self):
            """то же, что и п1, но транзакцию откатить"""
            def chunk():
                self.lab._do('''
                UPDATE "DB_USER_1"."SERVICES" SERVICE
                SET COST_OUR = COST_OUR + 10.00, COST_FOREIGN = COST_FOREIGN + 10.00
                WHERE SERVICE.ID IN (
                SELECT WORK."SERVICE_ID"
                FROM "DB_USER_1"."WORKS" WORK
                ORDER BY WORK."DATE_WORK" DESC
                FETCH FIRST 1 ROW ONLY
                )
                ''')
                raise Exception()

            self.lab.db.perform_in_transaction(chunk)

        def run(self):
            self.l1()
            self.l2()

    def run(self):
        a = __class__.A(self)
        a.run()
        b = __class__.B(self)
        b.run()
        pass

    def _do(self, query: str, *args, **kwargs):
        result = self.db.execute(query, *args, **kwargs)
        return result


def main(argv):
    app = QApplication(sys.argv)

    # with Database(username='DB_USER_1', password='ORACLE', host='192.168.56.101', port=1521, listener='orcl') as db:
    db = Database(username='SYSTEM', password='oracle', host='192.168.56.101', port=1521, listener='orcl')

    with db.connect() as db:
        if db is None:
            sys.exit(1)

        window = QWidget()
        window.resize(640, 480)
        window.setWindowTitle('LAB1 v9')
        window.show()

        # for lab_class in (LAB0, LAB1, LAB2, LAB3, LAB4):
        #     lab = lab_class(db, window)
        #     lab.run()

        # l2 = LAB2(db, window)
        # a = LAB2.A(l2)
        # a.run()

        lab = LAB4(db, window)
        b = LAB4.B(lab)
        b.run()

        return_code = app.exec()

    sys.exit(return_code)


if __name__ == '__main__':
    main(sys.argv)
