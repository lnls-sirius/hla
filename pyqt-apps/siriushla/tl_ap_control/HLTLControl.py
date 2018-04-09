#!/usr/bin/env python-sirius
"""HLA TB and TS AP Control Window."""

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)
from pydm.PyQt.uic import loadUi
from pydm.PyQt.QtCore import pyqtSlot, Qt
from pydm.PyQt.QtGui import (QVBoxLayout, QHBoxLayout,
                             QGridLayout, QFileDialog, QSizePolicy,
                             QDoubleValidator, QWidget, QFrame, QLabel,
                             QPixmap, QPushButton, QSpacerItem)
from pydm.PyQt.QtSvg import QSvgWidget
from pydm.widgets import PyDMLabel, PyDMLineEdit, PyDMEnumComboBox
import pyaccel as _pyaccel
import pymodels as _pymodels
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla import util as _hlautil
from siriushla.widgets import (SiriusLedAlert, SiriusLedState,
                               PyDMScrollBar, PyDMStateButton,
                               SiriusMainWindow)
from siriushla.as_ap_posang.HLPosAng import ASAPPosAngCorr
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow
from siriushla.as_ps_control.PSTabControlWindow import (
                                PSTabControlWindow)
from siriushla.as_pm_control.PulsedMagnetDetailWindow import (
                                PulsedMagnetDetailWindow)
from siriushla.as_pm_control.PulsedMagnetControlWindow import (
                                PulsedMagnetControlWindow)


CALC_LABELS_INITIALIZE = """
self.centralwidget.comboBox_CalcMethod_Scrn{0}.currentIndexChanged.connect(self._visibility_handle)
"""

CALC_LABELS_VISIBILITY = """
self.centralwidget.PyDMLabel_CenterXDimfei_Scrn{0}.setVisible({1})
self.centralwidget.PyDMLabel_CenterXNDStats_Scrn{0}.setVisible(not {1})
self.centralwidget.PyDMLabel_CenterYDimfei_Scrn{0}.setVisible({1})
self.centralwidget.PyDMLabel_CenterYNDStats_Scrn{0}.setVisible(not {1})
self.centralwidget.PyDMLabel_ThetaDimfei_Scrn{0}.setVisible({1})
self.centralwidget.PyDMLabel_ThetaNDStats_Scrn{0}.setVisible(not {1})
self.centralwidget.PyDMLabel_SigmaXDimfei_Scrn{0}.setVisible({1})
self.centralwidget.PyDMLabel_SigmaXNDStats_Scrn{0}.setVisible(not {1})
self.centralwidget.PyDMLabel_SigmaYDimfei_Scrn{0}.setVisible({1})
self.centralwidget.PyDMLabel_SigmaYNDStats_Scrn{0}.setVisible(not {1})
"""

CALC_LABELS_CHANNELS = """
self.centralwidget.PyDMLabel_CenterXDimfei_Scrn{0}.channel = ('ca://'
    + self.prefix + '{1}' + ':CenterXDimfei-Mon')
self.centralwidget.PyDMLabel_CenterXNDStats_Scrn{0}.channel = ('ca://'
    + self.prefix + '{1}' + ':CenterXNDStats-Mon')
self.centralwidget.PyDMLabel_CenterYDimfei_Scrn{0}.channel = ('ca://'
    + self.prefix + '{1}' + ':CenterYDimfei-Mon')
self.centralwidget.PyDMLabel_CenterYNDStats_Scrn{0}.channel = ('ca://'
    + self.prefix + '{1}' + ':CenterYNDStats-Mon')
self.centralwidget.PyDMLabel_ThetaDimfei_Scrn{0}.channel = ('ca://'
    + self.prefix + '{1}' + ':ThetaDimfei-Mon')
self.centralwidget.PyDMLabel_ThetaNDStats_Scrn{0}.channel = ('ca://'
    + self.prefix + '{1}' + ':ThetaNDStats-Mon')
self.centralwidget.PyDMLabel_SigmaXDimfei_Scrn{0}.channel = ('ca://'
    + self.prefix + '{1}' + ':SigmaXDimfei-Mon')
self.centralwidget.PyDMLabel_SigmaXNDStats_Scrn{0}.channel = ('ca://'
    + self.prefix + '{1}' + ':SigmaXNDStats-Mon')
self.centralwidget.PyDMLabel_SigmaYDimfei_Scrn{0}.channel = ('ca://'
    + self.prefix + '{1}' + ':SigmaYDimfei-Mon')
self.centralwidget.PyDMLabel_SigmaYNDStats_Scrn{0}.channel = ('ca://'
    + self.prefix + '{1}' + ':SigmaYNDStats-Mon')
"""


