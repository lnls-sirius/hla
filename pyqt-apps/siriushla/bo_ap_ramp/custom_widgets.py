
import numpy as _np

from qtpy.QtGui import QColor
from qtpy.QtCore import Qt, QLocale
from qtpy.QtWidgets import QLineEdit, QTableWidget, QTableWidgetItem, \
    QStyledItemDelegate, QToolTip
from pyqtgraph import functions
from pydm.widgets import PyDMWaveformPlot

from siriushla.widgets import QDoubleSpinBoxPlus
from siriushla.as_ap_configdb import LoadConfigDialog as _LoadConfigDialog


class MyTableWidget(QTableWidget):
    """Reimplement mousePressEvent to show contextMenu."""

    def __init__(self, parent=None, show_menu_fun=None, open_window_fun=None):
        super().__init__(parent)
        self.show_menu_fun = show_menu_fun
        self.open_window_fun = open_window_fun

    def mousePressEvent(self, ev):
        if ev.button() == Qt.RightButton:
            self.show_menu_fun(ev.pos())
        super().mousePressEvent(ev)

    def mouseDoubleClickEvent(self, ev):
        self.open_window_fun(ev.pos())
        super().mouseDoubleClickEvent(ev)


class SpinBoxDelegate(QStyledItemDelegate):
    """Auxiliar class to draw a SpinBox in table items on editing."""

    def __init__(self, parent, mini, maxi, prec):
        super().__init__(parent)
        self.mini = mini
        self.maxi = maxi
        self.prec = prec

    def createEditor(self, parent, option, index):
        """Create editor."""
        editor = QDoubleSpinBoxPlus(parent)
        editor.setMinimum(self.mini)
        editor.setMaximum(self.maxi)
        editor.setDecimals(self.prec)
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


class ConfigLineEdit(QLineEdit):

    def __init__(self, config_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configtype = config_type

    def mouseReleaseEvent(self, ev):
        popup = _LoadConfigDialog(self._configtype)
        popup.configname.connect(self.setText)
        popup.exec_()


class GraphKicks(PyDMWaveformPlot):

    def __init__(self, parent=None, xdata=list(), ydata=list(),
                 tooltip_names=list(), c0=0, color='blue'):
        super().__init__(parent)
        self.setBackgroundColor(QColor(255, 255, 255))
        self.setAutoRangeX(True)
        self.setAutoRangeY(True)
        self.setShowXGrid(True)
        self.setShowYGrid(True)
        self.setObjectName('graph')
        self.setStyleSheet('#graph{min-width:32em;min-height:14em;}')

        self.xdata = xdata
        self.ydata = ydata
        self.tooltip_names = tooltip_names
        self.c0 = c0

        self.addChannel(
            y_channel='Kicks', x_channel='Pos',
            color=color, lineWidth=2, symbol='o', symbolSize=10)
        self.curve = self.curveAtIndex(0)
        self.curve.receiveXWaveform(xdata)
        self.curve.receiveYWaveform(ydata)
        self.curve.redrawCurve()

        self.addChannel(
            y_channel='Mean', x_channel='Pos',
            color='black', lineStyle=1, lineWidth=2)
        self.mean = self.curveAtIndex(1)
        self.mean.receiveXWaveform(xdata)
        self.mean.receiveYWaveform(_np.array([_np.mean(ydata)]*len(ydata)))
        self.mean.redrawCurve()

    def mouseMoveEvent(self, ev):
        unit = 'urad'
        pos = ev.pos()

        posx = self.curve.scatter.mapFromScene(pos).x()
        posx = posx % self.c0
        ind = _np.argmin(_np.abs(_np.array(self.xdata)-posx))
        posy = self.curve.scatter.mapFromScene(pos).y()

        sca, prf = functions.siScale(posy)
        txt = '{0:s}, y = {1:.3f} {2:s}'.format(
            self.tooltip_names[ind], sca*posy, prf+unit)
        QToolTip.showText(
            self.mapToGlobal(pos), txt, self, self.geometry(), 500)
