"""Configuration Delegate."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QItemDelegate, QDoubleSpinBox, QLineEdit


class PVConfigurationDelegate(QItemDelegate):


    def createEditor(self, parent, option, index):
        """Override.

        Create and editor based on the cell type
        """
        if index.column() == 2:
            editor = QDoubleSpinBox(parent)
            editor.setDecimals(3)
            editor.setMaximum(1)
            editor.setMinimum(0)
            editor.setSingleStep(0.001)
        return editor

    def setEditorData(self, editor, index):
        """Override.

        Set cell data as float.
        """
        value = index.model().data(index, Qt.DisplayRole)
        editor.setValue(value)
