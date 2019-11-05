#!/usr/bin/env python-sirius

import numpy as np
from epics import PV
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QLabel, QGridLayout, QGroupBox, QFormLayout, \
    QMessageBox, QWidget, QSpinBox, QVBoxLayout, QHBoxLayout, QPushButton,\
    QFileDialog
import qtawesome as qta
from pyqtgraph import PlotCurveItem, mkPen

from pydm.widgets import PyDMTimePlot, PyDMImageView, PyDMEnumComboBox

import siriushla.util as _util
from siriushla.widgets.windows import create_window_from_widget
from siriushla.widgets import SiriusConnectionSignal, SiriusSpinbox, \
    PyDMStateButton, SiriusLabel, SiriusLedState


class ProcessImage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setupUi()

    def _setupUi(self):
        gl = QGridLayout(self)
        gl.setContentsMargins(0, 0, 0, 0)
        pref = 'LI-Glob:AP-MeasEnergy:'
        self.image_view = PyDMImageView(
            parent=self,
            image_channel=pref+'Image-RB',
            width_channel=pref+'Width-RB')
        self.image_view.setObjectName('image')
        self.image_view.setStyleSheet(
            '#image{min-width:30em; min-height:30em;}')
        self.image_view.maxRedrawRate = 5
        self.image_view.colorMap = self.image_view.Jet
        self.image_view.readingOrder = self.image_view.Clike
        self._roixproj = SiriusConnectionSignal(pref+'ROIProjX-Mon')
        self._roiyproj = SiriusConnectionSignal(pref+'ROIProjY-Mon')
        self._roixfit = SiriusConnectionSignal(pref+'ROIGaussFitX-Mon')
        self._roiyfit = SiriusConnectionSignal(pref+'ROIGaussFitY-Mon')
        self._roixaxis = SiriusConnectionSignal(pref+'ROIAxisX-Mon')
        self._roiyaxis = SiriusConnectionSignal(pref+'ROIAxisY-Mon')
        self._roistartx = SiriusConnectionSignal(pref+'ROIStartX-Mon')
        self._roistarty = SiriusConnectionSignal(pref+'ROIStartY-Mon')
        self._roiendx = SiriusConnectionSignal(pref+'ROIEndX-Mon')
        self._roiendy = SiriusConnectionSignal(pref+'ROIEndY-Mon')
        self._roixproj.new_value_signal[np.ndarray].connect(self._update_roi)
        self.plt_roi = PlotCurveItem([0, 0, 500, 500, 0], [0, 500, 500, 0, 0])
        pen = mkPen()
        pen.setColor(QColor('red'))
        pen.setWidth(1)
        self.plt_roi.setPen(pen)
        self.image_view.addItem(self.plt_roi)
        self.plt_fit_x = PlotCurveItem([0, 0], [0, 400])
        self.plt_fit_y = PlotCurveItem([0, 0], [0, 400])
        self.plt_his_x = PlotCurveItem([0, 0], [0, 400])
        self.plt_his_y = PlotCurveItem([0, 0], [0, 400])
        pen = mkPen()
        pen.setColor(QColor('yellow'))
        self.plt_his_x.setPen(pen)
        self.plt_his_y.setPen(pen)
        self.image_view.addItem(self.plt_fit_x)
        self.image_view.addItem(self.plt_fit_y)
        self.image_view.addItem(self.plt_his_x)
        self.image_view.addItem(self.plt_his_y)
        gl.addWidget(self.image_view, 0, 0, 1, 2)

        gb_pos = QGroupBox('Image Processing ', self)
        gl.addWidget(gb_pos, 1, 0, 2, 1)
        fl = QFormLayout(gb_pos)
        wid = QWidget(gb_pos)
        wid.setLayout(QHBoxLayout())
        cbox = PyDMEnumComboBox(wid, init_channel=pref+'CalcMethod-Sel')
        lbl = SiriusLabel(wid, init_channel=pref+'CalcMethod-Sts')
        wid.layout().addWidget(cbox)
        wid.layout().addWidget(lbl)
        fl.addRow(QLabel('Method', gb_pos, alignment=Qt.AlignBottom), wid)

        wid = QWidget(gb_pos)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=pref+'ROISizeX-SP')
        lbl = SiriusLabel(wid, init_channel=pref+'ROISizeX-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        fl.addRow(QLabel('ROI Size X', gb_pos, alignment=Qt.AlignBottom), wid)

        wid = QWidget(gb_pos)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=pref+'ROISizeY-SP')
        lbl = SiriusLabel(wid, init_channel=pref+'ROISizeY-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        fl.addRow(QLabel('ROI Size Y', gb_pos, alignment=Qt.AlignBottom), wid)

        wid = QWidget(gb_pos)
        wid.setLayout(QHBoxLayout())
        sttbtn = PyDMStateButton(wid, init_channel=pref+'ROIAutoCenter-Sel')
        lbl = SiriusLabel(wid, init_channel=pref+'ROIAutoCenter-Sts')
        wid.layout().addWidget(sttbtn)
        wid.layout().addWidget(lbl)
        fl.addRow(QLabel(
            'Auto Center:', gb_pos, alignment=Qt.AlignBottom), wid)

        wid = QWidget(gb_pos)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=pref+'ROICenterX-SP')
        lbl = SiriusLabel(wid, init_channel=pref+'ROICenterX-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        fl.addRow(QLabel(
            'ROI Center X', gb_pos, alignment=Qt.AlignBottom), wid)

        wid = QWidget(gb_pos)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=pref+'ROICenterY-SP')
        lbl = SiriusLabel(wid, init_channel=pref+'ROICenterY-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        fl.addRow(QLabel(
            'ROI Center Y', gb_pos, alignment=Qt.AlignBottom), wid)

        sts = QPushButton('', gb_pos)
        sts.setIcon(qta.icon('fa5s.list-ul'))
        sts.setToolTip('Open Detailed Configs')
        sts.setObjectName('sts')
        sts.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        icon = qta.icon(
            'mdi.gauge', color=_util.get_appropriate_color('LI'))
        Window = create_window_from_widget(
            DetailedWidget, title='Detailed Configs', icon=icon)
        _util.connect_window(sts, Window, gb_pos)
        fl.addRow('', sts)

        gb_posi = QGroupBox('Position [px / mm]', self)
        gb_size = QGroupBox('Size [px / mm]', self)
        gl.addWidget(gb_posi, 1, 1)
        gl.addWidget(gb_size, 2, 1)
        fl_posi = QFormLayout(gb_posi)
        fl_size = QFormLayout(gb_size)

        wid = QWidget(gb_posi)
        wid.setLayout(QHBoxLayout())
        xave = SiriusLabel(wid, init_channel=pref+'BeamCenterX-Mon')
        xavemm = SiriusLabel(wid, init_channel=pref+'BeamCentermmX-Mon')
        xave.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        xavemm.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        wid.layout().addWidget(xave)
        wid.layout().addWidget(QLabel('/', wid))
        wid.layout().addWidget(xavemm)
        fl_posi.addRow(QLabel(
            'X =', gb_posi, alignment=Qt.AlignBottom), wid)

        wid = QWidget(gb_posi)
        wid.setLayout(QHBoxLayout())
        yave = SiriusLabel(wid, init_channel=pref+'BeamCenterY-Mon')
        yavemm = SiriusLabel(wid, init_channel=pref+'BeamCentermmY-Mon')
        yave.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        yavemm.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        wid.layout().addWidget(yave)
        wid.layout().addWidget(QLabel('/', wid))
        wid.layout().addWidget(yavemm)
        fl_posi.addRow(QLabel(
            'Y =', gb_posi, alignment=Qt.AlignBottom), wid)

        wid = QWidget(gb_size)
        wid.setLayout(QHBoxLayout())
        xave = SiriusLabel(wid, init_channel=pref+'BeamSizeX-Mon')
        xavemm = SiriusLabel(wid, init_channel=pref+'BeamSizemmX-Mon')
        xave.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        xavemm.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        wid.layout().addWidget(xave)
        wid.layout().addWidget(QLabel('/', wid))
        wid.layout().addWidget(xavemm)
        fl_size.addRow(QLabel(
            'X =', gb_size, alignment=Qt.AlignBottom), wid)

        wid = QWidget(gb_size)
        wid.setLayout(QHBoxLayout())
        yave = SiriusLabel(wid, init_channel=pref+'BeamSizeY-Mon')
        yavemm = SiriusLabel(wid, init_channel=pref+'BeamSizemmY-Mon')
        yave.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        yavemm.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        wid.layout().addWidget(yave)
        wid.layout().addWidget(QLabel('/', wid))
        wid.layout().addWidget(yavemm)
        fl_size.addRow(QLabel(
            'Y =', gb_size, alignment=Qt.AlignBottom), wid)

    def _update_roi(self):
        xaxis = self._roixaxis.getvalue()
        yaxis = self._roiyaxis.getvalue()
        xproj = self._roixproj.getvalue()
        yproj = self._roiyproj.getvalue()
        xfit = self._roixfit.getvalue()
        yfit = self._roiyfit.getvalue()
        notnone = xaxis is not None
        notnone &= yaxis is not None
        notnone &= xproj is not None
        notnone &= yproj is not None
        notnone &= xfit is not None
        notnone &= yfit is not None
        if notnone:
            samesize = xaxis.size == xproj.size
            samesize &= xaxis.size == xfit.size
            samesize &= yaxis.size == yproj.size
            samesize &= yaxis.size == yfit.size
            if samesize:
                xproj = xproj/np.max(xproj) * 400 + yaxis[0]
                yproj = yproj/np.max(yproj) * 400 + xaxis[0]
                xfit = xfit/np.max(xfit) * 400 + yaxis[0]
                yfit = yfit/np.max(yfit) * 400 + xaxis[0]
                self.plt_his_x.setData(xaxis, xproj)
                self.plt_his_y.setData(yproj, yaxis)
                self.plt_fit_x.setData(xaxis, xfit)
                self.plt_fit_y.setData(yfit, yaxis)

        srtx = self._roistartx.getvalue()
        srty = self._roistarty.getvalue()
        endx = self._roiendx.getvalue()
        endy = self._roiendy.getvalue()
        if set([None, ]) - set([srtx, srty, endx, endy]):
            self.plt_roi.setData(
                [srtx, srtx, endx, endx, srtx],
                [srty, endy, endy, srty, srty])


