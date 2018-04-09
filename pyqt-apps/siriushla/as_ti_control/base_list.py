import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from siriuspy.namesys import SiriusPVName as _PVName


class BaseList(QGroupBox):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {}
    _LABELS = {}
    _ALL_PROPS = tuple()

    def __init__(self, name=None, parent=None, prefix='',
                 props=set(), obj_names=list()):
        """Initialize object."""
        super().__init__(name, parent)
        self.prefix = prefix
        self.props = props or set(self._ALL_PROPS)
        self.obj_names = obj_names
        self.setupUi()

    def setupUi(self):
        self.my_layout = QGridLayout(self)
        self.my_layout.setVerticalSpacing(30)
        self.my_layout.setHorizontalSpacing(30)

        objs = self.getLine(header=True)
        for j, obj in enumerate(objs):
            self.my_layout.addItem(obj, 0, j)
        for i, obj_name in enumerate(self.obj_names, 1):
            pref = _PVName(self.prefix + obj_name)
            objs = self.getLine(pref)
            for j, obj in enumerate(objs):
                self.my_layout.addItem(obj, i, j)

    def getLine(self, prefix=None, header=False):
        objects = list()
        for prop in self._ALL_PROPS:
            item = self.getColumn(prefix, prop, header)
            if item is not None:
                objects.append(item)
        return objects

    def getColumn(self, prefix, prop, header):
        if prop not in self.props:
            return
        lv = QVBoxLayout()
        lv.setAlignment(Qt.AlignHCenter)
        fun = self._createObjs if not header else self._headerLabel
        objs = fun(prefix, prop)
        for ob in objs:
            lv.addWidget(ob)
            ob.setMinimumWidth(self._MIN_WIDs[prop])
            ob.setSizePolicy(QSzPol.Minimum, QSzPol.Maximum)
        return lv

    def _headerLabel(self, prefix, prop):
        lb = QLabel(self._LABELS[prop], self)
        lb.setAlignment(Qt.AlignHCenter)
        return (lb, )

    def _createObjs(self, prefix, prop):
        return tuple()  # return tuple of widgets
