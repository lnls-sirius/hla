"""SiriusScrnView widget."""

import time
from copy import deepcopy as _dcopy
import numpy as np
from qtpy.QtWidgets import QHBoxLayout, QSizePolicy as QSzPlcy, QVBoxLayout, \
    QToolTip
from qtpy.QtCore import Qt, Slot, Signal, Property
from pydm.widgets import PyDMImageView, PyDMLabel, PyDMSpinbox, \
    PyDMPushButton, PyDMEnumComboBox, PyDMLineEdit
from pydm.widgets.channel import PyDMChannel

from siriushla.widgets import PyDMStateButton, SiriusLedState


class SiriusImageView(PyDMImageView):
    """A PyDMImageView with methods to handle screens calibration grids."""

    receivedData = Signal()
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
        self._calibration_grid_filterfactor = 0.25
        self._calibration_grid_removeborder = 150
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
        self.colorMap = self.Jet

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
        img = _dcopy(self._calibration_grid_orig)
        maxdata = self._calibration_grid_maxdata
        border = self._calibration_grid_removeborder
        if self.readingOrder == self.ReadingOrder.Clike:
            roi = img.reshape((-1, self._calibration_grid_width), order='C')
        else:
            roi = img.reshape((self._calibration_grid_width, -1), order='F')
        if border > 0:
            roi[:, 0:border] = np.full((roi.shape[0], border), maxdata)
            roi[:, -border:] = np.full((roi.shape[0], border), maxdata)
            roi[0:border, :] = np.full((border, roi.shape[1]), maxdata)
            roi[-border:, :] = np.full((border, roi.shape[1]), maxdata)
        self._calibration_grid_image = np.where(
            roi < self._calibration_grid_filterfactor*maxdata, True, False)

    @Slot(bool)
    def showCalibrationGrid(self, show):
        """Show calibration_grid_image over the current image_waveform."""
        self._show_calibration_grid = show
        self.needs_redraw = True

    @property
    def calibrationGrid(self):
        """Return Numpy array containing original grid."""
        return _dcopy(self._calibration_grid_orig)

    @calibrationGrid.setter
    def calibrationGrid(self, data):
        """Receive a list 'data' which elements are: [width, new_grid:]."""
        self._calibration_grid_orig = data[1:]
        self._calibration_grid_width = int(data[0])
        self._calibration_grid_maxdata = data[1:].max()
        self._update_calibration_grid_image()
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

    @property
    def calibration_grid_removeborder(self):
        """Factor used to remove border of the calibration grid.

        Returns
        -------
        float
            Number of Rows/Columns to be removed

        """
        return self._calibration_grid_removeborder

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
                self.needs_redraw = True

    def set_calibration_grid_border2remove(self, value):
        """Set factor used to remove border of the calibration grid.

        Parameters
        ----------
        value: int
            Number of Rows/Columns to be removed

        """
        self._calibration_grid_removeborder = value
        if self._calibration_grid_image is not None:
            self._update_calibration_grid_image()
            self.needs_redraw = True

    def process_image(self, image):
        """Reimplement process_image method to add grid to image."""
        self.receivedData.emit()
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
        Return the channel address in use for the image maximum width.

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
        Return the channel address in use for the image maximum width.

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
        Return the channel address in use for the image maximum height.

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
        Return the channel address in use for the image maximum height.

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

    def mousePressEvent(self, ev):
        pos = ev.pos()
        pos_scene = self.view.vb.mapSceneToView(pos)
        txt = '{0}, {1}'.format(round(pos_scene.x()),
                                round(pos_scene.y()))
        QToolTip.showText(
            self.mapToGlobal(pos), txt,
            self, self.geometry(), 5000)


def create_propty_layout(parent, prefix, propty, propty_type='', cmd=dict(),
                         layout='hbox', width=7.10, height=1.29,
                         use_linedit=False):
    """Return a layout that handles a property according to 'propty_type'."""
    if layout == 'hbox':
        layout = QHBoxLayout()
    elif layout == 'vbox':
        layout = QVBoxLayout()

    if propty_type == 'sprb':
        if use_linedit:
            setattr(parent, 'PyDMLineEdit_'+propty,
                    PyDMLineEdit(parent=parent,
                                 init_channel=prefix+':'+propty+'-SP'))
            sp = getattr(parent, 'PyDMLineEdit_'+propty)
        else:
            setattr(parent, 'PyDMSpinbox_'+propty,
                    PyDMSpinbox(parent=parent,
                                init_channel=prefix+':'+propty+'-SP'))
            sp = getattr(parent, 'PyDMSpinbox_'+propty)
            sp.showStepExponent = False
        sp.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        sp.setAlignment(Qt.AlignCenter)
        layout.addWidget(sp)
        setattr(parent, 'PyDMLabel_'+propty,
                PyDMLabel(parent=parent,
                          init_channel=prefix+':'+propty+'-RB'))
        label = getattr(parent, 'PyDMLabel_'+propty)
        if not cmd:
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
        led.setStyleSheet(
            "min-width:1.29em; max-width:1.29em; "
            "min-height:1.29em; max-height:1.29em;")
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
        if not cmd:
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
        if not cmd:
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
    elif propty_type == 'cte':
        setattr(parent, 'PyDMLabel_'+propty,
                PyDMLabel(parent=parent,
                          init_channel=prefix+':'+propty+'-Cte'))
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
                               pressValue=cmd['pressValue']))
        pb = getattr(parent, 'PyDMPushButton_'+propty)
        pb.setObjectName('PyDMPushButton_'+propty)
        if 'icon' in cmd.keys():
            pb.setIcon(cmd['icon'])
        if 'toolTip' in cmd.keys():
            pb.setToolTip(cmd['toolTip'])
        pb.channel = prefix+':'+cmd['name']+'-Cmd'

        _w = cmd['width']+'px' if 'width' in cmd.keys() else str(width)+'em'
        _h = cmd['height']+'px' if 'height' in cmd.keys() else str(height)+'em'
        stylesheet = """
            #PyDMPushButton_""" + propty + """{
                min-width:wval; max-width:wval;
                min-height:hval; max-height:hval;
                iconsize;
            }""".replace('wval', _w).replace('hval', _h)
        _is = 'icon-size:'+cmd['icon-size']+'px;' \
            if 'icon-size' in cmd.keys() else ''
        stylesheet.replace('iconsize;',  _is)
        pb.setStyleSheet(stylesheet)
        layout.addWidget(pb)

    layout.setAlignment(Qt.AlignVCenter)
    return layout
