#!/usr/bin/env python3.6
from pydm.PyQt.uic import loadUi
from pydm.PyQt.QtCore import pyqtSlot
from pydm.PyQt.QtGui import QMainWindow, QDialog, QVBoxLayout, QWidget, QLabel, QPixmap, QGraphicsPixmapItem, QFileDialog
from pydm import PyDMApplication
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import sys
import pyaccel as _pyaccel
import pymodels as _pymodels
# from siriusdm.as_ma_control.MagnetDetailWindow import MagnetDetailWindow
# from siriusdm.as_ma_control import ToBoosterMagnetControlWindow

CALC_LABELS_INITIALIZE = """
self.centralwidget.PyDMEnumComboBox_CalcMethod_Scrn{0}.currentIndexChanged.connect(self._visibility_handle)
"""

CALC_LABELS_VISIBILITY = """
self.centralwidget.PyDMLabel_Stats1CentroidX_Scrn{0}.setVisible(visible)
self.centralwidget.PyDMLabel_Stats2CentroidX_Scrn{0}.setVisible(not visible)
self.centralwidget.PyDMLabel_Stats1CentroidY_Scrn{0}.setVisible(visible)
self.centralwidget.PyDMLabel_Stats2CentroidY_Scrn{0}.setVisible(not visible)
self.centralwidget.PyDMLabel_Stats1Orientation_Scrn{0}.setVisible(visible)
self.centralwidget.PyDMLabel_Stats2Orientation_Scrn{0}.setVisible(not visible)
self.centralwidget.PyDMLabel_Stats1SigmaX_Scrn{0}.setVisible(visible)
self.centralwidget.PyDMLabel_Stats2SigmaX_Scrn{0}.setVisible(not visible)
self.centralwidget.PyDMLabel_Stats1SigmaY_Scrn{0}.setVisible(visible)
self.centralwidget.PyDMLabel_Stats2SigmaY_Scrn{0}.setVisible(not visible)
"""

