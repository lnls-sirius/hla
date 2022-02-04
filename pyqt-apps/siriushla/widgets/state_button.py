"""PyDM State Button Class."""

import os as _os
import hashlib as _hashlib
import logging as _log

import numpy as _np

from qtpy.QtWidgets import QStyleOption, QFrame, QMessageBox, QInputDialog, \
    QLineEdit
from qtpy.QtGui import QPainter
from qtpy.QtCore import Property, Q_ENUMS, QByteArray, QRectF, \
    QSize, Signal, Qt, QFile
from qtpy.QtSvg import QSvgRenderer

from pydm.widgets.base import PyDMWritableWidget


BUTTONSHAPE = {'Squared': 0, 'Rounded': 1}


class PyDMStateButton(QFrame, PyDMWritableWidget):
    """
    A StateButton with support for Channels and much more from PyDM.

    It consists on QPushButton with internal state.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    init_channel : str, optional
        The channel to be used by the widget.
    """

    class buttonShapeMap:
        """Enum class of shapes of button."""

        locals().update(**BUTTONSHAPE)

    Q_ENUMS(buttonShapeMap)

    # enumMap for buttonShapeMap
    locals().update(**BUTTONSHAPE)

    squaredbuttonstatesdict = dict()
    path = _os.path.abspath(_os.path.dirname(__file__))
    f = QFile(_os.path.join(path, 'resources/but_shapes/squared_on.svg'))
    if f.open(QFile.ReadOnly):
        squaredbuttonstatesdict['On'] = str(f.readAll(), 'utf-8')
    f.close()
    f = QFile(_os.path.join(path, 'resources/but_shapes/squared_off.svg'))
    if f.open(QFile.ReadOnly):
        squaredbuttonstatesdict['Off'] = str(f.readAll(), 'utf-8')
    f.close()
    f = QFile(_os.path.join(path, 'resources/but_shapes/squared_disconn.svg'))
    if f.open(QFile.ReadOnly):
        squaredbuttonstatesdict['Disconnected'] = str(f.readAll(), 'utf-8')
    f.close()

    roundedbuttonstatesdict = dict()
    f = QFile(_os.path.join(path, 'resources/but_shapes/rounded_on.svg'))
    if f.open(QFile.ReadOnly):
        roundedbuttonstatesdict['On'] = str(f.readAll(), 'utf-8')
    f.close()
    f = QFile(_os.path.join(path, 'resources/but_shapes/rounded_off.svg'))
    if f.open(QFile.ReadOnly):
        roundedbuttonstatesdict['Off'] = str(f.readAll(), 'utf-8')
    f.close()
    f = QFile(_os.path.join(path, 'resources/but_shapes/rounded_disconn.svg'))
    if f.open(QFile.ReadOnly):
        roundedbuttonstatesdict['Disconnected'] = str(f.readAll(), 'utf-8')
    f.close()

    clicked = Signal()
    DEFAULT_CONFIRM_MESSAGE = "Are you sure you want to proceed?"

    def __init__(self, parent=None, init_channel=None, invert=False):
        """Initialize all internal states and properties."""
        QFrame.__init__(self, parent)
        PyDMWritableWidget.__init__(self, init_channel=init_channel)

        self._off = 0
        self._on = 1
        self.invert = invert

        self._bit = -1
        self._bit_val = 0
        self.value = 0
        self.clicked.connect(self.send_value)
        self.shape = 0
        self.renderer = QSvgRenderer()

        self._show_confirm_dialog = False
        self._confirm_message = PyDMStateButton.DEFAULT_CONFIRM_MESSAGE
        self._password_protected = False
        self._password = ""
        self._protected_password = ""

    @Property(bool)
    def passwordProtected(self):
        """
        Whether or not this button is password protected.

        Returns
        -------
        bool
        """
        return self._password_protected

    @passwordProtected.setter
    def passwordProtected(self, value):
        """
        Whether or not this button is password protected.

        Parameters
        ----------
        value : bool
        """
        if self._password_protected != value:
            self._password_protected = value

    @Property(str)
    def password(self):
        """
        Password to be encrypted using SHA256.

        .. warning::
            To avoid issues exposing the password this method
            always returns an empty string.

        Returns
        -------
        str
        """
        return ""

    @password.setter
    def password(self, value):
        """
        Password to be encrypted using SHA256.

        Parameters
        ----------
        value : str
            The password to be encrypted
        """
        if value is not None and value != "":
            sha = _hashlib.sha256()
            sha.update(value.encode())
            # Use the setter as it also checks whether the existing password
            # is the same with the new one, and only updates if the new
            # password is different
            self.protectedPassword = sha.hexdigest()

    @Property(str)
    def protectedPassword(self):
        """
        The encrypted password.

        Returns
        -------
        str
        """
        return self._protected_password

    @protectedPassword.setter
    def protectedPassword(self, value):
        if self._protected_password != value:
            self._protected_password = value

    @Property(bool)
    def showConfirmDialog(self):
        """
        Wether or not to display a confirmation dialog.

        Returns
        -------
        bool
        """
        return self._show_confirm_dialog

    @showConfirmDialog.setter
    def showConfirmDialog(self, value):
        """
        Wether or not to display a confirmation dialog.

        Parameters
        ----------
        value : bool
        """
        if self._show_confirm_dialog != value:
            self._show_confirm_dialog = value

    @Property(str)
    def confirmMessage(self):
        """
        Message to be displayed at the Confirmation dialog.

        Returns
        -------
        str
        """
        return self._confirm_message

    @confirmMessage.setter
    def confirmMessage(self, value):
        """
        Message to be displayed at the Confirmation dialog.

        Parameters
        ----------
        value : str
        """
        if self._confirm_message != value:
            self._confirm_message = value

    def mouseReleaseEvent(self, ev):
        """Deal with mouse clicks. Only accept clicks within the figure."""
        cond = ev.button() == Qt.LeftButton
        cond &= ev.x() < self.width()/2+self.height()
        cond &= ev.x() > self.width()/2-self.height()
        if cond:
            self.clicked.emit()

    def value_changed(self, new_val):
        """
        Callback invoked when the Channel value is changed.

        Display the value of new_val accordingly. If :attr:'pvBit' is n>=0 or
        positive the button display the state of the n-th digit of the channel.

        Parameters
        ----------
        new_value : str, int, float, bool or np.ndarray
            The new value from the channel. The type depends on the channel.
        """
        if isinstance(new_val, _np.ndarray):
            _log.warning('PyDMStateButton received a numpy array to ' +
                         self.channel+' ('+str(new_val)+')!')
            return
        super(PyDMStateButton, self).value_changed(new_val)
        value = int(new_val)
        self.value = value
        if self._bit >= 0:
            value = (value >> self._bit) & 1
        self._bit_val = value
        self.update()

    def confirm_dialog(self):
        """
        Show the confirmation dialog with the proper message in case
        ```showConfirmMessage``` is True.

        Returns
        -------
        bool
            True if the message was confirmed or if ```showCofirmMessage```
            is False.
        """

        if not self._show_confirm_dialog:
            return True

        if self._confirm_message == "":
            self._confirm_message = PyDMStateButton.DEFAULT_CONFIRM_MESSAGE
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(self._confirm_message)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        ret = msg.exec_()
        return not ret == QMessageBox.No

    def validate_password(self):
        """
        If the widget is ```passwordProtected```, this method will propmt
        the user for the correct password.

        Returns
        -------
        bool
            True in case the password was correct of if the widget is not
            password protected.
        """
        if not self._password_protected:
            return True

        pwd, ok = QInputDialog().getText(
           None, "Authentication", "Please enter your password:",
           QLineEdit.Password, "")
        pwd = str(pwd)
        if not ok or pwd == "":
            return False

        sha = _hashlib.sha256()
        sha.update(pwd.encode())
        pwd_encrypted = sha.hexdigest()
        if pwd_encrypted != self._protected_password:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Invalid password.")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.setEscapeButton(QMessageBox.Ok)
            msg.exec_()
            return False
        return True

    def send_value(self):
        """
        Emit a :attr:`send_value_signal` to update channel value.

        If :attr:'pvBit' is n>=0 or positive the button toggles the state of
        the n-th digit of the channel. Otherwise it toggles the whole value.
        """
        if not self._connected:
            return None
        if not self.confirm_dialog():
            return None
        if not self.validate_password():
            return None

        checked = not self._bit_val
        val = checked
        if self._bit >= 0:
            val = int(self.value)
            val ^= (-checked ^ val) & (1 << self._bit)
            # For explanation look:
            # https://stackoverflow.com/questions/47981/how-do-you-set-clear-and-toggle-a-single-bit
        self.send_value_signal[self.channeltype].emit(self.channeltype(val))

    def sizeHint(self):
        """Return size hint to define size on initialization."""
        return QSize(72, 36)

    def paintEvent(self, event):
        """Treat appearence changes based on connection state and value."""
        self.style().unpolish(self)
        self.style().polish(self)

        if not self.isEnabled():
            state = 'Disconnected'
        elif self._bit_val == self._on:
            state = 'On'
        elif self._bit_val == self._off:
            state = 'Off'
        else:
            state = 'Disconnected'

        if self.shape == 0:
            shape_dict = PyDMStateButton.squaredbuttonstatesdict
        elif self.shape == 1:
            shape_dict = PyDMStateButton.roundedbuttonstatesdict

        option = QStyleOption()
        option.initFrom(self)
        h = option.rect.height()
        w = option.rect.width()
        aspect = 2.0
        ah = w/aspect
        aw = w
        if ah > h:
            ah = h
            aw = h*aspect
        x = abs(aw-w)/2.0
        y = abs(ah-h)/2.0
        bounds = QRectF(x, y, aw, ah)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        shape_str = shape_dict[state]
        buttonstate_bytearray = bytes(shape_str, 'utf-8')
        self.renderer.load(QByteArray(buttonstate_bytearray))
        self.renderer.render(painter, bounds)

    @Property(buttonShapeMap)
    def shape(self):
        """
        Property to define the shape of the button.

        Returns
        -------
        int
        """
        return self._shape

    @shape.setter
    def shape(self, new_shape):
        """
        Property to define the shape of the button.

        Parameters
        ----------
        value : int
        """
        if new_shape in [PyDMStateButton.Rounded, PyDMStateButton.Squared]:
            self._shape = new_shape
            self.update()
        else:
            raise ValueError('Button shape not defined!')

    @Property(int)
    def pvbit(self):
        """
        Property to define which PV bit to control.

        Returns
        -------
        int
        """
        return int(self._bit)

    @pvbit.setter
    def pvbit(self, bit):
        """
        Property to define which PV bit to control.

        Parameters
        ----------
        value : int
        """
        if bit >= 0:
            self._bit = int(bit)

    @Property(bool)
    def invert(self):
        """
        Property that indicates whether to invert button on/off representation.

        Return
        ------
        bool
        """
        return self._invert

    @invert.setter
    def invert(self, value):
        """
        Property that indicates whether to invert button on/off representation.

        Parameters
        ----------
        value: bool
        """
        self._invert = value
        if self._invert:
            self._on = 0
            self._off = 1
        else:
            self._on = 1
            self._off = 0
        # Trigger paintEvent somehow
