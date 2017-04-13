import sys, re
from pydm.PyQt.QtCore import *
from pydm.PyQt.QtGui import *
from pydm.widgets.label import PyDMLabel
from siriuspy.namesys import SiriusPVName
from CyclingThread import CyclingThread
from CyclePowerSupplies import CyclePowerSupplies


class PsCycleMenuWidget(QWidget):
    def __init__(self, parent=None):
        super(PsCycleMenuWidget, self).__init__(parent)

        #Anel
        self.siDCkB = QCheckBox("Dipoles")
        self.siQCkB = QCheckBox("Quadrupoles")
        self.siSCkB = QCheckBox("Sextupoles")
        self.siCCkb = QCheckBox("Corretoras")
        #Linhas de transpote
        self.ltDCkB = QCheckBox("Dipoles")
        self.ltQCkB = QCheckBox("Quadrupoles")
        self.ltCCkb = QCheckBox("Corretoras")
        #Linac
        self.liQCkB = QCheckBox("Quadrupoles")
        self.liCCkb = QCheckBox("Corretoras")
        #Create Group Boxes
        siPsBox = self._createGroupBox("Ring", [self.siDCkB, self.siQCkB, \
                self.siSCkB, self.siCCkb])
        ltPsBox = self._createGroupBox("Tansport Lines", [self.ltDCkB, \
                self.ltQCkB, self.ltCCkb])
        liPsBox = self._createGroupBox("Linac", [self.liQCkB, self.liCCkb])

        prepareButton = QPushButton("Set to Cycle")
        prepareButton.clicked.connect(self._prepareToCycle)
        cycleButton = QPushButton("Cycle")
        cycleButton.setEnabled(False)
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(prepareButton)
        buttonLayout.addWidget(cycleButton)


        grid = QGridLayout()
        grid.addWidget(siPsBox, 0, 0)
        grid.addWidget(ltPsBox, 0, 1)
        grid.addWidget(liPsBox, 1, 0)
        grid.addLayout(buttonLayout, 2, 0, 1, 2)
        self.setLayout(grid)


    def _prepareToCycle(self):
        threads = []
        #Anel
        if self.siDCkB.isChecked():
            cycling = CyclePowerSupplies(CyclePowerSupplies.ANEL, CyclePowerSupplies.DIPOLOS)
            threads.append(CyclingThread(cycling, self))
        if self.siQCkB.isChecked():
            cycling = CyclePowerSupplies(CyclePowerSupplies.ANEL, CyclePowerSupplies.QUADRUPOLOS)
            threads.append(CyclingThread(cycling, self))
        if self.siSCkB.isChecked():
            cycling = CyclePowerSupplies(CyclePowerSupplies.ANEL, CyclePowerSupplies.SEXTUPOLOS)
            threads.append(CyclingThread(cycling, self))
        if self.siCCkb.isChecked():
            cycling = CyclePowerSupplies(CyclePowerSupplies.ANEL, CyclePowerSupplies.CORRETORAS)
            threads.append(CyclingThread(cycling, self))
        #Linhas de transporte
        if self.ltDCkB.isChecked():
            cycling = CyclePowerSupplies(CyclePowerSupplies.TRANSPORTE, CyclePowerSupplies.DIPOLOS)
            threads.append(CyclingThread(cycling, self))
        if self.ltQCkB.isChecked():
            cycling = CyclePowerSupplies(CyclePowerSupplies.TRANSPORTE, CyclePowerSupplies.QUADRUPOLOS)
            threads.append(CyclingThread(cycling, self))
        if self.ltCCkb.isChecked():
            cycling = CyclePowerSupplies(CyclePowerSupplies.TRANSPORTE, CyclePowerSupplies.CORRETORAS)
            threads.append(CyclingThread(cycling, self))
        #Linac
        if self.liQCkB.isChecked():
            cycling = CyclePowerSupplies(CyclePowerSupplies.LINAC, CyclePowerSupplies.QUADRUPOLOS)
            threads.append(CyclingThread(cycling, self))
        if self.liCCkb.isChecked():
            cycling = CyclePowerSupplies(CyclePowerSupplies.LINAC, CyclePowerSupplies.CORRETORAS)
            threads.append(CyclingThread(cycling, self))


        for t in threads:
            t.start()


    def _createGroupBox(self, title, elements):
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
