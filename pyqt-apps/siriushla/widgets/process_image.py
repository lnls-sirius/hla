"""Process Image Widget."""

import numpy as np

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QLabel, QGridLayout, QGroupBox, QFormLayout, \
    QWidget, QHBoxLayout, QPushButton

import qtawesome as qta
from pyqtgraph import PlotCurveItem, mkPen

from pydm.widgets import PyDMImageView, PyDMEnumComboBox, PyDMLabel, \
    PyDMPushButton

from siriuspy.namesys import SiriusPVName

from ..util import connect_window
from .windows import create_window_from_widget
from .signal_channel import SiriusConnectionSignal
from .spinbox import SiriusSpinbox
from .state_button import PyDMStateButton
from .label import SiriusLabel
from .led import SiriusLedState


class SiriusProcessImage(QWidget):
    def __init__(self, parent=None, device='', convertion_set=True,
                 orientation='V'):
        super().__init__(parent)
        self._dev = SiriusPVName(device)
        self._conv_set = convertion_set
        self._ori = orientation
        self._setupUi()

    def _setupUi(self):
        self.image_view = PyDMImageView(
            parent=self,
            image_channel=self._dev+':Image-RB',
            width_channel=self._dev+':Width-RB')
        self.image_view.setObjectName('image')
        self.image_view.setStyleSheet(
            '#image{min-width:30em; min-height:30em;}')
        self.image_view.maxRedrawRate = 5
        self.image_view.colorMap = self.image_view.Jet
        self.image_view.readingOrder = self.image_view.Clike
        self._roixproj = SiriusConnectionSignal(self._dev+':ROIProjX-Mon')
        self._roiyproj = SiriusConnectionSignal(self._dev+':ROIProjY-Mon')
        self._roixfit = SiriusConnectionSignal(self._dev+':ROIGaussFitX-Mon')
        self._roiyfit = SiriusConnectionSignal(self._dev+':ROIGaussFitY-Mon')
        self._roixaxis = SiriusConnectionSignal(self._dev+':ROIAxisX-Mon')
        self._roiyaxis = SiriusConnectionSignal(self._dev+':ROIAxisY-Mon')
        self._roistartx = SiriusConnectionSignal(self._dev+':ROIStartX-Mon')
        self._roistarty = SiriusConnectionSignal(self._dev+':ROIStartY-Mon')
        self._roiendx = SiriusConnectionSignal(self._dev+':ROIEndX-Mon')
        self._roiendy = SiriusConnectionSignal(self._dev+':ROIEndY-Mon')
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

        gb_pos = self._get_config_widget(self)
        gb_posi = self._get_position_widget(self)
        gb_size = self._get_size_widget(self)

        gl = QGridLayout(self)
        gl.setContentsMargins(0, 0, 0, 0)
        if self._ori == 'V':
            gl.addWidget(self.image_view, 0, 0, 1, 2)
            gl.addWidget(gb_pos, 1, 0, 2, 1)
            gl.addWidget(gb_posi, 1, 1)
            gl.addWidget(gb_size, 2, 1)
        else:
            gl.addWidget(self.image_view, 0, 0, 1, 2)
            gl.addWidget(gb_pos, 0, 2, 2, 1)
            gl.addWidget(gb_posi, 1, 0)
            gl.addWidget(gb_size, 1, 1)

    def _get_config_widget(self, parent):
        gb_pos = QGroupBox('Image Processing ', parent)

        meth_sp = PyDMEnumComboBox(
            gb_pos, init_channel=self._dev+':CalcMethod-Sel')
        meth_lb = SiriusLabel(gb_pos, init_channel=self._dev+':CalcMethod-Sts')
        meth_ld = QLabel('Method', gb_pos)

        nrpt_ld = QLabel('Num. Pts.', gb_pos)
        nrpt_sp = SiriusSpinbox(
            gb_pos, init_channel=self._dev+':NrAverages-SP')
        nrpt_sp.showStepExponent = False
        rdb = PyDMLabel(gb_pos, init_channel=self._dev+':NrAverages-RB')
        rdb.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        slsh = QLabel('/', gb_pos, alignment=Qt.AlignCenter)
        slsh.setStyleSheet('min-width:0.7em; max-width:0.7em;')
        cnt = PyDMLabel(gb_pos, init_channel=self._dev+':BufferSize-Mon')
        cnt.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cnt.setToolTip('Current Buffer Size')
        nrpt_wd = QWidget(gb_pos)
        hbl = QHBoxLayout(nrpt_wd)
        hbl.addWidget(cnt)
        hbl.addWidget(slsh)
        hbl.addWidget(rdb)
        nrpt_pb = PyDMPushButton(
            gb_pos, init_channel=self._dev+':ResetBuffer-Cmd', pressValue=1)
        nrpt_pb.setToolTip('Reset Buffer')
        nrpt_pb.setIcon(qta.icon('mdi.delete-empty'))
        nrpt_pb.setObjectName('rst')
        nrpt_pb.setStyleSheet(
            '#rst{min-width:25px; max-width:25px; icon-size:20px;}')

        rsx_sp = SiriusSpinbox(gb_pos, init_channel=self._dev+':ROISizeX-SP')
        rsx_sp.showStepExponent = False
        rsx_lb = SiriusLabel(gb_pos, init_channel=self._dev+':ROISizeX-RB')
        rsx_ld = QLabel('ROI Size X', gb_pos)

        rsy_sp = SiriusSpinbox(gb_pos, init_channel=self._dev+':ROISizeY-SP')
        rsy_sp.showStepExponent = False
        rsy_lb = SiriusLabel(gb_pos, init_channel=self._dev+':ROISizeY-RB')
        rsy_ld = QLabel('ROI Size Y', gb_pos)

        ra_bt = PyDMStateButton(
            gb_pos, init_channel=self._dev+':ROIAutoCenter-Sel')
        ra_lb = SiriusLabel(
            gb_pos, init_channel=self._dev+':ROIAutoCenter-Sts')
        ra_ld = QLabel('Auto Center:', gb_pos)

        rcx_sp = SiriusSpinbox(gb_pos, init_channel=self._dev+':ROICenterX-SP')
        rcx_sp.showStepExponent = False
        rcx_lb = SiriusLabel(gb_pos, init_channel=self._dev+':ROICenterX-RB')
        rcx_ld = QLabel('ROI Center X', gb_pos)

        rcy_sp = SiriusSpinbox(gb_pos, init_channel=self._dev+':ROICenterY-SP')
        rcy_sp.showStepExponent = False
        rcy_lb = SiriusLabel(gb_pos, init_channel=self._dev+':ROICenterY-RB')
        rcy_ld = QLabel('ROI Center Y', gb_pos)

        sts_bt = QPushButton(qta.icon('fa5s.ellipsis-h'), '', gb_pos)
        sts_bt.setToolTip('Open Detailed Configs')
        sts_bt.setObjectName('sts')
        sts_bt.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        Window = create_window_from_widget(
            _DetailedWidget, title='Image Processing Detailed Configs')
        connect_window(
            sts_bt, Window, gb_pos, device=self._dev,
            convertion_set=self._conv_set)
        hlay = QHBoxLayout()
        hlay.addWidget(sts_bt, alignment=Qt.AlignRight)

        lay = QGridLayout(gb_pos)
        lay.addWidget(meth_ld, 0, 0, 2, 1, alignment=Qt.AlignCenter)
        lay.addWidget(meth_sp, 0, 1)
        lay.addWidget(meth_lb, 1, 1)
        lay.addWidget(nrpt_ld, 2, 0)
        lay.addWidget(nrpt_pb, 3, 0)
        lay.addWidget(nrpt_sp, 2, 1)
        lay.addWidget(nrpt_wd, 3, 1)
        lay.addWidget(rsx_ld, 4+0, 0, 2, 1, alignment=Qt.AlignCenter)
        lay.addWidget(rsx_sp, 4+0, 1)
        lay.addWidget(rsx_lb, 4+1, 1)
        lay.addWidget(rsy_ld, 6+0, 0, 2, 1, alignment=Qt.AlignCenter)
        lay.addWidget(rsy_sp, 6+0, 1)
        lay.addWidget(rsy_lb, 6+1, 1)
        lay.addWidget(ra_ld, 8+0, 0, 2, 1, alignment=Qt.AlignCenter)
        lay.addWidget(ra_bt, 8+0, 1)
        lay.addWidget(ra_lb, 8+1, 1, alignment=Qt.AlignCenter)
        lay.addWidget(rcx_ld, 10+0, 0, 2, 1, alignment=Qt.AlignCenter)
        lay.addWidget(rcx_sp, 10+0, 1)
        lay.addWidget(rcx_lb, 10+1, 1)
        lay.addWidget(rcy_ld, 12+0, 0, 2, 1, alignment=Qt.AlignCenter)
        lay.addWidget(rcy_sp, 12+0, 1)
        lay.addWidget(rcy_lb, 12+1, 1)
        lay.addWidget(sts_bt, 14, 0, alignment=Qt.AlignLeft)

        return gb_pos

    def _get_position_widget(self, parent):
        gb_posi = QGroupBox('Position [px / mm]', parent)
        fl_posi = QFormLayout(gb_posi)

        wid = QWidget(gb_posi)
        wid.setLayout(QHBoxLayout())
        xave = SiriusLabel(wid, init_channel=self._dev+':BeamCenterX-Mon')
        xavemm = SiriusLabel(wid, init_channel=self._dev+':BeamCentermmX-Mon')
        xave.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        xavemm.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        wid.layout().addWidget(xave)
        wid.layout().addWidget(QLabel('/', wid))
        wid.layout().addWidget(xavemm)
        fl_posi.addRow(QLabel(
            'X =', gb_posi, alignment=Qt.AlignBottom), wid)

        wid = QWidget(gb_posi)
        wid.setLayout(QHBoxLayout())
        yave = SiriusLabel(wid, init_channel=self._dev+':BeamCenterY-Mon')
        yavemm = SiriusLabel(wid, init_channel=self._dev+':BeamCentermmY-Mon')
        yave.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        yavemm.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        wid.layout().addWidget(yave)
        wid.layout().addWidget(QLabel('/', wid))
        wid.layout().addWidget(yavemm)
        fl_posi.addRow(QLabel(
            'Y =', gb_posi, alignment=Qt.AlignBottom), wid)

        return gb_posi

    def _get_size_widget(self, parent):
        gb_size = QGroupBox('Size [px / mm]', parent)
        fl_size = QFormLayout(gb_size)

        wid = QWidget(gb_size)
        wid.setLayout(QHBoxLayout())
        xave = SiriusLabel(wid, init_channel=self._dev+':BeamSizeX-Mon')
        xavemm = SiriusLabel(wid, init_channel=self._dev+':BeamSizemmX-Mon')
        xave.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        xavemm.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        wid.layout().addWidget(xave)
        wid.layout().addWidget(QLabel('/', wid))
        wid.layout().addWidget(xavemm)
        fl_size.addRow(QLabel(
            'X =', gb_size, alignment=Qt.AlignBottom), wid)

        wid = QWidget(gb_size)
        wid.setLayout(QHBoxLayout())
        yave = SiriusLabel(wid, init_channel=self._dev+':BeamSizeY-Mon')
        yavemm = SiriusLabel(wid, init_channel=self._dev+':BeamSizemmY-Mon')
        yave.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        yavemm.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        wid.layout().addWidget(yave)
        wid.layout().addWidget(QLabel('/', wid))
        wid.layout().addWidget(yavemm)
        fl_size.addRow(QLabel(
            'Y =', gb_size, alignment=Qt.AlignBottom), wid)

        return gb_size

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


