from PyQt5 import QtCore, QtGui, QtWidgets, uic
from Model import *
from typing import List
from Database import *
from .ListWidget import ListWidget


class MasterRoleWidget(QtWidgets.QWidget):
    class Mediator:
        pass

    def __init__(self, mediator: Mediator, cars_widget, services_widget, works_widget, parent=None):
        super().__init__(parent)
        uic.loadUi('./UI/MasterRoleWidget.ui', self)
        self._mediator = mediator
        self.infoLayout.addWidget(cars_widget)
        self.infoLayout.addWidget(services_widget)
        self.worksLayout.addWidget(works_widget)