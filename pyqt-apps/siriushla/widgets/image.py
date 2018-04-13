import numpy as np
import pyqtgraph
from pyqtgraph import ImageView, ColorMap
from pyqtgraph.graphicsItems.ViewBox.ViewBoxMenu import ViewBoxMenu
from pydm.PyQt.QtGui import QActionGroup
from pydm.PyQt.QtCore import pyqtSlot, pyqtProperty, Q_ENUMS, QTimer
from pydm.widgets.channel import PyDMChannel
from pydm.widgets.colormaps import cmaps, cmap_names, PyDMColorMap
from pydm.widgets.base import PyDMWidget
pyqtgraph.setConfigOption('imageAxisOrder', 'row-major')


class ReadingOrder(object):
    """Class to build ReadingOrder ENUM property."""

    Fortranlike = 0
    Clike = 1


class SiriusImageView(ImageView, PyDMWidget, PyDMColorMap, ReadingOrder):
    """
    A PyQtGraph ImageView with support for Channels and more from PyDM.

    If there is no :attr:`channelWidth` it is possible to define the width of
    the image with the :attr:`width` property.

    The :attr:`normalizeData` property defines if the colors of the images are
    relative to the :attr:`colorMapMin` and :attr:`colorMapMax` property or to
    the minimum and maximum values of the image.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    image_channel : str, optional
        The channel to be used by the widget for the image data.
    width_channel : str, optional
        The channel to be used by the widget to receive the image width
        information
    """

    Q_ENUMS(ReadingOrder)
    Q_ENUMS(PyDMColorMap)

    reading_orders = {ReadingOrder.Fortranlike: 'F',
                      ReadingOrder.Clike: 'C'}
    color_maps = cmaps

    def __init__(self, parent=None, image_channel=None, width_channel=None):
        """Initialize the object."""
        ImageView.__init__(self, parent)
        PyDMWidget.__init__(self)
        self.axes = dict({"t": None, "x": 0, "y": 1, "c": None})
        self._imagechannel = image_channel
        self._widthchannel = width_channel
        self.image_waveform = np.zeros(0)
        self._image_width = 0
        self._normalize_data = False

        # Hide some itens of the widget
        self.ui.histogram.hide()
        self.getImageItem().sigImageChanged.disconnect(
                                        self.ui.histogram.imageChanged)
        self.ui.roiBtn.hide()
        self.ui.menuBtn.hide()

        # Set color map limits
        self.cm_min = 0.0
        self.cm_max = 255.0

        # Set default reading order of numpy array data to Fortranlike
        self._reading_order = ReadingOrder.Fortranlike

        # Make a right-click menu for changing the color map.
        self.cm_group = QActionGroup(self)
        self.cmap_for_action = {}
        for cm in self.color_maps:
            action = self.cm_group.addAction(cmap_names[cm])
            action.setCheckable(True)
            self.cmap_for_action[action] = cm

        # Set the default colormap.
        self._colormap = PyDMColorMap.Inferno
        self._cm_colors = None
        self.colorMap = self._colormap

        # Setup the redraw timer.
        self.needs_redraw = False
        self.redraw_timer = QTimer(self)
        self.redraw_timer.timeout.connect(self.redrawImage)
        self._redraw_rate = 30
        self.maxRedrawRate = self._redraw_rate

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
        self.menu = ViewBoxMenu(self.getView())
        cm_menu = self.menu.addMenu("Color Map")
        for act in self.cmap_for_action.keys():
            cm_menu.addAction(act)
        cm_menu.triggered.connect(self._changeColorMap)
        return self.menu

    def _changeColorMap(self, action):
        """
        Change the colormap via action from ContextMenu.

        Method invoked by the colormap Action Menu that changes the
        current colormap used to render the image.

        Parameters
        ----------
        action : QAction
        """
        self.colorMap = self.cmap_for_action[action]

    @pyqtProperty(int)
    def colorMapMin(self):
        """Minimum value to be considered for color scale definition.

        Returns
        -------
        float
            minimum value of the color scale.
        """
        return self.cm_min

    @colorMapMin.setter
    @pyqtSlot(int)
    def colorMapMin(self, new_min):
        """Set the minimum value to be considered for color scale definition.

        Parameters
        -------
        new_min: float
        """
        if self.cm_min == new_min or new_min > self.cm_max:
            return
        self.cm_min = float(new_min)
        self.setColorMap()

    @pyqtProperty(int)
    def colorMapMax(self):
        """Maximum value to be considered for color scale definition.

        Returns
        -------
        float
            maximum value of the color scale.
        """
        return self.cm_max

    @colorMapMax.setter
    @pyqtSlot(int)
    def colorMapMax(self, new_max):
        """Set the maximum value to be considered for color scale definition.

        Parameters
        -------
        new_max: float
        """
        if self.cm_max == new_max or new_max < self.cm_min:
            return
        self.cm_max = float(new_max)
        self.setColorMap()

    def setColorMapLimits(self, mn, mx):
        """Set the limit values for the colormap.

        Parameters
        ----------
        mn : int
            The lower limit
        mx : int
            The upper limit
        """
        if mn >= mx:
            return
        self.cm_max = float(mx)
        self.cm_min = float(mn)
        self.setColorMap()

    @pyqtProperty(PyDMColorMap)
    def colorMap(self):
        """
        Return the color map used by the ImageView.

        Returns
        -------
        PyDMColorMap
        """
        return self._colormap

    @colorMap.setter
    def colorMap(self, new_cmap):
        """
        Set the color map used by the ImageView.

        Parameters
        ----------
        new_cmap: PyDMColorMap
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
            pos = np.linspace(0.0, 1.0, num=len(self._cm_colors))
            cmap = ColorMap(pos, self._cm_colors)
        self.getView().setBackgroundColor(cmap.map(0))
        lut = cmap.getLookupTable(0.0, 1.0, alpha=False)
        self.getImageItem().setLookupTable(lut)
        self.needs_redraw = True

    @pyqtSlot(bool)
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

    @pyqtSlot(np.ndarray)
    def image_value_changed(self, new_image):
        """
        Callback invoked when the Image Channel value is changed.

        Reshape and display the new image.

        Parameters
        ----------
        new_image : np.ndarray
            The new image data.  This can be a flat 1D array, or a 2D array.
        """
        if new_image is None or not new_image.size:
            return
        self.image_waveform = new_image
        self.needs_redraw = True

    @pyqtSlot(int)
    def image_width_changed(self, new_width):
        """
        Callback invoked when the Image Width Channel value is changed.

        Reshape the image data and triggers a ```redrawImage```

        Parameters
        ----------
        new_width : int
            The new image width
        """
        if new_width is None:
            return
        self._image_width = int(new_width)

    def redrawImage(self):
        """Set the image data into the ImageItem."""
        if not self.needs_redraw:
            return
        image_dimensions = len(self.image_waveform.shape)
        if image_dimensions == 1:
            if self.imageWidth < 1:
                # There is no width for this image yet, so we can't draw it.
                return
            img = self.image_waveform.reshape(
                self.imageWidth, -1,
                order=self.reading_orders[self._reading_order])
        else:
            img = self.image_waveform

        if len(img) <= 0:
            return
        if self._normalize_data:
            mini = self.image_waveform.min()
            maxi = self.image_waveform.max()
        else:
            mini = self.cm_min
            maxi = self.cm_max
        self.getImageItem().setLevels([mini, maxi])
        self.getImageItem().setImage(
            img,
            autoLevels=False,
            autoDownsample=True)
        self.needs_redraw = False

    @pyqtProperty(int)
    def imageWidth(self):
        """Return the width of the image.

        Return
        ------
        int
        """
        return self._image_width

    @imageWidth.setter
    def imageWidth(self, new_width):
        """Set the width of the image.

        Can be overridden by :attr:`widthChannel`.

        Parameters
        ----------
        new_width: int
        """
        if self._image_width != int(new_width) and self._widthchannel is None:
            self._image_width = int(new_width)

    @pyqtProperty(bool)
    def normalizeData(self):
        """Return True if the colors are relative to data maximum and minimum.

        Returns
        ----------
        bool
        """
        return self._normalize_data

    @normalizeData.setter
    @pyqtSlot(bool)
    def normalizeData(self, new_norm):
        """Define if the colors are relative to maximum and minimum of data.

        Parameters
        ----------
        new_norm: bool
        """
        if self._normalize_data == new_norm:
            return
        self._normalize_data = new_norm
        self.needs_redraw = True

    @pyqtProperty(ReadingOrder)
    def readingOrder(self):
        """Reading order of the :attr:`imageChannel` array.

        Returns
        -------
        ReadingOrder
        """
        return int(self._reading_order)

    @readingOrder.setter
    def readingOrder(self, new_order):
        """Set reading order of the :attr:`imageChannel` array.

        Parameters
        ----------
        new_order: ReadingOrder
        """
        if self._reading_order != new_order:
            self._reading_order = new_order
        self.needs_redraw = True

    def keyPressEvent(self, ev):
        """Handle keypress events."""
        return

    @pyqtProperty(str)
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

    @pyqtProperty(str)
    def widthChannel(self):
        """
        The channel address in use for the image width .

        Returns
        -------
        str
            Channel address
        """
        return str(self._widthchannel)

    @widthChannel.setter
    def widthChannel(self, value):
        """
        The channel address in use for the image width .

        Parameters
        ----------
        value : str
            Channel address
        """
        if self._widthchannel != value:
            self._widthchannel = str(value)

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
                    address=self.widthChannel,
                    connection_slot=self.connectionStateChanged,
                    value_slot=self.image_width_changed,
                    severity_slot=self.alarmSeverityChanged)]
        return self._channels

    def channels_for_tools(self):
        """Return channels for tools."""
        return [c for c in self.channels() if c.address == self.imageChannel]

    @pyqtProperty(int)
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
        self._redraw_rate = float(redraw_rate)
        self.redraw_timer.setInterval(int((1.0/self._redraw_rate)*1000))
