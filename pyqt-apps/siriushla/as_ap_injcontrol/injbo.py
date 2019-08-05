"""Booster Injection Control HLA module."""

from siriuspy.envars import vaca_prefix as _vaca_prefix

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout, QWidget, \
    QSizePolicy as QSzPlcy, QGroupBox, QLabel, QPushButton, QAction

from pydm.widgets import PyDMSpinbox, PyDMLabel, PyDMPushButton

from siriushla import util
from siriushla.as_ap_posang import CorrParamsDetailWindow
from siriushla.as_ap_injcontrol.base import BaseWindow


class InjBOControlWindow(BaseWindow):
    """Booster Injection Control HLA."""

    def __init__(self, parent=None, prefix=_vaca_prefix):
        super().__init__(parent, prefix)
        self.setWindowTitle('Booster Injection Control Window')
        self.setObjectName('BOApp')
        self.SVG_FILE = 'TB-BO.svg'
        self._scrns_dict = {0: 'BO-01D:DI-Scrn-1',
                            1: 'BO-01D:DI-Scrn-2',
                            2: 'BO-02U:DI-Scrn'}
        self._setupUi()
        self.lattice_wid.setStyleSheet('min-width:88em; min-height:18em;')

    def _setupMenu(self):
        PosAng = QAction("PosAng CH-Sept", self)
        util.connect_newprocess(
            PosAng, 'sirius-hla-tb-ap-posang.py', parent=self)
        self.menu.addAction(PosAng)
        PosAngCHCH = QAction("PosAng CH-CH", self)
        util.connect_newprocess(
            PosAngCHCH, 'sirius-hla-tb-ap-posang-chch.py',
            parent=self)
        self.menu.addAction(PosAngCHCH)

    def _setupDiagWidget(self):
        self.auxdig_wid = QWidget(self)

    def _setupScrnsCorrsWidget(self):
        # screens
        lay_screens = QVBoxLayout()
        lay_screens.setContentsMargins(0, 0, 0, 0)
        header_screens = self._create_headerline(
            [['', 0],
             ['Screen', 10], ['Camera', 3.5], ['Type-Sel', 5.8],
             ['Type-Sts', 5.8],
             ['', 0]])
        header_screens.setObjectName('header_screens')
        header_screens.setStyleSheet(
            '#header_screens {border-bottom: 2px solid gray;}')
        header_screens.layout().setContentsMargins(0, 9, 0, 9)
        header_screens.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        lay_screens.addWidget(header_screens)

        for idx, scrn_prefix in self._scrns_dict.items():
            w = self._create_scrn_summwidget(scrn_prefix, idx)
            w.layout().setContentsMargins(9, 9, 9, 9)
            lay_screens.addWidget(w)

        # correctors
        w_corr = QWidget()
        w_corr.setObjectName('w_corr')
        w_corr.setStyleSheet(
            '#w_corr {border-left: 2px solid gray;}')
        lay_corr = QGridLayout(w_corr)
        lay_corr.setContentsMargins(0, 0, 0, 0)
        lay_corr.setVerticalSpacing(60)
        lay_corr.setHorizontalSpacing(15)
        lay_corr.setAlignment(Qt.AlignTop)
        header_corrs = self._create_headerline(
            [['', 0],
             ['', 1.29], ['', 10], ['Kick-SP', 7.5], ['Kick-Mon', 5.8],
             ['', 0],
             ['', 1.29], ['', 10], ['Kick-SP', 7.5], ['Kick-Mon', 5.8],
             ['', 0]])
        header_corrs.setObjectName('header_corrs')
        header_corrs.setStyleSheet(
            '#header_corrs {border-bottom: 2px solid gray;}')
        header_corrs.layout().setContentsMargins(0, 9, 0, 9)
        header_corrs.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        lay_corr.addWidget(header_corrs, 0, 0, 1, 2)

        for corr, row, col in [['TB-04:MA-CH-1', 1, 0],
                               ['TB-04:MA-CH-2', 2, 0],
                               ['TB-04:MA-CV-1', 1, 1],
                               ['TB-04:MA-CV-2', 2, 1],
                               ['TB-04:PM-InjSept', 3, 0],
                               ['BO-01D:PM-InjKckr', 3, 1]]:
            w = self._create_corr_summwidget(corr)
            w.layout().setContentsMargins(9, 9, 9, 9)
            lay_corr.addWidget(w, row, col)

        # posang
        posang_prefix = self.prefix + 'TB-Glob:AP-PosAng'

        w_posang = QWidget()
        w_posang.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        w_posang.setObjectName('w_posang')
        w_posang.setStyleSheet(
            '#w_posang {border-top: 2px solid gray;}')
        lay_posang = QGridLayout(w_posang)
        lay_posang.setVerticalSpacing(9)
        lay_posang.setHorizontalSpacing(15)

        header_posang = self._create_headerline(
            [['', 0],
             ['', 1.29], ['Position and Angle Correction', 48.0],
             ['', 0]])
        header_posang.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        lay_posang.addWidget(header_posang, 0, 0, 1, 2)

        self.pb_update_ref = PyDMPushButton(
            label='Update Reference', parent=self,
            init_channel=posang_prefix+':SetNewRefKick-Cmd',
            pressValue=1)
        self.pb_update_ref.setStyleSheet('min-height: 2em;')
        lay_posang.addWidget(self.pb_update_ref, 1, 0, 1, 2)

        for col, title, axis in [[0, 'Horizontal', 'X'], [1, 'Vertical', 'Y']]:
            lb_pos = QLabel('<h4>Δ'+axis.lower()+'</h4>', self,
                            alignment=Qt.AlignRight)
            lb_pos.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
            pos_sp = PyDMSpinbox(
                parent=self, init_channel=posang_prefix+':DeltaPos'+axis+'-SP')
            pos_sp.setObjectName('pos_sp_'+axis.lower())
            pos_sp.showStepExponent = False
            pos_rb = PyDMLabel(
                parent=self, init_channel=posang_prefix+':DeltaPos'+axis+'-RB')
            pos_rb.setObjectName('pos_rb_'+axis.lower())
            lb_ang = QLabel('<h4>Δ'+axis.lower()+'\'</h4>', self,
                            alignment=Qt.AlignRight)
            lb_ang.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
            ang_sp = PyDMSpinbox(
                parent=self, init_channel=posang_prefix+':DeltaAng'+axis+'-SP')
            ang_sp.setObjectName('ang_sp_'+axis.lower())
            ang_sp.showStepExponent = False
            ang_rb = PyDMLabel(
                parent=self, init_channel=posang_prefix+':DeltaAng'+axis+'-RB')
            ang_rb.setObjectName('ang_rb_'+axis.lower())
            gbox_posang = QGroupBox(title, self)
            axlay = QGridLayout(gbox_posang)
            axlay.addWidget(lb_pos, 0, 0)
            axlay.addWidget(pos_sp, 0, 1)
            axlay.addWidget(pos_rb, 0, 2)
            axlay.addWidget(lb_ang, 1, 0)
            axlay.addWidget(ang_sp, 1, 1)
            axlay.addWidget(ang_rb, 1, 2)
            lay_posang.addWidget(gbox_posang, 2, col)

        self.pb_posang_settings = QPushButton('Settings', self)
        util.connect_window(self.pb_posang_settings, CorrParamsDetailWindow,
                            parent=self, tl='TB', prefix=self.prefix)
        lay_posang.addWidget(self.pb_posang_settings, 3, 0, 1, 2,
                             alignment=Qt.AlignRight)

        lay_posangref = QGridLayout()
        lay_posangref.setHorizontalSpacing(9)
        lay_posangref.setVerticalSpacing(9)
        lay_posangref.addWidget(QLabel('<h4>Reference Kicks</h4>', self,
                                       alignment=Qt.AlignCenter), 0, 0, 1, 7)
        for corr in ['CH1', 'CH2', 'CV1', 'CV2']:
            lb_corr = PyDMLabel(
                parent=self, init_channel=posang_prefix+':'+corr+'-Cte')
            lb_corr.setStyleSheet('font-weight:bold;')
            lb_refkick = PyDMLabel(
                parent=self, init_channel=posang_prefix+':RefKick'+corr+'-Mon')
            lb_refkick.showUnits = True
            col = 1 if 'CH' in corr else 4
            row = 0 if '1' in corr else 1
            lay_posangref.addWidget(lb_corr, row+1, col)
            lay_posangref.addWidget(lb_refkick, row+1, col+1)
        lay_posangref.setColumnStretch(0, 1)
        lay_posangref.setColumnStretch(1, 3)
        lay_posangref.setColumnStretch(2, 3)
        lay_posangref.setColumnStretch(3, 1)
        lay_posangref.setColumnStretch(4, 3)
        lay_posangref.setColumnStretch(5, 3)
        lay_posangref.setColumnStretch(6, 1)
        lay_posang.addLayout(lay_posangref, 4, 0, 1, 2)

        lay_corr.addWidget(w_posang, 4, 0, 1, 2)

        lay_corr.setRowStretch(0, 1)
        lay_corr.setRowStretch(1, 3)
        lay_corr.setRowStretch(2, 3)
        lay_corr.setRowStretch(3, 3)
        lay_corr.setRowStretch(4, 10)

        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addLayout(lay_screens)
        lay.addWidget(w_corr)
        self.corr_wid.setLayout(lay)


if __name__ == '__main__':
    import sys as _sys
    from siriushla.sirius_application import SiriusApplication

    application = SiriusApplication()
    w = InjBOControlWindow()
    w.show()
    _sys.exit(application.exec_())
