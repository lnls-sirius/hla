
import numpy as np

from qtpy.QtGui import QPalette, QColor
from qtpy.QtCore import Qt, Slot, Signal
from qtpy.QtWidgets import QWidget, QGridLayout, QHBoxLayout, \
    QComboBox, QCheckBox, QLabel, QSpinBox, QPushButton
import qtawesome as qta
from pydm.widgets import PyDMWaveformPlot

from siriuspy.namesys import SiriusPVName
from siriushla.widgets import SiriusSpectrogramView


class BOTuneSpectrogram(SiriusSpectrogramView):
    """BO Tune Spectrogram View."""

    new_data = Signal(np.ndarray)
    buffer_size = Signal(str)

    def __init__(self, parent=None, prefix='', orientation='H',
                 background='w'):
        """Init."""
        self.prefix = prefix
        self.device = SiriusPVName(prefix + 'BO-Glob:DI-Tune-' + orientation)
        image_channel = self.device.substitute(dev='TuneProc')+':SpecArray-Mon'
        xaxis_channel = self.device + ':TuneFracArray-Mon'
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
                         background=background)
        self.normalizeData = True
        self.ROIColor = QColor('cyan')
        self.autoSetColorbarLims = False
        self.colorbar.setLimits([-120, 0])
        self.format_tooltip = '{0:.3f}, {1:.3f}'
        self.idx2send = 0
        self.buffer = list()
        self.nravgs = 1

    @Slot(np.ndarray)
    def image_value_changed(self, new_image):
        """Reimplement image_value_changed slot."""
        if new_image is None or new_image.size == 0:
            return
        spec_size = self._image_height*self._image_width
        self.image_waveform = new_image[:spec_size]
        self.needs_redraw = True

    def process_image(self, image):
        """Process data."""
        # Flip data in X axis
        image = np.flip(image, 0)

        # Truncate image
        if self.nravgs > 1 and len(self.buffer) >= 1:
            last_buff_shape = self.buffer[-1].shape
            image_shape = image.shape
            aux = np.zeros(last_buff_shape)
            if last_buff_shape > image_shape:
                aux[:image_shape[0], :image_shape[1]] += image
            elif last_buff_shape < image_shape:
                aux += image[:last_buff_shape[0], :last_buff_shape[1]]
            else:
                aux += image
            image = aux

        # Manage buffer
        self.buffer.append(image)
        if len(self.buffer) > self.nravgs:
            self.buffer.pop(0)
        self.buffer_size.emit(str(len(self.buffer)))

        # Perform average
        image = np.mean(self.buffer, axis=0)

        # Emit spectrum data
        self.new_data.emit(image[self.idx2send, :])

        # Return image
        return image

    def toggleXChannel(self):
        """Toggle X channel between FreqArray and TuneFracArray."""
        if 'TuneFracArray' in self._xaxischannel.address:
            new_ch = ':FreqArray-Mon'
        elif 'FreqArray' in self._xaxischannel.address:
            new_ch = ':TuneFracArray-Mon'
        # TODO: remove this command when bug in Tune is resolved
        self.resetBuffer()
        self.xAxisChannel = self.prefix + self.device + new_ch

    def setNrAvgs(self, new_nravgs):
        """Set number of averages, or, buffer size."""
        if new_nravgs >= 1:
            self.nravgs = new_nravgs
            while len(self.buffer) > self.nravgs:
                self.buffer.pop(0)

    def resetBuffer(self):
        """Reset buffer."""
        self.buffer = list()

    def mouseDoubleClickEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            pos = self._image_item.mapFromDevice(ev.pos())
            if pos.y() > 0 and pos.y() <= self._image_item.height():
                self.idx2send = int(pos.y())
        super().mouseDoubleClickEvent(ev)


