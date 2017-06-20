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
from siriusdm.as_ma_control.MagnetDetailWindow import MagnetDetailWindow
from siriusdm.as_ma_control import ToSiriusMagnetControlWindow

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

class TSControlWindow(QMainWindow):
    def __init__(self, parent=None):
        super(TSControl, self).__init__(parent)

        #TS Optics Widget
        self._ts,self._twiss_in = _pymodels.ts.create_accelerator()
        self._ts_twiss, *_ = _pyaccel.optics.calc_twiss(accelerator=self._ts,init_twiss=self._twiss_in)
        fam_data = _pymodels.ts.families.get_family_data(self._ts)
        fam_mapping = _pymodels.ts.family_mapping
        self._fig,self._ax = _pyaccel.graphics.plot_twiss(accelerator=self._ts,twiss=self._ts_twiss,
                                                            family_data=fam_data, family_mapping=fam_mapping,
                                                            draw_edges=True,height=4,show_label=True)
        self.centralwidget = loadUi('ts_ap_control.ui')
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.lattice_and_twiss_plot.canvas = FigureCanvas(self._fig)
        self.centralwidget.lattice_and_twiss_plot.canvas.setParent(self)
        self.centralwidget.lattice_and_twiss_plot.vbox = QVBoxLayout()
        self.centralwidget.lattice_and_twiss_plot.vbox.addWidget(self.centralwidget.lattice_and_twiss_plot.canvas)
        self.centralwidget.lattice_and_twiss_plot.setLayout(self.centralwidget.lattice_and_twiss_plot.vbox)


        #Set Visibility of Labels
        for i in [1, 2, 3, 41, 42, 43]:
            exec(CALC_LABELS_INITIALIZE.format(i))
            visible = True
            exec(CALC_LABELS_VISIBILITY.format(i))

        #Reference Widget
        self._currScrn = 0
        self.reference_window = ShowImage()
        self.centralwidget.tabWidget_Scrns.currentChanged.connect(self._setCurrentScrn)
        self.centralwidget.pushButton_SaveRef_Scrn1.clicked.connect(self._saveReference)
        self.centralwidget.pushButton_SaveRef_Scrn2.clicked.connect(self._saveReference)
        self.centralwidget.pushButton_SaveRef_Scrn3.clicked.connect(self._saveReference)
        self.centralwidget.pushButton_SaveRef_Scrn41.clicked.connect(self._saveReference)
        self.centralwidget.pushButton_SaveRef_Scrn42.clicked.connect(self._saveReference)
        self.centralwidget.pushButton_SaveRef_Scrn43.clicked.connect(self._saveReference)
        self.centralwidget.pushButton_OpenRef_Scrn1.clicked.connect(self._openReference)
        self.centralwidget.pushButton_OpenRef_Scrn2.clicked.connect(self._openReference)
        self.centralwidget.pushButton_OpenRef_Scrn3.clicked.connect(self._openReference)
        self.centralwidget.pushButton_OpenRef_Scrn41.clicked.connect(self._openReference)
        self.centralwidget.pushButton_OpenRef_Scrn42.clicked.connect(self._openReference)
        self.centralwidget.pushButton_OpenRef_Scrn43.clicked.connect(self._openReference)

        #Open Correctors Details
        self.centralwidget.toolButton_CV1App_Scrn1.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CHApp_Scrn2.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CV2App_Scrn2.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CHApp_Scrn3.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CVApp_Scrn3.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CHApp_Scrn41.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CVApp_Scrn41.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CV1App_Scrn42.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CHApp_Scrn42.clicked.connect(self._openWindow)
        self.centralwidget.toolButton_CV2App_Scrn43.clicked.connect(self._openWindow)

        #Open TSApps
        self.centralwidget.pushButton_TSPSApp.clicked.connect(self._openTSPSApp)
        self.centralwidget.pushButton_TSBPMApp.clicked.connect(self._openTSBPMApp)
        self.centralwidget.pushButton_FCTApp.clicked.connect(self._openFCTApp)

        #Initialize Channels of each widget
        allwidgets = self.centralwidget.findChildren(QWidget)
        prefix = ""
        prop = ""
        for i in allwidgets:
            if i.objectName().startswith("PyDM"):
                name = i.objectName().split("_")

                if name[-1] in ("ICT1","ICT2","TransportEfficiancy"):
                    pass
                    #TODO

                if len(name)-1 >= 2:
                    if name[2] in ("Kick", "Current"):
                        prop = name[2] + "-" + name[3]
                    elif name[2] in ("PwrState", "OpMode"):
                        prop = name[2] + "-Sts"

                if name[-1] == "Scrn1":
                    if name[1] == "CV1":
                        prefix = "TS-01:MA-CV-1:"
                    elif name[1] in ("Position","Stats1","Stats2"):
                        pass
                        #TODO
                elif name[-1] == "Scrn2":
                    if name[1] == "CH":
                        prefix = "TS-01:MA-CH:"
                    elif name[1] == "CV2":
                        prefix = "TS-01:MA-CV-2:"
                    elif name[1] in ("Position","Stats1","Stats2"):
                        pass
                        #TODO
                elif name[-1] == "Scrn3":
                    if name[1] == "CH":
                        prefix = "TS-02:MA-CH:"
                    elif name[1] == "CV":
                        prefix = "TS-02:MA-CV:"
                    elif name[1] in ("Position","Stats1","Stats2"):
                        pass
                        #TODO
                elif name[-1] == "Scrn41":
                    if name[1] == "CH":
                        prefix = "TS-03:MA-CH:"
                    elif name[1] == "CV":
                        prefix = "TS-03:MA-CV:"
                    elif name[1] in ("Position","Stats1","Stats2"):
                        pass
                        #TODO
                elif name[-1] == "Scrn42":
                    if name[1] == "CH":
                        prefix = "TS-04:MA-CH:"
                    elif name[1] == "CV1":
                        prefix = "TS-04:MA-CV-1:"
                    elif name[1] in ("Position","Stats1","Stats2"):
                        pass
                        #TODO
                elif name[-1] == "Scrn43":
                    if name[1] == "CV2":
                        prefix = "TS-04:MA-CV-2:"
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

        if self._currScrn == 0:     scrn = 1
        elif self._currScrn == 1:   scrn = 2
        elif self._currScrn == 2:   scrn = 3
        elif self._currScrn == 3:   scrn = 41
        elif self._currScrn == 4:   scrn = 42
        elif self._currScrn == 5:   scrn = 43

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
            self.centralwidget.widget_Ref_Scrn1.setVisible(False)
            reference = self.centralwidget.widget_Scrn1.grab()
            self.centralwidget.widget_Ref_Scrn1.setVisible(True)
        elif self._currScrn == 1:
            self.centralwidget.widget_Ref_Scrn2.setVisible(False)
            reference = self.centralwidget.widget_Scrn2.grab()
            self.centralwidget.widget_Ref_Scrn2.setVisible(True)
        elif self._currScrn == 2:
            self.centralwidget.widget_Ref_Scrn3.setVisible(False)
            reference = self.centralwidget.widget_Scrn3.grab()
            self.centralwidget.widget_Ref_Scrn3.setVisible(True)
        elif self._currScrn == 3:
            self.centralwidget.widget_Ref_Scrn41.setVisible(False)
            reference = self.centralwidget.widget_Scrn41.grab()
            self.centralwidget.widget_Ref_Scrn41.setVisible(True)
        elif self._currScrn == 4:
            self.centralwidget.widget_Ref_Scrn42.setVisible(False)
            reference = self.centralwidget.widget_Scrn42.grab()
            self.centralwidget.widget_Ref_Scrn42.setVisible(True)
        elif self._currScrn == 5:
            self.centralwidget.widget_Ref_Scrn43.setVisible(False)
            reference = self.centralwidget.widget_Scrn43.grab()
            self.centralwidget.widget_Ref_Scrn43.setVisible(True)
        reference.save(fn)

    def _openWindow(self):
        sender = self.sender()
        if sender.objectName() == "toolButton_CV1App_Scrn1":    ma = "TS-01:MA-CV-1"
        elif sender.objectName() == "toolButton_CHApp_Scrn2":   ma = "TS-01:MA-CH"
        elif sender.objectName() == "toolButton_CV2App_Scrn2":  ma = "TS-01:MA-CV-2"
        elif sender.objectName() == "toolButton_CHApp_Scrn3":   ma = "TS-02:MA-CH"
        elif sender.objectName() == "toolButton_CVApp_Scrn3":   ma = "TS-02:MA-CV"
        elif sender.objectName() == "toolButton_CHApp_Scrn41":  ma = "TS-03:MA-CH"
        elif sender.objectName() == "toolButton_CVApp_Scrn41":  ma = "TS-03:MA-CV"
        elif sender.objectName() == "toolButton_CV1App_Scrn42": ma = "TS-04:MA-CV-1"
        elif sender.objectName() == "toolButton_CHApp_Scrn42":  ma = "TS-04:MA-CH"
        elif sender.objectName() == "toolButton_CV2App_Scrn43": ma = "TS-04:MA-CV-2"

        self._corrector_detail_window = MagnetDetailWindow(ma,self)
        self._corrector_detail_window.show()

    def _openTSPSApp(self):
        self._TSPS_window = ToSiriusMagnetControlWindow(self)
        self._TSPS_window.show()

    def _openTSBPMApp(self):
        pass
        #TODO

    def _openFCTApp(self):
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
window = TSControlWindow()
window.show()
sys.exit(app.exec_())
