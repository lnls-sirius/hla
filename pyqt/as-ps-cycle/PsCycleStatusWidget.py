import sys, re
from pydm.PyQt.QtCore import *
from pydm.PyQt.QtGui import *
from pydm.widgets.label import PyDMLabel
from siriuspy.namesys import SiriusPVName
import qrc_resource


class PsCycleStatusWidget(QWidget):
    def __init__(self, parent=None):
        super(PsCycleStatusWidget, self).__init__(parent)

        main_grid = QGridLayout()
        main_grid.addWidget(self._createGroupBox("Ring - Dipoles", self._getPs('si', 'b')), 0, 0)
        main_grid.addWidget(self._createGroupBox("Ring - Quadrupoles", self._getPs('si', 'q')), 0, 1)
        main_grid.addWidget(self._createGroupBox("Ring - Sextupoles", self._getPs('si', 's')), 0, 2)
        main_grid.addWidget(self._createGroupBox("Ring - Corretoras", self._getPs('si', 'c')), 0, 3, 3, 1)
        main_grid.addWidget(self._createGroupBox("Transport Lines - Dipoles", self._getPs('lt', 'b')), 1, 0)
        main_grid.addWidget(self._createGroupBox("Transport Lines - Quadrupoles", self._getPs('lt', 'q')), 1, 1)
        main_grid.addWidget(self._createGroupBox("Transport Lines - Corretoras", self._getPs('lt', 'c')), 1, 2, 2, 1)
        main_grid.addWidget(self._createGroupBox("Linac - Quadrupoles", self._getPs('li', 'q')), 2, 0)
        main_grid.addWidget(self._createGroupBox("Linac - Corretoras", self._getPs('li', 'c')), 2, 1)

        self.setLayout(main_grid)

    def _createGroupBox(self, title, elements):
        labels = []
        grid = QGridLayout()
        for idx, ps in enumerate(elements):
            #elem_name = QLabel("{0} - ".format(idx + 1) + ps.dev_name)
            elem_name = QLabel(ps.dev_name)
            elem_status = PyDMLabel(self, "ca://VAG-" + ps.dev_name + ":OpMode-Sts")
            elem_status.disconnected_signal.connect(self._pvDisconnected)
            elem_status.setText("Can't connect!")
            elem_status.setMaximumWidth(75)
            elem_val= PyDMLabel(self, "ca://VAG-" + ps.dev_name + ":Current-RB")
            elem_val.disconnected_signal.connect(self._pvDisconnected)
            elem_val.setText("Can't connect!")
            elem_val.setMaximumWidth(75)
            elem_val.setPrecision(2)
            grid.addWidget(elem_name, idx, 0)
            grid.addWidget(elem_status, idx, 1)
            grid.addWidget(elem_val, idx, 2)


        groupBox = QGroupBox(title)
        groupBox.setLayout(grid)
        scroll = QScrollArea()
        scroll.setWidget(groupBox)
        scroll.setMinimumWidth(275)

        return scroll


    def _getPs(self, section, element):
        ps = []
        with open("ps_map/ps_%s_%s.txt" % (section, element), "r") as fd:
            for line in fd:
                ps.append(SiriusPVName(line.strip()))

        return ps

    def _pvDisconnected(self):
        sender = self.sender()
        sender.setText("Disconnected")
