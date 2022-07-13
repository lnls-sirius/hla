"""SiriusSpectrogramView widget.

Based on ImageView from pydm and GradientLegend from pyqtgraph.
"""

import numpy as np
import logging
from qtpy.QtWidgets import QActionGroup, QToolTip, QMenu
from qtpy.QtGui import QColor, QLinearGradient, QBrush, QPen
from qtpy.QtCore import Signal, Slot, Property, QTimer, Q_ENUMS, \
    QThread, Qt, QRectF, QPointF
from pyqtgraph import ViewBox, ImageItem, AxisItem, GraphicsLayoutWidget, \
    ColorMap, GraphicsWidget, LabelItem, PlotCurveItem, mkPen
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
        self.labels = {1: 'min', 0: 'max'} if labels is None else labels
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
            self.setLabels({1: str(minVal), 0: str(maxVal)})
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
        for k in self.labels.keys():
            newv = minVal + (1-k)*(maxVal - minVal)
            newv = self.label_format.format(newv)
            self.labels[k] = newv
        self.setLabels(self.labels)

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
        for val in self.labels.values():
            b = p.boundingRect(QRectF(0, 0, 0, 0),
                               Qt.AlignLeft | Qt.AlignVCenter, str(val))
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
        for key, val in self.labels.items():
            y = y1_grad + key * (y2_grad-y1_grad)
            p.drawText(QRectF(tx, y - lh/2.0, lw, lh),
                       Qt.AlignLeft | Qt.AlignVCenter, str(val))

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
    xaxis_channel : str, optional
        The channel to be used by the widget to receive the image width
        (if ReadingOrder == Clike), and to set the xaxis values
    yaxis_channel : str, optional
        The channel to be used by the widget to receive the image width
        (if ReadingOrder == Fortranlike), and to set the yaxis values
    background : QColor, optional
        QColor to set the background color of the GraphicsView
    """

    Q_ENUMS(PyDMColorMap)
    Q_ENUMS(ReadingOrder)

    color_maps = cmaps

    def __init__(self, parent=None, image_channel=None,
                 xaxis_channel=None, yaxis_channel=None,
                 roioffsetx_channel=None, roioffsety_channel=None,
                 roiwidth_channel=None, roiheight_channel=None,
                 title='', background='w',
                 image_width=0, image_height=0):
        """Initialize widget."""
        GraphicsLayoutWidget.__init__(self, parent)
        PyDMWidget.__init__(self)
        self.thread = None
        self._imagechannel = None
        self._xaxischannel = None
        self._yaxischannel = None
        self._roioffsetxchannel = None
        self._roioffsetychannel = None
        self._roiwidthchannel = None
        self._roiheightchannel = None
        self._channels = 7*[None, ]
        self.image_waveform = np.zeros(0)
        self._image_width = image_width if not xaxis_channel else 0
        self._image_height = image_height if not yaxis_channel else 0
        self._roi_offsetx = 0
        self._roi_offsety = 0
        self._roi_width = 0
        self._roi_height = 0
        self._normalize_data = False
        self._auto_downsample = True
        self._last_yaxis_data = None
        self._last_xaxis_data = None
        self._auto_colorbar_lims = True
        self.format_tooltip = '{0:.4g}, {1:.4g}'

        # ViewBox and imageItem.
        self._view = ViewBox()
        self._image_item = ImageItem()
        self._view.addItem(self._image_item)

        # ROI
        self.ROICurve = PlotCurveItem([0, 0, 0, 0, 0], [0, 0, 0, 0, 0])
        self.ROIColor = QColor('red')
        pen = mkPen()
        pen.setColor(QColor('transparent'))
        pen.setWidth(1)
        self.ROICurve.setPen(pen)
        self._view.addItem(self.ROICurve)

        # Axis.
        self.xaxis = AxisItem('bottom')
        self.xaxis.setPen(QColor(0, 0, 0))
        if not xaxis_channel:
            self.xaxis.setVisible(False)
        self.yaxis = AxisItem('left')
        self.yaxis.setPen(QColor(0, 0, 0))
        if not yaxis_channel:
            self.yaxis.setVisible(False)

        # Colorbar legend.
        self.colorbar = _GradientLegend()

        # Title.
        start_row = 0
        if title:
            self.title = LabelItem(text=title, color='#000000')
            self.addItem(self.title, 0, 0, 1, 3)
            start_row = 1

        # Set layout.
        self.addItem(self._view, start_row, 1)
        self.addItem(self.yaxis, start_row, 0)
        self.addItem(self.colorbar, start_row, 2)
        self.addItem(self.xaxis, start_row+1, 1)
        self.setBackground(background)
        self.ci.layout.setColumnSpacing(0, 0)
        self.ci.layout.setRowSpacing(start_row, 0)

        # Set color map limits.
        self.cm_min = 0.0
        self.cm_max = 255.0

        # Set default reading order of numpy array data to Clike.
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

        # Set Channels.
        self.imageChannel = image_channel
        self.xAxisChannel = xaxis_channel
        self.yAxisChannel = yaxis_channel
        self.ROIOffsetXChannel = roioffsetx_channel
        self.ROIOffsetYChannel = roioffsety_channel
        self.ROIWidthChannel = roiwidth_channel
        self.ROIHeightChannel = roiheight_channel

        # Handle view range changed
        self._view.sigRangeChanged.connect(self._update_axis_range)
        self._view.suggestPadding = lambda x: 0.0

        # Context menu
        self.contextMenuEvent = None
        cm_menu = QMenu("Color Map")
        for act in self.cmap_for_action.keys():
            cm_menu.addAction(act)
        cm_menu.triggered.connect(self._changeColorMap)
        self._view.scene().contextMenu.append(cm_menu)

    # --- Colormap methods ---
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

    # --- Connection Slots ---
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

    @Slot(bool)
    def roioffsetx_connection_state_changed(self, conn):
        """
        Run when the ROIOffsetX Channel connection state changes.

        Parameters
        ----------
        conn : bool
            The new connection state.

        """
        if not conn:
            self._roi_offsetx = 0

    @Slot(bool)
    def roioffsety_connection_state_changed(self, conn):
        """
        Run when the ROIOffsetY Channel connection state changes.

        Parameters
        ----------
        conn : bool
            The new connection state.

        """
        if not conn:
            self._roi_offsety = 0

    @Slot(bool)
    def roiwidth_connection_state_changed(self, conn):
        """
        Run when the ROIWidth Channel connection state changes.

        Parameters
        ----------
        conn : bool
            The new connection state.

        """
        if not conn:
            self._roi_width = 0

    @Slot(bool)
    def roiheight_connection_state_changed(self, conn):
        """
        Run when the ROIHeight Channel connection state changes.

        Parameters
        ----------
        conn : bool
            The new connection state.

        """
        if not conn:
            self._roi_height = 0

    # --- Value Slots ---
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
        if not self._image_height and self._image_width:
            self._image_height = new_image.size/self._image_width
        elif not self._image_width and self._image_height:
            self._image_width = new_image.size/self._image_height

    @Slot(np.ndarray)
    @Slot(float)
    def xaxis_value_changed(self, new_array):
        """
        Callback invoked when the Image Width Channel value is changed.

        Parameters
        ----------
        new_array : np.ndarray
            The new x axis array
        """
        if new_array is None:
            return
        if isinstance(new_array, float):
            new_array = np.array([new_array, ])
        self._last_xaxis_data = new_array
        if self._reading_order == self.Clike:
            self._image_width = new_array.size
        else:
            self._image_height = new_array.size
        self.needs_redraw = True

    @Slot(np.ndarray)
    @Slot(float)
    def yaxis_value_changed(self, new_array):
        """
        Callback invoked when the TimeAxis Channel value is changed.

        Parameters
        ----------
        new_array : np.array
            The new y axis array
        """
        if new_array is None:
            return
        if isinstance(new_array, float):
            new_array = np.array([new_array, ])
        self._last_yaxis_data = new_array
        if self._reading_order == self.Fortranlike:
            self._image_width = new_array.size
        else:
            self._image_height = new_array.size
        self.needs_redraw = True

    @Slot(int)
    def roioffsetx_value_changed(self, new_offset):
        """
        Run when the ROIOffsetX Channel value changes.

        Parameters
        ----------
        new_offsetx : int
            The new image ROI horizontal offset

        """
        if new_offset is None:
            return
        self._roi_offsetx = new_offset
        self.redrawROI()

    @Slot(int)
    def roioffsety_value_changed(self, new_offset):
        """
        Run when the ROIOffsetY Channel value changes.

        Parameters
        ----------
        new_offsety : int
            The new image ROI vertical offset

        """
        if new_offset is None:
            return
        self._roi_offsety = new_offset
        self.redrawROI()

    @Slot(int)
    def roiwidth_value_changed(self, new_width):
        """
        Run when the ROIWidth Channel value changes.

        Parameters
        ----------
        new_width : int
            The new image ROI width

        """
        if new_width is None:
            return
        self._roi_width = int(new_width)
        self.redrawROI()

    @Slot(int)
    def roiheight_value_changed(self, new_height):
        """
        Run when the ROIHeight Channel value changes.

        Parameters
        ----------
        new_height : int
            The new image ROI height

        """
        if new_height is None:
            return
        self._roi_height = int(new_height)
        self.redrawROI()

    # --- Image update methods ---
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

    def _update_axis_range(self, *_):
        if self._last_xaxis_data is not None:
            iszx = self._last_xaxis_data.size
            ixMin = self._last_xaxis_data.min()
            ixMax = self._last_xaxis_data.max()
        else:
            iszx = self.imageWidth if self.readingOrder == self.Clike \
                else self.imageHeight
            ixMin = 0
            ixMax = iszx

        if self._last_yaxis_data is not None:
            iszy = self._last_yaxis_data.size
            iyMin = self._last_yaxis_data.min()
            iyMax = self._last_yaxis_data.max()
        else:
            iszy = self.imageHeight if self.readingOrder == self.Clike \
                else self.imageWidth
            iyMin = 0
            iyMax = iszy

        [_vx, _vy] = self._view.viewRange()
        limsx = np.array(_vx) / iszx * (ixMax-ixMin) + ixMin
        limsy = np.array(_vy) / iszy * (iyMax-iyMin) + iyMin
        self.xaxis.setRange(limsx[0], limsx[1])
        self.yaxis.setRange(limsy[0], limsy[1])

    @Slot(list)
    def _updateDisplay(self, data):
        logging.debug("SpectrogramView Update Display with new image")
        if self.autoSetColorbarLims:
            self.colorbar.setLimits(data)
        mini, maxi = data[0], data[1]
        img = data[2]
        self._image_item.setLevels([mini, maxi])
        self._image_item.setImage(
            img,
            autoLevels=False,
            autoDownsample=self.autoDownsample)

    # ROI update methods
    def redrawROI(self):
        startx = self._roi_offsetx
        endx = self._roi_offsetx + self._roi_width
        starty = self._roi_offsety
        endy = self._roi_offsety + self._roi_height
        self.ROICurve.setData(
            [startx, startx, endx, endx, startx],
            [starty, endy, endy, starty, starty])

    def showROI(self, show):
        """Set ROI visibility."""
        pen = mkPen()
        if show:
            pen.setColor(self.ROIColor)
        else:
            pen.setColor(QColor('transparent'))
        self.ROICurve.setPen(pen)

    # --- Properties ---
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

    @Property(bool)
    def autoSetColorbarLims(self):
        """
        Return if we should or not auto set colorbar limits.

        Return
        ------
        bool
        """
        return self._auto_colorbar_lims

    @autoSetColorbarLims.setter
    def autoSetColorbarLims(self, new_value):
        """
        Whether we should or not auto set colorbar limits.

        Parameters
        ----------
        new_value: bool
        """
        if new_value != self._auto_colorbar_lims:
            self._auto_colorbar_lims = new_value

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

    @Property(int)
    def imageHeight(self):
        """
        Return the height of the image.

        Return
        ------
        int
        """
        return self._image_height

    @Property(int)
    def ROIOffsetX(self):
        """
        Return the ROI offset in X axis in pixels.

        Return
        ------
        int
        """
        return self._roi_offsetx

    @ROIOffsetX.setter
    def ROIOffsetX(self, new_offset):
        """
        Set the ROI offset in X axis in pixels.

        Can be overridden by :attr:`ROIOffsetXChannel`.

        Parameters
        ----------
        new_offset: int
        """
        if new_offset is None:
            return
        boo = self._roi_offsetx != int(new_offset)
        boo &= not self._roioffsetxchannel
        if boo:
            self._roi_offsetx = int(new_offset)
            self.redrawROI()

    @Property(int)
    def ROIOffsetY(self):
        """
        Return the ROI offset in Y axis in pixels.

        Return
        ------
        int
        """
        return self._roi_offsety

    @ROIOffsetY.setter
    def ROIOffsetY(self, new_offset):
        """
        Set the ROI offset in Y axis in pixels.

        Can be overridden by :attr:`ROIOffsetYChannel`.

        Parameters
        ----------
        new_offset: int
        """
        if new_offset is None:
            return
        boo = self._roi_offsety != int(new_offset)
        boo &= not self._roioffsetychannel
        if boo:
            self._roi_offsety = int(new_offset)
            self.redrawROI()

    @Property(int)
    def ROIWidth(self):
        """
        Return the ROI width in pixels.

        Return
        ------
        int
        """
        return self._roi_width

    @ROIWidth.setter
    def ROIWidth(self, new_width):
        """
        Set the ROI width in pixels.

        Can be overridden by :attr:`ROIWidthChannel`.

        Parameters
        ----------
        new_width: int
        """
        if new_width is None:
            return
        boo = self._roi_width != int(new_width)
        boo &= not self._roiwidthchannel
        if boo:
            self._roi_width = int(new_width)
            self.redrawROI()

    @Property(int)
    def ROIHeight(self):
        """
        Return the ROI height in pixels.

        Return
        ------
        int
        """
        return self._roi_height

    @ROIHeight.setter
    def ROIHeight(self, new_height):
        """
        Set the ROI height in pixels.

        Can be overridden by :attr:`ROIHeightChannel`.

        Parameters
        ----------
        new_height: int
        """
        if new_height is None:
            return
        boo = self._roi_height != int(new_height)
        boo &= not self._roiheightchannel
        if boo:
            self._roi_height = int(new_height)
            self.redrawROI()

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

        if order == self.Clike:
            if self._last_xaxis_data is not None:
                self._image_width = self._last_xaxis_data.size
            if self._last_yaxis_data is not None:
                self._image_height = self._last_yaxis_data.size
        elif order == self.Fortranlike:
            if self._last_yaxis_data is not None:
                self._image_width = self._last_yaxis_data.size
            if self._last_xaxis_data is not None:
                self._image_height = self._last_xaxis_data.size

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

    # --- Events rederivations ---
    def keyPressEvent(self, ev):
        """Handle keypress events."""
        return

    def mouseMoveEvent(self, ev):
        if not self._image_item.width() or not self._image_item.height():
            super().mouseMoveEvent(ev)
            return
        pos = ev.pos()
        posaux = self._image_item.mapFromDevice(ev.pos())
        if not posaux:
            return
        if posaux.x() < 0 or posaux.x() >= self._image_item.width() or \
                posaux.y() < 0 or posaux.y() >= self._image_item.height():
            super().mouseMoveEvent(ev)
            return

        pos_scene = self._view.mapSceneToView(pos)
        x = round(pos_scene.x())
        y = round(pos_scene.y())

        if self.xAxisChannel and self._last_xaxis_data is not None:
            maxx = len(self._last_xaxis_data)-1
            x = x if x < maxx else maxx
            valx = self._last_xaxis_data[x]
        else:
            valx = x

        if self.yAxisChannel and self._last_yaxis_data is not None:
            maxy = len(self._last_yaxis_data)-1
            y = y if y < maxy else maxy
            valy = self._last_yaxis_data[y]
        else:
            valy = y

        txt = self.format_tooltip.format(valx, valy)
        QToolTip.showText(
            self.mapToGlobal(pos), txt, self, self.geometry(), 5000)
        super().mouseMoveEvent(ev)

    # --- Channels ---
    @Property(str)
    def imageChannel(self):
        """
        The channel address in use for the image data .

        Returns
        -------
        str
            Channel address
        """
        if self._imagechannel:
            return str(self._imagechannel.address)
        else:
            return ''

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
            # Disconnect old channel
            if self._imagechannel:
                self._imagechannel.disconnect()
            # Create and connect new channel
            self._imagechannel = PyDMChannel(
                address=value,
                connection_slot=self.image_connection_state_changed,
                value_slot=self.image_value_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[0] = self._imagechannel
            self._imagechannel.connect()

    @Property(str)
    def xAxisChannel(self):
        """
        The channel address in use for the x-axis of image.

        Returns
        -------
        str
            Channel address
        """
        if self._xaxischannel:
            return str(self._xaxischannel.address)
        else:
            return ''

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
            # Disconnect old channel
            if self._xaxischannel:
                self._xaxischannel.disconnect()
            # Create and connect new channel
            self._xaxischannel = PyDMChannel(
                address=value,
                connection_slot=self.connectionStateChanged,
                value_slot=self.xaxis_value_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[1] = self._xaxischannel
            self._xaxischannel.connect()

    @Property(str)
    def yAxisChannel(self):
        """
        The channel address in use for the time axis.

        Returns
        -------
        str
            Channel address
        """
        if self._yaxischannel:
            return str(self._yaxischannel.address)
        else:
            return ''

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
            # Disconnect old channel
            if self._yaxischannel:
                self._yaxischannel.disconnect()
            # Create and connect new channel
            self._yaxischannel = PyDMChannel(
                address=value,
                connection_slot=self.yaxis_connection_state_changed,
                value_slot=self.yaxis_value_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[2] = self._yaxischannel
            self._yaxischannel.connect()

    @Property(str)
    def ROIOffsetXChannel(self):
        """
        Return the channel address in use for the image ROI horizontal offset.

        Returns
        -------
        str
            Channel address

        """
        if self._roioffsetxchannel:
            return str(self._roioffsetxchannel.address)
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
        if self._roioffsetxchannel != value:
            # Disconnect old channel
            if self._roioffsetxchannel:
                self._roioffsetxchannel.disconnect()
            # Create and connect new channel
            self._roioffsetxchannel = PyDMChannel(
                address=value,
                connection_slot=self.roioffsetx_connection_state_changed,
                value_slot=self.roioffsetx_value_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[3] = self._roioffsetxchannel
            self._roioffsetxchannel.connect()

    @Property(str)
    def ROIOffsetYChannel(self):
        """
        Return the channel address in use for the image ROI vertical offset.

        Returns
        -------
        str
            Channel address

        """
        if self._roioffsetychannel:
            return str(self._roioffsetychannel.address)
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
        if self._roioffsetychannel != value:
            # Disconnect old channel
            if self._roioffsetychannel:
                self._roioffsetychannel.disconnect()
            # Create and connect new channel
            self._roioffsetychannel = PyDMChannel(
                address=value,
                connection_slot=self.roioffsety_connection_state_changed,
                value_slot=self.roioffsety_value_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[4] = self._roioffsetychannel
            self._roioffsetychannel.connect()

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
                connection_slot=self.roiwidth_connection_state_changed,
                value_slot=self.roiwidth_value_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[5] = self._roiwidthchannel
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
                connection_slot=self.roiheight_connection_state_changed,
                value_slot=self.roiheight_value_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[6] = self._roiheightchannel
            self._roiheightchannel.connect()

    def channels(self):
        """
        Return the channels being used for this Widget.

        Returns
        -------
        channels : list
            List of PyDMChannel objects
        """
        return [ch for ch in self._channels if ch is not None]

    def channels_for_tools(self):
        """Return channels for tools."""
        return [self._imagechannel]
