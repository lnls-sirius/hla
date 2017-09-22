#!/usr/bin/env python-sirius
"""HLA TB and TS AP Control Window."""

from pydm.PyQt.uic import loadUi
from pydm.PyQt.QtCore import pyqtSlot, Qt
from pydm.PyQt.QtGui import (QMainWindow, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QFileDialog, QSizePolicy,
                             QDoubleValidator, QWidget, QFrame, QLabel,
                             QPixmap, QPushButton, QSpacerItem, QApplication)
from pydm.widgets.led import PyDMLed
from pydm.widgets.label import PyDMLabel
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.scrollbar import PyDMScrollBar
from pydm.widgets.enum_combo_box import PyDMEnumComboBox
from pydm.widgets.state_button import PyDMStateButton
from matplotlib.backends.backend_qt5agg import (
        FigureCanvasQTAgg as FigureCanvas)
from pydm.PyQt.QtSvg import QSvgWidget
import pyaccel as _pyaccel
import pymodels as _pymodels
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla.as_ma_control.MagnetDetailWindow import MagnetDetailWindow
from siriushla.as_ma_control import ToSiriusMagnetControlWindow
from siriushla.as_ma_control import TBMagnetControlWindow
from siriushla.as_pm_control.PulsedMagnetDetailWidget import (
                                PulsedMagnetDetailWidget)
from siriushla.as_pm_control.PulsedMagnetControlWindow import (
                                PulsedMagnetControlWindow)
from siriushla.as_ap_posang.HLPosAng import ASAPPosAngCorr


CALC_LABELS_INITIALIZE = """
self.centralwidget.PyDMEnumComboBox_CalcMethod_Scrn{0}.currentIndexChanged.connect(self._visibility_handle)
"""

CALC_LABELS_VISIBILITY = """
self.centralwidget.PyDMLabel_CenterXDimfei_Scrn{0}.setVisible(visible)
self.centralwidget.PyDMLabel_CenterXNDStats_Scrn{0}.setVisible(not visible)
self.centralwidget.PyDMLabel_CenterYDimfei_Scrn{0}.setVisible(visible)
self.centralwidget.PyDMLabel_CenterYNDStats_Scrn{0}.setVisible(not visible)
self.centralwidget.PyDMLabel_ThetaDimfei_Scrn{0}.setVisible(visible)
self.centralwidget.PyDMLabel_ThetaNDStats_Scrn{0}.setVisible(not visible)
self.centralwidget.PyDMLabel_SigmaXDimfei_Scrn{0}.setVisible(visible)
self.centralwidget.PyDMLabel_SigmaXNDStats_Scrn{0}.setVisible(not visible)
self.centralwidget.PyDMLabel_SigmaYDimfei_Scrn{0}.setVisible(visible)
self.centralwidget.PyDMLabel_SigmaYNDStats_Scrn{0}.setVisible(not visible)
"""

CALC_LABELS_CHANNELS = """
self.centralwidget.PyDMLabel_CenterXDimfei_Scrn{0}.setChannel('ca://'
    + self.prefix + '{1}' + ':CenterXDimfei-Mon')
self.centralwidget.PyDMLabel_CenterXNDStats_Scrn{0}.setChannel('ca://'
    + self.prefix + '{1}' + ':CenterXNDStats-Mon')
self.centralwidget.PyDMLabel_CenterYDimfei_Scrn{0}.setChannel('ca://'
    + self.prefix + '{1}' + ':CenterYDimfei-Mon')
self.centralwidget.PyDMLabel_CenterYNDStats_Scrn{0}.setChannel('ca://'
    + self.prefix + '{1}' + ':CenterYNDStats-Mon')
self.centralwidget.PyDMLabel_ThetaDimfei_Scrn{0}.setChannel('ca://'
    + self.prefix + '{1}' + ':ThetaDimfei-Mon')
self.centralwidget.PyDMLabel_ThetaNDStats_Scrn{0}.setChannel('ca://'
    + self.prefix + '{1}' + ':ThetaNDStats-Mon')
self.centralwidget.PyDMLabel_SigmaXDimfei_Scrn{0}.setChannel('ca://'
    + self.prefix + '{1}' + ':SigmaXDimfei-Mon')
self.centralwidget.PyDMLabel_SigmaXNDStats_Scrn{0}.setChannel('ca://'
    + self.prefix + '{1}' + ':SigmaXNDStats-Mon')
self.centralwidget.PyDMLabel_SigmaYDimfei_Scrn{0}.setChannel('ca://'
    + self.prefix + '{1}' + ':SigmaYDimfei-Mon')
self.centralwidget.PyDMLabel_SigmaYNDStats_Scrn{0}.setChannel('ca://'
    + self.prefix + '{1}' + ':SigmaYNDStats-Mon')
"""


