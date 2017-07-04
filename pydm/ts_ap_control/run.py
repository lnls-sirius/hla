#!/usr/bin/env python3.6
from pydm.PyQt.uic import loadUi
from pydm.PyQt.QtCore import pyqtSlot, Qt
from pydm.PyQt.QtGui import (QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog, QSizePolicy, QDoubleValidator,
                            QWidget, QFrame, QScrollArea, QLabel, QPixmap, QPushButton, QSpacerItem)
from pydm import PyDMApplication
from pydm.widgets.led import PyDMLed
from pydm.widgets.label import PyDMLabel
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.scrollbar import PyDMScrollBar
from pydm.widgets.enum_combo_box import PyDMEnumComboBox
from pydm.widgets.checkbox import PyDMCheckbox
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from pydm.PyQt.QtSvg import QSvgWidget
import sys
import pyaccel as _pyaccel
import pymodels as _pymodels
# from siriusdm.as_ma_control.MagnetDetailWindow import MagnetDetailWindow
# from siriusdm.as_ma_control import ToSiriusMagnetControlWindow

CALC_LABELS_INITIALIZE = '''
self.centralwidget.PyDMEnumComboBox_CalcMethod_Scrn{0}.currentIndexChanged.connect(self._visibility_handle)
'''

CALC_LABELS_VISIBILITY = '''
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
'''

