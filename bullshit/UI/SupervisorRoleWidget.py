from PyQt5 import QtCore, QtGui, QtWidgets, uic
from Model import *
from typing import List
from Database import *
from .ListWidget import ListWidget
import math


class SupervisorRoleWidget(QtWidgets.QWidget):
    class Mediator:
        def l1(self):
            pass

        def l2(self):
            pass

    def __init__(self, mediator: Mediator, info_widgets, parent=None):
        super().__init__(parent)
        uic.loadUi('./UI/SupervisorRoleWidget.ui', self)
        self._mediator = mediator

        layout: QtWidgets.QGridLayout = self.infoLayout
        widgets_count = len(info_widgets)
        widgets_in_row = int(math.ceil(math.sqrt(widgets_count)))
        for index, widget in enumerate(info_widgets):
            layout.addWidget(widget, index / widgets_in_row, index % widgets_in_row)

        top_masters = self._mediator.l2()
        top_masters_string = ', '.join([str(master.NAME) + '(' + str(master.JOBSCOUNT) + ')' for master in top_masters])
        self.mastersInfoLabel.setText(top_masters_string)

        cars_info = self._mediator.l1()
        self.foreignCarsLabel.setText(str(cars_info.get(1, "–")))
        self.ourCarsLabel.setText(str(cars_info.get(0, "–")))
