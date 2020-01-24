from qtpy.QtGui import QColor
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QTabWidget, QVBoxLayout, \
    QLabel

from siriuspy.envars import vaca_prefix
from siriushla.widgets import SiriusMainWindow
from .spectrogram import BOTuneSpectrogramControls
from .spectra import TuneSpectraControls
from .controls import TuneControls
from .details import BOTuneTrigger


class Tune(SiriusMainWindow):
    """Tune Window."""

    def __init__(self, parent=None, prefix=vaca_prefix, section=''):
        super().__init__(parent)
        self.prefix = prefix
        self.section = section.upper()
        self.setObjectName(self.section+'App')
        self.setWindowTitle(self.section+' Tune')
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        label = QLabel('<h2>'+self.section+' Tune<h2>', self,
                       alignment=Qt.AlignHCenter)
        label.setObjectName('label')
        label.setStyleSheet('#label{min-height: 1.29em; max-height: 1.29em;}')

        # Settings
        self.tabCtrl = QTabWidget(self)
        hcolor = QColor(179, 229, 255)
        vcolor = QColor(255, 179, 179)
        self.ctrlH = TuneControls(parent=self, prefix=self.prefix,
                                  section=self.section, orientation='H',
                                  background=hcolor)
        self.tabCtrl.addTab(self.ctrlH, 'Horizontal')
        self.ctrlV = TuneControls(parent=self, prefix=self.prefix,
                                  section=self.section, orientation='V',
                                  background=vcolor)
        self.tabCtrl.addTab(self.ctrlV, 'Vertical')
        self.tabCtrl.setStyleSheet("""
            QTabWidget::pane {
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }
            QTabBar::tab:first {
                background-color: #B3E5FF;
            }
            QTabBar::tab:last {
                background-color: #FFB3B3;
            }
            """)
        vbox_sett = QVBoxLayout()
        vbox_sett.addWidget(self.tabCtrl)

        # Spectra view
        self.spectra_view = TuneSpectraControls(
            self, self.prefix, self.section)
        self.spectra_view.setObjectName('spectra_view')

        if self.section == 'BO':
            self.trig_gbox = BOTuneTrigger(self, self.prefix)
            vbox_sett.addWidget(self.trig_gbox)

            # Sepctrograms
            self.specH = BOTuneSpectrogramControls(
                parent=self, prefix=self.prefix, orientation='H',
                title='<h3>Horizontal</h3>', background=hcolor)
            self.specH.setObjectName('specH')
            self.specV = BOTuneSpectrogramControls(
                parent=self, prefix=self.prefix, orientation='V',
                title='<h3>Vertical</h3>', background=vcolor)
            self.specV.setObjectName('specV')
            vbox_meas = QVBoxLayout()
            vbox_meas.addWidget(self.specH)
            vbox_meas.addSpacing(10)
            vbox_meas.addWidget(self.specV)

            # Connect signals
            self.specH.spectrogram.idx2send_changed.connect(
                self.specV.update_idx2plot)
            self.specH.sb_idx2plot.editingFinished.connect(
                self.specV.update_idx2plot)
            self.specH.pb_resetbuff.clicked.connect(
                self.specV.spectrogram.resetBuffer)
            self.specH.sb_buffsz.editingFinished.connect(
                self.specV.update_buffsize)
            self.specV.spectrogram.idx2send_changed.connect(
                self.specH.update_idx2plot)
            self.specV.sb_idx2plot.editingFinished.connect(
                self.specH.update_idx2plot)
            self.specV.pb_resetbuff.clicked.connect(
                self.specH.spectrogram.resetBuffer)
            self.specV.sb_buffsz.editingFinished.connect(
                self.specH.update_buffsize)
            self.specH.spectrogram.new_data.connect(
                self.spectra_view.spectra.receiveDataH)
            self.specV.spectrogram.new_data.connect(
                self.spectra_view.spectra.receiveDataV)

        self.setStyleSheet(
            "#specH, #specV {min-width:40em;}"
            "#spectra_view {min-width:40em;}")

        cw = QWidget(self)
        lay = QGridLayout(cw)
        lay.addWidget(label, 0, 0, 1, 3)
        lay.addLayout(vbox_sett, 1, 0)
        if self.section == 'BO':
            lay.addLayout(vbox_meas, 1, 1)
            lay.addWidget(self.spectra_view, 1, 2)
            lay.setColumnStretch(0, 1)
            lay.setColumnStretch(1, 1)
            lay.setColumnStretch(2, 1)
        else:
            lay.addWidget(self.spectra_view, 1, 1)
            lay.setColumnStretch(0, 1)
            lay.setColumnStretch(1, 1)
        self.setCentralWidget(cw)
