#!/usr/bin/env python-sirius
"""HLA TB and TS AP Control Window."""

import os as _os
from datetime import datetime as _datetime
import epics as _epics
from qtpy.uic import loadUi
from qtpy.QtCore import Slot, Qt, QPoint
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, \
                            QFileDialog, QAction, QMenuBar, \
                            QWidget, QLabel, QPushButton, QMenu, \
                            QButtonGroup, QCheckBox, QSizePolicy as QSzPlcy
from qtpy.QtGui import QPixmap
from qtpy.QtSvg import QSvgWidget
from pydm.widgets import PyDMLabel, PyDMEnumComboBox
from pydm.widgets.base import PyDMWidget
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
# import pyaccel as _pyaccel
# import pymodels as _pymodels
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla import util as _hlautil
from siriushla.widgets import PyDMLed, SiriusLedAlert, SiriusLedState, \
    SiriusMainWindow, PyDMLinEditScrollbar
# from siriushla.widgets import SiriusFigureCanvas
from siriushla.as_di_scrns import SiriusScrnView
from siriushla.as_ap_posang.HLPosAng import ASAPPosAngCorr
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow
from siriushla.as_ps_control.PSTabControlWindow import PSTabControlWindow
from siriushla.as_pm_control.PulsedMagnetDetailWindow import (
    PulsedMagnetDetailWindow)
from siriushla.as_pm_control.PulsedMagnetControlWindow import (
    PulsedMagnetControlWindow)
from siriushla.tl_ap_control.ICT_monitor import ICTMonitoring
from siriushla.tl_ap_control.Slit_monitor import SlitMonitoring


