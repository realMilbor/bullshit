import sys
from PyQt5.QtWidgets import *


class UITable(QDialog):
    def __init__(self, cursor, parent=None):
        super().__init__(parent)

        schema = cursor.schema

        table = QTableWidget()
        table.setColumnCount(schema.properties_count)
        table.setHorizontalHeaderLabels(map(lambda x: x.name, schema))

        for i, row in enumerate(cursor):
            for j, element in enumerate(row):
                table.setRowCount(i + 1)
                table.setItem(i, j, QTableWidgetItem(str(element)))

        cursor.dismiss()

        layout = QGridLayout()
        layout.addWidget(table, 0, 0)
        self.setLayout(layout)
