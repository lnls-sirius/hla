"""SiriusSpectrogramView widget.

Based on ImageView from pydm and GradientLegend from pyqtgraph.
"""

import numpy as np
import logging
from qtpy.QtWidgets import QActionGroup
from qtpy.QtGui import QColor, QLinearGradient, QBrush, QPen
from qtpy.QtCore import Signal, Slot, Property, QTimer, Q_ENUMS, \
                         QThread, Qt, QRectF, QPointF
from pyqtgraph import ViewBox, ImageItem, AxisItem, GraphicsLayoutWidget, \
                      ColorMap, GraphicsWidget
from pyqtgraph.graphicsItems.ViewBox.ViewBoxMenu import ViewBoxMenu
from pydm.widgets.channel import PyDMChannel
from pydm.widgets.colormaps import cmaps, cmap_names, PyDMColorMap
from pydm.widgets.base import PyDMWidget
from pydm.widgets.image import ReadingOrder

logger = logging.getLogger(__name__)


class _GradientLegend(GraphicsWidget):
    """Class to make GradientLegend a GraphicsWidget.

    Draws a color gradient rectangle along with text labels denoting the value
    at specific points along the gradient.

    Parameters
    ----------
    size : list of int, optional
        Size of the widget within the GraphicsWidget rectangle.
    colors : a list of RGB codes, optional
        The lookup table to be used to design the gradient.
    labels : dict of keys = strings and values = int
        The labels that will appear along the colorbar.
        The values determine the sequence of labels in descending order.
    minVal : int, optional
        If labels is None, so only minVal and maxVal are displayed in the
        beggining and in the end of the colorbar.
    maxVal : int, optional
        If labels is None, so only minVal and maxVal are displayed in the
        beggining and in the end of the colorbar.
    """

    def __init__(self, size=None, colors=None,
                 labels=None, minVal=None, maxVal=None):
        GraphicsWidget.__init__(self)
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.size = size

        # if min and max values are None, assume normalized data
        self.minVal = 0 if minVal is None else minVal
        self.maxVal = 1 if maxVal is None else maxVal
        self.labels = {'min': 1, 'max': 0} if labels is None else labels
        self.label_format = '{: .3f}'

        self.gradient = QLinearGradient()
        if colors is None:
            self.colors = [[0, 0, 0], [255, 0, 0]]
        else:
            self.colors = colors
        self.setIntColorScale(colors=self.colors,
                              minVal=self.minVal, maxVal=self.maxVal,
                              labels=self.labels)

    def setIntColorScale(self, colors, minVal=None, maxVal=None, labels=None):
        # generate color gradient
        g = QLinearGradient()
        for i in range(len(colors)):
            x = float(i)/len(colors)
            g.setColorAt(x, QColor(colors[i][0], colors[i][1], colors[i][2]))
        self._setGradient(g)

        # add labels
        if labels is None and (minVal is None or maxVal is None):
            self.setLabels(self.labels)
        elif labels is None:
            self.setLabels({str(minVal): 0, str(maxVal): 1})
        else:
            self.setLabels(labels)

    def _setGradient(self, g):
        self.gradient = g
        self.update()

    def setLimits(self, data):
        minVal = data[0]
        maxVal = data[1]
        if minVal == self.minVal and maxVal == self.maxVal:
            return
        self.minVal = minVal
        self.maxVal = maxVal
        labels = dict()
        for v in self.labels.values():
            newv = minVal + (1-v)*(maxVal - minVal)
            newk = self.label_format.format(newv)
            labels[newk] = v
        self.setLabels(labels)

    def setLabels(self, l):
        """
        Define labels to appear next to the color scale.

        Accepts a dict of {text: value} pairs.
        """
        self.labels = l
        self.update()

    def paint(self, p, opt, widget):
        GraphicsWidget.paint(self, p, opt, widget)
        rect = self.boundingRect()  # Boundaries of visible area in scene coord
        size = self.size if self.size is not None \
            else [rect.right()-rect.left(), rect.bottom() - rect.top()]

        # determine max width of all labels
        textPadding = 2  # in px
        labelWidth = 0
        labelHeight = 0
        for k in self.labels:
            b = p.boundingRect(QRectF(0, 0, 0, 0),
                               Qt.AlignLeft | Qt.AlignVCenter, str(k))
            labelWidth = max(labelWidth, b.width())
            labelHeight = max(labelHeight, b.height())

        x1_back = (rect.right() - rect.left() - size[0])/2
        x2_back = (rect.right() - rect.left() + size[0])/2
        y1_back = (rect.bottom() - rect.top() - size[1])/2
        y2_back = (rect.bottom() - rect.top() + size[1])/2

        x1_grad = x1_back + textPadding*2
        x2_grad = x2_back - (labelWidth + textPadding*2)
        y1_grad = y1_back + (labelHeight/2 + textPadding)
        y2_grad = y2_back - (labelHeight/2 + textPadding)

        # Draw background
        p.setPen(QPen(QColor(0, 0, 0, 0)))
        p.setBrush(QBrush(QColor(255, 255, 255, 0)))
        rect = QRectF(QPointF(x1_back, y1_back),
                      QPointF(x2_back, y2_back))
        p.drawRect(rect)

        # Draw color bar
        self.gradient.setStart(0, y2_grad)
        self.gradient.setFinalStop(0, y1_grad)
        p.setPen(QPen(QColor(0, 0, 0)))
        p.setBrush(self.gradient)
        rect = QRectF(QPointF(x1_grad, y1_grad),
                      QPointF(x2_grad, y2_grad))
        p.drawRect(rect)

        # draw labels
        tx = x2_grad + textPadding*2
        lw = labelWidth
        lh = labelHeight
        for k in self.labels:
            y = y1_grad + self.labels[k] * (y2_grad-y1_grad)
            p.drawText(QRectF(tx, y - lh/2.0, lw, lh),
                       Qt.AlignLeft | Qt.AlignVCenter, str(k))

        self.setMinimumWidth(labelWidth + 2*textPadding + 20)