class TLAPControlWindow(SiriusMainWindow):
    """Class to create the main window for TB and TS HLA."""

    def __init__(self, parent=None, prefix=_vaca_prefix, tl=None):
        """Initialize widgets in main window."""
        super(TLAPControlWindow, self).__init__(parent)
        self.prefix = prefix
        self._tl = tl
        self.setWindowTitle(self._tl.upper() + ' Control Window')
        self._setupUi()

    def _setupUi(self):
        [UI_FILE, SVG_FILE, ICT1, ICT2, self._corr_devicenames_list,
            self._scrn_devicenames_list] = self._getTLData(self._tl)

        # Set central widget
        tmp_file = _substitute_in_file(
            '/home/sirius/repos/hla/pyqt-apps/siriushla'
            '/tl_ap_control/' + UI_FILE,
            {'PREFIX': self.prefix, 'ICT1': ICT1, 'ICT2': ICT2})
        self.centralwidget = loadUi(tmp_file)
        self.setCentralWidget(self.centralwidget)

        # Fill TL Lattice Widget
        lattice = QSvgWidget('/home/sirius/repos/hla/pyqt-apps/'
                             'siriushla/tl_ap_control/' + SVG_FILE)
        self.centralwidget.widget_lattice.setLayout(QVBoxLayout())
        self.centralwidget.widget_lattice.layout().addWidget(lattice)

        # Create MenuBar and connect TL apps
        menubar = QMenuBar(self)
        menubar.setNativeMenuBar(False)
        # openLatticeAndTwiss = QAction("Show Lattice and Twiss", self)
        # _hlautil.connect_window(openLatticeAndTwiss, ShowLatticeAndTwiss,
        #                         parent=self, tl=self._tl)
        openPosAngCorrApp = QAction("Position and Angle Correction", self)
        _hlautil.connect_window(openPosAngCorrApp, ASAPPosAngCorr, parent=self,
                                prefix=self.prefix, tl=self._tl)
        openMAApp = QAction("MA", self)
        _hlautil.connect_window(openMAApp, PSTabControlWindow, parent=self,
                                section=self._tl.upper(), discipline='MA')
        openPMApp = QAction("PM", self)
        _hlautil.connect_window(openPMApp, PulsedMagnetControlWindow, self)
        openSOFB = QAction("SOFB", self)
        _hlautil.connect_newprocess(openSOFB, 'sirius-hla-tb-ap-sofb.py')
        openICTsApp = QAction("ICTs", self)
        _hlautil.connect_window(openICTsApp, ICTMonitoring, parent=self,
                                tl=self._tl, prefix=self.prefix)
        appsMenu = menubar.addMenu("Open...")
        # appsMenu.addAction(openLatticeAndTwiss)
        appsMenu.addAction(openPosAngCorrApp)
        appsMenu.addAction(openMAApp)
        appsMenu.addAction(openPMApp)
        appsMenu.addAction(openSOFB)
        appsMenu.addAction(openICTsApp)
        self.setMenuBar(menubar)

        # Create ButtonGroup to handle ScrnViews
        self._scrn_selection_widget = QButtonGroup(
            parent=self.centralwidget.groupBox_allcorrPanel)
        self._scrn_selection_widget.setExclusive(True)
        self._currScrn = 0

        # Connect and initialize reference widget
        self.centralwidget.pushButton_SaveRef.clicked.connect(
                                self._saveReference)
        self.reference_window = ShowImage(parent=self)
        self.centralwidget.pushButton_OpenRef.clicked.connect(
                                self._openReference)

        # Connect Slits View widget
        if self._tl == 'tb':
            self.slith = SlitMonitoring('H', self, self.prefix)
            self.centralwidget.widget_SlitH.setLayout(QHBoxLayout())
            self.centralwidget.widget_SlitH.layout().addWidget(self.slith)
            self.centralwidget.widget_SlitH.layout().setAlignment(
                Qt.AlignCenter)
            self.slitv = SlitMonitoring('V', self, self.prefix)
            self.centralwidget.widget_SlitV.setLayout(QHBoxLayout())
            self.centralwidget.widget_SlitV.layout().addWidget(self.slitv)
            self.centralwidget.widget_SlitV.layout().setAlignment(
                Qt.AlignCenter)

        # Create Scrn+Correctors Panel
        scrn_headerline = self._create_headerline(
            [['Screen', 11], ['Type-Sel', 6], ['Type-Sts', 5.81],
             ['Moving', 3.87]])
        ch_headerline = self._create_headerline(
            [['', 1.29], ['CH', 10], ['Kick-SP', 7.10], ['Kick-Mon', 5.81]])
        cv_headerline = self._create_headerline(
            [['', 1.29], ['CV', 10], ['Kick-SP', 7.10], ['Kick-Mon', 5.81]])
        hlay_headerline = QHBoxLayout()
        hlay_headerline.addWidget(self._create_headerline([['', 1.29]]))
        hlay_headerline.addWidget(scrn_headerline)
        hlay_headerline.addWidget(self._create_headerline([['', 1.29]]))
        hlay_headerline.addWidget(ch_headerline)
        hlay_headerline.addWidget(self._create_headerline([['', 1.29]]))
        hlay_headerline.addWidget(cv_headerline)
        hlay_headerline.addWidget(self._create_headerline([['', 1.29]]))
        headerline = QWidget()
        headerline.setObjectName('headerline')
        headerline.setLayout(hlay_headerline)
        headerline.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)

        correctors_vlayout = QVBoxLayout()
        correctors_vlayout.addWidget(headerline)

        for ch_group, cv, scrn, scrnprefix in self._corr_devicenames_list:
            hlay_scrncorr = QHBoxLayout()
            scrn_details = self._create_scrndetailwidget(scrnprefix, scrn)
            hlay_scrncorr.addWidget(self._create_headerline([['', 1.29]]))
            hlay_scrncorr.addWidget(scrn_details)
            ch_widget = QWidget()
            ch_widget.setObjectName('widget_CHs_Scrn' + str(scrn))
            ch_widget.setLayout(QVBoxLayout())
            for ch in ch_group:
                ch_details = self._create_correctordetailwidget(scrn, ch)
                ch_widget.layout().addWidget(ch_details)
            hlay_scrncorr.addWidget(self._create_headerline([['', 1.29]]))
            hlay_scrncorr.addWidget(ch_widget)
            cv_details = self._create_correctordetailwidget(scrn, cv)
            hlay_scrncorr.addWidget(self._create_headerline([['', 1.29]]))
            hlay_scrncorr.addWidget(cv_details)
            hlay_scrncorr.addWidget(self._create_headerline([['', 1.29]]))
            widget_scrncorr = QWidget()
            widget_scrncorr.setObjectName('widget_correctors_scrn')
            widget_scrncorr.setLayout(hlay_scrncorr)
            widget_scrncorr.layout().setContentsMargins(0, 9, 0, 9)

            widget_scrncorr.setStyleSheet(
                '#widget_correctors_scrn {border-top: 2px solid gray;}')
            correctors_vlayout.addWidget(widget_scrncorr)

        self.centralwidget.groupBox_allcorrPanel.setLayout(
            correctors_vlayout)
        self.centralwidget.groupBox_allcorrPanel.setContentsMargins(0, 0, 0, 0)
        self.centralwidget.groupBox_allcorrPanel.layout().setContentsMargins(
            0, 0, 0, 0)

        # Create only one ScrnView, and the rest on selecting other screens
        self.scrnview_widgets_dict = dict()
        wid_scrn = SiriusScrnView(
            parent=self, prefix=self.prefix,
            device=self._scrn_devicenames_list[self._currScrn])
        self.centralwidget.widget_Scrn.layout().addWidget(wid_scrn, 2, 0)
        wid_scrn.setVisible(True)
        self.scrnview_widgets_dict[self._currScrn] = wid_scrn
        pydmcombobox_scrntype = self.findChild(
            PyDMEnumComboBox,
            name='PyDMEnumComboBox_ScrnType_Sel_Scrn'+str(self._currScrn))
        pydmcombobox_scrntype.currentIndexChanged.connect(
            self.scrnview_widgets_dict[self._currScrn].
            updateCalibrationGridFlag)

        # Create an action menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Set central widget StyleSheets
        self.centralwidget.setStyleSheet("""
            #widget_{0}{{
                min-width:136em;}}
            #widget_ICTs{{
                min-width:42em;}}
            #tabWidget{{
                min-width:42em;}}
            #widget_Scrn{{
                min-width:42em;}}
            #widget_Ref{{
                min-width:42em;
                min-height:2.58em;}}
            #widget_lattice{{
                min-width:88em;
                min-height:16em;}}
            #groupBox_allcorrPanel{{
                min-width:90em;\n}}""".format(self._tl.upper()))
        self.centralwidget.layout().setRowStretch(0, 2)
        self.centralwidget.layout().setRowStretch(1, 16)
        self.centralwidget.layout().setRowStretch(2, 48)
        self.centralwidget.layout().setRowStretch(3, 3)
        self.centralwidget.layout().setColumnStretch(0, 42)
        self.centralwidget.layout().setColumnStretch(1, 90)

    def _allCHsTurnOn(self):
        for ch_group, _, _, _ in self._corr_devicenames_list:
            for ch in ch_group:
                pv = _epics.PV(self.prefix+ch+':PwrState-Sel')
                if pv.connected:
                    pv.put(1)
                    pv.disconnect()
                    pv = None

    def _allCVsTurnOn(self):
        for _, cv, _, _ in self._corr_devicenames_list:
            pv = _epics.PV(self.prefix+cv+':PwrState-Sel')
            if pv.connected:
                pv.put(1)
                pv.disconnect()
                pv = None

    def _allScrnsDoHoming(self):
        for scrn in self._scrn_devicenames_list:
            pv = _epics.PV(self.prefix+scrn+':ScrnType-Sel')
            if pv.connected:
                pv.put(0)
                pv.disconnect()
                pv = None

    def _create_headerline(self, labels):
        """Create and return a headerline."""
        hl = QWidget()
        hl.setLayout(QHBoxLayout())
        hl.layout().setContentsMargins(0, 0, 0, 0)

        for text, width in labels:
            label = QLabel(text, self)
            label.setStyleSheet("""
                min-width:valueem; max-width:valueem;
                font-weight:bold;
                qproperty-alignment: AlignCenter;
                """.replace('value', str(width)))
            label.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Fixed)
            hl.layout().addWidget(label)
        return hl

    def _create_scrndetailwidget(self, scrn_device, scrn_idx):
        """Create and return a screen detail widget."""
        scrn_details = QWidget()
        scrn_details.setObjectName('widget_Scrn' + str(scrn_idx) + 'TypeSel')
        scrn_details.setLayout(QGridLayout())
        scrn_details.layout().setContentsMargins(0, 0, 0, 0)
        scrn_details.layout().setAlignment(Qt.AlignHCenter)

        scrn_checkbox = QCheckBox(scrn_device)
        self._scrn_selection_widget.addButton(scrn_checkbox)
        self._scrn_selection_widget.setId(scrn_checkbox, scrn_idx)
        if scrn_idx == self._currScrn:
            scrn_checkbox.setChecked(True)
        scrn_checkbox.clicked.connect(self._setScrnWidget)
        scrn_checkbox.setStyleSheet("""
            min-width:11em; max-width:11em;
            height:1.29em; font-weight:bold;""")
        scrn_details.layout().addWidget(scrn_checkbox, 1, 1)

        pydmcombobox_scrntype = PyDMEnumComboBox(
            parent=self,
            init_channel=self.prefix+scrn_device+':ScrnType-Sel')
        pydmcombobox_scrntype.setObjectName(
            'PyDMEnumComboBox_ScrnType_Sel_Scrn' + str(scrn_idx))
        pydmcombobox_scrntype.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Fixed)
        pydmcombobox_scrntype.setStyleSheet(
            """min-width:5.81em;\nmax-width:5.81em;\nheight:1.29em;\n""")
        scrn_details.layout().addWidget(pydmcombobox_scrntype, 1, 2)

        pydmlabel_scrntype = PyDMLabel(
            parent=self,
            init_channel=self.prefix+scrn_device+':ScrnType-Sts')
        pydmlabel_scrntype.setStyleSheet(
            """min-width:5.81em;\nmax-width:5.81em;\nheight:1.29em;\n""")
        pydmlabel_scrntype.setAlignment(Qt.AlignCenter)
        scrn_details.layout().addWidget(pydmlabel_scrntype, 1, 3)

        led_scrntype = SiriusLedAlert(
            parent=self,
            init_channel=self.prefix+scrn_device+':ScrnType-Sts')
        led_scrntype.shape = 2
        led_scrntype.setObjectName('Led_ScrnType_Sts_Scrn' + str(scrn_idx))
        led_scrntype.setStyleSheet("""
            min-height:1.29em; max-height:1.29em; max-width:5.81em;""")
        scrn_details.layout().addWidget(led_scrntype, 2, 3)

        led_movests = PyDMLed(
            parent=self,
            init_channel=self.prefix+scrn_device+':DoneMov-Mon',
            color_list=[PyDMLed.LightGreen, PyDMLed.DarkGreen])
        led_movests.shape = 2
        led_movests.setObjectName('Led_DoneMov_Mon_Scrn' + str(scrn_idx))
        led_movests.setStyleSheet(
            """min-width:3.87em;\nmax-width:3.87em;\nmax-height:1.29em;\n""")
        scrn_details.layout().addWidget(led_movests, 1, 4)

        return scrn_details

    def _create_correctordetailwidget(self, scrn, corr):
        """Create and return a corrector detail widget."""
        name = corr.split('-')
        if len(name) > 2:
            name = name[-2]+name[-1]
        else:
            name = name[-1]

        corr_details = QWidget()
        corr_details.setObjectName(
            'widget_details_' + name + '_Scrn' + str(scrn))
        corr_details.setLayout(QGridLayout())
        corr_details.layout().setContentsMargins(0, 0, 0, 0)

        if corr.split('-')[0] == 'LA':  # Linac PVs
            led = SiriusLedState(
                parent=self,
                init_channel=self.prefix+corr+':setpwm')
            led.setObjectName(
                'SiriusLed_Linac'+corr.split('-')[-1]+'_setpwm_Scrn'+str(scrn))
            corr_details.layout().addWidget(led, 1, 1)

            label_corr = QLabel(corr, self, alignment=Qt.AlignCenter)
            label_corr.setObjectName('label_'+name+'App_Scrn'+str(scrn))
            label_corr.setStyleSheet("""
                max-width:9.68em;\nmin-width:9.68em;\n
                max-height:1.16em;\nmin-height:1.16em;\n""")
            corr_details.layout().addWidget(label_corr, 1, 2)

            pydm_sp_current = PyDMLinEditScrollbar(
                parent=self, channel=self.prefix+corr+':seti')
            pydm_sp_current.setObjectName(
                'LeditScroll_Linac'+corr.split('-')[-1]+'_seti_Scrn'+str(scrn))
            pydm_sp_current.layout.setContentsMargins(0, 0, 0, 0)
            pydm_sp_current.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
            pydm_sp_current.sp_lineedit.setStyleSheet("""
                min-width:7.10em;\nmax-width:7.10em;\n
                min-height:1.16em;\nmax-height:1.16em;\n""")
            pydm_sp_current.sp_lineedit.setAlignment(Qt.AlignCenter)
            pydm_sp_current.sp_lineedit.setSizePolicy(
                QSzPlcy.Minimum, QSzPlcy.Minimum)
            pydm_sp_current.sp_scrollbar.setStyleSheet("""max-width:7.10em;""")
            pydm_sp_current.sp_scrollbar.limitsFromPV = True
            corr_details.layout().addWidget(pydm_sp_current, 1, 3, 2, 1)

            pydmlabel_current = PyDMLabel(
                parent=self, init_channel=self.prefix+corr+':rdi')
            pydmlabel_current.unit_changed('A')
            pydmlabel_current.showUnits = True
            pydmlabel_current.setObjectName(
                'PyDMLabel_Linac'+corr.split('-')[-1]+'_rdi_Scrn'+str(scrn))
            pydmlabel_current.setStyleSheet(
                """min-width:5.81em;\nmax-width:5.81em;\nheight:1.29em;\n""")
            pydmlabel_current.precFromPV = True
            pydmlabel_current.setAlignment(Qt.AlignCenter)
            corr_details.layout().addWidget(pydmlabel_current, 1, 4)

        else:
            led = SiriusLedState(
                parent=self,
                init_channel=self.prefix+corr+':PwrState-Sts')
            led.setObjectName('SiriusLed_'+name+'_PwrState_Scrn'+str(scrn))
            corr_details.layout().addWidget(led, 1, 1)

            pushbutton = QPushButton(corr, self)
            pushbutton.setObjectName('pushButton_'+name+'App_Scrn'+str(scrn))
            if corr.split('-')[1].split(':')[1] == 'PM':
                _hlautil.connect_window(pushbutton, PulsedMagnetDetailWindow,
                                        parent=self, maname=corr)
            else:
                _hlautil.connect_window(pushbutton, PSDetailWindow,
                                        parent=self, psname=corr)
            pushbutton.setStyleSheet("""
                max-width:9.68em;\nmin-width:9.68em;\n
                max-height:1.16em;\nmin-height:1.16em;\n""")
            corr_details.layout().addWidget(pushbutton, 1, 2)

            pydm_sp_kick = PyDMLinEditScrollbar(
                parent=self, channel=self.prefix+corr+':Kick-SP')
            pydm_sp_kick.setObjectName(
                'PyDMLineEdit' + name + '_Kick_SP_Scrn' + str(scrn))
            pydm_sp_kick.layout.setContentsMargins(0, 0, 0, 0)
            pydm_sp_kick.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Maximum)
            pydm_sp_kick.sp_lineedit.setStyleSheet("""
                width:7.10em; min-height:1.16em; max-height:1.16em; """)
            pydm_sp_kick.sp_lineedit.setAlignment(Qt.AlignCenter)
            pydm_sp_kick.sp_lineedit.setSizePolicy(
                QSzPlcy.Minimum, QSzPlcy.Minimum)
            pydm_sp_kick.sp_scrollbar.setStyleSheet("""max-width:7.10em; """)
            pydm_sp_kick.sp_scrollbar.limitsFromPV = True
            corr_details.layout().addWidget(pydm_sp_kick, 1, 3, 2, 1)

            pydmlabel_kick = PyDMLabel(
                parent=self, init_channel=self.prefix+corr+':Kick-Mon')
            pydmlabel_kick.setObjectName(
                'PyDMLabel_' + name + '_Kick_Mon_Scrn' + str(scrn))
            pydmlabel_kick.setStyleSheet(
                """min-width:5.81em;\nmax-width:5.81em;\nheight:1.29em;""")
            pydmlabel_kick.precFromPV = True
            pydmlabel_kick.setAlignment(Qt.AlignCenter)
            corr_details.layout().addWidget(pydmlabel_kick, 1, 4)
        corr_details.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Fixed)
        return corr_details

    def _getTLData(self, tl):
        """Return transport line data based on input 'tl'."""
        if tl.lower() == 'tb':
            UI_FILE = ('ui_tb_ap_control.ui')
            SVG_FILE = ('TB.svg')

            ICT1 = 'TB-02:DI-ICT'
            ICT2 = 'TB-04:DI-ICT'

            correctors_list = [
                [['LA-CN:H1LCPS-10'], 'LA-CN:H1LCPS-9', 0, 'TB-01:DI-Scrn-1'],
                [['TB-01:MA-CH-1'], 'TB-01:MA-CV-1', 1, 'TB-01:DI-Scrn-2'],
                [['TB-01:MA-CH-2'], 'TB-01:MA-CV-2', 2, 'TB-02:DI-Scrn-1'],
                [['TB-02:MA-CH-1'], 'TB-02:MA-CV-1', 3, 'TB-02:DI-Scrn-2'],
                [['TB-02:MA-CH-2'], 'TB-02:MA-CV-2', 4, 'TB-03:DI-Scrn'],
                [['TB-03:MA-CH', 'TB-04:PM-InjSept'],
                 'TB-04:MA-CV-1', 5, 'TB-04:DI-Scrn']]
            scrn_list = ['TB-01:DI-Scrn-1', 'TB-01:DI-Scrn-2',
                         'TB-02:DI-Scrn-1', 'TB-02:DI-Scrn-2',
                         'TB-03:DI-Scrn', 'TB-04:DI-Scrn']
        elif tl.lower() == 'ts':
            UI_FILE = ('ui_ts_ap_control.ui')
            SVG_FILE = ('TS.svg')

            ICT1 = 'TS-01:DI-ICT'
            ICT2 = 'TS-04:DI-ICT'

            correctors_list = [
                [['TS-01:PM-EjeSeptF', 'TS-01:PM-EjeSeptG'],
                 'TS-01:MA-CV-1', 0, 'TS-01:DI-Scrn'],
                [['TS-01:MA-CH'], 'TS-01:MA-CV-2', 1, 'TS-02:DI-Scrn'],
                [['TS-02:MA-CH'], 'TS-02:MA-CV', 2, 'TS-03:DI-Scrn'],
                [['TS-03:MA-CH'], 'TS-03:MA-CV', 3, 'TS-04:DI-Scrn-1'],
                [['TS-04:MA-CH'], 'TS-04:MA-CV-1', 4, 'TS-04:DI-Scrn-2'],
                [['TS-04:PM-InjSeptG-1', 'TS-04:PM-InjSeptG-2',
                  'TS-04:PM-InjSeptF'], 'TS-04:MA-CV-2', 5,
                 'TS-04:DI-Scrn-3']]
            scrn_list = ['TS-01:DI-Scrn', 'TS-02:DI-Scrn',
                         'TS-03:DI-Scrn', 'TS-04:DI-Scrn-1',
                         'TS-04:DI-Scrn-2', 'TS-04:DI-Scrn-3']

        return [UI_FILE, SVG_FILE, ICT1, ICT2, correctors_list, scrn_list]

    def _openReference(self):
        """Load and show reference image."""
        home = _os.path.expanduser('~')
        path = _os.path.join(home, 'sirius-hlas', self._tl + '_ap_control')
        fn, _ = QFileDialog.getOpenFileName(
            self, 'Open Reference...', path,
            'Images (*.png *.xpm *.jpg);;All Files (*)')
        if fn:
            self.reference_window.load_image(fn)
            self.reference_window.show()

    def _saveReference(self):
        """Save reference image."""
        home = _os.path.expanduser('~')
        path = _os.path.join(home, 'sirius-hlas', self._tl + '_ap_control')
        if not _os.path.exists(path):
            _os.makedirs(path)
        fn, _ = QFileDialog.getSaveFileName(
            self, 'Save Reference As...',
            path + '/' + self._scrn_devicenames_list[self._currScrn] +
            _datetime.now().strftime('_%Y-%m-%d_%Hh%Mmin'),
            'Images (*.png *.xpm *.jpg);;All Files (*)')
        if not fn:
            return False
        lfn = fn.lower()
        if not lfn.endswith(('.png', '.jpg', '.xpm')):
            fn += '.png'

        reference = self.centralwidget.widget_Scrn.grab()
        reference.save(fn)

    @Slot()
    def _setScrnWidget(self):
        scrn_obj = self.scrnview_widgets_dict[self._currScrn]
        scrn_obj.setVisible(False)
        for child in scrn_obj.findChildren(PyDMWidget):
            for ch in child.channels():
                ch.disconnect()

        sender = self.sender()
        self._currScrn = self._scrn_selection_widget.id(sender)

        if self._currScrn not in self.scrnview_widgets_dict.keys():
            scrn_obj = SiriusScrnView(
                parent=self, prefix=self.prefix,
                device=self._scrn_devicenames_list[self._currScrn])
            self.centralwidget.widget_Scrn.layout().addWidget(scrn_obj, 2, 0)
            self.scrnview_widgets_dict[self._currScrn] = scrn_obj
        else:
            scrn_obj = self.scrnview_widgets_dict[self._currScrn]
            for child in scrn_obj.findChildren(PyDMWidget):
                for ch in child.channels():
                    ch.connect()

        self.scrnview_widgets_dict[self._currScrn].setVisible(True)

    @Slot(QPoint)
    def _show_context_menu(self, point):
        """Show a custom context menu."""
        turn_CHs_on = QAction("Turn CHs On", self)
        turn_CHs_on.triggered.connect(self._allCHsTurnOn)
        turn_CVs_on = QAction("Turn CVs On", self)
        turn_CVs_on.triggered.connect(self._allCVsTurnOn)
        do_scrn_homing = QAction("Screens do Homing", self)
        do_scrn_homing.triggered.connect(self._allScrnsDoHoming)
        menu = QMenu("Actions", self)
        menu.addAction(turn_CHs_on)
        menu.addAction(turn_CVs_on)
        menu.addAction(do_scrn_homing)
        menu.popup(self.mapToGlobal(point))

    def keyPressEvent(self, event):
        """Override keyPressEvent."""
        super().keyPressEvent(event)
        if self._tl == 'tb':
            self.slith.updateSlitWidget()
            self.slitv.updateSlitWidget()


