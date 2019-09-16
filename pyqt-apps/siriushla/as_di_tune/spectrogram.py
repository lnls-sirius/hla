
import numpy as np

from qtpy.QtGui import QPalette
from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
    QComboBox, QCheckBox

from siriuspy.namesys import SiriusPVName
from siriushla.widgets import SiriusSpectrogramView


class BOTuneSpec(SiriusSpectrogramView):
    """BO Tune Spectrogram View."""

    def __init__(self, parent=None, prefix='', orientation='H',
                 title='', background='w'):
        """Init."""
        self.device = SiriusPVName(prefix + 'BO-Glob:DI-Tune-' + orientation)
        self.prefix = prefix
        image_channel = self.device.substitute(dev='TuneProc')+':SpecArray-Mon'
        xaxis_channel = self.device + ':FreqArray-Mon'
        yaxis_channel = self.device + ':TimeArray-Mon'
        roioffx_channel = self.device + ':ROIOffXConv-RB'
        roioffy_channel = self.device + ':ROIOffYConv-RB'
        roiwidth_channel = self.device + ':ROIWidthConv-RB'
        roiheight_channel = self.device + ':ROIHeightConv-RB'
        super().__init__(parent=parent,
                         image_channel=image_channel,
                         xaxis_channel=xaxis_channel,
                         yaxis_channel=yaxis_channel,
                         roioffsetx_channel=roioffx_channel,
                         roioffsety_channel=roioffy_channel,
                         roiwidth_channel=roiwidth_channel,
                         roiheight_channel=roiheight_channel,
                         title=title,
                         background=background,
                         image_width=500)
        self.normalizeData = True

    @Slot(np.ndarray)
    def image_value_changed(self, new_image):
        """Reimplement image_value_changed slot."""
        if new_image is None or new_image.size == 0:
            return
        spec_size = self._image_height*self._image_width
        self.image_waveform = new_image[:spec_size]
        self.needs_redraw = True

    def process_image(self, image):
        """Flip data in time axis."""
        return np.flip(image, 0)

    def toggleXChannel(self):
        """Toggle X channel between FreqArray and TuneFracArray."""
        if 'TuneFracArray' in self._xaxischannel.address:
            self.xAxisChannel = self.prefix+self.device+':FreqArray-Mon'
        elif 'FreqArray' in self._xaxischannel.address:
            self.xAxisChannel = self.prefix+self.device+':TuneFracArray-Mon'


class BOTuneSpecControls(QWidget):
    """Booster Tune Spectrogram Controls."""

    def __init__(self, parent=None, prefix='', orientation='H',
                 title='', background='w'):
        super().__init__(parent)
        self.prefix = prefix
        self.orientation = orientation
        self.title = title
        self.background = background
        self._setupUi()

    def _setupUi(self):
        self.spec = BOTuneSpec(self, self.prefix, self.orientation,
                               self.title, self.background)

        self.cb_show_roi = QCheckBox('Show ROI', self)
        self.cb_show_roi.stateChanged.connect(self.spec.showROI)
        self.cb_show_roi.setChecked(True)

        self.cb_choose_x = QComboBox(self)
        self.cb_choose_x.addItem('Frequency')
        self.cb_choose_x.addItem('Tune Fraction')
        self.cb_choose_x.currentIndexChanged.connect(self.spec.toggleXChannel)

        hbox_ctrls = QHBoxLayout()
        hbox_ctrls.setContentsMargins(6, 0, 6, 6)
        hbox_ctrls.addWidget(self.cb_show_roi)
        hbox_ctrls.addWidget(self.cb_choose_x, alignment=Qt.AlignRight)

        pal = self.palette()
        pal.setColor(QPalette.Background, self.background)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.spec)
        lay.addLayout(hbox_ctrls)
