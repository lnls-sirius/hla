#!/usr/local/bin/python3.6

import sys, time, threading
from pydm.PyQt.QtCore import *
from pydm.PyQt.QtGui import *
from pydm import PyDMApplication
from CyclePowerSupplies import CyclePowerSupplies
from PsCycleControlItem import PsCycleControlItem
from CommandThread import CommandThread
from siriuspy.namesys import SiriusPVName

class BusyDlg(QDialog):

    def __init__(self, parent=None, message=None):
        super(BusyDlg, self).__init__(parent)

        if message:
            self._message = message
        else:
            self._message = "Please wait"

        self._setupUi()

    def _setupUi(self):
        self.layout = QVBoxLayout()
        self.question_label = QLabel("Proceed?", self)
        self.button_box =  QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.layout.addWidget(self.question_label)
        self.layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.okButton)
        self.button_box.rejected.connect(self.reject)

        self.setLayout(self.layout)


    def okButton(self):
        self.msg_layout = QVBoxLayout()
        self.message_label = QLabel(self._message, self)
        self.msg_layout.addWidget(self.message_label)
        self.setLayout(self.msg_layout)
        self.parentWidget()._prep()
        self.accept()




class PsCycleWindow(QDialog):
    #Members
    _ready_to_cycle = False

    def __init__(self, parent=None):
        super(PsCycleWindow, self).__init__(parent)
        self._setupUi()
        self.ps_cycle = CyclePowerSupplies()

    @pyqtSlot(int)
    def changePsSet(self, state):
        sender = self.sender()
        name = sender.objectName()
        if state:
            self.ps_cycle.addPsSet(name)
        else:
            self.ps_cycle.removePsSet(name)

    def _setupUi(self):
        self.setWindowTitle("Power Supply Cycling")

        #Anel
        self.siDCkB = QCheckBox("Dipoles")
        self.siDCkB.setObjectName("si_b")
        self.siDCkB.stateChanged.connect(self.changePsSet)
        self.siQCkB = QCheckBox("Quadrupoles")
        self.siQCkB.setObjectName("si_q")
        self.siQCkB.stateChanged.connect(self.changePsSet)
        self.siSCkB = QCheckBox("Sextupoles")
        self.siSCkB.setObjectName("si_s")
        self.siSCkB.stateChanged.connect(self.changePsSet)
        self.siCCkB = QCheckBox("Corretoras")
        self.siCCkB.setObjectName("si_c")
        self.siCCkB.stateChanged.connect(self.changePsSet)
        #Linhas de transpote
        self.ltDCkB = QCheckBox("Dipoles")
        self.ltDCkB.setObjectName("lt_b")
        self.ltDCkB.stateChanged.connect(self.changePsSet)
        self.ltQCkB = QCheckBox("Quadrupoles")
        self.ltQCkB.setObjectName("lt_q")
        self.ltQCkB.stateChanged.connect(self.changePsSet)
        self.ltCCkB = QCheckBox("Corretoras")
        self.ltCCkB.setObjectName("lt_c")
        self.ltCCkB.stateChanged.connect(self.changePsSet)
        #Linac
        self.liQCkB = QCheckBox("Quadrupoles")
        self.liQCkB.setObjectName("li_q")
        self.liQCkB.stateChanged.connect(self.changePsSet)
        self.liCCkb = QCheckBox("Corretoras")
        self.liCCkb.setObjectName("li_c")
        self.liCCkb.stateChanged.connect(self.changePsSet)
        #Create Group Boxes
        siPsBox = self._createCheckBoxGroup("Ring", [self.siDCkB, self.siQCkB, \
                self.siSCkB, self.siCCkB ])
        ltPsBox = self._createCheckBoxGroup("Tansport Lines", [self.ltDCkB, \
                self.ltQCkB, self.ltCCkB ])
        liPsBox = self._createCheckBoxGroup("Linac", [self.liQCkB, self.liCCkb])
        #Create command buttons
        self.prepareButton = QPushButton("Set to Cycle")
        self.prepareButton.clicked.connect(self._prepareToCycle)
        self.cycleButton = QPushButton("Cycle")
        if self._ready_to_cycle:
            self.cycleButton.setEnabled(True)
        else:
            self.cycleButton.setEnabled(False)
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.prepareButton)
        buttonLayout.addWidget(self.cycleButton)
        #Build grid containing the main menu
        menu_grid = QGridLayout()
        menu_grid.addWidget(siPsBox, 0, 0)
        menu_grid.addWidget(ltPsBox, 0, 1)
        menu_grid.addWidget(liPsBox, 1, 0)
        menu_grid.addLayout(buttonLayout, 2, 0, 1, 2)

        #Create Group boxes with the power stupplies status
        status_grid = QGridLayout()
        status_grid.addWidget(self._createPsGroupBox("Ring - Dipoles", self._getPs('si', 'b')), 0, 0)
        status_grid.addWidget(self._createPsGroupBox("Ring - Quadrupoles", self._getPs('si', 'q')), 0, 1)
        status_grid.addWidget(self._createPsGroupBox("Ring - Sextupoles", self._getPs('si', 's')), 0, 2)
        status_grid.addWidget(self._createPsGroupBox("Ring - Corretoras", self._getPs('si', 'c')), 0, 3, 3, 1)
        status_grid.addWidget(self._createPsGroupBox("Transport Lines - Dipoles", self._getPs('lt', 'b')), 1, 0)
        status_grid.addWidget(self._createPsGroupBox("Transport Lines - Quadrupoles", self._getPs('lt', 'q')), 1, 1)
        status_grid.addWidget(self._createPsGroupBox("Transport Lines - Corretoras", self._getPs('lt', 'c')), 1, 2, 2, 1)
        status_grid.addWidget(self._createPsGroupBox("Linac - Quadrupoles", self._getPs('li', 'q')), 2, 0)
        status_grid.addWidget(self._createPsGroupBox("Linac - Corretoras", self._getPs('li', 'c')), 2, 1)

        #Create frame that'll contain the PS status widgets
        self.moreFrame = QFrame()
        self.moreFrame.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        frameLayout = QVBoxLayout()
        frameLayout.addLayout(status_grid)
        self.moreFrame.setLayout(frameLayout)
        self.moreFrame.setMinimumHeight(800)
        self.moreFrame.setMaximumHeight(800)
        self.moreFrame.setMaximumWidth(1500)
        self.moreFrame.setMinimumWidth(1500)
        self.moreFrame.hide()

        self.moreButton = QPushButton("Show More")
        self.moreButton.setCheckable(True)
        self.moreButton.toggled.connect(self.moreFrame.setVisible)
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.moreButton)

        #Build main grid and set as dlg layout
        main_grid = QGridLayout()
        #main_grid.addLayout(menuLayout, 0, 0)
        main_grid.addLayout(menu_grid, 0, 0)
        main_grid.addWidget(self.moreFrame, 0, 1, 1, 2)
        main_grid.addLayout(buttonLayout, 1, 0)
        main_grid.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(main_grid)

    def _createCheckBoxGroup(self, title, elements):
        groupBox = QGroupBox(title)
        #Group box setting
        groupBox.setCheckable(True)
        groupBox.setChecked(False)
        #Add group box elements
        boxLayout = QVBoxLayout()
        for e in elements:
            boxLayout.addWidget(e)
        #boxLayout.addStretch()
        groupBox.setLayout(boxLayout)
        #Create signals
        for e in elements:
            groupBox.toggled.connect(e.setChecked)

        return groupBox

    def _prepareToCycle(self):
        #t = CommandThread(self.ps_cycle, "setToCycle", self)
        #t.start()

        input_dlg = QMessageBox(QMessageBox.Question, "Prepare to Cycle", \
                "Proceed?", QMessageBox.Cancel|QMessageBox.Ok, self)
        warning_dlg = QMessageBox(QMessageBox.Warning, "Setting power supplies", \
                "Setting power supplies to cycling mode, this may take a while", parent=self)

        ret = input_dlg.exec_()
        if ret == QMessageBox.Ok:
            #TODO: use thread to start task and show a block message box
            t = threading.Thread(target=self._prep)
            t.start()
            warning_dlg.exec_()
            t.join()

    def _prep(self):
        if self.ps_cycle.setToCycle():
            self._ready_to_cycle = True
            self.cycleButton.setEnabled(True)
        else:
            self._ready_to_cycle = False
            self.cycleButton.setEnabled(False)


    def _createPsGroupBox(self, title, elements):
        labels = []
        #grid = QGridLayout()
        vBox = QVBoxLayout()
        vBox.setSpacing(0)
        vBox.setContentsMargins(0, 0, 0, 0)
        for idx, ps in enumerate(elements):
            controlItem = PsCycleControlItem(ps, self)
            vBox.addWidget(controlItem)

        groupBox = QGroupBox(title)
        groupBox.setLayout(vBox)
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



if __name__ == '__main__':
    app = PyDMApplication(None, sys.argv)
    window = PsCycleWindow()
    window.show()
    app.exec_()
