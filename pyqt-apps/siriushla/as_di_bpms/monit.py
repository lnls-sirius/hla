from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout
from siriushla.as_di_bpms.base import BaseWidget, GraphTime


class MonitData(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)

        graph = GraphTime(parent=self, prefix=self.prefix, bpm=self.bpm)
        vbl.addWidget(graph)
        labsty = {'font-size': '20pt'}
        graph.setLabel('left', text='Positions', units='m', **labsty)

        dt = (
            ('PosX-Mon', 'blue'),
            ('PosY-Mon', 'red'),
            ('PosQ-Mon', 'green'),
            ('Sum-Mon', 'black'))
        for name, cor in dt:
            opts = dict(
                y_channel=name,
                name=name[:-4],
                color=cor,
                lineStyle=1,
                lineWidth=1)  # NOTE: If > 1: very low performance
            graph.addYChannel(**opts, add_scale=1e-9)

        graph = GraphTime(parent=self, prefix=self.prefix, bpm=self.bpm)
        vbl.addWidget(graph)
        labsty = {'font-size': '20pt'}
        graph.setLabel('left', text='Antennas', units='au', **labsty)

        dt = (
            ('AmplA-Mon', 'blue'),
            ('AmplB-Mon', 'red'),
            ('AmplC-Mon', 'green'),
            ('AmplD-Mon', 'magenta'))
        for name, cor in dt:
            opts = dict(
                y_channel=self.get_pvname(name, False),
                name=name[:-4],
                color=cor,
                lineStyle=1,
                lineWidth=1)  # NOTE: If > 1: very low performance
            graph.addYChannel(**opts)


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriushla.util import set_style
    import sys

    app = SiriusApplication()
    set_style(app)
    wind = SiriusDialog()
    wind.resize(1000, 1500)
    hbl = QHBoxLayout(wind)
    bpm_name = 'SI-07SP:DI-BPM-1'
    wid = MonitData(prefix='ca://', bpm=bpm_name)
    hbl.addWidget(wid)
    wind.show()
    sys.exit(app.exec_())
