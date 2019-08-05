#!/usr/bin/env python-sirius
"""HLA TB and TS AP Control Window."""

from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QAction, \
    QSizePolicy as QSzPlcy, QTabWidget
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla import util
from siriushla.as_di_icts import ICTSummary
from siriushla.as_di_slits import SlitMonitoring
from siriushla.as_ap_injcontrol.base import BaseWindow


class TLControlWindow(BaseWindow):
    """Class to create the main window for TB and TS HLA."""

    def __init__(self, parent=None, prefix=_vaca_prefix, tl=None):
        """Initialize widgets in main window."""
        super().__init__(parent, prefix)
        self.setWindowTitle(tl.upper() + ' Control Window')
        self.setObjectName(tl.upper()+'App')
        self.tl = tl.lower()
        self.SVG_FILE = tl.upper() + '.svg'
        self._devices_dict = self._getTLData()
        self._scrns_dict = {idx: scr for scr, [_, _, idx]
                            in self._devices_dict.items()}
        self._setupUi()

    def _setupMenu(self):
        # LatticeAndTwiss = QAction("Show Lattice and Twiss", self)
        # util.connect_window(LatticeAndTwiss, ShowLatticeAndTwiss,
        #                         parent=self, tl=self.tl)
        # self.menu.addAction(LatticeAndTwiss)
        MA = QAction("MA", self)
        util.connect_newprocess(
            MA, 'sirius-hla-'+self.tl+'-ma-control.py', parent=self)
        self.menu.addAction(MA)
        PM = QAction("PM", self)
        util.connect_newprocess(
            PM, 'sirius-hla-'+self.tl+'-pm-control.py', parent=self)
        self.menu.addAction(PM)
        SOFB = QAction("SOFB", self)
        util.connect_newprocess(
            SOFB, 'sirius-hla-'+self.tl+'-ap-sofb.py', parent=self)
        self.menu.addAction(SOFB)
        ICTs = QAction("ICTs", self)
        util.connect_newprocess(
            ICTs, 'sirius-hla-'+self.tl+'-di-icts.py', parent=self)
        self.menu.addAction(ICTs)

    def _setupScrnsCorrsWidget(self):
        lay = QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)

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
        lay.addWidget(headerline)

        for scrnprefix, devices in self._devices_dict.items():
            ch_group, cv_group, scrn_idx = devices

            scrn_details = self._create_scrn_summwidget(scrnprefix, scrn_idx)
            scrn_details.setObjectName(scrnprefix)
            scrn_details.layout().setContentsMargins(0, 9, 0, 9)

            ch_widget = QWidget()
            ch_widget.setLayout(QVBoxLayout())
            ch_widget.layout().setContentsMargins(0, 9, 0, 9)
            for ch in ch_group:
                ch_details = self._create_corr_summwidget(ch)
                ch_details.setObjectName(ch)
                ch_widget.layout().addWidget(ch_details)

            cv_widget = QWidget()
            cv_widget.setLayout(QVBoxLayout())
            cv_widget.layout().setContentsMargins(0, 9, 0, 9)
            for cv in cv_group:
                cv_details = self._create_corr_summwidget(cv)
                cv_details.setObjectName(ch)
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
            lay.addWidget(widget_scrncorr)

        self.corr_wid.setLayout(lay)

    def _setupDiagWidget(self):
        self.ictmon = ICTSummary(self, prefix=self.prefix, tl=self.tl)
        if self.tl == 'tb':
            self.auxdig_wid = QTabWidget()
            self.auxdig_wid.setStyleSheet("""
                QTabBar::tab{margin-top: 0em;}""")
            self.auxdig_wid.addTab(self.ictmon, 'ICTs')
            self.slith = SlitMonitoring('H', self, self.prefix)
            self.auxdig_wid.addTab(self.slith, 'Slit H')
            self.slitv = SlitMonitoring('V', self, self.prefix)
            self.auxdig_wid.addTab(self.slitv, 'Slit V')
        elif self.tl == 'ts':
            self.auxdig_wid = QWidget()
            lay = QVBoxLayout()
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addStretch()
            lay.addWidget(self.ictmon)
            lay.addStretch()
            self.auxdig_wid.setLayout(lay)

    def _getTLData(self):
        """Return transport line data based on input 'tl'."""
        if self.tl == 'tb':
            devices_dict = {
                'TB-01:DI-Scrn-1': [['LI-01:PS-CH-7'], ['LI-01:PS-CV-7'], 0],
                'TB-01:DI-Scrn-2': [['TB-01:MA-CH-1'], ['TB-01:MA-CV-1'], 1],
                'TB-02:DI-Scrn-1': [['TB-01:MA-CH-2'], ['TB-01:MA-CV-2'], 2],
                'TB-02:DI-Scrn-2': [['TB-02:MA-CH-1'], ['TB-02:MA-CV-1'], 3],
                'TB-03:DI-Scrn':   [['TB-02:MA-CH-2'], ['TB-02:MA-CV-2'], 4],
                'TB-04:DI-Scrn':   [['TB-04:MA-CH-1'], ['TB-04:MA-CV-1'], 5]}
        elif self.tl == 'ts':
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
        return devices_dict

    def keyPressEvent(self, event):
        """Override keyPressEvent."""
        super().keyPressEvent(event)
        if self.tl == 'tb':
            self.slith.updateSlitWidget()
            self.slitv.updateSlitWidget()


# import pyaccel as _pyaccel
# import pymodels as _pymodels
# from siriushla.widgets import SiriusFigureCanvas
#
#
# class ShowLatticeAndTwiss(SiriusMainWindow):
#     """Class to create Lattice and Twiss Widget."""
#
#     def __init__(self, parent=None, tl=None):
#         """Create Lattice and Twiss Graph."""
#         super(ShowLatticeAndTwiss, self).__init__(parent)
#         self.setWindowTitle(tl.upper() + ' Nominal Lattice and Twiss')
#         if tl == 'tb':
#             self.tl, self._twiss_in = _pymodels.tb.create_accelerator()
#             fam_data = _pymodels.tb.families.get_family_data(self.tl)
#             fam_mapping = _pymodels.tb.family_mapping
#         elif tl == 'ts':
#             self.tl, self._twiss_in = _pymodels.ts.create_accelerator()
#             fam_data = _pymodels.ts.families.get_family_data(self.tl)
#             fam_mapping = _pymodels.ts.family_mapping
#
#         self.tl_twiss, _ = _pyaccel.optics.calc_twiss(
#                                                     accelerator=self.tl,
#                                                     init_twiss=self._twiss_in)
#         self._fig, self._ax = _pyaccel.graphics.plot_twiss(
#                                                     accelerator=self.tl,
#                                                     twiss=self.tl_twiss,
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


if __name__ == '__main__':
    """Run Example."""
    import os
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
    app = SiriusApplication()
    window = TLControlWindow(prefix=_vaca_prefix, tl='tb')
    window.show()
    sys.exit(app.exec_())
