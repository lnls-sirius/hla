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
from siriushla import util
from siriushla.widgets import PyDMLed, SiriusLedAlert, SiriusLedState, \
    SiriusMainWindow, PyDMLinEditScrollbar
# from siriushla.widgets import SiriusFigureCanvas
from siriushla.as_di_scrns import SiriusScrnView
from siriushla.as_ps_control import PSDetailWindow
from siriushla.as_pm_control import PulsedMagnetDetailWindow
from siriushla.tl_ap_control.Slit_monitor import SlitMonitoring


class TLAPControlWindow(SiriusMainWindow):
    """Class to create the main window for TB and TS HLA."""

    def __init__(self, parent=None, prefix=_vaca_prefix, tl=None):
        """Initialize widgets in main window."""
        super(TLAPControlWindow, self).__init__(parent)
        self.prefix = prefix
        self._tl = tl
        self.setObjectName(tl.upper()+'App')
        self.setWindowTitle(self._tl.upper() + ' Control Window')
        self._setupUi()

    def _setupUi(self):
        [UI_FILE, SVG_FILE, ICT1, ICT2, self._devices_dict] = \
            self._getTLData(self._tl)
        self._scrns_dict = {idx: scr for scr, [_, _, idx]
                            in self._devices_dict.items()}

        # Set central widget
        curr_dir = _os.path.abspath(_os.path.dirname(__file__)) + '/'
        tmp_file = _substitute_in_file(
            curr_dir + UI_FILE,
            {'PREFIX': self.prefix, 'ICT1': ICT1, 'ICT2': ICT2})
        self.centralwidget = loadUi(tmp_file)
        self.setCentralWidget(self.centralwidget)

        # Fill TL Lattice Widget
        lattice = QSvgWidget(curr_dir + SVG_FILE)
        self.centralwidget.widget_lattice.setLayout(QVBoxLayout())
        self.centralwidget.widget_lattice.layout().addWidget(lattice)

        # Create MenuBar and connect TL apps
        menubar = QMenuBar(self)
        menubar.setNativeMenuBar(False)
        appsMenu = menubar.addMenu("Open...")
        # openLatticeAndTwiss = QAction("Show Lattice and Twiss", self)
        # util.connect_window(openLatticeAndTwiss, ShowLatticeAndTwiss,
        #                         parent=self, tl=self._tl)
        # appsMenu.addAction(openLatticeAndTwiss)
        openPosAngApp = QAction("PosAng CH-Sept", self)
        util.connect_newprocess(
            openPosAngApp, 'sirius-hla-'+self._tl+'-ap-posang.py',
            parent=self)
        appsMenu.addAction(openPosAngApp)
        if self._tl == 'tb':
            openPosAngCHCHApp = QAction("PosAng CH-CH", self)
            util.connect_newprocess(
                openPosAngCHCHApp, 'sirius-hla-tb-ap-posang-chch.py',
                parent=self)
            appsMenu.addAction(openPosAngCHCHApp)
        openMAApp = QAction("MA", self)
        util.connect_newprocess(
            openMAApp, 'sirius-hla-'+self._tl+'-ma-control.py', parent=self)
        appsMenu.addAction(openMAApp)
        openPMApp = QAction("PM", self)
        util.connect_newprocess(
            openPMApp, 'sirius-hla-'+self._tl+'-pm-control.py', parent=self)
        appsMenu.addAction(openPMApp)
        openSOFB = QAction("SOFB", self)
        util.connect_newprocess(
            openSOFB, 'sirius-hla-'+self._tl+'-ap-sofb.py', parent=self)
        appsMenu.addAction(openSOFB)
        openICTsApp = QAction("ICTs", self)
        util.connect_newprocess(
            openICTsApp, 'sirius-hla-'+self._tl+'-di-icts.py', parent=self)
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
        correctors_vlayout = QVBoxLayout()
        correctors_vlayout.setContentsMargins(0, 0, 0, 0)

        headerline = self._create_headerline(
            [['', 0],
             ['Screen', 10], ['Camera', 3.5], ['Type-Sel', 5.8],
             ['Type-Sts', 5.8],
             ['', 0],
             ['', 1.29], ['CH', 10], ['Kick-SP', 7.5], ['Kick-Mon', 5.8],
             ['', 0],
             ['', 1.29], ['CV', 10], ['Kick-SP', 7.5], ['Kick-Mon', 5.8],
             ['', 0]])
        headerline.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        correctors_vlayout.addWidget(headerline)

        for scrnprefix, devices in self._devices_dict.items():
            ch_group, cv_group, scrn = devices

            scrn_details = self._create_scrndetailwidget(scrnprefix, scrn)
            scrn_details.layout().setContentsMargins(0, 9, 0, 9)

            ch_widget = QWidget()
            ch_widget.setLayout(QVBoxLayout())
            ch_widget.layout().setContentsMargins(0, 9, 0, 9)
            for ch in ch_group:
                ch_details = self._create_correctordetailwidget(scrn, ch)
                ch_widget.layout().addWidget(ch_details)

            cv_widget = QWidget()
            cv_widget.setLayout(QVBoxLayout())
            cv_widget.layout().setContentsMargins(0, 9, 0, 9)
            for cv in cv_group:
                cv_details = self._create_correctordetailwidget(scrn, cv)
                cv_widget.layout().addWidget(cv_details)

            hlay_scrncorr = QHBoxLayout()
            hlay_scrncorr.setContentsMargins(0, 0, 0, 0)
            hlay_scrncorr.addStretch()
            hlay_scrncorr.addWidget(scrn_details)
            hlay_scrncorr.addStretch()
            hlay_scrncorr.addWidget(ch_widget)
            hlay_scrncorr.addStretch()
            hlay_scrncorr.addWidget(cv_widget)
            hlay_scrncorr.addStretch()
            widget_scrncorr = QWidget()
            widget_scrncorr.setObjectName('widget_correctors_scrn')
            widget_scrncorr.setLayout(hlay_scrncorr)
            widget_scrncorr.setStyleSheet(
                '#widget_correctors_scrn {border-top: 2px solid gray;}')
            correctors_vlayout.addWidget(widget_scrncorr)

        self.centralwidget.groupBox_allcorrPanel.setLayout(correctors_vlayout)

        # Create only one ScrnView, and the rest on selecting other screens
        self.scrnview_widgets_dict = dict()
        wid_scrn = SiriusScrnView(
            parent=self, prefix=self.prefix,
            device=self._scrns_dict[self._currScrn])
        self.centralwidget.widget_Scrn.layout().addWidget(wid_scrn, 2, 0)
        wid_scrn.setVisible(True)
        self.scrnview_widgets_dict[self._currScrn] = wid_scrn

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
        self.centralwidget.layout().setRowStretch(2, 44)
        self.centralwidget.layout().setRowStretch(3, 3)
        self.centralwidget.layout().setColumnStretch(0, 42)
        self.centralwidget.layout().setColumnStretch(1, 90)

    def _allCHsTurnOn(self):
        for ch_group, _, _, in self._devices_dict.values():
            for ch in ch_group:
                pv = _epics.PV(self.prefix+ch+':PwrState-Sel')
                if pv.connected:
                    pv.put(1)
                    pv.disconnect()
                    pv = None

    def _allCVsTurnOn(self):
        for _, cv, _, in self._devices_dict.values():
            pv = _epics.PV(self.prefix+cv+':PwrState-Sel')
            if pv.connected:
                pv.put(1)
                pv.disconnect()
                pv = None

    def _allScrnsDoHoming(self):
        for scrn in self._devices_dict.keys():
            pv = _epics.PV(self.prefix+scrn+':ScrnType-Sel')
            if pv.connected:
                pv.put(0)
                pv.disconnect()
                pv = None

    def _create_headerline(self, labels):
        """Create and return a headerline."""
        hl = QWidget()
        hl.setLayout(QHBoxLayout())
        hl.layout().setContentsMargins(0, 9, 0, 0)

        glay = None
        for text, width in labels:
            if not width:
                if glay:
                    hl.layout().addLayout(glay)
                hl.layout().addStretch()
                glay = QGridLayout()
                glay.setAlignment(Qt.AlignCenter)
                glay.setContentsMargins(0, 0, 0, 0)
                c = 0
            else:
                label = QLabel(text, self)
                label.setStyleSheet("""
                    min-width:valueem; min-height:1.29em; max-height:1.29em;
                    font-weight:bold; qproperty-alignment: AlignCenter;
                    """.replace('value', str(width)))
                glay.addWidget(label, 0, c)
                c += 1
        return hl

    def _create_scrndetailwidget(self, scrn_device, scrn_idx):
        """Create and return a screen detail widget."""
        scrn_details = QWidget()
        scrn_details.setObjectName('widget_Scrn' + str(scrn_idx) + 'TypeSel')
        scrn_details.setLayout(QGridLayout())
        scrn_details.layout().setAlignment(Qt.AlignCenter)

        scrn_checkbox = QCheckBox(scrn_device)
        self._scrn_selection_widget.addButton(scrn_checkbox)
        self._scrn_selection_widget.setId(scrn_checkbox, scrn_idx)
        if scrn_idx == self._currScrn:
            scrn_checkbox.setChecked(True)
        scrn_checkbox.clicked.connect(self._setScrnWidget)
        scrn_checkbox.setStyleSheet("""
            min-width:10em; max-width:10em; font-weight:bold;""")
        scrn_details.layout().addWidget(scrn_checkbox, 1, 1)

        camenbl = SiriusLedState(
            parent=self, init_channel=self.prefix+scrn_device+':CamEnbl-Sts')
        camenbl.setStyleSheet("min-width:3.5em; max-width:3.5em;")
        scrn_details.layout().addWidget(camenbl, 1, 2)

        pydmcombobox_scrntype = PyDMEnumComboBox(
            parent=self, init_channel=self.prefix+scrn_device+':ScrnType-Sel')
        pydmcombobox_scrntype.setObjectName(
            'PyDMEnumComboBox_ScrnType_Sel_Scrn' + str(scrn_idx))
        pydmcombobox_scrntype.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Fixed)
        pydmcombobox_scrntype.setStyleSheet("min-width:5.8em;max-width:5.8em;")
        scrn_details.layout().addWidget(pydmcombobox_scrntype, 1, 3)

        pydmlabel_scrntype = PyDMLabel(
            parent=self, init_channel=self.prefix+scrn_device+':ScrnType-Sts')
        pydmlabel_scrntype.setStyleSheet("min-width:5.8em; max-width:5.8em;")
        pydmlabel_scrntype.setAlignment(Qt.AlignCenter)
        scrn_details.layout().addWidget(pydmlabel_scrntype, 1, 4)

        led_scrntype = PyDMLed(
            parent=self, init_channel=self.prefix+scrn_device+':ScrnType-Sts',
            color_list=[PyDMLed.LightGreen, PyDMLed.Red, PyDMLed.Red,
                        PyDMLed.Yellow])
        led_scrntype.shape = 2
        led_scrntype.setObjectName('Led_ScrnType_Sts_Scrn' + str(scrn_idx))
        led_scrntype.setStyleSheet("""min-width:5.8em; max-width:5.8em;""")
        scrn_details.layout().addWidget(led_scrntype, 2, 4)

        return scrn_details

    def _create_correctordetailwidget(self, scrn, corr):
        """Create and return a corrector detail widget."""
        name = corr.split('-')
        if len(name) > 2:
            name = name[-2]+name[-1]
        else:
            name = name[-1]

        corr_details = QWidget()
        corr_details.setObjectName('widget_details_'+name+'_Scrn'+str(scrn))
        corr_details.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        corr_details.setLayout(QGridLayout())
        corr_details.layout().setContentsMargins(0, 0, 0, 0)
        corr_details.layout().setAlignment(Qt.AlignCenter)

        if corr.split('-')[0] == 'LI':  # Linac PVs
            led = SiriusLedAlert(
                parent=self, init_channel=self.prefix+corr+':rdpwm')
            led.onColor = SiriusLedAlert.LightGreen
            led.offColor = SiriusLedAlert.DarkGreen
            led.alarmSensitiveBorder = False
            led.setObjectName(
                'SiriusLed_Linac'+corr.split('-')[-1]+'_rdpwm_Scrn'+str(scrn))
            led.setStyleSheet("max-width:1.29em;")
            corr_details.layout().addWidget(led, 1, 1)

            label_corr = QLabel(corr, self, alignment=Qt.AlignCenter)
            label_corr.setObjectName('label_'+name+'App_Scrn'+str(scrn))
            label_corr.setStyleSheet("""
                max-width:10em; min-width:10em; min-height:1.29em;""")
            corr_details.layout().addWidget(label_corr, 1, 2)

            pydm_sp_current = PyDMLinEditScrollbar(
                parent=self, channel=self.prefix+corr+':seti')
            pydm_sp_current.setObjectName(
                'LeditScroll_Linac'+corr.split('-')[-1]+'_seti_Scrn'+str(scrn))
            pydm_sp_current.layout.setContentsMargins(0, 0, 0, 0)
            pydm_sp_current.layout.setSpacing(3)
            pydm_sp_current.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
            pydm_sp_current.sp_lineedit.setStyleSheet("""
                min-width:7.5em; max-width:7.5em; min-height:1.29em;""")
            pydm_sp_current.sp_lineedit.setAlignment(Qt.AlignCenter)
            pydm_sp_current.sp_lineedit.setSizePolicy(
                QSzPlcy.Ignored, QSzPlcy.Fixed)
            pydm_sp_current.sp_scrollbar.setStyleSheet("""max-width:7.5em;""")
            pydm_sp_current.sp_scrollbar.limitsFromPV = True
            corr_details.layout().addWidget(pydm_sp_current, 1, 3, 2, 1)

            pydmlabel_current = PyDMLabel(
                parent=self, init_channel=self.prefix+corr+':rdi')
            pydmlabel_current.unit_changed('A')
            pydmlabel_current.showUnits = True
            pydmlabel_current.setObjectName(
                'PyDMLabel_Linac'+corr.split('-')[-1]+'_rdi_Scrn'+str(scrn))
            pydmlabel_current.setStyleSheet("""
                min-width:5.8em; max-width:5.8em; min-height: 1.29em;""")
            pydmlabel_current.precFromPV = True
            pydmlabel_current.setAlignment(Qt.AlignCenter)
            corr_details.layout().addWidget(pydmlabel_current, 1, 4)

        else:
            led = SiriusLedState(
                parent=self, init_channel=self.prefix+corr+':PwrState-Sts')
            led.setObjectName('SiriusLed_'+name+'_PwrState_Scrn'+str(scrn))
            led.setStyleSheet("max-width:1.29em;")
            corr_details.layout().addWidget(led, 1, 1)

            pushbutton = QPushButton(corr, self)
            pushbutton.setObjectName('pushButton_'+name+'App_Scrn'+str(scrn))
            if corr.split('-')[1].split(':')[1] == 'PM':
                util.connect_window(pushbutton, PulsedMagnetDetailWindow,
                                    parent=self, maname=corr)
            else:
                util.connect_window(pushbutton, PSDetailWindow,
                                    parent=self, psname=corr)
            pushbutton.setStyleSheet("""
                min-width:10em; max-width:10em; min-height:1.29em;""")
            corr_details.layout().addWidget(pushbutton, 1, 2)

            pydm_sp_kick = PyDMLinEditScrollbar(
                parent=self, channel=self.prefix+corr+':Kick-SP')
            pydm_sp_kick.setObjectName(
                'PyDMLineEdit' + name + '_Kick_SP_Scrn' + str(scrn))
            pydm_sp_kick.layout.setContentsMargins(0, 0, 0, 0)
            pydm_sp_kick.layout.setSpacing(3)
            pydm_sp_kick.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Maximum)
            pydm_sp_kick.sp_lineedit.setStyleSheet("""
                min-width:7.5em; max-width:7.5em; min-height:1.29em;""")
            pydm_sp_kick.sp_lineedit.setAlignment(Qt.AlignCenter)
            pydm_sp_kick.sp_lineedit.setSizePolicy(
                QSzPlcy.Minimum, QSzPlcy.Minimum)
            pydm_sp_kick.sp_lineedit.precisionFromPV = False
            pydm_sp_kick.sp_lineedit.precision = 1
            pydm_sp_kick.sp_scrollbar.setStyleSheet("""max-width:7.5em;""")
            pydm_sp_kick.sp_scrollbar.limitsFromPV = True
            corr_details.layout().addWidget(pydm_sp_kick, 1, 3, 2, 1)

            pydmlabel_kick = PyDMLabel(
                parent=self, init_channel=self.prefix+corr+':Kick-Mon')
            pydmlabel_kick.setObjectName(
                'PyDMLabel_' + name + '_Kick_Mon_Scrn' + str(scrn))
            pydmlabel_kick.setStyleSheet("""
                min-width:5.8em; max-width:5.8em; min-height:1.29em;""")
            pydmlabel_kick.showUnits = True
            pydmlabel_kick.precisionFromPV = False
            pydmlabel_kick.precision = 1
            pydmlabel_kick.setAlignment(Qt.AlignCenter)
            corr_details.layout().addWidget(pydmlabel_kick, 1, 4)
        return corr_details

    def _getTLData(self, tl):
        """Return transport line data based on input 'tl'."""
        if tl.lower() == 'tb':
            UI_FILE = ('ui_tb_ap_control.ui')
            SVG_FILE = ('TB.svg')

            ICT1 = 'TB-02:DI-ICT'
            ICT2 = 'TB-04:DI-ICT'

            devices_dict = {
                'TB-01:DI-Scrn-1': [['LI-01:PS-CH-7'], ['LI-01:PS-CV-7'], 0],
                'TB-01:DI-Scrn-2': [['TB-01:MA-CH-1'], ['TB-01:MA-CV-1'], 1],
                'TB-02:DI-Scrn-1': [['TB-01:MA-CH-2'], ['TB-01:MA-CV-2'], 2],
                'TB-02:DI-Scrn-2': [['TB-02:MA-CH-1'], ['TB-02:MA-CV-1'], 3],
                'TB-03:DI-Scrn':   [['TB-02:MA-CH-2'], ['TB-02:MA-CV-2'], 4],
                'TB-04:DI-Scrn':   [
                    ['TB-04:MA-CH-1', 'TB-04:MA-CH-2', 'TB-04:PM-InjSept'],
                    ['TB-04:MA-CV-1', 'TB-04:MA-CV-2'], 5]}
        elif tl.lower() == 'ts':
            UI_FILE = ('ui_ts_ap_control.ui')
            SVG_FILE = ('TS.svg')

            ICT1 = 'TS-01:DI-ICT'
            ICT2 = 'TS-04:DI-ICT'

            devices_dict = {
                'TS-01:DI-Scrn':   [['TS-01:PM-EjeSeptF', 'TS-01:PM-EjeSeptG'],
                                    ['TS-01:MA-CV-1'], 0],
                'TS-02:DI-Scrn':   [['TS-01:MA-CH'], ['TS-01:MA-CV-2'], 1],
                'TS-03:DI-Scrn':   [['TS-02:MA-CH'], ['TS-02:MA-CV'], 2],
                'TS-04:DI-Scrn-1': [['TS-03:MA-CH'], ['TS-03:MA-CV'], 3],
                'TS-04:DI-Scrn-2': [['TS-04:MA-CH'], ['TS-04:MA-CV-1'], 4],
                'TS-04:DI-Scrn-3': [
                    ['TS-04:PM-InjSeptG-1', 'TS-04:PM-InjSeptG-2',
                     'TS-04:PM-InjSeptF'], ['TS-04:MA-CV-2'], 5]}

        return [UI_FILE, SVG_FILE, ICT1, ICT2, devices_dict]

    def _openReference(self):
        """Load and show reference image."""
        home = _os.path.expanduser('~')
        folder_month = _datetime.now().strftime('%Y-%m')
        folder_day = _datetime.now().strftime('%Y-%m-%d')
        path = _os.path.join(
            home, 'Desktop', 'screen-iocs', folder_month, folder_day)
        fn, _ = QFileDialog.getOpenFileName(
            self, 'Open Reference...', path,
            'Images (*.png *.xpm *.jpg);;All Files (*)')
        if fn:
            self.reference_window.load_image(fn)
            self.reference_window.show()

    def _saveReference(self):
        """Save reference image."""
        home = _os.path.expanduser('~')
        folder_month = _datetime.now().strftime('%Y-%m')
        folder_day = _datetime.now().strftime('%Y-%m-%d')
        path = _os.path.join(
            home, 'Desktop', 'screen-iocs', folder_month, folder_day)
        if not _os.path.exists(path):
            _os.makedirs(path)
        fn, _ = QFileDialog.getSaveFileName(
            self, 'Save Reference As...',
            path + '/' + self._scrns_dict[self._currScrn] +
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

        sender = self.sender()
        self._currScrn = self._scrn_selection_widget.id(sender)

        if self._currScrn not in self.scrnview_widgets_dict.keys():
            scrn_obj = SiriusScrnView(
                parent=self, prefix=self.prefix,
                device=self._scrns_dict[self._currScrn])
            self.centralwidget.widget_Scrn.layout().addWidget(scrn_obj, 2, 0)
            self.scrnview_widgets_dict[self._currScrn] = scrn_obj
        else:
            scrn_obj = self.scrnview_widgets_dict[self._currScrn]

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