class BTSControlWindow(QMainWindow):
    def __init__(self, parent=None):
        super(BTSControlWindow, self).__init__(parent)
        self.centralwidget = loadUi('ts_ap_control.ui')
        self.setCentralWidget(self.centralwidget)

        #TS Lattice Widget
        lattice = QSvgWidget('devnames-TS.svg')
        self.centralwidget.widget_lattice.setLayout(QVBoxLayout())
        self.centralwidget.widget_lattice.layout().addWidget(lattice)

        #TS Optics Widget
        self.lattice_and_twiss_window = ShowLatticeAndTwiss()
        self.centralwidget.pushButton_LatticeAndTwiss.clicked.connect(self._openLaticeAndTwiss)

        #Set Visibility of Scrn Calculations Labels
        for i in [1, 2, 3, 41, 42, 43]:
            exec(CALC_LABELS_INITIALIZE.format(i))
            visible = True
            exec(CALC_LABELS_VISIBILITY.format(i))

        #Reference Widget
        self.centralwidget.tabWidget_Scrns.setCurrentIndex(0)
        self._currScrn = 0
        self.reference_window = ShowImage()
        self.centralwidget.tabWidget_Scrns.currentChanged.connect(self._setCurrentScrn)
        self.centralwidget.pushButton_SaveRef.clicked.connect(self._saveReference)
        self.centralwidget.pushButton_OpenRef.clicked.connect(self._openReference)

        #Open BTSApps
        self.centralwidget.pushButton_BTS_MAApp.clicked.connect(self._openMAApp)
        self.centralwidget.pushButton_BTS_BPMApp.clicked.connect(self._openBPMApp)
        self.centralwidget.pushButton_FCTApp.clicked.connect(self._openFCTApp)
        self.centralwidget.pushButton_BTS_PosAngleCorrApp.clicked.connect(self._openPosAngleCorrApp)

        #Create Scrn+Correctors Panel
        scrn_headerline = QWidget()
        scrn_headerline.setLayout(QHBoxLayout())
        label_scrn = QLabel('Scrn')
        label_position = QLabel('Position')
        label_lamp = QLabel('Lamp')
        scrn_headerline.layout().addWidget(label_scrn)
        scrn_headerline.layout().addWidget(label_position)
        scrn_headerline.layout().addWidget(label_lamp)
        scrn_headerline.layout().setContentsMargins(0,0,0,0)
        # scrn_headerline.setStyleSheet('''QLabel{background-color:blue;}''')

        ch_headerline = QWidget()
        ch_headerline.setLayout(QHBoxLayout())
        label_ch_led = QLabel('')
        label_ch = QLabel('CH')
        label_ch.setStyleSheet("""font-size:16pt""")
        # label_ch_sp_ctrlvar = QLabel('PS SP')
        # label_ch_rb_ctrlvar = QLabel('PS RB')
        label_ch_sp_kick = QLabel('Kick SP')
        label_ch_rb_kick = QLabel('Kick RB')
        ch_headerline.layout().addWidget(label_ch_led)
        ch_headerline.layout().addWidget(label_ch)
        # ch_headerline.layout().addWidget(label_ch_sp_ctrlvar)
        # ch_headerline.layout().addWidget(label_ch_rb_ctrlvar)
        ch_headerline.layout().addWidget(label_ch_sp_kick)
        ch_headerline.layout().addWidget(label_ch_rb_kick)
        ch_headerline.layout().setContentsMargins(0,0,0,0)
        # ch_headerline.setStyleSheet('''QLabel{background-color:blue;}''')

        cv_headerline = QWidget()
        cv_headerline.setLayout(QHBoxLayout())
        label_cv_led = QLabel('')
        label_cv = QLabel('CV')
        label_cv.setStyleSheet("""font-size:16pt""")
        # label_cv_sp_ctrlvar = QLabel('PS SP')
        # label_cv_rb_ctrlvar = QLabel('PS RB')
        label_cv_sp_kick = QLabel('Kick SP')
        label_cv_rb_kick = QLabel('Kick RB')
        cv_headerline.layout().addWidget(label_cv_led)
        cv_headerline.layout().addWidget(label_cv)
        # cv_headerline.layout().addWidget(label_cv_sp_ctrlvar)
        # cv_headerline.layout().addWidget(label_cv_rb_ctrlvar)
        cv_headerline.layout().addWidget(label_cv_sp_kick)
        cv_headerline.layout().addWidget(label_cv_rb_kick)
        cv_headerline.layout().setContentsMargins(0,0,0,0)
        # cv_headerline.setStyleSheet('''QLabel{background-color:blue;}''')

        headerline = QWidget()
        headerline.setMaximumHeight(40)
        headerline.setLayout(QHBoxLayout())
        headerline.layout().addWidget(scrn_headerline)
        headerline.layout().addItem(QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum))
        headerline.layout().addWidget(ch_headerline)
        headerline.layout().addItem(QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum))
        headerline.layout().addWidget(cv_headerline)
        headerline.setStyleSheet("""font-weight:bold;text-align:center;""")
        correctors_gridlayout = QGridLayout()
        correctors_gridlayout.addWidget(headerline,1,1)
        line = 2
        for ch_group,cv,scrn,scrnpv in [[['01:PM-EjeSF','01:PM-EjeSG'],'01:MA-CV-1',1,'01:DI-Scrn'],\
                                        [['01:MA-CH'],'01:MA-CV-2',2,'02:DI-Scrn'],\
                                        [['02:MA-CH'],'02:MA-CV',3,'03:DI-Scrn'],\
                                        [['02:MA-CH'],'03:MA-CV',41,'04:DI-Scrn-1'],\
                                        [['04:MA-CH'],'04:MA-CV-1',42,'04:DI-Scrn-2'],\
                                        [['04:PM-InjSG-1','04:PM-InjSG-2','04:PM-InjSF'],'04:MA-CV-2',43,'04:DI-Scrn-3']]:
            #Scrn
            scrn_details = QWidget()
            scrn_details.setObjectName('widget_Scrn' + str(scrn))
            scrn_details.setLayout(QHBoxLayout())

            scrn_label = QLabel(scrnpv)
            scrn_label.setMinimumWidth(100)
            scrn_label.setStyleSheet("""font-weight:bold;""")
            scrn_details.layout().addWidget(scrn_label)

            widget_position_sp = QWidget()
            widget_position_sp.setLayout(QVBoxLayout())
            widget_position_sp.layout().setContentsMargins(0,0,0,0)
            pydmcombobox = PyDMEnumComboBox(scrn_details,'ca://TS-' + scrnpv + ':Position-SP')
            pydmcombobox.setObjectName('PyDMEnumComboBox_Position_SP_Scrn' + str(scrn))
            pydmcombobox.setMinimumWidth(80)
            widget_position_sp.layout().addWidget(pydmcombobox)
            pydmlabel_position = PyDMLabel(scrn_details, 'ca://TS-' + scrnpv + ':Position-RB')
            pydmlabel_position.setObjectName('PyDMLabel_Position_RB_Scrn' + str(scrn))
            pydmlabel_position.setPrecision(3)
            pydmlabel_position.setMinimumWidth(80)
            frame_label = QFrame()
            frame_label.setFrameShadow(QFrame.Raised)
            frame_label.setFrameShape(QFrame.Box)
            frame_label.setLayout(QVBoxLayout())
            frame_label.layout().setContentsMargins(3,3,3,3)
            frame_label.setMinimumHeight(28)
            frame_label.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
            frame_label.layout().addWidget(pydmlabel_position)
            widget_position_sp.layout().addWidget(frame_label)
            widget_position_sp.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
            scrn_details.layout().addWidget(widget_position_sp)

            scrn_details.layout().addItem(QSpacerItem(40,20,QSizePolicy.Fixed,QSizePolicy.Minimum))

            pydmcheckbox = PyDMCheckbox(scrn_details, 'ca://TS-' + scrnpv + ':LampState-SP')
            pydmcheckbox.setObjectName('PyDMCheckbox_LampState_SP_Scrn' + str(scrn))
            pydmcheckbox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
            scrn_details.layout().addWidget(pydmcheckbox)

            pydmled = PyDMLed(scrn_details,'ca://TS-' + scrnpv + ':LampState-Sts')
            pydmled.setObjectName('PyDMLed_LampState_Sts_Scrn' + str(scrn))
            pydmled.setMinimumWidth(24)
            scrn_details.layout().addWidget(pydmled)

            scrn_details.layout().addItem(QSpacerItem(40,20,QSizePolicy.Fixed,QSizePolicy.Minimum))

            #CH
            ch_widget = QWidget()
            ch_widget.setObjectName('widget_CHs_Scrn' + str(scrn))
            ch_widget.setLayout(QVBoxLayout())
            ch_widget.layout().setContentsMargins(0,0,0,0)

            for ch in ch_group:
                name = ch.split('-')
                if len(name) > 3:
                    name = name[-2]+name[-1]
                else:
                    name = name[-1]

                if scrn in (1,43):
                    ctrlvar = 'Voltage'
                else:
                    ctrlvar = 'Current'

                ch_details = QWidget()
                ch_details.setObjectName('widget_details_' + name + '_Scrn' + str(scrn))
                ch_details.setLayout(QGridLayout())
                ch_details.layout().setContentsMargins(3,3,3,3)

                pydmled = PyDMLed(ch_details,'ca://TS-' + ch + ':PwrState-Sts')
                pydmled.setObjectName('PyDMLed_' + name + '_PwrState' + '_Scrn' + str(scrn))
                pydmled.setMinimumWidth(24)
                pydmled.setMinimumHeight(24)
                ch_details.layout().addWidget(pydmled,1,1)

                pushbutton = QPushButton(ch, ch_details)
                pushbutton.setObjectName('pushButton_' + name + 'App_Scrn' + str(scrn))
                pushbutton.clicked.connect(self._openWindow)
                pushbutton.setMinimumWidth(100)
                pushbutton.setMinimumHeight(24)
                ch_details.layout().addWidget(pushbutton,1,2)

                # pydmlineedit_ctrlvar = PyDMLineEdit(ch_details, 'ca://TS-' + ch + ':' + ctrlvar + '-SP')
                # pydmlineedit_ctrlvar.setObjectName('PyDMLineEdit_' + name + ctrlvar + '_SP' + '_Scrn' + str(scrn))
                # pydmlineedit_ctrlvar.receivePrecision(3)
                # pydmlineedit_ctrlvar.setValidator(QDoubleValidator())
                # pydmlineedit_ctrlvar._useunits = False
                # pydmlineedit_ctrlvar.setMinimumWidth(80)
                # ch_details.layout().addWidget(pydmlineedit_ctrlvar,1,3)
                #
                # scrollbar_ctrlvar = PyDMScrollBar(ch_details, Qt.Horizontal, 'ca://TS-' + ch + ':' + ctrlvar + '-SP')
                # scrollbar_ctrlvar.setObjectName('PyDMScrollBar_' + name + ctrlvar + '_SP' + '_Scrn' + str(scrn))
                # scrollbar_ctrlvar.setMinimumWidth(80)
                # ch_details.layout().addWidget(scrollbar_ctrlvar,2,3)
                #
                # pydmlabel_ctrlvar = PyDMLabel(ch_details, 'ca://TS-' + ch + ':' + ctrlvar + '-RB')
                # pydmlabel_ctrlvar.setObjectName('PyDMLabel_' + name + ctrlvar + '_RB' + '_Scrn' + str(scrn))
                # pydmlabel_ctrlvar.setPrecision(3)
                # pydmlabel_ctrlvar.setMinimumWidth(80)
                # ch_details.layout().addWidget(pydmlabel_ctrlvar,1,4)

                pydmlineedit_kick = PyDMLineEdit(ch_details, 'ca://TS-' + ch + ':Kick-SP')
                pydmlineedit_kick.setObjectName('PyDMLineEdit' + name + '_Kick_SP_Scrn' + str(scrn))
                pydmlineedit_kick.receivePrecision(3)
                pydmlineedit_kick.setValidator(QDoubleValidator())
                pydmlineedit_kick._useunits = False
                pydmlineedit_kick.setMinimumWidth(80)
                pydmlineedit_kick.setMinimumHeight(24)
                ch_details.layout().addWidget(pydmlineedit_kick,1,5)

                scrollbar_kick = PyDMScrollBar(ch_details, Qt.Horizontal, 'ca://TS-' + ch + ':Kick-SP')
                scrollbar_kick.setObjectName('PyDMScrollBar' + name + '_Kick_SP_Scrn' + str(scrn))
                scrollbar_kick.setMinimumWidth(80)
                ch_details.layout().addWidget(scrollbar_kick,2,5)

                pydmlabel_kick = PyDMLabel(ch_details, 'ca://TS-' + ch + ':Kick-RB')
                pydmlabel_kick.setObjectName('PyDMLabel_' + name + '_Kick_RB_Scrn' + str(scrn))
                pydmlabel_kick.setPrecision(3)
                pydmlabel_kick.setMinimumWidth(80)
                pydmlabel_kick.setMinimumHeight(24)
                frame_label = QFrame()
                frame_label.setFrameShadow(QFrame.Raised)
                frame_label.setFrameShape(QFrame.Box)
                frame_label.setLayout(QVBoxLayout())
                frame_label.layout().setContentsMargins(3,3,3,3)
                frame_label.setMinimumHeight(28)
                frame_label.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
                frame_label.layout().addWidget(pydmlabel_kick)
                ch_details.layout().addWidget(frame_label,1,6)
                ch_details.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
                ch_widget.layout().addWidget(ch_details)

            #CV
            name = cv.split('-')
            if len(name) > 3:
                name = name[-2]+name[-1]
            else:
                name = name[-1]

            ctrlvar = 'Current'

            cv_details = QWidget()
            cv_details.setObjectName('widget_details_' + name + '_Scrn' + str(scrn))
            cv_details.setLayout(QGridLayout())
            cv_details.layout().setContentsMargins(2,2,2,2)

            pydmled = PyDMLed(cv_details,'ca://TS-' + cv + ':PwrState-Sts')
            pydmled.setObjectName('PyDMLed_' + name + '_PwrState' + '_Scrn' + str(scrn))
            pydmled.setMinimumWidth(24)
            cv_details.layout().addWidget(pydmled,1,1)

            pushbutton = QPushButton(cv, cv_details)
            pushbutton.setObjectName('pushButton_' + name + 'App_Scrn' + str(scrn))
            pushbutton.clicked.connect(self._openWindow)
            pushbutton.setMinimumWidth(100)
            pushbutton.setMinimumHeight(24)
            cv_details.layout().addWidget(pushbutton,1,2)

            # pydmlineedit_ctrlvar = PyDMLineEdit(cv_details, 'ca://TS-' + cv + ':' + ctrlvar + '-SP')
            # pydmlineedit_ctrlvar.setObjectName('PyDMLineEdit_' + name + ctrlvar + '_SP' + '_Scrn' + str(scrn))
            # pydmlineedit_ctrlvar.receivePrecision(3)
            # pydmlineedit_ctrlvar.setValidator(QDoubleValidator())
            # pydmlineedit_ctrlvar._useunits = False
            # pydmlineedit_ctrlvar.setMinimumWidth(80)
            # pydmlineedit_ctrlvar.setMinimumHeight(24)
            # cv_details.layout().addWidget(pydmlineedit_ctrlvar,1,3)
            #
            # scrollbar_ctrlvar = PyDMScrollBar(cv_details, Qt.Horizontal, 'ca://TS-' + cv + ':' + ctrlvar + '-SP')
            # scrollbar_ctrlvar.setObjectName('PyDMScrollBar_' + name + ctrlvar + '_SP' + '_Scrn' + str(scrn))
            # scrollbar_ctrlvar.setMinimumWidth(80)
            # cv_details.layout().addWidget(scrollbar_ctrlvar,2,3)
            #
            # pydmlabel_ctrlvar = PyDMLabel(cv_details, 'ca://TS-' + cv + ':' + ctrlvar + '-RB')
            # pydmlabel_ctrlvar.setObjectName('PyDMLabel_' + name + ctrlvar + '_RB' + '_Scrn' + str(scrn))
            # pydmlabel_ctrlvar.setPrecision(3)
            # pydmlabel_ctrlvar.setMinimumWidth(80)
            # pydmlabel_ctrlvar.setMinimumHeight(24)
            # cv_details.layout().addWidget(pydmlabel_ctrlvar,1,4)

            pydmlineedit_kick = PyDMLineEdit(cv_details, 'ca://TS-' + cv + ':Kick-SP')
            pydmlineedit_kick.setObjectName('PyDMLineEdit' + name + '_Kick_SP_Scrn' + str(scrn))
            pydmlineedit_kick.receivePrecision(3)
            pydmlineedit_kick.setValidator(QDoubleValidator())
            pydmlineedit_kick._useunits = False
            pydmlineedit_kick.setMinimumWidth(80)
            pydmlineedit_kick.setMinimumHeight(24)
            cv_details.layout().addWidget(pydmlineedit_kick,1,5)

            scrollbar_kick = PyDMScrollBar(cv_details, Qt.Horizontal, 'ca://TS-' + cv + ':Kick-SP')
            scrollbar_kick.setObjectName('PyDMScrollBar' + name + '_Kick_SP_Scrn' + str(scrn))
            scrollbar_kick.setMinimumWidth(80)
            cv_details.layout().addWidget(scrollbar_kick,2,5)

            pydmlabel_kick = PyDMLabel(cv_details, 'ca://TS-' + cv + ':Kick-RB')
            pydmlabel_kick.setObjectName('PyDMLabel_' + name + '_Kick_RB_Scrn' + str(scrn))
            pydmlabel_kick.setPrecision(3)
            pydmlabel_kick.setMinimumWidth(80)
            pydmlabel_kick.setMinimumHeight(24)
            frame_label = QFrame()
            frame_label.setFrameShadow(QFrame.Raised)
            frame_label.setFrameShape(QFrame.Box)
            frame_label.setLayout(QVBoxLayout())
            frame_label.layout().setContentsMargins(3,3,3,3)
            frame_label.setMinimumHeight(28)
            frame_label.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
            frame_label.layout().addWidget(pydmlabel_kick)
            cv_details.layout().addWidget(frame_label,1,6)
            cv_details.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)

            widget_scrncorr = QWidget()
            widget_scrncorr.setLayout(QHBoxLayout())
            widget_scrncorr.layout().addWidget(scrn_details)
            widget_scrncorr.layout().addItem(QSpacerItem(40,20,QSizePolicy.Fixed,QSizePolicy.Minimum))
            widget_scrncorr.layout().addWidget(ch_widget)
            widget_scrncorr.layout().addItem(QSpacerItem(40,20,QSizePolicy.Fixed,QSizePolicy.Minimum))
            widget_scrncorr.layout().addWidget(cv_details)
            widget_scrncorr.layout().setContentsMargins(2,2,2,2)

            if line%2 == 0:
                widget_scrncorr.setStyleSheet("""background-color: rgb(211, 211, 211);""")
            correctors_gridlayout.addWidget(widget_scrncorr,line,1)
            line += 1

        self.centralwidget.groupBox_allcorrectorsPanel.setLayout(correctors_gridlayout)
        self.centralwidget.groupBox_allcorrectorsPanel.layout().setContentsMargins(2,2,2,2)
        label_scrn.setMaximumWidth(100)
        label_scrn.setMinimumWidth(100)
        label_position.setMaximumWidth(140)
        label_position.setMinimumWidth(140)
        label_lamp.setMaximumWidth(100)
        label_lamp.setMinimumWidth(100)
        label_ch_led.setMaximumWidth(25)
        label_ch_led.setMinimumWidth(25)
        label_ch.setMaximumWidth(100)
        label_ch.setMinimumWidth(100)
        label_ch_sp_kick.setMaximumWidth(180)
        label_ch_sp_kick.setMinimumWidth(180)
        label_ch_rb_kick.setMaximumWidth(100)
        label_ch_rb_kick.setMinimumWidth(100)
        label_cv_led.setMaximumWidth(25)
        label_cv_led.setMinimumWidth(25)
        label_cv.setMaximumWidth(100)
        label_cv.setMinimumWidth(100)
        label_cv_sp_kick.setMaximumWidth(180)
        label_cv_sp_kick.setMinimumWidth(180)
        label_cv_rb_kick.setMaximumWidth(100)
        label_cv_rb_kick.setMinimumWidth(100)

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
        fn, _ = QFileDialog.getOpenFileName(self, 'Open Reference...', None,
                'Images (*.png *.xpm *.jpg);;All Files (*)')
        if fn:
            self.reference_window.load_image(fn)
            self.reference_window.show()

    def _saveReference(self):
        fn, _ = QFileDialog.getSaveFileName(self, 'Save Reference As...', None,
                'Images (*.png *.xpm *.jpg);;All Files (*)')
        if not fn: return False
        lfn = fn.lower()
        if not lfn.endswith(('.png', '.jpg', '.xpm')): fn += '.png'

        if self._currScrn == 0:
            reference = self.centralwidget.widget_Scrn1.grab()
        elif self._currScrn == 1:
            reference = self.centralwidget.widget_Scrn2.grab()
        elif self._currScrn == 2:
            reference = self.centralwidget.widget_Scrn3.grab()
        elif self._currScrn == 3:
            reference = self.centralwidget.widget_Scrn41.grab()
        elif self._currScrn == 4:
            reference = self.centralwidget.widget_Scrn42.grab()
        elif self._currScrn == 5:
            reference = self.centralwidget.widget_Scrn43.grab()
        reference.save(fn)

    def _openWindow(self):
        sender = self.sender()
        ma = 'TS-' + sender.text()

        # self._corrector_detail_window = MagnetDetailWindow(ma,self)
        # self._corrector_detail_window.show()

    def _openMAApp(self):
        pass
        # self._BTS_MA_window = ToSiriusMagnetControlWindow(self)
        # self._BTS_MA_window.show()

    def _openBPMApp(self):
        pass
        #TODO

    def _openFCTApp(self):
        pass
        #TODO

    def _openPosAngleCorrApp(self):
        pass
        #TODO

    def _openLaticeAndTwiss(self):
        self.lattice_and_twiss_window.show()


class ShowLatticeAndTwiss(QWidget):
    def __init__(self,parent=None):
        super(ShowLatticeAndTwiss, self).__init__(parent)
        self._ts,self._twiss_in = _pymodels.ts.create_accelerator()
        self._ts_twiss, *_ = _pyaccel.optics.calc_twiss(accelerator=self._ts,init_twiss=self._twiss_in)
        fam_data = _pymodels.ts.families.get_family_data(self._ts)
        fam_mapping = _pymodels.ts.family_mapping
        self._fig,self._ax = _pyaccel.graphics.plot_twiss(accelerator=self._ts,twiss=self._ts_twiss,
                                                            family_data=fam_data, family_mapping=fam_mapping,
                                                            draw_edges=True,height=4,show_label=True)
        self.canvas = FigureCanvas(self._fig)
        self.canvas.setParent(self)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.canvas)
        self.setLayout(self.vbox)
        self.layout().setContentsMargins(0,0,0,0)
        self.setGeometry(10,10,400,1500)


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
window = BTSControlWindow()
window.show()
sys.exit(app.exec_())