class DetailedWidget(QWidget):
    """."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._setupui()
        self.setObjectName('LIApp')

    def _setupui(self):
        self.setLayout(QFormLayout())
        self.layout().setSpacing(0)
        pref = 'LI-Glob:AP-MeasEnergy:'

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        sttbtn = PyDMStateButton(wid, init_channel=pref+'ImgCropUse-Sel')
        lbl = SiriusLedState(wid, init_channel=pref+'ImgCropUse-Sts')
        wid.layout().addWidget(sttbtn)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Crop Image Levels', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=pref+'ImgCropLow-SP')
        lbl = SiriusLabel(wid, init_channel=pref+'ImgCropLow-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Min. Pixel Val.', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=pref+'ImgCropHigh-SP')
        lbl = SiriusLabel(wid, init_channel=pref+'ImgCropHigh-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Max. Pixel Val.', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=pref+'Px2mmScaleX-SP')
        lbl = SiriusLabel(wid, init_channel=pref+'Px2mmScaleX-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Pxl 2 mm Scale X', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=pref+'Px2mmScaleY-SP')
        lbl = SiriusLabel(wid, init_channel=pref+'Px2mmScaleY-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Pxl 2 mm Scale Y', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        sttbtn = PyDMStateButton(wid, init_channel=pref+'Px2mmAutoCenter-Sel')
        lbl = SiriusLedState(wid, init_channel=pref+'Px2mmAutoCenter-Sts')
        wid.layout().addWidget(sttbtn)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Auto Center', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=pref+'Px2mmCenterX-SP')
        lbl = SiriusLabel(wid, init_channel=pref+'Px2mmCenterX-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Pxl 2 mm Center X', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=pref+'Px2mmCenterY-SP')
        lbl = SiriusLabel(wid, init_channel=pref+'Px2mmCenterY-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Pxl 2 mm Center Y', self, alignment=Qt.AlignBottom), wid)


class EnergyMeasure(QWidget):
    """."""

    def __init__(self, parent=None):
        """."""
        super().__init__(parent=parent)
        self._setupUi()
        self.setObjectName('LIApp')

    def _setupUi(self):
        pref = 'LI-Glob:AP-MeasEnergy:'
        gl = QGridLayout(self)
        self.plt_energy = PyDMTimePlot(
            self, init_y_channels=[pref+'Energy-Mon'],
            background=QColor('white'))
        gl.addWidget(self.plt_energy, 1, 0, 1, 2)
        self.plt_spread = PyDMTimePlot(
            self, init_y_channels=[pref+'Spread-Mon'],
            background=QColor('white'))
        gl.addWidget(self.plt_spread, 2, 0, 1, 2)

        self.plt_energy.setLabel('left', text='Energy [MeV]')
        self.plt_energy.setShowXGrid(True)
        self.plt_energy.setShowYGrid(True)
        c = self.plt_energy.curveAtIndex(0)
        c.color = QColor('blue')
        c.symbol = c.symbols['Circle']
        c.symbolSize = 10
        c.lineWidth = 3
        c.data_changed.connect(self._update_energy_stats)
        self.plt_energy.setTimeSpan(100)

        self.plt_spread.setLabel('left', text='Spread [%]')
        self.plt_spread.setShowXGrid(True)
        self.plt_spread.setShowYGrid(True)
        c = self.plt_spread.curveAtIndex(0)
        c.color = QColor('red')
        c.symbol = c.symbols['Circle']
        c.symbolSize = 10
        c.lineWidth = 3
        c.data_changed.connect(self._update_spread_stats)
        self.plt_spread.setTimeSpan(100)

        gb_ctrl = QGroupBox('Control', self)
        gb_ener = QGroupBox('Properties', self)
        gl.addWidget(gb_ctrl, 3, 0)
        gl.addWidget(gb_ener, 3, 1)
        hl_ctrl = QHBoxLayout(gb_ctrl)
        fl_ener = QFormLayout(gb_ener)

        vl = QVBoxLayout()
        wid = QWidget(gb_ctrl)
        wid.setLayout(QHBoxLayout())
        btn = PyDMStateButton(gb_ctrl, init_channel=pref+'MeasureCtrl-Sel')
        led = SiriusLedState(gb_ctrl, init_channel=pref+'MeasureCtrl-Sts')
        wid.layout().addWidget(btn)
        wid.layout().addWidget(led)
        vl.addWidget(QLabel('Start/Stop Acq.', gb_ctrl))
        vl.addWidget(wid)
        hl_ctrl.addItem(vl)

        vl = QVBoxLayout()
        wid = QWidget(gb_ctrl)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel='LI-01:PS-Spect:seti')
        lbl = SiriusLabel(wid, init_channel='LI-01:PS-Spect:rdi')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        vl.addWidget(QLabel('Spectrometer Current [A]', gb_ctrl))
        vl.addWidget(wid)
        hl_ctrl.addItem(vl)

        wid = QWidget(gb_ener)
        wid.setLayout(QHBoxLayout())
        self.lb_ave_en = QLabel('0.000', wid)
        self.lb_std_en = QLabel('0.000', wid)
        wid.layout().addWidget(self.lb_ave_en)
        wid.layout().addWidget(QLabel(
            '<html><head/><body><p>&#177;</p></body></html>', wid))
        wid.layout().addWidget(self.lb_std_en)
        fl_ener.addRow('Energy [MeV]', wid)

        wid = QWidget(gb_ener)
        wid.setLayout(QHBoxLayout())
        self.lb_ave_sp = QLabel('0.000', wid)
        self.lb_std_sp = QLabel('0.000', wid)
        wid.layout().addWidget(self.lb_ave_sp)
        wid.layout().addWidget(QLabel(
            '<html><head/><body><p>&#177;</p></body></html>', wid))
        wid.layout().addWidget(self.lb_std_sp)
        fl_ener.addRow('Spread [%]', wid)

        vl = QVBoxLayout()
        gl.addItem(vl, 0, 0, 1, 2)
        hl = QHBoxLayout()
        hl.setSpacing(0)
        self.spbox_npoints = QSpinBox(self)
        self.spbox_npoints.setKeyboardTracking(False)
        self.spbox_npoints.setMinimum(10)
        self.spbox_npoints.setMaximum(200000)
        self.spbox_npoints.setValue(100)
        self.spbox_npoints.editingFinished.connect(self.nrpoints_edited)
        hl.addWidget(QLabel('Choose TimeSpan [s]:', self))
        hl.addWidget(self.spbox_npoints)
        self.pb_reset_data = QPushButton('Reset Data', self)
        self.pb_reset_data.clicked.connect(self.pb_reset_data_clicked)
        hl.addWidget(self.pb_reset_data)
        vl.addItem(hl)

        self.plt_image = ProcessImage(self)
        gl.addWidget(self.plt_image, 0, 2, 4, 1)

    def _update_energy_stats(self):
        c = self.plt_energy.curveAtIndex(0)
        if c.points_accumulated:
            ener = np.array(c.data_buffer[1, -c.points_accumulated:])
            self.lb_ave_en.setText('{:.3f}'.format(np.mean(ener)))
            self.lb_std_en.setText('{:.3f}'.format(np.std(ener)))

    def _update_spread_stats(self):
        c = self.plt_spread.curveAtIndex(0)
        if c.points_accumulated:
            sprd = np.array(c.data_buffer[1, -c.points_accumulated:])
            self.lb_ave_sp.setText('{:.3f}'.format(np.mean(sprd)))
            self.lb_std_sp.setText('{:.3f}'.format(np.std(sprd)))

    def nrpoints_edited(self):
        val = self.spbox_npoints.value()
        self.plt_energy.setTimeSpan(val)
        self.plt_spread.setTimeSpan(val)

    def pb_reset_data_clicked(self):
        """."""
        c = self.plt_energy.curveAtIndex(0)
        c.points_accumulated = 0
        c = self.plt_spread.curveAtIndex(0)
        c.points_accumulated = 0
