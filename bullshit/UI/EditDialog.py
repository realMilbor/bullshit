import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from Model import *
from Schema import Schema
from datetime import datetime
from numbers import Number
import cx_Oracle


class EditDialog(QtWidgets.QDialog):
    class Mediator:
        def read(self) -> Model:
            pass

        def write(self, model: Model):
            pass

    class AbstractField:
        def __init__(self):
            self._widget = None

        def set(self, value):
            pass

        def get(self):
            pass

        def widget(self):
            return self._widget

    class DatePickerField(AbstractField):
        def __init__(self):
            super().__init__()
            self._widget = QtWidgets.QDateTimeEdit()

        def set(self, value):
            self._widget.setDateTime(QtCore.QDateTime(value) if value else QtCore.QDateTime.currentDateTime())

        def get(self):
            return self._widget.dateTime().toPyDateTime()

    class LineEditField(AbstractField):
        def __init__(self):
            super().__init__()
            self._widget = QtWidgets.QLineEdit()

        def set(self, value):
            self._widget.setText(value or "")

        def get(self):
            return self._widget.text()

    class SpinboxField(AbstractField):
        def __init__(self):
            super().__init__()
            self._widget = QtWidgets.QSpinBox()
            self._widget.setRange(-2147483647, 2147483647)

        def set(self, value):
            self._widget.setValue(int(value) if value else 0)

        def get(self):
            return self._widget.value()

    class DoubleSpinboxField(AbstractField):
        def __init__(self):
            super().__init__()
            self._widget = QtWidgets.QDoubleSpinBox()
            self._widget.setRange(-2147483647, 2147483647)

        def set(self, value):
            self._widget.setValue(float(value) if value else 0.0)

        def get(self):
            return self._widget.value()

    def __init__(self, mediator: Mediator, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        uic.loadUi('./UI/EditDialog.ui', self)
        self.buttonBox.clicked.connect(self._slot_clicked)
        self._mediator = mediator
        self._current_model_class = None
        self._input_fields = {}
        self.load()

    def accept(self):
        try:
            self.save()
        except cx_Oracle.DatabaseError as error:
            self._show_error_dialog(error)
        else:
            super().accept()

    def save(self):
        model_class = self._current_model_class
        if model_class is None:
            return

        schema = model_class.static_schema
        params = {}
        for property in schema:
            key = property.name
            value = self._input_fields[key].get()
            params[key] = value

        self._mediator.write(model_class(**params))


    def load(self):
        self._clear_form()
        model = self._mediator.read()
        self._current_model_class = type(model)
        self._create_form(model.schema)
        for key, value in model.serialize().items():
            self._input_fields[key].set(value)

    def _slot_clicked(self, button):
        standard_button = self.sender().standardButton(button)
        if standard_button == QtWidgets.QDialogButtonBox.Reset:
            self.load()
        elif standard_button == QtWidgets.QDialogButtonBox.Apply:
            try:
                self.save()
            except cx_Oracle.DatabaseError as error:
                self._show_error_dialog(error)
            else:
                self.load()

    def _create_form(self, schema: Schema):
        def field_class_for_type(self, type: type) -> type:
            if type in (int, Number):
                return self.__class__.SpinboxField
            elif type == float:
                return self.__class__.DoubleSpinboxField
            elif type == str:
                return self.__class__.LineEditField
            elif type == datetime:
                return self.__class__.DatePickerField
            else:
                assert False

        input_fields = {}
        layout: QtWidgets.QFormLayout = self.groupBox.layout()
        for property in schema.properties:
            field = field_class_for_type(self, property.type)()
            field.widget().setEnabled(property.name != 'ID')

            input_fields[property.name] = field
            layout.addRow(property.name, field.widget())

        self._input_fields = input_fields

    def _clear_form(self):
        self._input_fields = {}
        layout = self.groupBox.layout()
        for i in reversed(range(layout.count())):
            widget: QtWidgets.QWidget = layout.takeAt(i).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _show_error_dialog(self, err: cx_Oracle.DatabaseError):
        (error,) = err.args
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Critical if error.isrecoverable else QtWidgets.QMessageBox.Warning)
        msg.setText(str(error.code))
        msg.setInformativeText(str(error.message))
        msg.setWindowTitle("Error")
        msg.setDetailedText(str(error.context))
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setModal(True)
        msg.show()
