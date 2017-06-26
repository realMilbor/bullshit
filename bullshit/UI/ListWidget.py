from PyQt5 import QtCore, QtGui, QtWidgets, uic
from Model import *
from typing import List, Callable
from Database import *


class ListWidget(QtWidgets.QWidget):
    class Mediator:
        def load(self) -> List[Model]:
            return []

        def edit_available(self) -> bool:
            return True

        def edit(self, item: Model):
            return

        def delete_available(self) -> bool:
            return True

        def delete(self, item: Model):
            return

    class AccessoryWidget(QtWidgets.QWidget):
        def __init__(self, edit_callback: Callable, delete_callback: Callable, parent=None):
            super().__init__(parent)

            self._edit_callback = edit_callback
            self._delete_callback = delete_callback

            layout = QtWidgets.QHBoxLayout()

            if edit_callback is not None:
                edit_button = QtWidgets.QPushButton(''''✏''')
                edit_button.clicked.connect(self._slot_clicked_edit)
                layout.addWidget(edit_button)

            if delete_callback is not None:
                delete_button = QtWidgets.QPushButton('''❌''')
                delete_button.clicked.connect(self._slot_clicked_delete)
                layout.addWidget(delete_button)

            self.setLayout(layout)

        def _slot_clicked_edit(self):
            if self._edit_callback is not None:
                self._edit_callback()

        def _slot_clicked_delete(self):
            if self._delete_callback is not None:
                self._delete_callback()

    def __init__(self, mediator: Mediator, title: str = None, parent=None):
        super().__init__(parent)
        uic.loadUi('./UI/ListWidget.ui', self)

        self._mediator = mediator
        self.groupBox.setTitle(title)
        self.refreshButton.clicked.connect(self._slot_refresh)
        self._populate()

    def _populate(self):
        table = self.tableWidget
        self.refreshLabel.setText('Last update time: ' + str(datetime.now()))

        items = self._mediator.load()
        if not items:
            table.setRowCount(0)
            return

        schema = items[0].schema
        table: QtWidgets.QTableWidget = self.tableWidget
        table.setColumnCount(schema.properties_count + 1)
        table.setHorizontalHeaderLabels(['⚒'] + list(map(lambda x: x.name, schema)))

        for i, row in enumerate(items):
            table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
            table.setRowCount(i + 1)
            edit_callback = (lambda: self._mediator.edit(row)) if self._mediator.edit_available() else None
            delete_callback = (lambda: self._mediator.delete(row)) if self._mediator.delete_available() else None
            widget = __class__.AccessoryWidget(edit_callback=edit_callback, delete_callback=delete_callback)
            table.setCellWidget(i, 0, widget)

            for j, element in enumerate(row.serialize().values()):
                table.setItem(i, j + 1, QtWidgets.QTableWidgetItem(str(element)))

    def _slot_refresh(self):
        self._populate()
