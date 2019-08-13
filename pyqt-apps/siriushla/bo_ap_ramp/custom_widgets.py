
from qtpy.QtCore import Qt, QLocale
from qtpy.QtWidgets import QLineEdit, QTableWidget, QTableWidgetItem, \
    QStyledItemDelegate, QDoubleSpinBox

from siriushla.as_ap_configdb import LoadConfigDialog as _LoadConfigDialog


class MyTableWidget(QTableWidget):
    """Reimplement mousePressEvent to show contextMenu."""

    def __init__(self, parent=None, show_menu_fun=None):
        super().__init__(parent)
        self.show_menu_fun = show_menu_fun

    def mousePressEvent(self, ev):
        if ev.button() == Qt.RightButton:
            self.show_menu_fun(ev.pos())
        super().mousePressEvent(ev)


class SpinBoxDelegate(QStyledItemDelegate):
    """Auxiliar class to draw a SpinBox in table items on editing."""

    def createEditor(self, parent, option, index):
        """Create editor."""
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(500)
        editor.setDecimals(4)
        locale = QLocale(QLocale.English, country=QLocale.UnitedStates)
        locale.setNumberOptions(locale.RejectGroupSeparator)
        editor.setLocale(locale)
        return editor

    def setEditorData(self, spinBox, index):
        """Set editor data."""
        value = index.model().data(index, Qt.EditRole)
        spinBox.setValue(float(value))

    def setModelData(self, spinBox, model, index):
        """Set model data."""
        spinBox.interpretText()
        value = spinBox.value()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, spinBox, option, index):
        """Update editor geometry."""
        spinBox.setGeometry(option.rect)


class CustomTableWidgetItem(QTableWidgetItem):
    """Auxiliar class to make a table column sortable by numeric data."""

    def __init__(self, value):
        """Initialize object."""
        super().__init__('{}'.format(value))

    def __lt__(self, other):
        """Change default sort method to sort by numeric data."""
        if isinstance(other, CustomTableWidgetItem):
            selfDataValue = float(self.data(Qt.EditRole))
            otherDataValue = float(other.data(Qt.EditRole))
            return selfDataValue < otherDataValue
        else:
            return QTableWidgetItem.__lt__(self, other)


class MyDoubleSpinBox(QDoubleSpinBox):
    """Subclass QDoubleSpinBox to reimplement wheelEvent."""

    def __init__(self, parent):
        """Initialize object."""
        super().__init__(parent)
        locale = QLocale(QLocale.English, country=QLocale.UnitedStates)
        locale.setNumberOptions(locale.RejectGroupSeparator)
        self.setLocale(locale)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, event):
        """Reimplement wheel event to ignore event when out of focus."""
        if not self.hasFocus():
            event.ignore()
        else:
            super().wheelEvent(event)


class ConfigLineEdit(QLineEdit):

    def mouseReleaseEvent(self, ev):
        popup = _LoadConfigDialog('bo_normalized')
        popup.configname.connect(self.setText)
        popup.exec_()
