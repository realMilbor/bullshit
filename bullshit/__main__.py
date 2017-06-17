import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Model import *

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
            SELECT COUNT(1), SUM(COST_OUR), SUM(COST_FOREIGN)
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

        def l1(self):
            """Добавить новую услугу"""
            pass

        def l2(self):
            """Добавить работу по новой услуге из {lab_2_a_1}"""
            pass

    class B:
        """многотабличная вставка в рамках транзакции"""
        def __init__(self, lab):
            self.lab = lab

        def l1(self):
            """Добавить в рамках транзакции новый автомобиль и услугу
            и провести работу для этого автомобиля по новой услуге."""
            pass

        def l2(self):
            """Добавить в рамках транзакции работу, в случае, если для мастера уже была работа за день,
            транзакцию откатить."""
            pass

    def run(self):
        pass


class LAB3(LAB):
    """Удаление данных"""
    class A:
        """удаление по фильтру и удаление из связанных таблиц"""
        def __init__(self, lab):
            self.lab = lab

        def l1(self):
            """Удалить статью автомобиль и все работы по нему"""
            pass

    class B:
        """удаление в рамках транзакции"""
        def __init__(self, lab):
            self.lab = lab

        def l1(self):
            """Удалить в рамках транзакции услуги, которые оказывались только заданным мастером.
            Удалить работы по таким услугам этого мастера."""
            pass

        def l2(self):
            """то же, что и п1, но еще удалить мастера и транзакцию откатить"""
            pass

    def run(self):
        pass


class LAB4(LAB):
    """Модификация данных"""
    class A:
        """модификация по фильтру"""
        def __init__(self, lab):
            self.lab = lab

        def l1(self):
            """Увеличить стоимость всех услуг на 15%"""
            pass

    class B:
        """модификация в рамках транзакции"""
        def __init__(self, lab):
            self.lab = lab

        def l1(self):
            """В рамках транзакции в таблице услуг увеличить цену услуги, оказанной последней, на 10.00"""
            pass

        def l2(self):
            """то же, что и п1, но транзакцию откатить"""
            pass

    def run(self):
        pass


def main(argv):
    app = QApplication(sys.argv)

    # with Database(username='DB_USER_1', password='ORACLE', host='192.168.56.101', port=1521, listener='orcl') as db:
    with Database(username='SYSTEM', password='oracle', host='192.168.56.101', port=1521, listener='orcl') as db:
        if db is None:
            sys.exit(1)

        window = QWidget()
        window.resize(320, 240)
        window.setWindowTitle('LAB1 v9')
        window.show()

        for lab_class in (LAB0, LAB1, LAB2, LAB3, LAB4):
            lab = lab_class(db, window)
            lab.run()

        return_code = app.exec()

    sys.exit(return_code)


if __name__ == '__main__':
    main(sys.argv)