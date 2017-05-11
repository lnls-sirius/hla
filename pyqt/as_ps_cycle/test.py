#!/usr/local/bin/python3.6

import sys
from pydm.PyQt import QtCore, QtGui
from pydm.widgets.label import PyDMLabel
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.slider import PyDMSlider
from pydm.application import PyDMApplication

class testUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(testUI, self).__init__(parent)

        self.pvlabel = PyDMLabel(self, "ca://VAG-SI-Fam:PS-QFA:OpMode-Sts")
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.pvlabel)

        self.setLayout(layout)



if __name__ == '__main__':
    app = PyDMApplication(None, sys.argv)
    window = testUI()
    window.show()
    app.exec_()