class SpectrogramUpdateThread(QThread):
    """Thread to update image."""

    updateSignal = Signal(list)

    def __init__(self, spectrogram_view):
        """Initialize Thread."""
        QThread.__init__(self)
        self.spectrogram_view = spectrogram_view

    def run(self):
        """Thread main."""
        img = self.spectrogram_view.image_waveform
        needs_redraw = self.spectrogram_view.needs_redraw
        image_dimensions = len(img.shape)
        width = self.spectrogram_view.imageWidth
        reading_order = self.spectrogram_view.readingOrder
        normalize_data = self.spectrogram_view._normalize_data
        cm_min = self.spectrogram_view.cm_min
        cm_max = self.spectrogram_view.cm_max

        if not needs_redraw:
            logging.debug(
                "ImageUpdateThread - needs redraw is False. Aborting.")
            return
        if image_dimensions == 1:
            if width < 1:
                # We don't have a width for this image yet, so we can't draw it
                logging.debug(
                    "ImageUpdateThread - no width available. Aborting.")
                return
            try:
                if reading_order == ReadingOrder.Clike:
                    img = img.reshape((-1, width), order='C')
                else:
                    img = img.reshape((width, -1), order='F')
            except ValueError:
                logger.error("Invalid width for image during reshape: %d",
                             width)

        if len(img) <= 0:
            return
        logging.debug("ImageUpdateThread - Will Process Image")
        img = self.spectrogram_view.process_image(img)
        if normalize_data:
            mini = img.min()
            maxi = img.max()
        else:
            mini = cm_min
            maxi = cm_max
        logging.debug("ImageUpdateThread - Emit Update Signal")
        self.updateSignal.emit([mini, maxi, img])
        logging.debug("ImageUpdateThread - Set Needs Redraw -> False")
        self.spectrogram_view.needs_redraw = False


