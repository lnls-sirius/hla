from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QSizePolicy, QSpacerItem
from pydm import PyDMApplication
from pydm.widgets.checkbox import PyDMCheckbox
from pydm.widgets.led import PyDMLed
import sys

subsections = ('M1', 'M2', 'C1-1', 'C1-2', 'C2', 'C3-1', 'C3-2', 'C4')
dev = 'BPMX'
indices = list(range(1,20*len(subsections)+1))

def main():
    app = PyDMApplication()
    #app = QApplication([])
    #main_win = QMainWindow()
    #uii = Ui_MainWindow()
    #uii.setupUi(main_win)
    main_win = uic.loadUi('main_window.ui')
    wid = main_win.tab_2
    gl = QGridLayout(wid)
    vl = mk_matrix(wid,subsections,dev,indices)
    gl.addItem(vl,0,0)
    vspace = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
    gl.addItem(vl,1,0)
    main_win.show()
    sys.exit(app.exec_())

def mk_matrix(parent,subsections,dev,indices):
    len_ = len(subsections)
    sections = ['{0:02d}'.format(i) for i in range(1,21)]
    vl = QVBoxLayout()
    wid = mk_line(parent, '00', subsections, dev, list(range(len_)), True)
    vl.addWidget(wid)
    for i,section in enumerate(sections):
        wid = mk_line(parent, section, subsections, dev, indices[i*len_:(i+1)*len_], False)
        vl.addWidget(wid)
    return vl

def mk_line(parent, section, subsections, dev, indices, header):
    label = section+dev
    wid = QWidget(parent)
    if int(section) % 2:
        wid.setStyleSheet('background-color: rgb(220, 220, 220);')
    wid.setObjectName('Wid_'+label)
    hl = QHBoxLayout(wid)
    hl.setObjectName('HL_'+label)
    hspace = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
    hl.addItem(hspace)
    lab = QLabel(wid)
    lab.setObjectName('LB_'+label)
    lab.setText('  ' if header else section)
    hl.addWidget(lab)
    hspace = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
    hl.addItem(hspace)
    for subsection, index in zip(subsections, indices):
        if header:
            lab = QLabel(wid)
            lab.setObjectName('LB_'+dev+subsection)
            lab.setText(subsection)
            hl.addWidget(lab)
        else:
            subhl = mk_unit(wid, section, subsection, dev, index)
            hl.addLayout(subhl)
        hspace = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hl.addItem(hspace)
    return wid

def mk_unit(parent, section, subsection, dev, index):
    label = dev+section+subsection
    hl = QHBoxLayout()
    hl.setObjectName('HL_'+label)
    cb = PyDMCheckbox(parent)
    cb.setObjectName('PyDMCB_'+label)
    cb.channel = 'ca://'+dev+'EnblList-SP'
    cb.pvbit   = index
    hl.addWidget(cb)
    led = PyDMLed(parent)
    led.setObjectName('PyDMLed_'+label)
    led.channel = 'ca://'+dev+'EnblList-RB'
    led.pvbit   = index
    hl.addWidget(led)
    return hl

#    QtCore.QMetaObject.connectSlotsByName(Form)
if __name__ == '__main__':
    main()
