import os
from datetime import datetime
import time
from functools import partial as _part
import numpy as np

from qtpy.QtGui import QPalette, QColor
from qtpy.QtCore import Qt, Slot, Signal
from qtpy.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, \
    QComboBox, QCheckBox, QLabel, QSpinBox, QPushButton, QMenu, QSpacerItem, \
    QSizePolicy as QSzPlcy, QFileDialog
import qtawesome as qta
from pydm.widgets import PyDMWaveformPlot

from siriuspy.namesys import SiriusPVName
from siriushla.widgets import SiriusSpectrogramView


class BOTuneSpectrogram(SiriusSpectrogramView):
    """BO Tune Spectrogram View."""

    new_data = Signal(np.ndarray)
    buffer_curr_size = Signal(str)
    buffer_data_size = Signal(int)
    buffer_size_changed = Signal(int)
    idx2send_changed = Signal(int)

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
        # self.autoSetColorbarLims = False
        # self.colorbar.setLimits([-120, 0])
        self.format_tooltip = '{0:.3f}, {1:.3f}'
        self._idx2send = 0
        self.buffer = list()
        self.last_data = None
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
        self.buffer_curr_size.emit(str(len(self.buffer)))

        # Perform average
        image = np.mean(self.buffer, axis=0)

        # update last data
        self.last_data = image
        last_data_size = self.last_data.shape[0]-1
        self.buffer_data_size.emit(last_data_size)
        if self.nravgs == 1 and self._idx2send < last_data_size:
            # Emit spectrum data
            self.new_data.emit(image[self._idx2send, :])

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

    def setBufferSize(self, new_size):
        """Set number of averages, or, buffer size."""
        if new_size >= 1:
            self.nravgs = new_size
            while len(self.buffer) > self.nravgs:
                self.buffer.pop(0)
            self.buffer_size_changed.emit(self.nravgs)

    def resetBuffer(self):
        """Reset buffer."""
        self.buffer = list()

    def getDataIndex(self):
        """Return index of the spectrogram to send in new_data signal."""
        return self._idx2send

    def setIndex2Send(self, new_idx):
        """Set index of the spectrogram to send in new_data signal."""
        max_idx = self.buffer[-1].shape[0] - 1
        if new_idx > max_idx:
            self._idx2send = max_idx
        else:
            self._idx2send = new_idx
        self.new_data.emit(self.last_data[self._idx2send, :])

    def mouseDoubleClickEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            pos = self._image_item.mapFromDevice(ev.pos())
            if not self._image_item.height():
                pass
            elif pos.y() > 0 and pos.y() <= self._image_item.height():
                self._idx2send = int(pos.y())
                self.idx2send_changed.emit(self._idx2send)
                if self.last_data is not None:
                    self.new_data.emit(self.last_data[self._idx2send, :])
        super().mouseDoubleClickEvent(ev)


