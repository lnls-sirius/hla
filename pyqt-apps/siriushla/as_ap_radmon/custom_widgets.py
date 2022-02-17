"""Custom widgets."""

import numpy as _np

from qtpy.QtCore import Qt
from qtpy.QtGui import QPalette
from qtpy.QtWidgets import QToolTip

from siriuspy.clientarch import Time as _Time

from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusTimePlot


class MyTimePlot(SiriusTimePlot):
    """Reimplement mousePressEvent."""

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            pos = ev.pos()

            # find nearest curve point
            nearest = (self._curves[0], _np.inf, 0)
            for idx, curve in enumerate(self._curves):
                if not curve.isVisible():
                    continue
                mappos = curve.mapFromScene(pos)
                posx, posy = mappos.x(), mappos.y()
                xData, yData = curve.curve.xData, curve.curve.yData
                idx = _np.where(_np.isclose(xData-posx, 0, atol=0.5))[0]
                if idx.size:
                    valx, valy = xData[idx[0]], yData[idx[0]]
                    diff = abs(valy - posy)
                    if diff < nearest[1]:
                        nearest = (curve, diff, valy)

            # show tooltip
            curve, diff, valy = nearest
            if diff < 0.01:
                txt = _Time(timestamp=valx).get_iso8601()+'\n'
                txt += f'{curve.name()}: {valy:.3f}'
                font = SiriusApplication.instance().font()
                font.setPointSize(font.pointSize() - 10)
                QToolTip.setFont(font)
                palette = QPalette()
                palette.setColor(QPalette.ToolTipText, curve.color)
                palette.setColor(QPalette.ToolTipBase, Qt.darkGray)
                QToolTip.setPalette(palette)
                QToolTip.showText(
                    self.mapToGlobal(pos), txt, self, self.geometry(), 5000)
        else:
            super().mousePressEvent(ev)
