import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Model import *

from Database import *
from UITable import UITable


def main(argv):
    app = QApplication(sys.argv)

    # with Database(username='DB_USER_1', password='ORACLE', host='192.168.56.101', port=1521, listener='orcl') as db:
    with Database(username='SYSTEM', password='oracle', host='192.168.56.101', port=1521, listener='orcl') as db:
        if db is None:
            sys.exit(1)

        window = QWidget()
        window.resize(320, 240)
        window.setWindowTitle('Lab9')
        window.show()

        def run(query, title=None):
            table = UITable(db.execute(query), window)
            table.setWindowTitle(title or query)
            table.show()

        def lab_1_a_1():
            """Вычислить общее услуг и общую сумму стоимости для отечественных и импортных автомобилей"""
            run('''
            SELECT COUNT(1), SUM(COST_OUR), SUM(COST_FOREIGN)
            FROM "DB_USER_1"."SERVICES"
            ''')

        def lab_1_a_2():
            """Вывести все работы за последний месяц"""
            run('''
            SELECT *
            FROM "DB_USER_1"."WORKS"
            WHERE "DATE_WORK" < CURRENT_DATE AND "DATE_WORK" > ADD_MONTHS(CURRENT_DATE, -1)
            ''')

        def lab_1_b_1():
            """Вывести все иностранные автомобили, которые обслуживались за последний месяц больше двух раз"""
            run('''
            SELECT CAR.*
            FROM "DB_USER_1"."CARS" CAR
            WHERE CAR.IS_FOREIGN = 1 AND 2 < (SELECT COUNT(1) FROM "DB_USER_1"."WORKS" JOB WHERE JOB.CAR_ID = CAR.ID)
            ''')

        def lab_1_b_2():
            """Вывести стоимость обслуживания каждого автомобиля за последний год,
            включая автомобили, которые не обслуживались, упорядочив по убыванию стоимости"""
            run('''
            SELECT CAR.ID AS CAR_ID, SUM(CASE WHEN CAR.IS_FOREIGN = 1 THEN SERVICE.COST_OUR ELSE SERVICE.COST_FOREIGN END) AS COST
            FROM "DB_USER_1"."CARS" CAR
            LEFT OUTER JOIN "DB_USER_1"."WORKS" JOB ON JOB.CAR_ID = CAR.ID
            INNER JOIN "DB_USER_1"."SERVICES" SERVICE ON JOB.SERVICE_ID = SERVICE.ID
            WHERE JOB.DATE_WORK < CURRENT_DATE AND JOB.DATE_WORK > ADD_MONTHS(CURRENT_DATE, -1)
            GROUP BY CAR.ID
            ''')

        def lab_1_c_1():
            """Вычислить общую стоимость обслуживания отечественных и импортных автомобилей
            за все время существования сервиса"""
            run('''
            SELECT CAR.IS_FOREIGN AS IS_FOREIGN, SUM(CASE WHEN CAR.IS_FOREIGN = 1 THEN SERVICE.COST_OUR ELSE SERVICE.COST_FOREIGN END) AS COST
            FROM "DB_USER_1"."CARS" CAR
            INNER JOIN "DB_USER_1"."WORKS" JOB ON JOB.CAR_ID = CAR.ID
            INNER JOIN "DB_USER_1"."SERVICES" SERVICE ON JOB.SERVICE_ID = SERVICE.ID
            GROUP BY CAR.IS_FOREIGN
            ''')

        def lab_1_c_2():
            """Пять мастеров, которые за последний месяц сделали большего всего машин (разных)"""
            run('''
            SELECT MASTER.ID, SUM(1) AS JOBSCOUNT
            FROM "DB_USER_1"."MASTERS" MASTER
            INNER JOIN "DB_USER_1"."WORKS" JOB ON JOB.MASTER_ID = MASTER.ID
            GROUP BY MASTER.ID
            ORDER BY JOBSCOUNT DESC
            ''')

        # lab_1_c_2()

        def test(query: str, name: str):
            print("\n\n\n" + name)
            cursor = db.execute(query)
            cls = MetaModel.create(name, cursor.schema)
            models = [cls(*args) for args in cursor]
            for item in models:
                print(item)


        test('''SELECT * FROM "DB_USER_1"."CARS"''', "CAR")
        test('''SELECT * FROM "DB_USER_1"."SERVICES"''', "SERVICE")
        test('''SELECT * FROM "DB_USER_1"."MASTERS"''', "MASTER")
        test('''SELECT * FROM "DB_USER_1"."WORKS"''', "WORK")
        # run('''SELECT * FROM all_objects WHERE object_type IN ('TABLE','VIEW') AND OWNER = 'DB_USER_1' ''')

        return_code = app.exec()

    sys.exit(return_code)


if __name__ == '__main__':
    main(sys.argv)