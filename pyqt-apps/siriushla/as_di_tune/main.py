from qtpy.QtGui import QColor
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QTabWidget, QVBoxLayout, \
    QLabel, QGroupBox, QHBoxLayout, QPushButton
import qtawesome as qta
from siriuspy.envars import VACA_PREFIX
from siriushla import util
from siriushla.widgets import SiriusMainWindow
from siriushla.as_ti_control import HLTriggerSimple
from .spectrogram import BOTuneSpectrogramControls
from .spectra import TuneSpectraControls
from .controls import TuneControls, SITuneMonitor


class Tune(SiriusMainWindow):
    """Tune Window."""

    def __init__(self, parent=None, prefix=VACA_PREFIX, section=''):
        super().__init__(parent)
        self.prefix = prefix
        self.section = section.upper()
        self.setObjectName(self.section+'App')
        self.setWindowTitle(self.section+' Tune')
        self.setWindowIcon(
            qta.icon('mdi.pulse',
                     color=util.get_appropriate_color(self.section)))
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        label = QLabel('<h2>'+self.section+' Tune<h2>', self,
                       alignment=Qt.AlignHCenter)
        label.setObjectName('label')
        label.setStyleSheet('#label{min-height: 1.29em; max-height: 1.29em;}')

        if self.section == 'SI':
            # Tune
            self.wid_tune_mon = SITuneMonitor(self, self.prefix)

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
        self.settings = QWidget()
        vbox_sett = QVBoxLayout(self.settings)
        vbox_sett.addWidget(self.tabCtrl)

        # Spectra view
        self.spectra_view = TuneSpectraControls(
            self, self.prefix, self.section)
        self.spectra_view.setObjectName('spectra_view')

        if self.section == 'BO':
            self.trig_gbox = QGroupBox('Trigger', self)
            self.trig_gbox.setLayout(QHBoxLayout())
            self.trig_gbox.layout().addWidget(HLTriggerSimple(
                self.trig_gbox,
                self.prefix + 'BO-Glob:TI-TuneProc',
                duration=True, nrpulses=True))
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

        self.pb_showsett = QPushButton('>', self)
        self.pb_showsett.setObjectName('showsett')
        self.pb_showsett.setToolTip('Hide settings')
        self.pb_showsett.setStyleSheet(
            '#showsett{min-width:0.7em;max-width:0.7em;}')
        self.pb_showsett.released.connect(self._handle_settings_vis)
        hbox_vis = QHBoxLayout()
        hbox_vis.addWidget(self.pb_showsett, alignment=Qt.AlignLeft)

        self.setStyleSheet(
            "#specH, #specV {min-width:40em; min-height: 18em;}"
            "#spectra_view {min-width:40em; min-height: 36em;}"
            "#wid_tuneh, #wid_tunev {border:2px solid gray;}")

        cw = QWidget(self)
        self.setCentralWidget(cw)
        lay = QVBoxLayout(cw)
        if self.section == 'BO':
            hbox = QHBoxLayout()
            hbox.addWidget(self.settings)
            hbox.addLayout(vbox_meas)
            hbox.addWidget(self.spectra_view)
            hbox.setStretch(0, 1)
            hbox.setStretch(1, 1)
            hbox.setStretch(2, 1)

            lay.addWidget(label)
            lay.addLayout(hbox)
            lay.addLayout(hbox_vis)
        else:
            hbox = QHBoxLayout()
            hbox.addWidget(self.settings)
            hbox.addWidget(self.spectra_view)
            hbox.setStretch(0, 1)
            hbox.setStretch(1, 1)

            lay.addWidget(label)
            lay.addWidget(self.wid_tune_mon)
            lay.addLayout(hbox)
            lay.addLayout(hbox_vis)

    def _handle_settings_vis(self):
        vis = self.settings.isVisible()
        text = '<' if vis else '>'
        ttip = 'Show' if vis else 'Hide'
        self.pb_showsett.setText(text)
        self.pb_showsett.setToolTip(ttip+' settings')
        self.settings.setVisible(not vis)
        self.sender().parent().adjustSize()
        self.centralWidget().adjustSize()
        self.adjustSize()