class TLAPControlWindow(SiriusMainWindow):
    """Class to create the main window for TB and TS HLA."""

    def __init__(self, parent=None, prefix='', tl=None):
        """Initialize widgets in main window."""
        super(TLAPControlWindow, self).__init__(parent)
        if prefix == '':
            self.prefix = _vaca_prefix
        else:
            self.prefix = prefix
        self._tl = tl
        self.setWindowTitle(self._tl.upper() + ' Control Window')

        if tl.lower() == 'tb':
            UI_FILE = ('ui_tb_ap_control.ui')
            SVG_FILE = ('TB.svg')
            correctors_list = [
                [['LI-01:MA-CH-7'], 'LI-01:MA-CV-7', 11, 'TB-01:DI-Scrn-1'],
                [['TB-01:MA-CH-1'], 'TB-01:MA-CV-1', 12, 'TB-01:DI-Scrn-2'],
                [['TB-01:MA-CH-2'], 'TB-01:MA-CV-2', 21, 'TB-02:DI-Scrn-1'],
                [['TB-02:MA-CH-1'], 'TB-02:MA-CV-1', 22, 'TB-02:DI-Scrn-2'],
                [['TB-02:MA-CH-2'], 'TB-02:MA-CV-2', 3, 'TB-03:DI-Scrn'],
                [['TB-03:MA-CH'], 'TB-04:MA-CV-1', 4, 'TB-04:DI-Scrn']]
            scrn_list = [
                [11, 'TB-01:DI-Scrn-1'], [12, 'TB-01:DI-Scrn-2'],
                [21, 'TB-02:DI-Scrn-1'], [22, 'TB-02:DI-Scrn-2'],
                [3, 'TB-03:DI-Scrn'], [4, 'TB-04:DI-Scrn']]
        elif tl.lower() == 'ts':
            UI_FILE = ('ui_ts_ap_control.ui')
            SVG_FILE = ('TS.svg')
            correctors_list = [
                [['TS-01:PM-EjeSF', 'TS-01:PM-EjeSG'],
                 'TS-01:MA-CV-1', 1, 'TS-01:DI-Scrn'],
                [['TS-01:MA-CH'], 'TS-01:MA-CV-2', 2, 'TS-02:DI-Scrn'],
                [['TS-02:MA-CH'], 'TS-02:MA-CV', 3, 'TS-03:DI-Scrn'],
                [['TS-03:MA-CH'], 'TS-03:MA-CV', 41, 'TS-04:DI-Scrn-1'],
                [['TS-04:MA-CH'], 'TS-04:MA-CV-1', 42, 'TS-04:DI-Scrn-2'],
                [['TS-04:PM-InjSG-1', 'TS-04:PM-InjSG-2', 'TS-04:PM-InjSF'],
                 'TS-04:MA-CV-2', 43, 'TS-04:DI-Scrn-3']]
            scrn_list = [
                [1, 'TS-01:DI-Scrn'], [2, 'TS-02:DI-Scrn'],
                [3, 'TS-03:DI-Scrn'], [41, 'TS-04:DI-Scrn-1'],
                [42, 'TS-04:DI-Scrn-2'], [43, 'TS-04:DI-Scrn-3']]

        self.centralwidget = loadUi('/home/fac_files/lnls-sirius/hla/'
                                    'pyqt-apps/siriushla/tl_ap_control/'
                                    + UI_FILE)
        self.setCentralWidget(self.centralwidget)

        # TL Lattice Widget
        lattice = QSvgWidget('/home/fac_files/lnls-sirius/hla/pyqt-apps/'
                             'siriushla/tl_ap_control/' + SVG_FILE)
        self.centralwidget.widget_lattice.setLayout(QVBoxLayout())
        self.centralwidget.widget_lattice.layout().addWidget(lattice)

        # TL Optics Widget
        self.lattice_and_twiss_window = ShowLatticeAndTwiss(
            parent=self, tl=self._tl)
        self.centralwidget.pushButton_LatticeAndTwiss.clicked.connect(
            self._openLaticeAndTwiss)

        # Set Visibility of Scrn Calculations Labels
        for i, device in scrn_list:
            exec(CALC_LABELS_INITIALIZE.format(i))
            visible = True
            exec(CALC_LABELS_VISIBILITY.format(i, visible))
            exec(CALC_LABELS_CHANNELS.format(i, device))

        # Open TL Apps
        _hlautil.connect_window(self.centralwidget.pushButton_PosAngCorrApp,
                                ASAPPosAngCorr, parent=self,
                                prefix=self.prefix, tl=self._tl)
        _hlautil.connect_window(self.centralwidget.pushButton_MAApp,
                                PSTabControlWindow, parent=self,
                                section=self._tl.upper(), discipline=1)  # MA
        _hlautil.connect_window(self.centralwidget.pushButton_PMApp,
                                PulsedMagnetControlWindow, self)
        self.centralwidget.pushButton_SlitApp.clicked.connect(
                                self._openSlitsApp)
        self.centralwidget.pushButton_BPMApp.clicked.connect(
                                self._openBPMApp)
        # self.centralwidget.pushButton_FCTApp.clicked.connect(
        #                         self._openFCTApp)

        # Reference Widget
        self.centralwidget.tabWidget_Scrns.setCurrentIndex(0)
        self._currScrn = 0
        self.centralwidget.tabWidget_Scrns.currentChanged.connect(
                                self._setCurrentScrn)
        self.centralwidget.pushButton_SaveRef.clicked.connect(
                                self._saveReference)
        self.reference_window = ShowImage(parent=self)
        self.centralwidget.pushButton_OpenRef.clicked.connect(
                                self._openReference)

        # Create Scrn+Correctors Panel
        scrn_headerline = QWidget()
        scrn_headerline.setLayout(QHBoxLayout())
        label_device = QLabel('Device')
        label_device.setAlignment(Qt.AlignHCenter)
        label_scrntype = QLabel('Screen Type')
        label_scrntype.setAlignment(Qt.AlignHCenter)
        label_led = QLabel('Led')
        label_led.setAlignment(Qt.AlignHCenter)
        scrn_headerline.layout().addWidget(label_device)
        scrn_headerline.layout().addWidget(label_scrntype)
        scrn_headerline.layout().addWidget(label_led)
        scrn_headerline.layout().setContentsMargins(0, 0, 0, 0)
        scrn_headerline.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        # scrn_headerline.setStyleSheet('''QLabel{background-color:blue;}''')

        ch_headerline = QWidget()
        ch_headerline.setLayout(QHBoxLayout())
        label_ch_led = QLabel('')
        label_ch_led.setAlignment(Qt.AlignHCenter)
        label_ch = QLabel('CH')
        label_ch.setAlignment(Qt.AlignHCenter)
        label_ch_sp_kick = QLabel('Kick-SP')
        label_ch_sp_kick.setAlignment(Qt.AlignHCenter)
        label_ch_mon_kick = QLabel('Kick-Mon')
        label_ch_mon_kick.setAlignment(Qt.AlignHCenter)
        ch_headerline.layout().addWidget(label_ch_led)
        ch_headerline.layout().addWidget(label_ch)
        ch_headerline.layout().addWidget(label_ch_sp_kick)
        ch_headerline.layout().addWidget(label_ch_mon_kick)
        ch_headerline.layout().setContentsMargins(0, 0, 0, 0)
        ch_headerline.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        # ch_headerline.setStyleSheet('''QLabel{background-color:blue;}''')

        cv_headerline = QWidget()
        cv_headerline.setLayout(QHBoxLayout())
        label_cv_led = QLabel('')
        label_cv_led.setAlignment(Qt.AlignHCenter)
        label_cv = QLabel('CV')
        label_cv.setAlignment(Qt.AlignHCenter)
        label_cv_sp_kick = QLabel('Kick-SP')
        label_cv_sp_kick.setAlignment(Qt.AlignHCenter)
        label_cv_mon_kick = QLabel('Kick-Mon')
        label_cv_mon_kick.setAlignment(Qt.AlignHCenter)
        cv_headerline.layout().addWidget(label_cv_led)
        cv_headerline.layout().addWidget(label_cv)
        cv_headerline.layout().addWidget(label_cv_sp_kick)
        cv_headerline.layout().addWidget(label_cv_mon_kick)
        cv_headerline.layout().setContentsMargins(0, 0, 0, 0)
        cv_headerline.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        # cv_headerline.setStyleSheet('''QLabel{background-color:blue;}''')

        headerline = QWidget()
        headerline.setMaximumHeight(60)
        headerline.setLayout(QHBoxLayout())
        headerline.layout().addItem(QSpacerItem(40, 20,
                                                QSizePolicy.Expanding,
                                                QSizePolicy.Minimum))
        headerline.layout().addWidget(scrn_headerline)
        headerline.layout().addItem(QSpacerItem(40, 20,
                                                QSizePolicy.MinimumExpanding,
                                                QSizePolicy.Minimum))
        headerline.layout().addWidget(ch_headerline)
        headerline.layout().addItem(QSpacerItem(40, 20,
                                                QSizePolicy.MinimumExpanding,
                                                QSizePolicy.Minimum))
        headerline.layout().addWidget(cv_headerline)
        headerline.layout().addItem(QSpacerItem(40, 20,
                                                QSizePolicy.Expanding,
                                                QSizePolicy.Minimum))
        headerline.setStyleSheet("""font-weight:bold;""")
        headerline.layout().setContentsMargins(0, 9, 0, 9)
        correctors_gridlayout = QGridLayout()
        correctors_gridlayout.addWidget(headerline, 1, 1)

        for item, width in [[label_device, 250], [label_scrntype, 200],
                            [label_led, 200], [label_ch_led, 40],
                            [label_ch, 250], [label_ch_sp_kick, 250],
                            [label_ch_mon_kick, 180], [label_cv_led, 40],
                            [label_cv, 250], [label_cv_sp_kick, 250],
                            [label_cv_mon_kick, 180]]:
            item.setMaximumWidth(width)
            item.setMinimumWidth(width)
            item.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        line = 2
        for ch_group, cv, scrn, scrnprefix in correctors_list:

            # Scrn
            scrn_details = QWidget()
            scrn_details.setObjectName('widget_Scrn' + str(scrn))
            scrn_details.setLayout(QHBoxLayout())
            scrn_details.layout().setContentsMargins(3, 3, 3, 3)

            scrn_label = QLabel(scrnprefix)
            scrn_label.setMinimumWidth(250)
            scrn_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
            scrn_label.setStyleSheet("""font-weight:bold;""")
            scrn_details.layout().addWidget(scrn_label)

            widget_scrntype_sp = QWidget()
            widget_scrntype_sp.setLayout(QVBoxLayout())
            widget_scrntype_sp.layout().setContentsMargins(0, 0, 0, 0)
            widget_scrntype_sp.layout().setAlignment(Qt.AlignHCenter)
            pydmcombobox_scrntype = PyDMEnumComboBox(
                self, 'ca://' + self.prefix + scrnprefix + ':ScrnType-Sel')
            pydmcombobox_scrntype.setObjectName(
                'PyDMEnumComboBox_ScrnType_Sel_Scrn'+str(scrn))
            widget_scrntype_sp.layout().addWidget(pydmcombobox_scrntype)
            led_scrntype = SiriusLedAlert(
                self, 'ca://' + self.prefix + scrnprefix + ':ScrnType-Sts')
            led_scrntype.shape = 2
            led_scrntype.setObjectName(
                'Led_ScrnType_Sts_Scrn' + str(scrn))
            led_scrntype.setMaximumHeight(40)
            widget_scrntype_sp.layout().addWidget(led_scrntype)
            widget_scrntype_sp.setMinimumWidth(200)
            widget_scrntype_sp.setMaximumWidth(200)
            widget_scrntype_sp.setSizePolicy(
                QSizePolicy.Fixed, QSizePolicy.Fixed)
            scrn_details.layout().addWidget(widget_scrntype_sp)

            scrn_details.layout().addItem(QSpacerItem(40, 20,
                                                      QSizePolicy.Fixed,
                                                      QSizePolicy.Minimum))

            pydmstatebutton = PyDMStateButton(
                parent=self,
                init_channel='ca://'+self.prefix + scrnprefix + ':LedEnbl-Sel')
            pydmstatebutton.shape = 1
            pydmstatebutton.setObjectName(
                'PyDMStateButton_LedEnbl_Sel_Scrn' + str(scrn))
            pydmstatebutton.setSizePolicy(QSizePolicy.Fixed,
                                          QSizePolicy.Minimum)
            scrn_details.layout().addWidget(pydmstatebutton)
            led = SiriusLedState(
                self, 'ca://' + self.prefix + scrnprefix + ':LedEnbl-Sts')
            led.setObjectName('SiriusLed_LedEnbl_Sts_Scrn' + str(scrn))
            led.setMinimumWidth(40)
            led.setMinimumHeight(40)
            led.setMaximumHeight(40)
            led.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
            scrn_details.layout().addWidget(led)

            scrn_details.layout().addItem(QSpacerItem(40, 20,
                                                      QSizePolicy.Fixed,
                                                      QSizePolicy.Minimum))

            # CH
            ch_widget = QWidget()
            ch_widget.setObjectName('widget_CHs_Scrn' + str(scrn))
            ch_widget.setLayout(QVBoxLayout())
            ch_widget.layout().setContentsMargins(0, 0, 0, 0)

            for ch in ch_group:
                name = ch.split('-')
                if len(name) > 2:
                    name = name[-2]+name[-1]
                else:
                    name = name[-1]

                ch_details = QWidget()
                ch_details.setObjectName(
                    'widget_details_' + name + '_Scrn' + str(scrn))
                ch_details.setLayout(QGridLayout())
                ch_details.layout().setContentsMargins(3, 3, 3, 3)

                led = SiriusLedState(
                    self, 'ca://' + self.prefix + ch + ':PwrState-Sts')
                led.setObjectName(
                    'SiriusLed_' + name + '_PwrState_Scrn' + str(scrn))
                led.setMinimumWidth(40)
                led.setMinimumHeight(40)
                led.setMaximumHeight(40)
                led.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
                ch_details.layout().addWidget(led, 1, 1)

                pushbutton = QPushButton(ch, self)
                pushbutton.setObjectName(
                    'pushButton_' + name + 'App_Scrn' + str(scrn))
                if ch.split('-')[0] == 'LI':
                    pass
                    # TODO
                elif ch.split('-')[1].split(':')[1] == 'PM':
                    _hlautil.connect_window(pushbutton,
                                            PulsedMagnetDetailWindow,
                                            parent=self, maname=ch)
                else:
                    _hlautil.connect_window(pushbutton,
                                            PSDetailWindow,
                                            parent=self, psname=ch)
                pushbutton.setMinimumWidth(250)
                pushbutton.setMaximumWidth(250)
                pushbutton.setMinimumHeight(40)
                pushbutton.setSizePolicy(QSizePolicy.Fixed,
                                         QSizePolicy.Minimum)
                ch_details.layout().addWidget(pushbutton, 1, 2)

                frame = QFrame()
                frame.setStyleSheet("background-color: rgb(255, 255, 255);")
                frame.setLayout(QVBoxLayout())
                frame.layout().setContentsMargins(0, 0, 0, 0)
                pydmlineedit_kick = PyDMLineEdit(
                    self, 'ca://' + self.prefix + ch + ':Kick-SP')
                pydmlineedit_kick.setObjectName(
                    'PyDMLineEdit' + name + '_Kick_SP_Scrn' + str(scrn))
                pydmlineedit_kick.setValidator(QDoubleValidator())
                pydmlineedit_kick.showUnits = True
                pydmlineedit_kick.setMinimumWidth(250)
                pydmlineedit_kick.setMaximumWidth(250)
                pydmlineedit_kick.setMinimumHeight(40)
                pydmlineedit_kick.setSizePolicy(QSizePolicy.Fixed,
                                                QSizePolicy.Minimum)
                frame.layout().addWidget(pydmlineedit_kick)
                ch_details.layout().addWidget(frame, 1, 5)

                scrollbar_kick = PyDMScrollBar(
                    self, Qt.Horizontal,
                    'ca://' + self.prefix + ch + ':Kick-SP')
                scrollbar_kick.setObjectName(
                    'PyDMScrollBar' + name + '_Kick_SP_Scrn' + str(scrn))
                scrollbar_kick.setMinimumWidth(250)
                scrollbar_kick.setSizePolicy(QSizePolicy.Expanding,
                                             QSizePolicy.Minimum)
                scrollbar_kick.limitsFromPV = True
                ch_details.layout().addWidget(scrollbar_kick, 2, 5)

                frame = QFrame()
                frame.setLayout(QVBoxLayout())
                frame.layout().setContentsMargins(0, 0, 0, 0)
                frame.setFrameShadow(QFrame.Raised)
                frame.setFrameShape(QFrame.Box)
                pydmlabel_kick = PyDMLabel(
                    self, 'ca://' + self.prefix + ch + ':Kick-Mon')
                pydmlabel_kick.setObjectName(
                    'PyDMLabel_' + name + '_Kick_Mon_Scrn' + str(scrn))
                pydmlabel_kick.setMinimumWidth(180)
                pydmlabel_kick.setMinimumHeight(40)
                pydmlabel_kick.precFromPV = True
                pydmlabel_kick.setLayout(QVBoxLayout())
                pydmlabel_kick.layout().setContentsMargins(3, 3, 3, 3)
                pydmlabel_kick.setSizePolicy(QSizePolicy.Fixed,
                                             QSizePolicy.Fixed)
                frame.layout().addWidget(pydmlabel_kick)
                ch_details.layout().addWidget(frame, 1, 6)
                ch_details.setSizePolicy(QSizePolicy.Minimum,
                                         QSizePolicy.Fixed)
                ch_widget.layout().addWidget(ch_details)

            # CV
            name = cv.split('-')
            if len(name) > 2:
                name = name[-2]+name[-1]
            else:
                name = name[-1]

            cv_details = QWidget()
            cv_details.setObjectName(
                'widget_details_' + name + '_Scrn' + str(scrn))
            cv_details.setLayout(QGridLayout())
            cv_details.layout().setContentsMargins(3, 3, 3, 3)

            led = SiriusLedState(
                self, 'ca://' + self.prefix + cv + ':PwrState-Sts')
            led.setObjectName(
                'SiriusLed_' + name + '_PwrState_Scrn' + str(scrn))
            led.setMinimumWidth(40)
            led.setMinimumHeight(40)
            led.setMaximumHeight(40)
            led.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
            cv_details.layout().addWidget(led, 1, 1)

            pushbutton = QPushButton(cv, self)
            pushbutton.setObjectName(
                'pushButton_' + name + 'App_Scrn' + str(scrn))
            if cv.split('-')[0] == 'LI':
                pass
                # TODO
            elif cv.split('-')[1].split(':')[1] == 'PM':
                _hlautil.connect_window(pushbutton,
                                        PulsedMagnetDetailWindow,
                                        parent=self, maname=cv)
            else:
                _hlautil.connect_window(pushbutton,
                                        PSDetailWindow,
                                        parent=self, psname=cv)
            pushbutton.setMinimumWidth(250)
            pushbutton.setMaximumWidth(250)
            pushbutton.setMinimumHeight(40)
            pushbutton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
            cv_details.layout().addWidget(pushbutton, 1, 2)

            frame = QFrame()
            frame.setStyleSheet("background-color: rgb(255, 255, 255);")
            frame.setLayout(QVBoxLayout())
            frame.layout().setContentsMargins(0, 0, 0, 0)
            pydmlineedit_kick = PyDMLineEdit(
                self, 'ca://' + self.prefix + cv + ':Kick-SP')
            pydmlineedit_kick.setObjectName(
                'PyDMLineEdit' + name + '_Kick_SP_Scrn' + str(scrn))
            pydmlineedit_kick.setValidator(QDoubleValidator())
            pydmlineedit_kick.showUnits = True
            pydmlineedit_kick.setMinimumWidth(250)
            pydmlineedit_kick.setMaximumWidth(250)
            pydmlineedit_kick.setMinimumHeight(40)
            pydmlineedit_kick.setSizePolicy(QSizePolicy.Fixed,
                                            QSizePolicy.Minimum)
            frame.layout().addWidget(pydmlineedit_kick)
            cv_details.layout().addWidget(frame, 1, 5)

            scrollbar_kick = PyDMScrollBar(
                self, Qt.Horizontal,
                'ca://' + self.prefix + cv + ':Kick-SP')
            scrollbar_kick.setObjectName(
                'PyDMScrollBar' + name + '_Kick_SP_Scrn' + str(scrn))
            scrollbar_kick.setMinimumWidth(250)
            scrollbar_kick.setSizePolicy(QSizePolicy.Expanding,
                                         QSizePolicy.Minimum)
            scrollbar_kick.limitsFromPV = True
            cv_details.layout().addWidget(scrollbar_kick, 2, 5)

            frame = QFrame()
            frame.setLayout(QVBoxLayout())
            frame.layout().setContentsMargins(0, 0, 0, 0)
            frame.setFrameShadow(QFrame.Raised)
            frame.setFrameShape(QFrame.Box)
            pydmlabel_kick = PyDMLabel(
                self, 'ca://' + self.prefix + cv + ':Kick-Mon')
            pydmlabel_kick.setObjectName(
                'PyDMLabel_' + name + '_Kick_Mon_Scrn' + str(scrn))
            pydmlabel_kick.setMinimumWidth(180)
            pydmlabel_kick.setMinimumHeight(40)
            pydmlabel_kick.precFromPV = True
            pydmlabel_kick.setFrameShadow(QFrame.Raised)
            pydmlabel_kick.setFrameShape(QFrame.Box)
            pydmlabel_kick.setLayout(QVBoxLayout())
            pydmlabel_kick.layout().setContentsMargins(3, 3, 3, 3)
            pydmlabel_kick.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            frame.layout().addWidget(pydmlabel_kick)
            cv_details.layout().addWidget(frame, 1, 6)
            cv_details.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

            widget_scrncorr = QWidget()
            widget_scrncorr.setLayout(QHBoxLayout())
            widget_scrncorr.layout().addItem(QSpacerItem(40, 20,
                                                         QSizePolicy.Expanding,
                                                         QSizePolicy.Minimum))
            widget_scrncorr.layout().addWidget(scrn_details)
            widget_scrncorr.layout().addItem(QSpacerItem(40, 20,
                                                         QSizePolicy.Expanding,
                                                         QSizePolicy.Minimum))
            widget_scrncorr.layout().addWidget(ch_widget)
            widget_scrncorr.layout().addItem(QSpacerItem(40, 20,
                                                         QSizePolicy.Expanding,
                                                         QSizePolicy.Minimum))
            widget_scrncorr.layout().addWidget(cv_details)
            widget_scrncorr.layout().addItem(QSpacerItem(40, 20,
                                                         QSizePolicy.Expanding,
                                                         QSizePolicy.Minimum))
            widget_scrncorr.layout().setContentsMargins(2, 2, 2, 2)

            if line % 2 == 0:
                widget_scrncorr.setStyleSheet(
                    """background-color: rgb(211, 211, 211);""")
            correctors_gridlayout.addWidget(widget_scrncorr, line, 1)
            line += 1

        self.centralwidget.groupBox_allcorrPanel.setLayout(
            correctors_gridlayout)
        self.centralwidget.groupBox_allcorrPanel.layout().setContentsMargins(
            2, 2, 2, 2)

    @pyqtSlot(int)
    def _visibility_handle(self, index):
        if index == 0:
            visible = True
        else:
            visible = False

        if self._tl.lower() == 'tb':
            scrn_dict = {'tb0': 11,
                         'tb1': 12,
                         'tb2': 21,
                         'tb3': 22,
                         'tb4': 3,
                         'tb5': 4,
                         }
        elif self._tl.lower() == 'ts':
            scrn_dict = {'ts0': 1,
                         'ts1': 2,
                         'ts2': 3,
                         'ts3': 41,
                         'ts4': 42,
                         'ts5': 43,
                         }
        scrn = scrn_dict[self._tl.lower()+str(self._currScrn)]
        exec(CALC_LABELS_VISIBILITY.format(scrn, visible))

    @pyqtSlot(int)
    def _setCurrentScrn(self, currScrn):
        self._currScrn = currScrn

    def _openReference(self):
        fn, _ = QFileDialog.getOpenFileName(
                                self, 'Open Reference...', None,
                                'Images (*.png *.xpm *.jpg);;All Files (*)')
        if fn:
            self.reference_window.load_image(fn)
            self.reference_window.show()

    def _saveReference(self):
        fn, _ = QFileDialog.getSaveFileName(
                                self, 'Save Reference As...', None,
                                'Images (*.png *.xpm *.jpg);;All Files (*)')
        if not fn:
            return False

        lfn = fn.lower()
        if not lfn.endswith(('.png', '.jpg', '.xpm')):
            fn += '.png'

        if self._tl.lower() == 'tb':
            scrn_dict = {'tb0': self.centralwidget.widget_Scrn11,
                         'tb1': self.centralwidget.widget_Scrn12,
                         'tb2': self.centralwidget.widget_Scrn21,
                         'tb3': self.centralwidget.widget_Scrn22,
                         'tb4': self.centralwidget.widget_Scrn3,
                         'tb5': self.centralwidget.widget_Scrn4,
                         }
        elif self._tl.lower() == 'ts':
            scrn_dict = {'ts0': self.centralwidget.widget_Scrn1,
                         'ts1': self.centralwidget.widget_Scrn2,
                         'ts2': self.centralwidget.widget_Scrn3,
                         'ts3': self.centralwidget.widget_Scrn41,
                         'ts4': self.centralwidget.widget_Scrn42,
                         'ts5': self.centralwidget.widget_Scrn43,
                         }
        scrn_widget = scrn_dict[self._tl.lower() + str(self._currScrn)]
        reference = scrn_widget.grab()
        reference.save(fn)

    def _openBPMApp(self):
        pass
        # TODO

    # def _openFCTApp(self):
    #     pass
    #     # TODO

    def _openSlitsApp(self):
        pass
        # TODO

    def _openLaticeAndTwiss(self):
        self.lattice_and_twiss_window.show()


