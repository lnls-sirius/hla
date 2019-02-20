"""SiriusScrnView widget."""

import time
from copy import deepcopy as _dcopy
import numpy as np
from qtpy.QtWidgets import QHBoxLayout, QSizePolicy as QSzPlcy, QVBoxLayout
from qtpy.QtCore import Qt, Slot, Signal, Property
from pydm.widgets import PyDMImageView, PyDMLabel, PyDMSpinbox, \
                         PyDMPushButton, PyDMEnumComboBox
from pydm.widgets.channel import PyDMChannel
from siriushla.widgets import PyDMStateButton, SiriusLedState


class SiriusImageView(PyDMImageView):
    """A PyDMImageView with methods to handle screens calibration grids."""

    failToSaveGrid = Signal()

    def __init__(self, parent=None,
                 image_channel=None, width_channel=None,
                 offsetx_channel=None, offsety_channel=None,
                 maxwidth_channel=None, maxheight_channel=None):
        """Initialize the object."""
        PyDMImageView.__init__(
            self, parent=parent, image_channel=image_channel,
            width_channel=width_channel)
        self._channels.extend(4*[None, ])
        self._calibration_grid_image = None
        self._calibration_grid_maxdata = None
        self._calibration_grid_width = None
        self._calibration_grid_filterfactor = 0.5
        self._image_roi_offsetx = 0
        self._offsetxchannel = None
        self._image_roi_offsety = 0
        self._offsetychannel = None
        self._image_maxwidth = 0
        self._maxwidthchannel = None
        self._image_maxheight = 0
        self._maxheightchannel = None
        self._show_calibration_grid = False
        # Set live channels if requested on initialization
        if offsetx_channel:
            self.ROIOffsetXChannel = offsetx_channel
        if offsety_channel:
            self.ROIOffsetYChannel = offsety_channel
        if maxwidth_channel:
            self.maxWidthChannel = maxwidth_channel
        if maxheight_channel:
            self.maxHeightChannel = maxheight_channel

    @Slot()
    def saveCalibrationGrid(self):
        """Save current image as calibration_grid_image."""
        for i in range(40):
            if self.image_waveform.size == (
                    self.image_maxwidth*self.image_maxheight):
                img = self.image_waveform.copy()
                self._calibration_grid_orig = img
                self._calibration_grid_width = self.imageWidth
                self._calibration_grid_maxdata = img.max()
                self._update_calibration_grid_image()
                break
            time.sleep(0.05)
        else:
            self.failToSaveGrid.emit()

    def _update_calibration_grid_image(self):
        img = self._calibration_grid_orig
        grid = np.where(img < self._calibration_grid_filterfactor *
                        self._calibration_grid_maxdata, True, False)
        if self.readingOrder == self.ReadingOrder.Clike:
            self._calibration_grid_image = grid.reshape(
                (-1, self._calibration_grid_width), order='C')
        else:
            self._calibration_grid_image = grid.reshape(
                (self._calibration_grid_width, -1), order='F')

    @Slot(bool)
    def showCalibrationGrid(self, show):
        """Show calibration_grid_image over the current image_waveform."""
        self._show_calibration_grid = show
        self.needs_redraw = True

    @property
    def calibration_grid_filterfactor(self):
        """Factor used to filter calibration grid.

        Pixels with values smaller than filterfactor*img_maxdata
        are set to zero.

        Returns
        -------
        float
            Calibration Grid Filter Factor

        """
        return self._calibration_grid_filterfactor*100

    def set_calibration_grid_filterfactor(self, value):
        """Set factor used to filter calibration grid.

        Pixels with values smaller than filterfactor*img_maxdata
        are set to zero.

        Parameters
        ----------
        value: int
            Calibration Grid Filter Factor

        """
        value /= 100
        if value >= 0 and self._calibration_grid_filterfactor != value:
            self._calibration_grid_filterfactor = value
            if self._calibration_grid_image is not None:
                self._update_calibration_grid_image()

    def process_image(self, image):
        """Reimplement process_image method to add grid to image."""
        image2process = _dcopy(image)
        if ((self._show_calibration_grid) and
                (self._calibration_grid_image is not None)):
            try:
                grid = self._adjust_calibration_grid(image2process)
                image2process[grid] = self._calibration_grid_maxdata
            except Exception:
                print('Grid dimentions do not match image dimentions!')
        return image2process

    def _adjust_calibration_grid(self, img):
        height = np.size(img, 0)
        width = np.size(img, 1)
        grid = self._calibration_grid_image[
            self._image_roi_offsety:(self._image_roi_offsety+height),
            self._image_roi_offsetx:(self._image_roi_offsetx+width)]
        return grid

    def roioffsetx_connection_state_changed(self, conn):
        """
        Run when the ROIOffsetX Channel connection state changes.

        Parameters
        ----------
        conn : bool
            The new connection state.

        """
        if not conn:
            self._image_roi_offsetx = 0

    def roioffsety_connection_state_changed(self, conn):
        """
        Run when the ROIOffsetY Channel connection state changes.

        Parameters
        ----------
        conn : bool
            The new connection state.

        """
        if not conn:
            self._image_roi_offsety = 0

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
        self._image_roi_offsetx = new_offset

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
        self._image_roi_offsety = new_offset

    @property
    def image_maxwidth(self):
        """Return image maximum width."""
        return self._image_maxwidth

    def image_maxwidth_changed(self, new_max):
        """
        Run when the maxWidth Channel value changes.

        Parameters
        ----------
        new_max : int
            The new image max width

        """
        if new_max is None:
            return
        self._image_maxwidth = int(new_max)

    @property
    def image_maxheight(self):
        """Return image maximum height."""
        return self._image_maxheight

    def image_maxheight_changed(self, new_max):
        """
        Run when the maxHeight Channel value changes.

        Parameters
        ----------
        new_max : int
            The new image max height

        """
        if new_max is None:
            return
        self._image_maxheight = int(new_max)

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
    def maxWidthChannel(self):
        """
        Return the channel address in use for the image ROI horizontal offset.

        Returns
        -------
        str
            Channel address

        """
        if self._maxwidthchannel:
            return str(self._maxwidthchannel.address)
        else:
            return ''

    @maxWidthChannel.setter
    def maxWidthChannel(self, value):
        """
        Return the channel address in use for the image ROI horizontal offset.

        Parameters
        ----------
        value : str
            Channel address

        """
        if self._maxwidthchannel != value:
            # Disconnect old channel
            if self._maxwidthchannel:
                self._maxwidthchannel.disconnect()
            # Create and connect new channel
            self._maxwidthchannel = PyDMChannel(
                address=value,
                value_slot=self.image_maxwidth_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[4] = self._maxwidthchannel
            self._maxwidthchannel.connect()

    @Property(str)
    def maxHeightChannel(self):
        """
        Return the channel address in use for the image ROI vertical offset.

        Returns
        -------
        str
            Channel address

        """
        if self._maxheightchannel:
            return str(self._maxheightchannel.address)
        else:
            return ''

    @maxHeightChannel.setter
    def maxHeightChannel(self, value):
        """
        Return the channel address in use for the image ROI vertical offset.

        Parameters
        ----------
        value : str
            Channel address

        """
        if self._maxheightchannel != value:
            # Disconnect old channel
            if self._maxheightchannel:
                self._maxheightchannel.disconnect()
            # Create and connect new channel
            self._maxheightchannel = PyDMChannel(
                address=value,
                value_slot=self.image_maxheight_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[5] = self._maxheightchannel
            self._maxheightchannel.connect()


def create_propty_layout(parent, prefix, propty, propty_type, cmd=dict(),
                         layout='hbox', width=7.10, height=1.29):
    """Return a layout that handles a property according to 'propty_type'."""
    if layout == 'hbox':
        layout = QHBoxLayout()
    elif layout == 'vbox':
        layout = QVBoxLayout()

    if propty_type == 'sprb':
        setattr(parent, 'PyDMSpinbox_'+propty,
                PyDMSpinbox(parent=parent,
                            init_channel=prefix+':'+propty+'-SP'))
        spinbox = getattr(parent, 'PyDMSpinbox_'+propty)
        spinbox.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        spinbox.setAlignment(Qt.AlignCenter)
        spinbox.showStepExponent = False
        layout.addWidget(spinbox)
        setattr(parent, 'PyDMLabel_'+propty,
                PyDMLabel(parent=parent,
                          init_channel=prefix+':'+propty+'-RB'))
        label = getattr(parent, 'PyDMLabel_'+propty)
        label.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
    elif propty_type == 'enbldisabl':
        setattr(parent, 'PyDMStateButton_'+propty,
                PyDMStateButton(parent=parent,
                                init_channel=prefix+':'+propty+'-Sel'))
        statebutton = getattr(parent, 'PyDMStateButton_'+propty)
        statebutton.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        statebutton.shape = 1
        layout.addWidget(statebutton)
        setattr(parent, 'SiriusLedState_'+propty,
                SiriusLedState(parent=parent,
                               init_channel=prefix+':'+propty+'-Sts'))
        led = getattr(parent, 'SiriusLedState_'+propty)
        led.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        led.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
        layout.addWidget(led)
    elif propty_type == 'offon':
        setattr(parent, 'PyDMStateButton_'+propty,
                PyDMStateButton(parent=parent,
                                init_channel=prefix+':'+propty+'-Sel'))
        statebutton = getattr(parent, 'PyDMStateButton_'+propty)
        statebutton.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        statebutton.shape = 1
        layout.addWidget(statebutton)
        setattr(parent, 'PyDMLabel_'+propty,
                PyDMLabel(parent=parent,
                          init_channel=prefix+':'+propty+'-Sts'))
        label = getattr(parent, 'PyDMLabel_'+propty)
        label.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
    elif propty_type == 'enum':
        setattr(parent, 'PyDMEnumComboBox_'+propty,
                PyDMEnumComboBox(parent=parent,
                                 init_channel=prefix+':'+propty+'-Sel'))
        combobox = getattr(parent, 'PyDMEnumComboBox_'+propty)
        combobox.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        layout.addWidget(combobox)
        setattr(parent, 'PyDMLabel_'+propty,
                PyDMLabel(parent=parent,
                          init_channel=prefix+':'+propty+'-Sts'))
        label = getattr(parent, 'PyDMLabel_'+propty)
        label.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
    elif propty_type == 'mon':
        setattr(parent, 'PyDMLabel_'+propty,
                PyDMLabel(parent=parent,
                          init_channel=prefix+':'+propty+'-Mon'))
        label = getattr(parent, 'PyDMLabel_'+propty)
        label.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

    if cmd:
        setattr(parent, 'PyDMPushButton_'+propty,
                PyDMPushButton(parent=parent, label=cmd['label'],
                               pressValue=cmd['pressValue'],
                               init_channel=prefix+':'+cmd['name']+'-Cmd'))
        pb = getattr(parent, 'PyDMPushButton_'+propty)
        pb.setStyleSheet("""max-width:wvalem; max-height:hvalem;""".replace(
            'wval', str(width)).replace('hval', str(height)))
        layout.addWidget(pb)

    layout.setAlignment(Qt.AlignVCenter)

    return layout
