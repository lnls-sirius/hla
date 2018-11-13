#!/usr/bin/env python-sirius
"""HLA TB and TS AP Control Window."""

import os as _os
from datetime import datetime as _datetime
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)
import epics as _epics
from qtpy.uic import loadUi
from qtpy.QtCore import Slot, Qt, QPoint
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, \
                            QSpacerItem, QFileDialog, QAction, QMenuBar, \
                            QWidget, QLabel, QPushButton, QMenu, \
                            QButtonGroup, QCheckBox, QSizePolicy as QSzPlcy
from qtpy.QtGui import QPixmap
from qtpy.QtSvg import QSvgWidget
from pydm.widgets import PyDMLabel, PyDMEnumComboBox
from pydm.widgets.base import PyDMWidget
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
import pyaccel as _pyaccel
import pymodels as _pymodels
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla import util as _hlautil
from siriushla.widgets import PyDMLed, SiriusLedAlert, SiriusLedState, \
                              SiriusMainWindow, SiriusScrnView, \
                              PyDMLinEditScrollbar
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

    def __init__(self, parent=None, prefix='', tl=None):
        """Initialize widgets in main window."""
        super(TLAPControlWindow, self).__init__(parent)
        self.prefix = prefix
        self._tl = tl
        self.setWindowTitle(self._tl.upper() + ' Control Window')
        self._setupUi()

    def _setupUi(self):
        [UI_FILE, SVG_FILE, self._corr_devicenames_list,
            self._scrn_devicenames_list] = self._getTLData(self._tl)

        # Define prefixes to substitute in file
        if self._tl == 'tb':
            ICT1 = 'TB-02:DI-ICT'
            ICT2 = 'TB-04:DI-ICT'
        elif self._tlt == 'ts':
            ICT1 = 'TS-01:DI-ICT'
            ICT2 = 'TS-04:DI-ICT'

        # Set central widget
        tmp_file = _substitute_in_file(
            '/home/fac_files/lnls-sirius/hla/pyqt-apps/siriushla'
            '/tl_ap_control/' + UI_FILE,
            {'PREFIX': self.prefix, 'ICT1': ICT1, 'ICT2': ICT2})
        self.centralwidget = loadUi(tmp_file)
        self.setCentralWidget(self.centralwidget)

        # Fill TL Lattice Widget
        lattice = QSvgWidget('/home/fac_files/lnls-sirius/hla/pyqt-apps/'
                             'siriushla/tl_ap_control/' + SVG_FILE)
        self.centralwidget.widget_lattice.setLayout(QVBoxLayout())
        self.centralwidget.widget_lattice.layout().addWidget(lattice)

        # Create MenuBar and connect TL apps
        menubar = QMenuBar(self)
        menubar.setNativeMenuBar(False)
        openLatticeAndTwiss = QAction("Show Lattice and Twiss", self)
        _hlautil.connect_window(openLatticeAndTwiss, ShowLatticeAndTwiss,
                                parent=self, tl=self._tl)
        openPosAngCorrApp = QAction("Position and Angle Correction", self)
        _hlautil.connect_window(openPosAngCorrApp, ASAPPosAngCorr, parent=self,
                                prefix=self.prefix, tl=self._tl)
        openMAApp = QAction("MA", self)
        _hlautil.connect_window(openMAApp, PSTabControlWindow, parent=self,
                                section=self._tl.upper(), discipline=1)  # MA
        openPMApp = QAction("PM", self)
        _hlautil.connect_window(openPMApp, PulsedMagnetControlWindow, self)
        openSOFB = QAction("SOFB", self)
        _hlautil.connect_newprocess(openSOFB, 'sirius-hla-tb-ap-sofb.py')
        appsMenu = menubar.addMenu("Open...")
        appsMenu.addAction(openLatticeAndTwiss)
        appsMenu.addAction(openPosAngCorrApp)
        appsMenu.addAction(openMAApp)
        appsMenu.addAction(openPMApp)
        appsMenu.addAction(openSOFB)
        if self._tl == 'tb':
            openICTsApp = QAction("ICTs", self)
            _hlautil.connect_window(openICTsApp, ICTMonitoring, parent=self,
                                    tl=self._tl, prefix=self.prefix)
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
            self.centralwidget.widget_SlitH.layout().setAlignment(
                Qt.AlignHCenter | Qt.AlignVCenter)
            self.centralwidget.widget_SlitH.layout().addWidget(
                SlitMonitoring('H', self, self.prefix))
            self.centralwidget.widget_SlitV.layout().setAlignment(
                Qt.AlignHCenter | Qt.AlignVCenter)
            self.centralwidget.widget_SlitV.layout().addWidget(
                SlitMonitoring('V', self, self.prefix))

        # Create Scrn+Correctors Panel
        hlay_headerline = QHBoxLayout()
        hlay_headerline.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        scrn_headerline = self._create_headerline(
            [['Screen', 300], ['Type-Sel', 180], ['Type-Sts', 180],
             ['Moving', 120]])
        hlay_headerline.addWidget(scrn_headerline)
        hlay_headerline.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        ch_headerline = self._create_headerline(
            [['', 40], ['CH', 300], ['Kick-SP', 220], ['Kick-Mon', 180]])
        hlay_headerline.addWidget(ch_headerline)
        hlay_headerline.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        cv_headerline = self._create_headerline(
            [['', 40], ['CV', 300], ['Kick-SP', 220], ['Kick-Mon', 180]])
        hlay_headerline.addWidget(cv_headerline)
        hlay_headerline.setAlignment(Qt.AlignVCenter)
        hlay_headerline.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        headerline = QWidget()
        headerline.setObjectName('headerline')
        headerline.setMaximumHeight(60)
        headerline.setStyleSheet('* { font-weight:bold; }')
        headerline.setLayout(hlay_headerline)
        headerline.layout().setContentsMargins(0, 9, 0, 9)

        correctors_gridlayout = QGridLayout()
        correctors_gridlayout.addWidget(headerline, 1, 1)

        line = 2
        for ch_group, cv, scrn, scrnprefix in self._corr_devicenames_list:
            hlay_scrncorr = QHBoxLayout()
            hlay_scrncorr.addItem(
                QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
            scrn_details = self._create_scrndetailwidget(scrnprefix, scrn)
            hlay_scrncorr.addWidget(scrn_details)
            hlay_scrncorr.addItem(
                QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
            ch_widget = QWidget()
            ch_widget.setObjectName('widget_CHs_Scrn' + str(scrn))
            ch_widget.setLayout(QVBoxLayout())
            ch_widget.layout().setContentsMargins(0, 0, 0, 0)
            for ch in ch_group:
                ch_details = self._create_correctordetailwidget(scrn, ch)
                ch_widget.layout().addWidget(ch_details)
            hlay_scrncorr.addWidget(ch_widget)
            hlay_scrncorr.addItem(
                QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
            cv_details = self._create_correctordetailwidget(scrn, cv)
            hlay_scrncorr.addWidget(cv_details)
            hlay_scrncorr.addItem(
                QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
            widget_scrncorr = QWidget()
            widget_scrncorr.setObjectName('widget_correctors_scrn')
            widget_scrncorr.setLayout(hlay_scrncorr)
            widget_scrncorr.layout().setContentsMargins(0, 9, 0, 9)

            widget_scrncorr.setStyleSheet(
                '#widget_correctors_scrn {border-top: 2px solid gray;}')
            correctors_gridlayout.addWidget(widget_scrncorr, line, 1)
            line += 1

        self.centralwidget.groupBox_allcorrPanel.setLayout(
            correctors_gridlayout)
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
        hl.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Minimum)
        hl.layout().setContentsMargins(0, 0, 0, 0)

        for text, width in labels:
            label = QLabel(text, self, alignment=Qt.AlignHCenter)
            label.setFixedWidth(width)
            hl.layout().addWidget(label)
        return hl

    def _create_scrndetailwidget(self, scrn_device, scrn_idx):
        """Create and return a screen detail widget."""
        scrn_details = QWidget()
        scrn_details.setObjectName('widget_Scrn' + str(scrn_idx) + 'TypeSel')
        scrn_details.setLayout(QGridLayout())
        scrn_details.layout().setContentsMargins(0, 0, 0, 0)
        scrn_details.layout().setAlignment(Qt.AlignHCenter)

        scrn_details.layout().addItem(
            QSpacerItem(2, 15, QSzPlcy.Fixed, QSzPlcy.Fixed), 0, 1)

        scrn_checkbox = QCheckBox(scrn_device)
        self._scrn_selection_widget.addButton(scrn_checkbox)
        self._scrn_selection_widget.setId(scrn_checkbox, scrn_idx)
        if scrn_idx == self._currScrn:
            scrn_checkbox.setChecked(True)
        scrn_checkbox.clicked.connect(self._setScrnWidget)
        scrn_checkbox.setFixedWidth(300)
        scrn_checkbox.setStyleSheet('font-weight:bold;')
        scrn_details.layout().addWidget(scrn_checkbox, 1, 1)

        pydmcombobox_scrntype = PyDMEnumComboBox(
            parent=self,
            init_channel=self.prefix+scrn_device+':ScrnType-Sel')
        pydmcombobox_scrntype.setObjectName(
            'PyDMEnumComboBox_ScrnType_Sel_Scrn' + str(scrn_idx))
        pydmcombobox_scrntype.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Fixed)
        pydmcombobox_scrntype.setFixedSize(180, 40)
        scrn_details.layout().addWidget(pydmcombobox_scrntype, 1, 2)

        pydmlabel_scrntype = PyDMLabel(
            parent=self,
            init_channel=self.prefix+scrn_device+':ScrnType-Sts')
        pydmlabel_scrntype.setFixedSize(180, 40)
        pydmlabel_scrntype.setAlignment(Qt.AlignCenter)
        scrn_details.layout().addWidget(pydmlabel_scrntype, 1, 3)

        led_scrntype = SiriusLedAlert(
            parent=self,
            init_channel=self.prefix+scrn_device+':ScrnType-Sts')
        led_scrntype.shape = 2
        led_scrntype.setObjectName(
            'Led_ScrnType_Sts_Scrn' + str(scrn_idx))
        led_scrntype.setFixedHeight(40)
        scrn_details.layout().addWidget(led_scrntype, 2, 3)

        led_movests = PyDMLed(
            parent=self,
            init_channel=self.prefix+scrn_device+':DoneMov-Mon',
            color_list=[PyDMLed.LightGreen, PyDMLed.DarkGreen])
        led_movests.shape = 2
        led_movests.setObjectName(
            'Led_DoneMov_Mon_Scrn' + str(scrn_idx))
        led_movests.setFixedSize(120, 40)
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
            led.setFixedSize(40, 40)
            corr_details.layout().addWidget(led, 1, 1)

            label_corr = QLabel(corr, self, alignment=Qt.AlignCenter)
            label_corr.setObjectName('label_'+name+'App_Scrn'+str(scrn))
            label_corr.setFixedSize(300, 40)
            corr_details.layout().addWidget(label_corr, 1, 2)

            pydm_sp_current = PyDMLinEditScrollbar(
                parent=self, channel=self.prefix+corr+':seti')
            pydm_sp_current.setObjectName(
                'LeditScroll_Linac'+corr.split('-')[-1]+'_seti_Scrn'+str(scrn))
            pydm_sp_current.setMaximumWidth(220)
            pydm_sp_current.layout.setContentsMargins(0, 0, 0, 0)
            pydm_sp_current.sp_lineedit.setFixedSize(220, 40)
            pydm_sp_current.sp_lineedit.setAlignment(Qt.AlignCenter)
            pydm_sp_current.sp_lineedit.setSizePolicy(
                QSzPlcy.Minimum, QSzPlcy.Minimum)
            pydm_sp_current.sp_scrollbar.limitsFromPV = True
            pydm_sp_current.sp_scrollbar.setSizePolicy(
                QSzPlcy.Minimum, QSzPlcy.Maximum)
            corr_details.layout().addWidget(pydm_sp_current, 1, 3, 2, 1)

            pydmlabel_current = PyDMLabel(
                parent=self, init_channel=self.prefix+corr+':rdi')
            pydmlabel_current.unit_changed('A')
            pydmlabel_current.showUnits = True
            pydmlabel_current.setObjectName(
                'PyDMLabel_Linac'+corr.split('-')[-1]+'_rdi_Scrn'+str(scrn))
            pydmlabel_current.setFixedSize(180, 40)
            pydmlabel_current.precFromPV = True
            pydmlabel_current.setAlignment(Qt.AlignCenter)
            corr_details.layout().addWidget(pydmlabel_current, 1, 4)

        else:
            led = SiriusLedState(
                parent=self,
                init_channel=self.prefix+corr+':PwrState-Sts')
            led.setObjectName('SiriusLed_'+name+'_PwrState_Scrn'+str(scrn))
            led.setFixedSize(40, 40)
            corr_details.layout().addWidget(led, 1, 1)

            pushbutton = QPushButton(corr, self)
            pushbutton.setObjectName('pushButton_'+name+'App_Scrn'+str(scrn))
            if corr.split('-')[1].split(':')[1] == 'PM':
                _hlautil.connect_window(pushbutton, PulsedMagnetDetailWindow,
                                        parent=self, maname=corr)
            else:
                _hlautil.connect_window(pushbutton, PSDetailWindow,
                                        parent=self, psname=corr)
            pushbutton.setFixedSize(300, 40)
            corr_details.layout().addWidget(pushbutton, 1, 2)

            pydm_sp_kick = PyDMLinEditScrollbar(
                parent=self, channel=self.prefix+corr+':Kick-SP')
            pydm_sp_kick.setObjectName(
                'PyDMLineEdit' + name + '_Kick_SP_Scrn' + str(scrn))
            pydm_sp_kick.setMaximumWidth(220)
            pydm_sp_kick.layout.setContentsMargins(0, 0, 0, 0)
            pydm_sp_kick.sp_lineedit.setFixedSize(220, 40)
            pydm_sp_kick.sp_lineedit.setAlignment(Qt.AlignCenter)
            pydm_sp_kick.sp_lineedit.setSizePolicy(
                QSzPlcy.Minimum, QSzPlcy.Minimum)
            pydm_sp_kick.sp_scrollbar.limitsFromPV = True
            pydm_sp_kick.sp_scrollbar.setSizePolicy(
                QSzPlcy.Minimum, QSzPlcy.Maximum)
            corr_details.layout().addWidget(pydm_sp_kick, 1, 3, 2, 1)

            pydmlabel_kick = PyDMLabel(
                parent=self, init_channel=self.prefix+corr+':Kick-Mon')
            pydmlabel_kick.setObjectName(
                'PyDMLabel_' + name + '_Kick_Mon_Scrn' + str(scrn))
            pydmlabel_kick.setFixedSize(180, 40)
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

        return [UI_FILE, SVG_FILE, correctors_list, scrn_list]

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


if __name__ == '__main__':
    """Run Example."""
    import os
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
    app = SiriusApplication()
    _hlautil.set_style(app)
    window = TLAPControlWindow(prefix=_vaca_prefix, tl='tb')
    window.show()
    sys.exit(app.exec_())