class ShowLatticeAndTwiss(SiriusMainWindow):
    """Class to create Lattice and Twiss Widget."""

    def __init__(self, parent=None, tl=None):
        """Create Lattice and Twiss Graph."""
        super(ShowLatticeAndTwiss, self).__init__(parent)
        if tl == 'tb':
            self._tl, self._twiss_in = _pymodels.tb.create_accelerator()
            fam_data = _pymodels.tb.families.get_family_data(self._tl)
            fam_mapping = _pymodels.tb.family_mapping
        elif tl == 'ts':
            self._tl, self._twiss_in = _pymodels.ts.create_accelerator()
            fam_data = _pymodels.ts.families.get_family_data(self._tl)
            fam_mapping = _pymodels.ts.family_mapping

        self._tl_twiss, _ = _pyaccel.optics.calc_twiss(
                                                    accelerator=self._tl,
                                                    init_twiss=self._twiss_in)
        self._fig, self._ax = _pyaccel.graphics.plot_twiss(
                                                    accelerator=self._tl,
                                                    twiss=self._tl_twiss,
                                                    family_data=fam_data,
                                                    family_mapping=fam_mapping,
                                                    draw_edges=True,
                                                    height=4,
                                                    show_label=True)
        self.centralwidget = QWidget()
        self.centralwidget.setLayout(QVBoxLayout())
        self.canvas = FigureCanvas(self._fig)
        self.canvas.setParent(self.centralwidget)
        self.centralwidget.layout().addWidget(self.canvas)
        self.centralwidget.layout().setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.centralwidget)
        self.setGeometry(10, 10, 2000, 500)


class ShowImage(SiriusMainWindow):
    """Class to create Show Reference Image Widget."""

    def __init__(self, parent=None):
        """Create label widget to handle image pixmap."""
        super(ShowImage, self).__init__(parent)
        self.centralwidget = QWidget()
        self.centralwidget.setLayout(QVBoxLayout())
        self.label = QLabel()
        self.centralwidget.layout().addWidget(self.label)
        self.setCentralWidget(self.centralwidget)

    def load_image(self, filename):
        """Load pixmap from filename."""
        self.setWindowTitle(filename)
        self.pixmap = QPixmap(filename)
        self.label.setPixmap(self.pixmap)
        self.setGeometry(300, 300,
                         self.pixmap.width(),
                         self.pixmap.height())
