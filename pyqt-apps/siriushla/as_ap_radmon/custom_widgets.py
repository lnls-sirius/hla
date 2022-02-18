"""Custom widgets."""

import numpy as _np

from qtpy.QtCore import Qt
from qtpy.QtGui import QPalette
from qtpy.QtWidgets import QToolTip

from pyqtgraph import mkBrush

from siriuspy.clientarch import Time as _Time

from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusTimePlot


class MyTimePlot(SiriusTimePlot):
    """Reimplement mouseMoveEvent."""

    def mouseMoveEvent(self, ev):
        pos = ev.pos()

        # find nearest curve point
        nearest = (self._curves[0], _np.inf, None, None)
        for idx, curve in enumerate(self._curves):
            if not curve.isVisible():
                continue
            mappos = curve.mapFromScene(pos)
            posx, posy = mappos.x(), mappos.y()
            xData, yData = curve.curve.xData, curve.curve.yData
            if not xData.size:
                continue
            idx = _np.argmin(_np.abs(xData-posx))
            if idx.size:
                valx, valy = xData[idx], yData[idx]
                diff = abs(valy - posy)
                if diff < nearest[1]:
                    nearest = (curve, diff, valx, valy)

        # show tooltip
        curve, diff, valx, valy = nearest
        ylimts = self.getViewBox().state['viewRange'][1]
        ydelta = ylimts[1] - ylimts[0]
        if diff < 2e-2*ydelta:
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
                self.mapToGlobal(pos), txt, self, self.geometry(), 1000)
            curve.scatter.setData(
                pos=[(valx, valy), ], symbol='o', size=15,
                brush=mkBrush(curve.color))
            curve.scatter.show()

        super().mouseMoveEvent(ev)