class LTBControlWindow(QMainWindow):
    def __init__(self, parent=None):
        super(LTBControlWindow, self).__init__(parent)

        #TS Optics Widget
        self._tb,self._twiss_in = _pymodels.tb.create_accelerator()
        self._tb_twiss, *_ = _pyaccel.optics.calc_twiss(accelerator=self._tb,init_twiss=self._twiss_in)
        fam_data = _pymodels.tb.families.get_family_data(self._tb)
        fam_mapping = _pymodels.tb.family_mapping
        self._fig,self._ax = _pyaccel.graphics.plot_twiss(accelerator=self._tb,twiss=self._tb_twiss,
                                                            family_data=fam_data, family_mapping=fam_mapping,
                                                            draw_edges=True,height=4,show_label=True)
        self.centralwidget = loadUi('tb_ap_control.ui')
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.lattice_and_twiss_plot.canvas = FigureCanvas(self._fig)
        self.centralwidget.lattice_and_twiss_plot.canvas.setParent(self)
        self.centralwidget.lattice_and_twiss_plot.vbox = QVBoxLayout()
        self.centralwidget.lattice_and_twiss_plot.vbox.addWidget(self.centralwidget.lattice_and_twiss_plot.canvas)
        self.centralwidget.lattice_and_twiss_plot.setLayout(self.centralwidget.lattice_and_twiss_plot.vbox)


        #Set Visibility of Labels
        for i in [11, 12, 21, 22, 3, 4]:
            exec(CALC_LABELS_INITIALIZE.format(i))
            visible = True
            exec(CALC_LABELS_VISIBILITY.format(i))

        #Reference Widget
        self.centralwidget.tabWidget_Scrns.setCurrentIndex(0)
        self._currScrn = 0
        self.reference_window = ShowImage()
        self.centralwidget.tabWidget_Scrns.currentChanged.connect(self._setCurrentScrn)
        self.centralwidget.pushButton_SaveRef_Scrn11.clicked.connect(self._saveReference)
        self.centralwidget.pushButton_SaveRef_Scrn12.clicked.connect(self._saveReference)
        self.centralwidget.pushButton_SaveRef_Scrn21.clicked.connect(self._saveReference)
        self.centralwidget.pushButton_SaveRef_Scrn22.clicked.connect(self._saveReference)
        self.centralwidget.pushButton_SaveRef_Scrn3.clicked.connect(self._saveReference)
        self.centralwidget.pushButton_SaveRef_Scrn4.clicked.connect(self._saveReference)
        self.centralwidget.pushButton_OpenRef_Scrn11.clicked.connect(self._openReference)
        self.centralwidget.pushButton_OpenRef_Scrn12.clicked.connect(self._openReference)
        self.centralwidget.pushButton_OpenRef_Scrn21.clicked.connect(self._openReference)
        self.centralwidget.pushButton_OpenRef_Scrn22.clicked.connect(self._openReference)
        self.centralwidget.pushButton_OpenRef_Scrn3.clicked.connect(self._openReference)
        self.centralwidget.pushButton_OpenRef_Scrn4.clicked.connect(self._openReference)

        #Open Correctors Details
        self.centralwidget.toolButton_CH7App_Scrn11.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CV7App_Scrn11.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CH1App_Scrn12.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CV1App_Scrn12.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CV2App_Scrn21.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CH2App_Scrn21.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CH1App_Scrn22.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CV1App_Scrn22.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CH2App_Scrn3.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CV2App_Scrn3.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CHApp_Scrn4.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CV1App_Scrn4.clicked.connect(self._openWindow)

        #Open TSApps
        self.centralwidget.pushButton_LTB_MAApp.clicked.connect(self._openMAApp)
        self.centralwidget.pushButton_LTB_BPMApp.clicked.connect(self._openBPMApp)
        self.centralwidget.pushButton_FCTApp.clicked.connect(self._openFCTApp)
        self.centralwidget.pushButton_LTB_PosAngleCorrApp.clicked.connect(self._openPosAngleCorrApp)

        #Initialize Channels of each widget
        allwidgets = self.centralwidget.findChildren(QWidget)
        prefix = ""
        prop = ""
        for i in allwidgets:
            if i.objectName().startswith("PyDM"):
                name = i.objectName().split("_")

                if name[-1] in ("ICT1","ICT2","TransportEfficiency","HSlit","VSlit"):
                    pass
                    #TODO

                if len(name)-1 >= 2:
                    if name[2] in ("Kick", "Current"):
                        prop = name[2] + "-" + name[3]
                    elif name[2] in ("PwrState", "OpMode"):
                        prop = name[2] + "-Sts"

                if name[-1] == "Scrn11":
                    if name[1] == "CH7":
                        prefix = "LI-01:MA-CH-7:"
                    elif name[1] == "CV7":
                        prefix = "LI-01:MA-CV-7:"
                    elif name[1] in ("Position","Stats1","Stats2"):
                        pass
                        #TODO
                elif name[-1] == "Scrn12":
                    if name[1] == "CH1":
                        prefix = "TB-01:MA-CH-1:"
                    elif name[1] == "CV1":
                        prefix = "TB-01:MA-CV-1:"
                    elif name[1] in ("Position","Stats1","Stats2"):
                        pass
                        #TODO
                elif name[-1] == "Scrn21":
                    if name[1] == "CH2":
                        prefix = "TB-01:MA-CH-2:"
                    elif name[1] == "CV2":
                        prefix = "TB-01:MA-CV-2:"
                    elif name[1] in ("Position","Stats1","Stats2"):
                        pass
                        #TODO
                elif name[-1] == "Scrn22":
                    if name[1] == "CH1":
                        prefix = "TB-02:MA-CH-1:"
                    elif name[1] == "CV1":
                        prefix = "TB-02:MA-CV-1:"
                    elif name[1] in ("Position","Stats1","Stats2"):
                        pass
                        #TODO
                elif name[-1] == "Scrn3":
                    if name[1] == "CH2":
                        prefix = "TB-02:MA-CH-2:"
                    elif name[1] == "CV2":
                        prefix = "TB-02:MA-CV-2:"
                    elif name[1] in ("Position","Stats1","Stats2"):
                        pass
                        #TODO
                elif name[-1] == "Scrn4":
                    if name[1] == "CH":
                        prefix = "TB-03:MA-CH:"
                    elif name[1] == "CV1":
                        prefix = "TB-04:MA-CV-1:"
                    elif name[1] in ("Position","Stats1","Stats2"):
                        pass
                        #TODO
                if prefix != "":
                    i.channel = "ca://" + prefix + prop
                    # print(i.channel)
                prefix = ""
                prop = ""

    @pyqtSlot(int)
    def _visibility_handle(self,index):
        if index == 0:  visible = True
        else:           visible = False

        if self._currScrn == 0:     scrn = 11
        elif self._currScrn == 1:   scrn = 12
        elif self._currScrn == 2:   scrn = 21
        elif self._currScrn == 3:   scrn = 22
        elif self._currScrn == 4:   scrn = 3
        elif self._currScrn == 5:   scrn = 4

        exec(CALC_LABELS_VISIBILITY.format(scrn))

    @pyqtSlot(int)
    def _setCurrentScrn(self,currScrn):
        self._currScrn = currScrn

    def _openReference(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Open Reference...", None,
                "Images (*.png *.xpm *.jpg);;All Files (*)")
        if fn:
            self.reference_window.load_image(fn)
            self.reference_window.show()

    def _saveReference(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Save Reference As...", None,
                "Images (*.png *.xpm *.jpg);;All Files (*)")
        if not fn: return False
        lfn = fn.lower()
        if not lfn.endswith(('.png', '.jpg', '.xpm')): fn += '.png'

        if self._currScrn == 0:
            self.centralwidget.widget_Ref_Scrn11.setVisible(False)
            reference = self.centralwidget.widget_Scrn11.grab()
            self.centralwidget.widget_Ref_Scrn11.setVisible(True)
        elif self._currScrn == 1:
            self.centralwidget.widget_Ref_Scrn12.setVisible(False)
            reference = self.centralwidget.widget_Scrn12.grab()
            self.centralwidget.widget_Ref_Scrn12.setVisible(True)
        elif self._currScrn == 2:
            self.centralwidget.widget_Ref_Scrn21.setVisible(False)
            reference = self.centralwidget.widget_Scrn21.grab()
            self.centralwidget.widget_Ref_Scrn21.setVisible(True)
        elif self._currScrn == 3:
            self.centralwidget.widget_Ref_Scrn22.setVisible(False)
            reference = self.centralwidget.widget_Scrn22.grab()
            self.centralwidget.widget_Ref_Scrn22.setVisible(True)
        elif self._currScrn == 4:
            self.centralwidget.widget_Ref_Scrn3.setVisible(False)
            reference = self.centralwidget.widget_Scrn3.grab()
            self.centralwidget.widget_Ref_Scrn3.setVisible(True)
        elif self._currScrn == 5:
            self.centralwidget.widget_Ref_Scrn4.setVisible(False)
            reference = self.centralwidget.widget_Scrn4.grab()
            self.centralwidget.widget_Ref_Scrn4.setVisible(True)
        reference.save(fn)

    def _openWindow(self):
        sender = self.sender()
        if sender.objectName() == "toolButton_CH7App_Scrn11":   ma = "LI-01:MA-CH-7"
        elif sender.objectName() == "toolButton_CV7App_Scrn11": ma = "LI-01:MA-CV-7"
        elif sender.objectName() == "toolButton_CH1App_Scrn12": ma = "TB-01:MA-CH-1"
        elif sender.objectName() == "toolButton_CV1App_Scrn12": ma = "TB-01:MA-CV-1"
        elif sender.objectName() == "toolButton_CH2App_Scrn21": ma = "TB-01:MA-CH-2"
        elif sender.objectName() == "toolButton_CV2App_Scrn21": ma = "TB-01:MA-CV-2"
        elif sender.objectName() == "toolButton_CH1App_Scrn22": ma = "TB-02:MA-CH-1"
        elif sender.objectName() == "toolButton_CV1App_Scrn22": ma = "TB-02:MA-CV-1"
        elif sender.objectName() == "toolButton_CH2App_Scrn3":  ma = "TB-02:MA-CH-2"
        elif sender.objectName() == "toolButton_CV2App_Scrn3":  ma = "TB-02:MA-CV-2"
        elif sender.objectName() == "toolButton_CHApp_Scrn4":   ma = "TB-03:MA-CH"
        elif sender.objectName() == "toolButton_CV1App_Scrn4":  ma = "TB-04:MA-CV-1"

        # self._corrector_detail_window = MagnetDetailWindow(ma,self)
        # self._corrector_detail_window.show()

    def _openMAApp(self):
        pass
        # self._LTB_MA_window = ToBoosterMagnetControlWindow(self)
        # self._LTB_MA_window.show()

    def _openBPMApp(self):
        pass
        #TODO

    def _openFCTApp(self):
        pass
        #TODO

    def _openPosAngleCorrApp(self):
        pass
        #TODO

class ShowImage(QWidget):
    def __init__(self, parent=None):
        super(ShowImage, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.label = QLabel()
        self.layout().addWidget(self.label)

    def load_image(self,filename):
        self.setWindowTitle(filename)
        self.pixmap = QPixmap(filename)
        self.label.setPixmap(self.pixmap)
        self.setGeometry(300,300,self.pixmap.width(),self.pixmap.height())

app = PyDMApplication(None, sys.argv)
window = LTBControlWindow()
window.show()
sys.exit(app.exec_())