class BOTuneSpectrogramControls(QWidget):
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

        self.cb_show_roi = QCheckBox('Show ROI', self)
        self.cb_show_roi.stateChanged.connect(self.spectrogram.showROI)
        self.cb_show_roi.setChecked(True)

        self.sb_idx2plot = QSpinBox(self)
        self.sb_idx2plot.editingFinished.connect(self.update_idx2plot)
        self.lb_idx2plot = QLabel('0')
        self.spectrogram.idx2send_changed.connect(self.update_idx2plot)
        self.spectrogram.buffer_data_size.connect(self.sb_idx2plot.setMaximum)

        self.sb_buffsz = QSpinBox(self)
        self.sb_buffsz.setValue(1)
        self.sb_buffsz.setMinimum(1)
        self.sb_buffsz.setMaximum(100)
        self.sb_buffsz.editingFinished.connect(self.update_buffsize)
        self.lb_buffsz = QLabel('1', self)
        self.lb_buffsz.setStyleSheet('min-width:1.29em;max-width:1.29em;')
        self.spectrogram.buffer_curr_size.connect(self.lb_buffsz.setText)
        self.pb_resetbuff = QPushButton(
            qta.icon('mdi.delete-empty'), '', self)
        self.pb_resetbuff.setToolTip('Reset buffer')
        self.pb_resetbuff.setObjectName('resetbuff')
        self.pb_resetbuff.setStyleSheet(
            "#resetbuff{min-width:25px; max-width:25px; icon-size:20px;}")
        self.pb_resetbuff.clicked.connect(self.spectrogram.resetBuffer)

        self.cb_choose_x = QComboBox(self)
        self.cb_choose_x.addItem('Tune Frac.')
        self.cb_choose_x.addItem('Frequency')
        self.cb_choose_x.currentIndexChanged.connect(
            self.spectrogram.toggleXChannel)

        hbox_ctrls = QHBoxLayout()
        hbox_ctrls.setContentsMargins(0, 0, 0, 0)
        hbox_ctrls.setSpacing(6)
        hbox_ctrls.addWidget(self.cb_show_roi)
        hbox_ctrls.addStretch()
        hbox_ctrls.addWidget(QLabel('Plot Index:'), alignment=Qt.AlignLeft)
        hbox_ctrls.addWidget(self.sb_idx2plot, alignment=Qt.AlignLeft)
        hbox_ctrls.addWidget(self.lb_idx2plot, alignment=Qt.AlignLeft)
        hbox_ctrls.addStretch()
        hbox_ctrls.addWidget(QLabel('Buff.:'), alignment=Qt.AlignLeft)
        hbox_ctrls.addWidget(self.sb_buffsz, alignment=Qt.AlignLeft)
        hbox_ctrls.addWidget(self.lb_buffsz, alignment=Qt.AlignLeft)
        hbox_ctrls.addWidget(self.pb_resetbuff, alignment=Qt.AlignLeft)
        hbox_ctrls.addStretch()
        hbox_ctrls.addWidget(QLabel('X Axis:'), alignment=Qt.AlignRight)
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
        lay.addLayout(hbox_ctrls, 2, 0, 1, 2)

    def update_idx2plot(self, value=None):
        if not value:
            value = self.sender().value()
        self.sb_idx2plot.blockSignals(True)
        self.sb_idx2plot.setValue(value)
        self.lb_idx2plot.setText(str(value))
        self.spectrogram.setIndex2Send(value)
        self.sb_idx2plot.blockSignals(False)

    def update_buffsize(self):
        value = self.sender().value()
        self.sb_buffsz.blockSignals(True)
        self.sb_buffsz.setValue(value)
        self.spectrogram.setBufferSize(value)
        self.sb_buffsz.blockSignals(False)