class TLAPControlWindow(QMainWindow):
    """Class to create the main window for TB and TS HLA."""

    def __init__(self, parent=None, prefix=None, tl=None):
        """Initialize widgets in main window."""
        super(TLAPControlWindow, self).__init__(parent)
        if prefix is None:
            self.prefix = _vaca_prefix
        else:
            self.prefix = prefix
        self._tl = tl

        if tl.lower() == 'tb':
            UI_FILE = ('ui_tb_ap_control.ui')
            SVG_FILE = ('TB.svg')
            correctors_list = [
                [['01:MA-CH-7'], '01:MA-CV-7', 11, '01:DI-Scrn-1'],
                [['01:MA-CH-1'], '01:MA-CV-1', 12, '01:DI-Scrn-2'],
                [['01:MA-CH-2'], '01:MA-CV-2', 21, '02:DI-Scrn-1'],
                [['02:MA-CH-1'], '02:MA-CV-1', 22, '02:DI-Scrn-2'],
                [['02:MA-CH-2'], '02:MA-CV-2', 3, '03:DI-Scrn'],
                [['03:MA-CH'], '04:MA-CV-1', 4, '04:DI-Scrn']]
            scrn_list = [
                [11, 'TB-01:DI-Scrn-1'], [12, 'TB-01:DI-Scrn-2'],
                [21, 'TB-02:DI-Scrn-1'], [22, 'TB-02:DI-Scrn-2'],
                [3, 'TB-03:DI-Scrn'], [4, 'TB-04:DI-Scrn']]
        elif tl.lower() == 'ts':
            UI_FILE = ('ui_ts_ap_control.ui')
            SVG_FILE = ('BTS.svg')
            correctors_list = [
                [['01:PM-EjeSF', '01:PM-EjeSG'],
                 '01:MA-CV-1', 1, '01:DI-Scrn'],
                [['01:MA-CH'], '01:MA-CV-2', 2, '02:DI-Scrn'],
                [['02:MA-CH'], '02:MA-CV', 3, '03:DI-Scrn'],
                [['03:MA-CH'], '03:MA-CV', 41, '04:DI-Scrn-1'],
                [['04:MA-CH'], '04:MA-CV-1', 42, '04:DI-Scrn-2'],
                [['04:PM-InjSG-1', '04:PM-InjSG-2', '04:PM-InjSF'],
                 '04:MA-CV-2', 43, '04:DI-Scrn-3']]
            scrn_list = [
                [1, 'TB-01:DI-Scrn'], [2, 'TB-02:DI-Scrn'],
                [3, 'TB-03:DI-Scrn'], [41, 'TB-04:DI-Scrn-1'],
                [42, 'TB-04:DI-Scrn-2'], [43, 'TB-04:DI-Scrn-3']]

        self.centralwidget = loadUi('/home/fac_files/lnls-sirius/hla/'
                                    'pyqt-apps/siriushla/tl_ap_control/'
                                    + UI_FILE)
        self.setCentralWidget(self.centralwidget)

        # Estabilish widget connections
        self.app = QApplication.instance()
        self.app.establish_widget_connections(self)

        # TL Lattice Widget
        lattice = QSvgWidget('/home/fac_files/lnls-sirius/hla/pyqt-apps/'
                             'siriushla/tl_ap_control/' + SVG_FILE)
        self.centralwidget.widget_lattice.setLayout(QVBoxLayout())
        self.centralwidget.widget_lattice.layout().addWidget(lattice)

        # TL Optics Widget
        self.lattice_and_twiss_window = ShowLatticeAndTwiss(parent=self,
                                                            tl=self._tl)
        self.centralwidget.pushButton_LatticeAndTwiss.clicked.connect(
                                                    self._openLaticeAndTwiss)

        # Set Visibility of Scrn Calculations Labels
        for i, device in scrn_list:
            exec(CALC_LABELS_INITIALIZE.format(i))
            visible = True
            exec(CALC_LABELS_VISIBILITY.format(i))
            exec(CALC_LABELS_CHANNELS.format(i, device))

        # Open TL Apps
        self.centralwidget.pushButton_PosAngCorrApp.clicked.connect(
                                                    self._openPosAngCorrApp)
        self.centralwidget.pushButton_MAApp.clicked.connect(self._openMAApp)
        self.centralwidget.pushButton_PMApp.clicked.connect(self._openPMApp)
        self.centralwidget.pushButton_FCTApp.clicked.connect(self._openFCTApp)
        self.centralwidget.pushButton_BPMApp.clicked.connect(self._openBPMApp)

        # Reference Widget
        self.centralwidget.tabWidget_Scrns.setCurrentIndex(0)
        self._currScrn = 0
        self.reference_window = ShowImage(parent=self)
        self.centralwidget.tabWidget_Scrns.currentChanged.connect(
                                                    self._setCurrentScrn)
        self.centralwidget.pushButton_SaveRef.clicked.connect(
                                                    self._saveReference)
        self.centralwidget.pushButton_OpenRef.clicked.connect(
                                                    self._openReference)

        # Create Scrn+Correctors Panel
        scrn_headerline = QWidget()
        scrn_headerline.setLayout(QHBoxLayout())
        scrn_headerline.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        label_scrn = QLabel('Scrn')
        label_scrn.setAlignment(Qt.AlignHCenter)
        label_scrn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        label_fluorscrn = QLabel('Position')
        label_fluorscrn.setAlignment(Qt.AlignHCenter)
        label_fluorscrn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        label_lamp = QLabel('Led')
        label_lamp.setAlignment(Qt.AlignHCenter)
        label_lamp.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        scrn_headerline.layout().addWidget(label_scrn)
        scrn_headerline.layout().addWidget(label_fluorscrn)
        scrn_headerline.layout().addWidget(label_lamp)
        scrn_headerline.layout().setContentsMargins(0, 0, 0, 0)
        # scrn_headerline.setStyleSheet('''QLabel{background-color:blue;}''')

        ch_headerline = QWidget()
        ch_headerline.setLayout(QHBoxLayout())
        ch_headerline.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        label_ch_led = QLabel('')
        label_ch_led.setAlignment(Qt.AlignHCenter)
        label_ch_led.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        label_ch = QLabel('CH')
        label_ch.setAlignment(Qt.AlignHCenter)
        label_ch.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        label_ch_sp_kick = QLabel('Kick-SP')
        label_ch_sp_kick.setAlignment(Qt.AlignHCenter)
        label_ch_sp_kick.setSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Minimum)
        label_ch_mon_kick = QLabel('Kick-Mon')
        label_ch_mon_kick.setAlignment(Qt.AlignHCenter)
        label_ch_mon_kick.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        ch_headerline.layout().addWidget(label_ch_led)
        ch_headerline.layout().addWidget(label_ch)
        ch_headerline.layout().addWidget(label_ch_sp_kick)
        ch_headerline.layout().addWidget(label_ch_mon_kick)
        ch_headerline.layout().setContentsMargins(0, 0, 0, 0)
        # ch_headerline.setStyleSheet('''QLabel{background-color:blue;}''')

        cv_headerline = QWidget()
        cv_headerline.setLayout(QHBoxLayout())
        cv_headerline.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        label_cv_led = QLabel('')
        label_cv_led.setAlignment(Qt.AlignHCenter)
        label_cv_led.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        label_cv = QLabel('CV')
        label_cv.setAlignment(Qt.AlignHCenter)
        label_cv.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        label_cv_sp_kick = QLabel('Kick-SP')
        label_cv_sp_kick.setAlignment(Qt.AlignHCenter)
        label_cv_sp_kick.setSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Minimum)
        label_cv_mon_kick = QLabel('Kick-Mon')
        label_cv_mon_kick.setAlignment(Qt.AlignHCenter)
        label_cv_mon_kick.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        cv_headerline.layout().addWidget(label_cv_led)
        cv_headerline.layout().addWidget(label_cv)
        cv_headerline.layout().addWidget(label_cv_sp_kick)
        cv_headerline.layout().addWidget(label_cv_mon_kick)
        cv_headerline.layout().setContentsMargins(0, 0, 0, 0)
        # cv_headerline.setStyleSheet('''QLabel{background-color:blue;}''')

        headerline = QWidget()
        headerline.setMaximumHeight(60)
        headerline.setLayout(QHBoxLayout())
        headerline.layout().addWidget(scrn_headerline)
        headerline.layout().addItem(QSpacerItem(40, 20,
                                                QSizePolicy.Fixed,
                                                QSizePolicy.Minimum))
        headerline.layout().addWidget(ch_headerline)
        headerline.layout().addItem(QSpacerItem(40, 20,
                                                QSizePolicy.Fixed,
                                                QSizePolicy.Minimum))
        headerline.layout().addWidget(cv_headerline)
        headerline.setStyleSheet("""font-weight:bold;""")
        headerline.layout().setContentsMargins(0, 9, 0, 9)
        correctors_gridlayout = QGridLayout()
        correctors_gridlayout.addWidget(headerline, 1, 1)
        for item, width in [[label_scrn, 200], [label_fluorscrn, 200],
                            [label_lamp, 200], [label_ch_led, 40],
                            [label_ch, 180], [label_ch_sp_kick, 350],
                            [label_ch_mon_kick, 180], [label_cv_led, 40],
                            [label_cv, 180], [label_cv_sp_kick, 350],
                            [label_cv_mon_kick, 180]]:
            item.setMaximumWidth(width)
            item.setMinimumWidth(width)

        line = 2
        for ch_group, cv, scrn, scrnpv in correctors_list:

            if self._tl.lower() == 'tb':
                if scrn == 11:
                    acc = 'LI-'
                else:
                    acc = 'TB-'
            elif self._tl.lower() == 'ts':
                acc = 'TS-'

            # Scrn
            scrn_details = QWidget()
            scrn_details.setObjectName('widget_Scrn' + str(scrn))
            scrn_details.setLayout(QHBoxLayout())
            scrn_details.layout().setContentsMargins(3, 3, 3, 3)

            scrn_label = QLabel(scrnpv)
            scrn_label.setMinimumWidth(200)
            scrn_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
            scrn_label.setStyleSheet("""font-weight:bold;""")
            scrn_details.layout().addWidget(scrn_label)

            widget_fluorscrn_sp = QWidget()
            widget_fluorscrn_sp.setLayout(QVBoxLayout())
            widget_fluorscrn_sp.layout().setContentsMargins(0, 0, 0, 0)
            pydmcombobox_fluorscrn = PyDMEnumComboBox(
                scrn_details,
                'ca://' + prefix + acc + scrnpv + ':FluorScrn-Sel')
            pydmcombobox_fluorscrn.setObjectName(
                'PyDMEnumComboBox_FluorScrn_Sel_Scrn' + str(scrn))
            widget_fluorscrn_sp.layout().addWidget(pydmcombobox_fluorscrn)
            # pydmcombobox_fluorscrn_items = [
            #     pydmcombobox_fluorscrn.itemText(i)
            #     for i in range(pydmcombobox_fluorscrn.count())]
            pydmled_fluorscrn = PyDMLed(
                scrn_details,
                'ca://' + prefix + acc + scrnpv + ':FluorScrn-Sts')
            #     enum_map = {pydmcombobox_fluorscrn_items[0]: -1,
            #     pydmcombobox_fluorscrn_items[1]: 2,
            #     pydmcombobox_fluorscrn_items[2]: 0})
            #     TODO
            pydmled_fluorscrn.shape = 2
            pydmled_fluorscrn.setObjectName(
                'PyDMLed_FluorScrn_Sts_Scrn' + str(scrn))
            widget_fluorscrn_sp.layout().addWidget(pydmled_fluorscrn)
            widget_fluorscrn_sp.setMinimumWidth(200)
            widget_fluorscrn_sp.setSizePolicy(QSizePolicy.Fixed,
                                              QSizePolicy.Fixed)
            scrn_details.layout().addWidget(widget_fluorscrn_sp)

            scrn_details.layout().addItem(QSpacerItem(40, 20,
                                                      QSizePolicy.Fixed,
                                                      QSizePolicy.Minimum))
            pydmstatebutton = PyDMStateButton(
                parent=scrn_details,
                init_channel='ca://' + prefix + acc + scrnpv + ':LedState-SP',
                shape=1)
            pydmstatebutton.setObjectName(
                'PyDMStateButton_LedState_SP_Scrn' + str(scrn))
            pydmstatebutton.setSizePolicy(QSizePolicy.Fixed,
                                          QSizePolicy.Minimum)
            scrn_details.layout().addWidget(pydmstatebutton)
            pydmled = PyDMLed(
                scrn_details,
                'ca://' + prefix + acc + scrnpv + ':LedState-RB')
            pydmled.setObjectName('PyDMLed_LedState_RB_Scrn' + str(scrn))
            pydmled.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
            scrn_details.layout().addWidget(pydmled)
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
                if len(name) > 3:
                    name = name[-2]+name[-1]
                else:
                    name = name[-1]

                ch_details = QWidget()
                ch_details.setObjectName(
                    'widget_details_' + name + '_Scrn' + str(scrn))
                ch_details.setLayout(QGridLayout())
                ch_details.layout().setContentsMargins(3, 3, 3, 3)

                pydmled = PyDMLed(
                    ch_details,
                    'ca://' + prefix + acc + ch + ':PwrState-Sts')
                pydmled.setObjectName(
                    'PyDMLed_' + name + '_PwrState' + '_Scrn' + str(scrn))
                pydmled.setMinimumWidth(40)
                pydmled.setMinimumHeight(40)
                pydmled.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
                ch_details.layout().addWidget(pydmled, 1, 1)

                pushbutton = QPushButton(ch, ch_details)
                pushbutton.setObjectName(
                    'pushButton_' + name + 'App_Scrn' + str(scrn))
                pushbutton.clicked.connect(self._openWindow)
                pushbutton.setMinimumWidth(180)
                pushbutton.setMinimumHeight(40)
                pushbutton.setSizePolicy(QSizePolicy.Fixed,
                                         QSizePolicy.Minimum)
                ch_details.layout().addWidget(pushbutton, 1, 2)

                pydmlineedit_kick = PyDMLineEdit(
                    ch_details,
                    'ca://' + prefix + acc + ch + ':Kick-SP')
                pydmlineedit_kick.setObjectName(
                    'PyDMLineEdit' + name + '_Kick_SP_Scrn' + str(scrn))
                pydmlineedit_kick.setValidator(QDoubleValidator())
                pydmlineedit_kick._useunits = False
                pydmlineedit_kick.setMinimumWidth(350)
                pydmlineedit_kick.setMinimumHeight(40)
                pydmlineedit_kick.setSizePolicy(QSizePolicy.Expanding,
                                                QSizePolicy.Minimum)
                ch_details.layout().addWidget(pydmlineedit_kick, 1, 5)

                scrollbar_kick = PyDMScrollBar(
                    ch_details, Qt.Horizontal,
                    'ca://' + prefix + acc + ch + ':Kick-SP', 1)
                scrollbar_kick.setObjectName(
                    'PyDMScrollBar' + name + '_Kick_SP_Scrn' + str(scrn))
                scrollbar_kick.setMinimumWidth(350)
                scrollbar_kick.setSizePolicy(QSizePolicy.Expanding,
                                             QSizePolicy.Minimum)
                scrollbar_kick.limitsFromPV = True
                ch_details.layout().addWidget(scrollbar_kick, 2, 5)

                pydmlabel_kick = PyDMLabel(
                    ch_details,
                    'ca://' + prefix + acc + ch + ':Kick-Mon')
                pydmlabel_kick.setObjectName(
                    'PyDMLabel_' + name + '_Kick_Mon_Scrn' + str(scrn))
                pydmlabel_kick.setMinimumWidth(180)
                pydmlabel_kick.setMinimumHeight(40)
                pydmlabel_kick.precFromPV = True
                pydmlabel_kick.setFrameShadow(QFrame.Raised)
                pydmlabel_kick.setFrameShape(QFrame.Box)
                pydmlabel_kick.setLayout(QVBoxLayout())
                pydmlabel_kick.layout().setContentsMargins(3, 3, 3, 3)
                pydmlabel_kick.setSizePolicy(QSizePolicy.Fixed,
                                             QSizePolicy.Fixed)
                ch_details.layout().addWidget(pydmlabel_kick, 1, 6)
                ch_details.setSizePolicy(QSizePolicy.Minimum,
                                         QSizePolicy.Fixed)
                ch_widget.layout().addWidget(ch_details)

            # CV
            name = cv.split('-')
            if len(name) > 3:
                name = name[-2]+name[-1]
            else:
                name = name[-1]

            cv_details = QWidget()
            cv_details.setObjectName(
                'widget_details_' + name + '_Scrn' + str(scrn))
            cv_details.setLayout(QGridLayout())
            cv_details.layout().setContentsMargins(3, 3, 3, 3)

            pydmled = PyDMLed(
                cv_details,
                'ca://' + prefix + acc + cv + ':PwrState-Sts')
            pydmled.setObjectName(
                'PyDMLed_' + name + '_PwrState' + '_Scrn' + str(scrn))
            pydmled.setMinimumWidth(40)
            pydmled.setSizePolicy(QSizePolicy.Fixed,
                                  QSizePolicy.Minimum)
            cv_details.layout().addWidget(pydmled, 1, 1)

            pushbutton = QPushButton(cv, cv_details)
            pushbutton.setObjectName(
                'pushButton_' + name + 'App_Scrn' + str(scrn))
            pushbutton.clicked.connect(self._openWindow)
            pushbutton.setMinimumWidth(180)
            pushbutton.setMinimumHeight(40)
            pushbutton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
            cv_details.layout().addWidget(pushbutton, 1, 2)

            pydmlineedit_kick = PyDMLineEdit(
                cv_details,
                'ca://' + prefix + acc + cv + ':Kick-SP')
            pydmlineedit_kick.setObjectName(
                'PyDMLineEdit' + name + '_Kick_SP_Scrn' + str(scrn))
            pydmlineedit_kick.setValidator(QDoubleValidator())
            pydmlineedit_kick._useunits = False
            pydmlineedit_kick.setMinimumWidth(350)
            pydmlineedit_kick.setMinimumHeight(40)
            pydmlineedit_kick.setSizePolicy(QSizePolicy.Expanding,
                                            QSizePolicy.Minimum)
            cv_details.layout().addWidget(pydmlineedit_kick, 1, 5)

            scrollbar_kick = PyDMScrollBar(
                cv_details, Qt.Horizontal,
                'ca://' + prefix + acc + cv + ':Kick-SP', 1)
            scrollbar_kick.setObjectName(
                'PyDMScrollBar' + name + '_Kick_SP_Scrn' + str(scrn))
            scrollbar_kick.setMinimumWidth(350)
            scrollbar_kick.setSizePolicy(QSizePolicy.Expanding,
                                         QSizePolicy.Minimum)
            scrollbar_kick.limitsFromPV = True
            cv_details.layout().addWidget(scrollbar_kick, 2, 5)

            pydmlabel_kick = PyDMLabel(
                cv_details,
                'ca://' + prefix + acc + cv + ':Kick-Mon')
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
            cv_details.layout().addWidget(pydmlabel_kick, 1, 6)
            cv_details.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

            widget_scrncorr = QWidget()
            widget_scrncorr.setLayout(QHBoxLayout())
            widget_scrncorr.layout().addWidget(scrn_details)
            widget_scrncorr.layout().addItem(QSpacerItem(40, 20,
                                                         QSizePolicy.Fixed,
                                                         QSizePolicy.Minimum))
            widget_scrncorr.layout().addWidget(ch_widget)
            widget_scrncorr.layout().addItem(QSpacerItem(40, 20,
                                                         QSizePolicy.Fixed,
                                                         QSizePolicy.Minimum))
            widget_scrncorr.layout().addWidget(cv_details)
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
        scrn = scrn_dict[self._tl.lower() + str(self._currScrn)]
        exec(CALC_LABELS_VISIBILITY.format(scrn))

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

    def _openWindow(self):
        sender = self.sender()

        if sender.text().split('-')[0] == 'LI':
            pass
            # TODO
        elif sender.text().split('-')[0].split(':')[1] == 'PM':
            corr = self._tl.upper() + '-' + sender.text()
            self.w = QMainWindow(self)
            self.w.setCentralWidget(PulsedMagnetDetailWidget(corr, self.w))
            self.app.establish_widget_connections(self.w)
            self.w.show()
        else:
            corr = self._tl.upper() + '-' + sender.text()
            self._corrector_detail_window = MagnetDetailWindow(corr, self)
            self._corrector_detail_window.show()

    def _openMAApp(self):
        if self._tl.lower() == 'tb':
            self._TB_MA_window = TBMagnetControlWindow(self)
            self._TB_MA_window.show()
        elif self._tl.lower() == 'ts':
            self._TS_MA_window = ToSiriusMagnetControlWindow(self)
            self._TS_MA_window.show()

    def _openPMApp(self):
        self._PM_window = PulsedMagnetControlWindow(self)
        self._PM_window.show()

    def _openBPMApp(self):
        pass
        # TODO

    def _openFCTApp(self):
        pass
        # TODO

    def _openPosAngCorrApp(self):
        if self._tl.lower() == 'tb':
            self._TB_PosAng_window = ASAPPosAngCorr(parent=self,
                                                     prefix=self.prefix,
                                                     tl='tb')
            self._TB_PosAng_window.show()
        elif self._tl.lower() == 'ts':
            self._BTS_PosAng_window = ASAPPosAngCorr(parent=self,
                                                     prefix=self.prefix,
                                                     tl='ts')
            self._BTS_PosAng_window.show()

    def _openLaticeAndTwiss(self):
        self.lattice_and_twiss_window.show()

    def closeEvent(self, event):
        """Reimplement close event to close widget connections."""
        self.app.close_widget_connections(self)
        super().closeEvent(event)


class ShowLatticeAndTwiss(QMainWindow):
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


class ShowImage(QMainWindow):
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