class SiriusSpectrogramView(
        GraphicsLayoutWidget, PyDMWidget, PyDMColorMap, ReadingOrder):
    """
    A SpectrogramView with support for Channels and more from PyDM.

    If there is no :attr:`channelWidth` it is possible to define the width of
    the image with the :attr:`width` property.

    The :attr:`normalizeData` property defines if the colors of the images are
    relative to the :attr:`colorMapMin` and :attr:`colorMapMax` property or to
    the minimum and maximum values of the image.

    Use the :attr:`newImageSignal` to hook up to a signal that is emitted when
    a new image is rendered in the widget.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    image_channel : str, optional
        The channel to be used by the widget for the image data.
    width_channel : str, optional
        The channel to be used by the widget to receive the image width
        information,
    time_channel : str, optional
        The channel to be used by the widget to receive the image width
        information
    background : QColor, optional
        QColor to set the background color of the GraphicsView
    """

    Q_ENUMS(PyDMColorMap)
    Q_ENUMS(ReadingOrder)

    color_maps = cmaps

    def __init__(self, parent=None, image_channel=None, xaxis_channel=None,
                 yaxis_channel=None, background='default'):
        """Initialize widget."""
        GraphicsLayoutWidget.__init__(self, parent)
        PyDMWidget.__init__(self)
        self.thread = None
        self._imagechannel = image_channel
        self._xaxischannel = xaxis_channel
        self._yaxischannel = yaxis_channel
        self.image_waveform = np.zeros(0)
        self._image_width = 0
        self._normalize_data = False
        self._auto_downsample = True
        self._last_yaxis_data = None
        self._last_xaxis_data = None

        self.setBackground(background)

        # Add viewBox and imageItem.
        self._view = ViewBox()
        self._image_item = ImageItem()
        self._view.addItem(self._image_item)
        self.addItem(self._view, 0, 1)
        self.ci.layout.setColumnSpacing(0, 0)
        self.ci.layout.setRowSpacing(0, 0)

        # Add axis.
        self.xaxis = AxisItem('bottom')
        self.xaxis.setPen(QColor(0, 0, 0))
        self.yaxis = AxisItem('left')
        self.yaxis.setPen(QColor(0, 0, 0))
        self.addItem(self.yaxis, 0, 0)
        self.addItem(self.xaxis, 1, 1)

        # Add colorbar legend.
        self.colorbar = _GradientLegend()
        self.addItem(self.colorbar, 0, 2)

        # Set color map limits.
        self.cm_min = 0.0
        self.cm_max = 255.0

        # Set default reading order of numpy array data to Fortranlike.
        self._reading_order = ReadingOrder.Clike

        # Make a right-click menu for changing the color map.
        self.cm_group = QActionGroup(self)
        self.cmap_for_action = {}
        for cm in self.color_maps:
            action = self.cm_group.addAction(cmap_names[cm])
            action.setCheckable(True)
            self.cmap_for_action[action] = cm

        # Set the default colormap.
        self._cm_colors = None
        self.colorMap = PyDMColorMap.Inferno

        # Setup the redraw timer.
        self.needs_redraw = False
        self.redraw_timer = QTimer(self)
        self.redraw_timer.timeout.connect(self.redrawImage)
        self._redraw_rate = 30
        self.maxRedrawRate = self._redraw_rate
        self.newImageSignal = self._image_item.sigImageChanged

    def widget_ctx_menu(self):
        """
        Fetch the Widget specific context menu.

        It will be populated with additional tools by `assemble_tools_menu`.

        Returns
        -------
        QMenu or None
            If the return of this method is None a new QMenu will be created by
            `assemble_tools_menu`.
        """
        self.menu = ViewBoxMenu(self._view)
        cm_menu = self.menu.addMenu("Color Map")
        for act in self.cmap_for_action.keys():
            cm_menu.addAction(act)
        cm_menu.triggered.connect(self._changeColorMap)
        return self.menu

    def _changeColorMap(self, action):
        """
        Method invoked by the colormap Action Menu.

        Changes the current colormap used to render the image.

        Parameters
        ----------
        action : QAction
        """
        self.colorMap = self.cmap_for_action[action]

    @Property(float)
    def colorMapMin(self):
        """
        Minimum value for the colormap.

        Returns
        -------
        float
        """
        return self.cm_min

    @colorMapMin.setter
    @Slot(float)
    def colorMapMin(self, new_min):
        """
        Set the minimum value for the colormap.

        Parameters
        ----------
        new_min : float
        """
        if self.cm_min != new_min:
            self.cm_min = new_min
            if self.cm_min > self.cm_max:
                self.cm_max = self.cm_min

    @Property(float)
    def colorMapMax(self):
        """
        Maximum value for the colormap.

        Returns
        -------
        float
        """
        return self.cm_max

    @colorMapMax.setter
    @Slot(float)
    def colorMapMax(self, new_max):
        """
        Set the maximum value for the colormap.

        Parameters
        ----------
        new_max : float
        """
        if self.cm_max != new_max:
            self.cm_max = new_max
            if self.cm_max < self.cm_min:
                self.cm_min = self.cm_max

    def setColorMapLimits(self, mn, mx):
        """
        Set the limit values for the colormap.

        Parameters
        ----------
        mn : int
            The lower limit
        mx : int
            The upper limit
        """
        if mn >= mx:
            return
        self.cm_max = mx
        self.cm_min = mn

    @Property(PyDMColorMap)
    def colorMap(self):
        """
        Return the color map used by the SpectrogramView.

        Returns
        -------
        PyDMColorMap
        """
        return self._colormap

    @colorMap.setter
    def colorMap(self, new_cmap):
        """
        Set the color map used by the SpectrogramView.

        Parameters
        -------
        new_cmap : PyDMColorMap
        """
        self._colormap = new_cmap
        self._cm_colors = self.color_maps[new_cmap]
        self.setColorMap()
        for action in self.cm_group.actions():
            if self.cmap_for_action[action] == self._colormap:
                action.setChecked(True)
            else:
                action.setChecked(False)

    def setColorMap(self, cmap=None):
        """
        Update the image colormap.

        Parameters
        ----------
        cmap : ColorMap
        """
        if not cmap:
            if not self._cm_colors.any():
                return
            # Take default values
            pos = np.linspace(0.0, 1.0, num=len(self._cm_colors))
            cmap = ColorMap(pos, self._cm_colors)
        self._view.setBackgroundColor(cmap.map(0))
        lut = cmap.getLookupTable(0.0, 1.0, alpha=False)
        self.colorbar.setIntColorScale(colors=lut)
        self._image_item.setLookupTable(lut)

    @Slot(bool)
    def image_connection_state_changed(self, conn):
        """
        Callback invoked when the Image Channel connection state is changed.

        Parameters
        ----------
        conn : bool
            The new connection state.
        """
        if conn:
            self.redraw_timer.start()
        else:
            self.redraw_timer.stop()

    @Slot(bool)
    def yaxis_connection_state_changed(self, connected):
        """
        Callback invoked when the TimeAxis Channel connection state is changed.

        Parameters
        ----------
        conn : bool
            The new connection state.
        """
        self._timeaxis_connected = connected

    @Slot(np.ndarray)
    def image_value_changed(self, new_image):
        """
        Callback invoked when the Image Channel value is changed.

        We try to do as little as possible in this method, because it
        gets called every time the image channel updates, which might
        be extremely often.  Basically just store the data, and set
        a flag requesting that the image be redrawn.

        Parameters
        ----------
        new_image : np.ndarray
            The new image data.  This can be a flat 1D array, or a 2D array.
        """
        if new_image is None or new_image.size == 0:
            return
        logging.debug("SpectrogramView Received New Image: Needs Redraw->True")
        self.image_waveform = new_image
        self.needs_redraw = True

    @Slot(np.ndarray)
    def image_xaxis_changed(self, new_array):
        """
        Callback invoked when the Image Width Channel value is changed.

        Parameters
        ----------
        new_array : np.ndarray
            The new frequency array
        """
        if new_array is None:
            return
        self._last_xaxis_data = new_array
        if self._reading_order == self.Clike:
            self._image_width = new_array.size

    @Slot(np.ndarray)
    def image_yaxis_changed(self, new_array):
        """
        Callback invoked when the TimeAxis Channel value is changed.

        Parameters
        ----------
        new_array : np.array
            The new time array
        """
        if new_array is None:
            return
        self._last_yaxis_data = new_array
        if self._reading_order == self.Fortranlike:
            self._image_width = new_array.size

    def process_image(self, image):
        """
        Boilerplate method.

        To be used by applications in order to add calculations and also modify
        the image before it is displayed at the widget.

        .. warning::
           This code runs in a separated QThread so it **MUST** not try to
           write to QWidgets.

        Parameters
        ----------
        image : np.ndarray
            The Image Data as a 2D numpy array

        Returns
        -------
        np.ndarray
            The Image Data as a 2D numpy array after processing.
        """
        return image

    def redrawImage(self):
        """
        Set the image data into the ImageItem, if needed.

        If necessary, reshape the image to 2D first.
        """
        if self.thread is not None and not self.thread.isFinished():
            logger.warning(
                "Image processing has taken longer than the refresh rate.")
            return
        self.thread = SpectrogramUpdateThread(self)
        self.thread.updateSignal.connect(self._updateDisplay)
        logging.debug("SpectrogramView RedrawImage Thread Launched")
        self.thread.start()

    @Slot(list)
    def _updateDisplay(self, data):
        logging.debug("SpectrogramView Update Display with new image")

        # Update axis
        if self._last_yaxis_data is None or \
                self._last_xaxis_data is None:
            return
        xMin = min(self._last_xaxis_data)
        xMax = max(self._last_xaxis_data)
        yMin = 0
        yMax = max(self._last_yaxis_data)-min(self._last_yaxis_data)
        self.xaxis.setRange(xMin, xMax)
        self.yaxis.setRange(yMin, yMax)
        self._view.setLimits(
            xMin=0, xMax=xMax-xMin, yMin=0, yMax=yMax-yMin,
            minXRange=xMax-xMin, maxXRange=xMax-xMin,
            minYRange=yMax-yMin, maxYRange=yMax-yMin)

        # Update image
        self.colorbar.setLimits(data)
        mini, maxi = data[0], data[1]
        img = data[2]
        self._image_item.setLevels([mini, maxi])
        self._image_item.setImage(
            img,
            autoLevels=False,
            autoDownsample=self.autoDownsample)

    @Property(bool)
    def autoDownsample(self):
        """
        Return if we should or not apply the autoDownsample option.

        Return
        ------
        bool
        """
        return self._auto_downsample

    @autoDownsample.setter
    def autoDownsample(self, new_value):
        """
        Whether we should or not apply the autoDownsample option.

        Parameters
        ----------
        new_value: bool
        """
        if new_value != self._auto_downsample:
            self._auto_downsample = new_value

    @Property(int)
    def imageWidth(self):
        """
        Return the width of the image.

        Return
        ------
        int
        """
        return self._image_width

    @imageWidth.setter
    def imageWidth(self, new_width):
        """
        Set the width of the image.

        Can be overridden by :attr:`xAxisChannel` and :attr:`yAxisChannel`.

        Parameters
        ----------
        new_width: int
        """
        boo = self._image_width != int(new_width)
        boo &= not self._xaxischannel
        boo &= not self._yaxischannel
        if boo:
            self._image_width = int(new_width)

    @Property(bool)
    def normalizeData(self):
        """
        Return True if the colors are relative to data maximum and minimum.

        Returns
        -------
        bool
        """
        return self._normalize_data

    @normalizeData.setter
    @Slot(bool)
    def normalizeData(self, new_norm):
        """
        Define if the colors are relative to minimum and maximum of the data.

        Parameters
        ----------
        new_norm: bool
        """
        if self._normalize_data != new_norm:
            self._normalize_data = new_norm

    @Property(ReadingOrder)
    def readingOrder(self):
        """
        Return the reading order of the :attr:`imageChannel` array.

        Returns
        -------
        ReadingOrder
        """
        return self._reading_order

    @readingOrder.setter
    def readingOrder(self, order):
        """
        Set reading order of the :attr:`imageChannel` array.

        Parameters
        ----------
        order: ReadingOrder
        """
        if self._reading_order != order:
            self._reading_order = order

        if order == self.Clike and self._last_xaxis_data is not None:
            self._image_width = self._last_xaxis_data.size
        elif order == self.Fortranlike and self._last_yaxis_data is not None:
            self._image_width = self._last_yaxis_data.size

    def keyPressEvent(self, ev):
        """Handle keypress events."""
        return

    @Property(str)
    def imageChannel(self):
        """
        The channel address in use for the image data .

        Returns
        -------
        str
            Channel address
        """
        return str(self._imagechannel)

    @imageChannel.setter
    def imageChannel(self, value):
        """
        The channel address in use for the image data .

        Parameters
        ----------
        value : str
            Channel address
        """
        if self._imagechannel != value:
            self._imagechannel = str(value)

    @Property(str)
    def xAxisChannel(self):
        """
        The channel address in use for the x-axis of image.

        Returns
        -------
        str
            Channel address
        """
        return str(self._xaxischannel)

    @xAxisChannel.setter
    def xAxisChannel(self, value):
        """
        The channel address in use for the x-axis of image.

        Parameters
        ----------
        value : str
            Channel address
        """
        if self._xaxischannel != value:
            self._xaxischannel = str(value)

    @Property(str)
    def yAxisChannel(self):
        """
        The channel address in use for the time axis.

        Returns
        -------
        str
            Channel address
        """
        return str(self._yaxischannel)

    @yAxisChannel.setter
    def yAxisChannel(self, value):
        """
        The channel address in use for the time axis.

        Parameters
        ----------
        value : str
            Channel address
        """
        if self._yaxischannel != value:
            self._yaxischannel = str(value)

    def channels(self):
        """
        Return the channels being used for this Widget.

        Returns
        -------
        channels : list
            List of PyDMChannel objects
        """
        if self._channels is None:
            self._channels = [
                PyDMChannel(
                    address=self.imageChannel,
                    connection_slot=self.image_connection_state_changed,
                    value_slot=self.image_value_changed,
                    severity_slot=self.alarmSeverityChanged),
                PyDMChannel(
                    address=self.xAxisChannel,
                    connection_slot=self.connectionStateChanged,
                    value_slot=self.image_xaxis_changed,
                    severity_slot=self.alarmSeverityChanged),
                PyDMChannel(
                    address=self.yAxisChannel,
                    connection_slot=self.yaxis_connection_state_changed,
                    value_slot=self.image_yaxis_changed,
                    severity_slot=self.alarmSeverityChanged)]
        return self._channels

    def channels_for_tools(self):
        """Return channels for tools."""
        return [c for c in self.channels() if c.address == self.imageChannel]

    @Property(int)
    def maxRedrawRate(self):
        """
        The maximum rate (in Hz) at which the plot will be redrawn.

        The plot will not be redrawn if there is not new data to draw.

        Returns
        -------
        int
        """
        return self._redraw_rate

    @maxRedrawRate.setter
    def maxRedrawRate(self, redraw_rate):
        """
        The maximum rate (in Hz) at which the plot will be redrawn.

        The plot will not be redrawn if there is not new data to draw.

        Parameters
        -------
        redraw_rate : int
        """
        self._redraw_rate = redraw_rate
        self.redraw_timer.setInterval(int((1.0 / self._redraw_rate) * 1000))
