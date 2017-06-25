from PyQt5 import QtCore, QtGui, QtWidgets, uic
from Model import *
from typing import List
from Database import *


class ListWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def populate(self, cursor: Database.Cursor):
        schema = cursor.schema
        table: QtWidgets.QTableWidget = self.tableWidget
        table.setColumnCount(schema.properties_count)
        table.setHorizontalHeaderLabels(map(lambda x: x.name, schema))

        for i, row in enumerate(cursor):
            for j, element in enumerate(row.serialize().values()):
                table.setRowCount(i + 1)
                table.setItem(i, j, QtWidgets.QTableWidgetItem(str(element)))
