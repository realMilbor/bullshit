from PyQt5 import QtCore, QtGui, QtWidgets, uic
from Model import *
from Schema import Schema
from datetime import datetime
from numbers import Number


class EditDialog(QtWidgets.QDialog):
    class Mediator:
        def read(self) -> Model:
            pass

        def write(self, model: Model):
            pass

    def __init__(self, mediator: Mediator, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        uic.loadUi('./UI/EditDialog.ui', self)
        self.buttonBox.clicked.connect(self._slot_clicked)
        self._mediator = mediator
        self._current_model_class = None
        self._input_fields = {}
        self.load()

    def accept(self):
        self.save()
        super().accept()

    def save(self):
        model_class = self._current_model_class
        if model_class is None:
            return

        schema = model_class.static_schema
        params = {}
        for property in schema:
            key = property.name
            value = self._input_fields[key].text() or None
            if property.type is Number:
                params[key] = float(value) if value is not None else 0
            else:
                params[key] = property.type(value) if value is not None else property.type()

        self._mediator.write(model_class(**params))

    def load(self):
        self._clear_form()
        model = self._mediator.read()
        self._current_model_class = type(model)
        self._create_form(model.schema)
        for key, value in model.serialize().items():
            self._input_fields[key].setText(str(value) if value is not None else str())

    def _slot_clicked(self, button):
        standard_button = self.sender().standardButton(button)
        if standard_button == QtWidgets.QDialogButtonBox.Reset:
            self.load()
        elif standard_button == QtWidgets.QDialogButtonBox.Apply:
            self.save()
            self.load()

    def _create_form(self, schema: Schema):
        def validator_for_type(type: type) -> QtGui.QValidator:
            return {
                Number: QtGui.QDoubleValidator(),
                int: QtGui.QIntValidator(),
                float: QtGui.QDoubleValidator(),
            }.get(type, None)

        input_fields = {}
        layout: QtWidgets.QFormLayout = self.groupBox.layout()
        for property in schema.properties:
            line_edit = QtWidgets.QLineEdit()
            line_edit.setEnabled(property.name != 'ID')

            validator = validator_for_type(property.type)
            line_edit.setValidator(validator) if validator is not None else None

            input_fields[property.name] = line_edit
            layout.addRow(property.name, line_edit)

        self._input_fields = input_fields

    def _clear_form(self):
        self._input_fields = {}
        layout = self.groupBox.layout()
        for i in reversed(range(layout.count())):
            widget: QtWidgets.QWidget = layout.takeAt(i).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