class BOTuneSpectrumView(PyDMWaveformPlot):
    """BO Tune Spectrum View."""

    def __init__(self, parent=None, prefix='', orientation='H'):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = SiriusPVName(prefix + 'BO-Glob:DI-Tune-' + orientation)

        self.autoRangeX = True
        self.autoRangeY = True
        self.showLegend = False
        self.showXGrid = True
        self.showYGrid = True
        self.axisColor = QColor(0, 0, 0)
        self.backgroundColor = QColor(255, 255, 255)
        self.setLabels(left='Spectrum')
        leftAxis = self.getAxis('left')
        leftAxis.setStyle(autoExpandTextSpace=False, tickTextWidth=25)
        self.addChannel(
            y_channel='FAKE:Spectrum',
            x_channel=self.prefix+self.device+':TuneFracArray-Mon',
            redraw_mode=2, color='blue', lineWidth=1, lineStyle=Qt.SolidLine)
        self.curve = self.curveAtIndex(0)

    def toggleXChannel(self):
        """Toggle X channel between FreqArray and TuneFracArray."""
        if 'TuneFracArray' in self.curve.x_address:
            new_ch = ':FreqArray-Mon'
        elif 'FreqArray' in self.curve.x_address:
            new_ch = ':TuneFracArray-Mon'
        self.curve.x_address = self.prefix + self.device + new_ch
        self.curve.x_channel.connect()

    def receiveData(self, data):
        """Update curve."""
        self.curve.receiveYWaveform(data)
        self.curve.redrawCurve()


class BOTuneSpecControls(QWidget):
    """Booster Tune Spectrogram Controls."""

    def __init__(self, parent=None, prefix='', orientation='H',
                 title='', background='w'):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.orientation = orientation
        self.title = title
        self.background = background
        self._setupUi()

    def _setupUi(self):
        self.lb_title = QLabel(self.title, self, alignment=Qt.AlignCenter)

        self.spectrogram = BOTuneSpectrogram(
            self, self.prefix, self.orientation)
        self.spectrum = BOTuneSpectrumView(
            self, self.prefix, self.orientation)
        self.spectrogram.new_data.connect(self.spectrum.receiveData)

        self.cb_show_roi = QCheckBox('Show ROI', self)
        self.cb_show_roi.stateChanged.connect(self.spectrogram.showROI)
        self.cb_show_roi.setChecked(True)

        self.sb_nravgs = QSpinBox(self)
        self.sb_nravgs.setValue(1)
        self.sb_nravgs.setMinimum(1)
        self.sb_nravgs.setMaximum(100)
        self.sb_nravgs.valueChanged.connect(self.spectrogram.setNrAvgs)
        self.lb_buffsz = QLabel('1', self)
        self.lb_buffsz.setStyleSheet('min-width:1.29em;max-width:1.29em;')
        self.spectrogram.buffer_size.connect(self.lb_buffsz.setText)
        self.pb_resetbuff = QPushButton(
            qta.icon('mdi.delete-empty'), '', self)
        self.pb_resetbuff.setToolTip('Reset buffer')
        self.pb_resetbuff.setObjectName('resetbuff')
        self.pb_resetbuff.setStyleSheet(
            "#resetbuff{min-width:25px; max-width:25px; icon-size:20px;}")
        self.pb_resetbuff.clicked.connect(self.spectrogram.resetBuffer)

        self.cb_choose_x = QComboBox(self)
        self.cb_choose_x.addItem('Tune Fraction')
        self.cb_choose_x.addItem('Frequency')
        self.cb_choose_x.currentIndexChanged.connect(
            self.spectrogram.toggleXChannel)
        self.cb_choose_x.currentIndexChanged.connect(
            self.spectrum.toggleXChannel)

        hbox_ctrls = QHBoxLayout()
        hbox_ctrls.setContentsMargins(0, 0, 0, 0)
        hbox_ctrls.setSpacing(6)
        hbox_ctrls.addWidget(self.cb_show_roi)
        hbox_ctrls.addStretch()
        hbox_ctrls.addWidget(QLabel('Nr. Averages: '), alignment=Qt.AlignLeft)
        hbox_ctrls.addWidget(self.sb_nravgs, alignment=Qt.AlignLeft)
        hbox_ctrls.addWidget(self.lb_buffsz, alignment=Qt.AlignLeft)
        hbox_ctrls.addWidget(self.pb_resetbuff, alignment=Qt.AlignLeft)
        hbox_ctrls.addStretch()
        hbox_ctrls.addWidget(QLabel('X Axis: '), alignment=Qt.AlignRight)
        hbox_ctrls.addWidget(self.cb_choose_x, alignment=Qt.AlignRight)

        pal = self.palette()
        pal.setColor(QPalette.Background, self.background)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        lay = QGridLayout(self)
        lay.setHorizontalSpacing(9)
        lay.setVerticalSpacing(6)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.addWidget(self.lb_title, 0, 0, 1, 2)
        lay.addWidget(self.spectrogram, 1, 0)
        lay.addWidget(self.spectrum, 1, 1)
        lay.addLayout(hbox_ctrls, 2, 0, 1, 2)