class BOTuneSpectraView(PyDMWaveformPlot):
    """BO Tune Spectra View."""

    def __init__(self, parent=None, prefix=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix

        self.autoRangeX = True
        self.autoRangeY = True
        self.showLegend = False
        self.showXGrid = True
        self.showYGrid = True
        self.axisColor = QColor(0, 0, 0)
        self.backgroundColor = QColor(255, 255, 255)
        self.showLegend = True
        leftAxis = self.getAxis('left')
        leftAxis.setStyle(autoExpandTextSpace=False, tickTextWidth=25)

        self.addChannel(
            y_channel='FAKE:SpectrumH', name='Tune H',
            x_channel=self.prefix+'BO-Glob:DI-Tune-H:TuneFracArray-Mon',
            redraw_mode=2, color='blue', lineWidth=2, lineStyle=Qt.SolidLine)
        self.curveH = self.curveAtIndex(0)
        self.curveH.setVisible(True)

        self.addChannel(
            y_channel='FAKE:SpectrumV', name='Tune V',
            x_channel=self.prefix+'BO-Glob:DI-Tune-V:TuneFracArray-Mon',
            redraw_mode=2, color='red', lineWidth=2, lineStyle=Qt.SolidLine)
        self.curveV = self.curveAtIndex(1)
        self.curveV.setVisible(True)

    def toggleXChannel(self):
        """Toggle X channel between FreqArray and TuneFracArray."""
        if 'TuneFracArray' in self.curveH.x_address:
            new_ch = ':FreqArray-Mon'
        elif 'FreqArray' in self.curveH.x_address:
            new_ch = ':TuneFracArray-Mon'
        self.curveH.x_address = self.prefix + 'BO-Glob:DI-Tune-H' + new_ch
        self.curveH.x_channel.connect()
        self.curveV.x_address = self.prefix + 'BO-Glob:DI-Tune-V' + new_ch
        self.curveV.x_channel.connect()

    def showTuneH(self, show):
        """Whether to show or not curve of Tune H."""
        if show != self.curveH.isVisible():
            self.curveH.setVisible(show)

    def showTuneV(self, show):
        """Whether to show or not curve of Tune V."""
        if show != self.curveV.isVisible():
            self.curveV.setVisible(show)

    def receiveDataH(self, data):
        """Update curve H."""
        self.curveH.receiveYWaveform(data)
        self.curveH.redrawCurve()

    def receiveDataV(self, data):
        """Update curve V."""
        self.curveV.receiveYWaveform(data)
        self.curveV.redrawCurve()


class BOTuneSpectraControls(QWidget):
    """Booster Tune Spectra Controls."""

    def __init__(self, parent=None, prefix=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self._setupUi()

    def _setupUi(self):
        self.spectra = BOTuneSpectraView(self, self.prefix)

        lb_show_trace = QLabel('Show')
        self.cb_show_x = QCheckBox('H', self)
        self.cb_show_x.setStyleSheet('color: blue;')
        self.cb_show_x.setChecked(True)
        self.cb_show_x.stateChanged.connect(self.spectra.showTuneH)
        self.cb_show_y = QCheckBox('V', self)
        self.cb_show_y.setStyleSheet('color: red;')
        self.cb_show_y.setChecked(True)
        self.cb_show_y.stateChanged.connect(self.spectra.showTuneV)

        self.cb_choose_x = QComboBox(self)
        self.cb_choose_x.addItem('Tune Frac.')
        self.cb_choose_x.addItem('Frequency')
        self.cb_choose_x.currentIndexChanged.connect(
            self.spectra.toggleXChannel)

        hbox_ctrls = QHBoxLayout()
        hbox_ctrls.setContentsMargins(0, 0, 0, 0)
        hbox_ctrls.setSpacing(6)
        hbox_ctrls.addWidget(lb_show_trace, alignment=Qt.AlignLeft)
        hbox_ctrls.addWidget(self.cb_show_x, alignment=Qt.AlignLeft)
        hbox_ctrls.addWidget(self.cb_show_y, alignment=Qt.AlignLeft)
        hbox_ctrls.addStretch()
        hbox_ctrls.addWidget(QLabel('X Axis: '), alignment=Qt.AlignRight)
        hbox_ctrls.addWidget(self.cb_choose_x, alignment=Qt.AlignRight)

        # Registers
        self.registers = {i: None for i in range(4)}
        self.spectra.curveReg = [None, None, None, None]
        self.cb_reg = {i: QCheckBox(self) for i in range(4)}
        self.bt_reg = {i: QPushButton('Register '+str(i), self)
                       for i in range(4)}
        self.lb_reg = {i: QLabel('Empty') for i in range(4)}
        self.bt_save = {i: QPushButton(qta.icon('fa5s.save'), '', self)
                        for i in range(4)}
        self.colors = ['cyan', 'darkGreen', 'magenta', 'darkRed']
        glay_reg = QGridLayout()
        # glay_reg.setAlignment(Qt.AlignLeft)
        for i in range(4):
            # checks
            self.spectra.addChannel(
                y_channel='FAKE:Register'+str(i), name='Register '+str(i),
                redraw_mode=2, color=self.colors[i],
                lineWidth=2, lineStyle=Qt.SolidLine)
            self.spectra.curveReg[i] = self.spectra.curveAtIndex(i+2)
            self.spectra.curveReg[i].setVisible(False)
            self.cb_reg[i].setStyleSheet(
                'min-width:1.2em; max-width:1.2em;'
                'min-height:1.29em; color:'+self.colors[i]+';')
            self.cb_reg[i].stateChanged.connect(_part(self._show_curve, i))
            glay_reg.addWidget(self.cb_reg[i], i, 0, alignment=Qt.AlignLeft)
            # buttons
            self.bt_reg[i].setStyleSheet('min-width:5em; max-width:5em;')
            self.bt_reg[i].setMenu(QMenu())
            self.bt_reg[i].menu().addAction(
                'Save Tune H', _part(self._registerData, i, 'H'))
            self.bt_reg[i].menu().addAction(
                'Save Tune V', _part(self._registerData, i, 'V'))
            self.bt_reg[i].menu().addAction(
                'Clear', _part(self._clear_register, i))
            glay_reg.addWidget(self.bt_reg[i], i, 1, alignment=Qt.AlignLeft)
            # label
            self.lb_reg[i].setStyleSheet('min-height:1.29em;')
            glay_reg.addWidget(self.lb_reg[i], i, 2, alignment=Qt.AlignLeft)
            glay_reg.addItem(
                QSpacerItem(i, 1, QSzPlcy.Expanding, QSzPlcy.Ignored), i, 3)
            # save button
            self.bt_save[i].clicked.connect(_part(self._export_data, i))
            glay_reg.addWidget(self.bt_save[i], i, 4, alignment=Qt.AlignRight)

        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.setContentsMargins(10, 6, 6, 6)
        lay.addWidget(self.spectra)
        lay.addLayout(hbox_ctrls)
        lay.addLayout(glay_reg)

    def _registerData(self, idx, tune):
        curve = self.spectra.curveH if tune == 'H' else self.spectra.curveV
        self.registers[idx] = [curve.latest_x, curve.latest_y]
        self.lb_reg[idx].setText(
            'Tune '+tune+' at '+time.strftime(
                '%d/%m/%Y %H:%M:%S', time.localtime(time.time())))
        self._show_curve(idx, self.cb_reg[idx].checkState())

    def _clear_register(self, idx):
        self.registers[idx] = None
        self._show_curve(idx, self.cb_reg[idx].checkState())

    def _show_curve(self, idx, show):
        if not self.registers[idx]:
            self.spectra.curveReg[idx].receiveXWaveform([])
            self.spectra.curveReg[idx].receiveYWaveform([])
            self.spectra.curveReg[idx].redrawCurve()
            return
        if show:
            self.spectra.curveReg[idx].receiveXWaveform(self.registers[idx][0])
            self.spectra.curveReg[idx].receiveYWaveform(self.registers[idx][1])
            self.spectra.curveReg[idx].redrawCurve()
            self.spectra.curveReg[idx].setVisible(True)
        else:
            self.spectra.curveReg[idx].setVisible(False)

    def _export_data(self, idx):
        if not self.registers[idx]:
            return

        home = os.path.expanduser('~')
        folder_month = datetime.now().strftime('%Y-%m')
        folder_day = datetime.now().strftime('%Y-%m-%d')
        path = os.path.join(
            home, 'Desktop', 'screens-iocs', folder_month, folder_day)
        if not os.path.exists(path):
            os.makedirs(path)
        fn, _ = QFileDialog.getSaveFileName(self, 'Save as...', path, '*.txt')
        if not fn:
            return False
        if not fn.endswith('.txt'):
            fn += '.txt'

        data = np.array([self.registers[idx][0], self.registers[idx][1]]).T
        np.savetxt(fn, data)