class _DetailedWidget(QWidget):
    """Process Image Detail Control."""

    def __init__(self, parent=None, device='', convertion_set=True):
        super().__init__(parent=parent)
        self._dev = SiriusPVName(device)
        sec = 'ID' if 'BL' in self._dev else self._dev.sec
        self._conv_set = convertion_set
        self.setObjectName(sec+'App')
        self._setupui()

    def _setupui(self):
        self.setLayout(QFormLayout())
        self.layout().setSpacing(0)

        self.layout().addRow(QLabel(
            '<h4>Image Processing Detailed Controls</h4>', self,
            alignment=Qt.AlignTop | Qt.AlignHCenter))

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        sttbtn = PyDMEnumComboBox(
            wid, init_channel=self._dev+':ReadingOrder-Sel')
        lbl = SiriusLabel(wid, init_channel=self._dev+':ReadingOrder-Sts')
        wid.layout().addWidget(sttbtn)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Reading Order', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        sttbtn = PyDMStateButton(wid, init_channel=self._dev+':ImgFlipX-Sel')
        lbl = SiriusLedState(wid, init_channel=self._dev+':ImgFlipX-Sts')
        wid.layout().addWidget(sttbtn)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Flip Horintal', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        sttbtn = PyDMStateButton(wid, init_channel=self._dev+':ImgFlipY-Sel')
        lbl = SiriusLedState(wid, init_channel=self._dev+':ImgFlipY-Sts')
        wid.layout().addWidget(sttbtn)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Flip Vertical', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=self._dev+':ImgCropLow-SP')
        lbl = SiriusLabel(wid, init_channel=self._dev+':ImgCropLow-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Min. Pixel Val.', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        sttbtn = PyDMStateButton(wid, init_channel=self._dev+':ImgCropUse-Sel')
        lbl = SiriusLedState(wid, init_channel=self._dev+':ImgCropUse-Sts')
        wid.layout().addWidget(sttbtn)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Crop Image Levels', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=self._dev+':ImgCropHigh-SP')
        lbl = SiriusLabel(wid, init_channel=self._dev+':ImgCropHigh-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Max. Pixel Val.', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        if self._conv_set:
            spb = SiriusSpinbox(wid, init_channel=self._dev+':Px2mmScaleX-SP')
            lbl = SiriusLabel(wid, init_channel=self._dev+':Px2mmScaleX-RB')
            spb.showStepExponent = False
            wid.layout().addWidget(spb)
            wid.layout().addWidget(lbl)
        else:
            lbl = SiriusLabel(wid, init_channel=self._dev+':Px2mmScaleX-Cte')
            wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Pxl 2 mm Scale X', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        if self._conv_set:
            spb = SiriusSpinbox(wid, init_channel=self._dev+':Px2mmScaleY-SP')
            lbl = SiriusLabel(wid, init_channel=self._dev+':Px2mmScaleY-RB')
            spb.showStepExponent = False
            wid.layout().addWidget(spb)
            wid.layout().addWidget(lbl)
        else:
            lbl = SiriusLabel(wid, init_channel=self._dev+':Px2mmScaleY-Cte')
            wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Pxl 2 mm Scale Y', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        sttbtn = PyDMStateButton(
            wid, init_channel=self._dev+':Px2mmAutoCenter-Sel')
        lbl = SiriusLedState(
            wid, init_channel=self._dev+':Px2mmAutoCenter-Sts')
        wid.layout().addWidget(sttbtn)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Auto Center', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=self._dev+':Px2mmCenterX-SP')
        lbl = SiriusLabel(wid, init_channel=self._dev+':Px2mmCenterX-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Pxl 2 mm Center X', self, alignment=Qt.AlignBottom), wid)

        wid = QWidget(self)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel=self._dev+':Px2mmCenterY-SP')
        lbl = SiriusLabel(wid, init_channel=self._dev+':Px2mmCenterY-RB')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        self.layout().addRow(QLabel(
            'Pxl 2 mm Center Y', self, alignment=Qt.AlignBottom), wid)