# class ShowLatticeAndTwiss(SiriusMainWindow):
#     """Class to create Lattice and Twiss Widget."""
#
#     def __init__(self, parent=None, tl=None):
#         """Create Lattice and Twiss Graph."""
#         super(ShowLatticeAndTwiss, self).__init__(parent)
#         self.setWindowTitle(tl.upper() + ' Nominal Lattice and Twiss')
#         if tl == 'tb':
#             self._tl, self._twiss_in = _pymodels.tb.create_accelerator()
#             fam_data = _pymodels.tb.families.get_family_data(self._tl)
#             fam_mapping = _pymodels.tb.family_mapping
#         elif tl == 'ts':
#             self._tl, self._twiss_in = _pymodels.ts.create_accelerator()
#             fam_data = _pymodels.ts.families.get_family_data(self._tl)
#             fam_mapping = _pymodels.ts.family_mapping
#
#         self._tl_twiss, _ = _pyaccel.optics.calc_twiss(
#                                                     accelerator=self._tl,
#                                                     init_twiss=self._twiss_in)
#         self._fig, self._ax = _pyaccel.graphics.plot_twiss(
#                                                     accelerator=self._tl,
#                                                     twiss=self._tl_twiss,
#                                                     family_data=fam_data,
#                                                     family_mapping=fam_mapping,
#                                                     draw_edges=True,
#                                                     height=4,
#                                                     show_label=True)
#         self.centralwidget = QWidget()
#         self.centralwidget.setLayout(QVBoxLayout())
#         self.canvas = SiriusFigureCanvas(self._fig)
#         self.canvas.setParent(self.centralwidget)
#         self.centralwidget.layout().addWidget(self.canvas)
#         self.centralwidget.layout().setContentsMargins(0, 0, 0, 0)
#         self.setCentralWidget(self.centralwidget)
#         self.centralwidget.setStyleSheet("""min-width:90em;max-width:90em;""")


class ShowImage(SiriusMainWindow):
    """Class to create Show Reference Image Widget."""

    def __init__(self, parent=None):
        """Create label widget to handle image pixmap."""
        super(ShowImage, self).__init__(parent)
        self.label = QLabel()
        self.setCentralWidget(self.label)

    def load_image(self, filename):
        """Load pixmap from filename."""
        self.setWindowTitle(filename)
        self.pixmap = QPixmap(filename)
        self.label.setPixmap(self.pixmap)
        self.resize(self.sizeHint())


if __name__ == '__main__':
    """Run Example."""
    import os
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
    app = SiriusApplication()
    window = TLAPControlWindow(prefix=_vaca_prefix, tl='tb')
    window.show()
    sys.exit(app.exec_())
