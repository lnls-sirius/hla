
import numpy as np

from qtpy.QtGui import QColor, QPalette
from qtpy.QtCore import Qt, Property, Slot
from qtpy.QtWidgets import QWidget, QToolTip, QVBoxLayout, QHBoxLayout, \
    QComboBox, QCheckBox
from pyqtgraph import PlotCurveItem, mkPen
from pydm.widgets.channel import PyDMChannel

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
        super().__init__(parent=parent,
                         image_channel=image_channel,
                         xaxis_channel=xaxis_channel,
                         yaxis_channel=yaxis_channel,
                         title=title,
                         background=background)
        self.normalizeData = True
        # ROI
        self._channels.extend(4*[None, ])
        self._image_roioffsetx = 0
        self._image_roioffsety = 0
        self._image_roiwidth = 0
        self._image_roiheight = 0
        self._offsetxchannel = None
        self._offsetychannel = None
        self._roiwidthchannel = None
        self._roiheightchannel = None
        self.ROIOffsetXChannel = self.device + ':ROIOffXConv-RB'
        self.ROIOffsetYChannel = self.device + ':ROIOffYConv-RB'
        self.ROIWidthChannel = self.device + ':ROIWidthConv-RB'
        self.ROIHeightChannel = self.device + ':ROIHeightConv-RB'
        self.ROICurve = PlotCurveItem([0, 0, 0, 0, 0], [0, 0, 0, 0, 0])
        pen = mkPen()
        pen.setColor(QColor('red'))
        pen.setWidth(1)
        self.ROICurve.setPen(pen)
        self._view.addItem(self.ROICurve)

    @Slot(np.ndarray)
    def image_value_changed(self, new_image):
        """Reimplement image_value_changed slot."""
        if new_image is None or new_image.size == 0:
            return
        spec_size = self._image_height*self._image_width
        self.image_waveform = new_image[:spec_size]
        self.needs_redraw = True

    def roioffsetx_connection_state_changed(self, conn):
        """
        Run when the ROIOffsetX Channel connection state changes.

        Parameters
        ----------
        conn : bool
            The new connection state.

        """
        if not conn:
            self._image_roioffsetx = 0

    def roioffsety_connection_state_changed(self, conn):
        """
        Run when the ROIOffsetY Channel connection state changes.

        Parameters
        ----------
        conn : bool
            The new connection state.

        """
        if not conn:
            self._image_roioffsety = 0

    def image_roioffsetx_changed(self, new_offset):
        """
        Run when the ROIOffsetX Channel value changes.

        Parameters
        ----------
        new_offsetx : int
            The new image ROI horizontal offset

        """
        if new_offset is None:
            return
        self._image_roioffsetx = new_offset
        self.redrawROI()

    def image_roioffsety_changed(self, new_offset):
        """
        Run when the ROIOffsetY Channel value changes.

        Parameters
        ----------
        new_offsety : int
            The new image ROI vertical offset

        """
        if new_offset is None:
            return
        self._image_roioffsety = new_offset
        self.redrawROI()

    def image_roiwidth_changed(self, new_width):
        """
        Run when the ROIWidth Channel value changes.

        Parameters
        ----------
        new_width : int
            The new image ROI width

        """
        if new_width is None:
            return
        self._image_roiwidth = int(new_width)
        self.redrawROI()

    def image_roiheight_changed(self, new_height):
        """
        Run when the ROIHeight Channel value changes.

        Parameters
        ----------
        new_height : int
            The new image ROI height

        """
        if new_height is None:
            return
        self._image_roiheight = int(new_height)
        self.redrawROI()

    @Property(str)
    def ROIOffsetXChannel(self):
        """
        Return the channel address in use for the image ROI horizontal offset.

        Returns
        -------
        str
            Channel address

        """
        if self._offsetxchannel:
            return str(self._offsetxchannel.address)
        else:
            return ''

    @ROIOffsetXChannel.setter
    def ROIOffsetXChannel(self, value):
        """
        Return the channel address in use for the image ROI horizontal offset.

        Parameters
        ----------
        value : str
            Channel address

        """
        if self._offsetxchannel != value:
            # Disconnect old channel
            if self._offsetxchannel:
                self._offsetxchannel.disconnect()
            # Create and connect new channel
            self._offsetxchannel = PyDMChannel(
                address=value,
                connection_slot=self.roioffsetx_connection_state_changed,
                value_slot=self.image_roioffsetx_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[2] = self._offsetxchannel
            self._offsetxchannel.connect()

    @Property(str)
    def ROIOffsetYChannel(self):
        """
        Return the channel address in use for the image ROI vertical offset.

        Returns
        -------
        str
            Channel address

        """
        if self._offsetychannel:
            return str(self._offsetychannel.address)
        else:
            return ''

    @ROIOffsetYChannel.setter
    def ROIOffsetYChannel(self, value):
        """
        Return the channel address in use for the image ROI vertical offset.

        Parameters
        ----------
        value : str
            Channel address

        """
        if self._offsetychannel != value:
            # Disconnect old channel
            if self._offsetychannel:
                self._offsetychannel.disconnect()
            # Create and connect new channel
            self._offsetychannel = PyDMChannel(
                address=value,
                connection_slot=self.roioffsety_connection_state_changed,
                value_slot=self.image_roioffsety_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[3] = self._offsetychannel
            self._offsetychannel.connect()

    @Property(str)
    def ROIWidthChannel(self):
        """
        Return the channel address in use for the image ROI width.

        Returns
        -------
        str
            Channel address

        """
        if self._roiwidthchannel:
            return str(self._roiwidthchannel.address)
        else:
            return ''

    @ROIWidthChannel.setter
    def ROIWidthChannel(self, value):
        """
        Return the channel address in use for the image ROI width.

        Parameters
        ----------
        value : str
            Channel address

        """
        if self._roiwidthchannel != value:
            # Disconnect old channel
            if self._roiwidthchannel:
                self._roiwidthchannel.disconnect()
            # Create and connect new channel
            self._roiwidthchannel = PyDMChannel(
                address=value,
                value_slot=self.image_roiwidth_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[4] = self._roiwidthchannel
            self._roiwidthchannel.connect()

    @Property(str)
    def ROIHeightChannel(self):
        """
        Return the channel address in use for the image ROI height.

        Returns
        -------
        str
            Channel address

        """
        if self._roiheightchannel:
            return str(self._roiheightchannel.address)
        else:
            return ''

    @ROIHeightChannel.setter
    def ROIHeightChannel(self, value):
        """
        Return the channel address in use for the image ROI height.

        Parameters
        ----------
        value : str
            Channel address

        """
        if self._roiheightchannel != value:
            # Disconnect old channel
            if self._roiheightchannel:
                self._roiheightchannel.disconnect()
            # Create and connect new channel
            self._roiheightchannel = PyDMChannel(
                address=value,
                value_slot=self.image_roiheight_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[5] = self._roiheightchannel
            self._roiheightchannel.connect()

    def redrawROI(self):
        startx = self._image_roioffsetx
        endx = self._image_roioffsetx + self._image_roiwidth
        starty = self._image_roioffsety
        endy = self._image_roioffsety + self._image_roiheight
        self.ROICurve.setData(
            [startx, startx, endx, endx, startx],
            [starty, endy, endy, starty, starty])

    def toggleXChannel(self):
        """Toggle X channel between FreqArray and TuneFracArray."""
        if 'TuneFracArray' in self._xaxischannel.address:
            self.xAxisChannel = self.prefix+self.device+':FreqArray-Mon'
        elif 'FreqArray' in self._xaxischannel.address:
            self.xAxisChannel = self.prefix+self.device+':TuneFracArray-Mon'

    def showROI(self, show):
        """Set ROI visibility."""
        pen = mkPen()
        if show:
            pen.setColor(QColor('red'))
            pen.setWidth(1)
        else:
            pen.setColor(QColor('transparent'))
            pen.setWidth(0)
        self.ROICurve.setPen(pen)

    def mouseMoveEvent(self, ev):
        pos = ev.pos()
        posaux = self._image_item.mapFromDevice(ev.pos())
        if posaux.x() < 0 or posaux.x() >= self._image_item.width() or \
                posaux.y() < 0 or posaux.y() >= self._image_item.height():
            super().mouseMoveEvent(ev)
            return

        pos_scene = self._view.mapSceneToView(pos)
        x = round(pos_scene.x())
        maxx = len(self._last_xaxis_data)-1
        x = x if x < maxx else maxx
        y = round(pos_scene.y())
        maxy = len(self._last_yaxis_data)-1
        y = y if y < maxy else maxy
        txt = '{0:.3f}, {1:.3f}'.format(
            self._last_xaxis_data[x],
            self._last_yaxis_data[y])
        QToolTip.showText(
            self.mapToGlobal(pos), txt, self, self.geometry(), 5000)
        super().mouseMoveEvent(ev)


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
