import re
from qtpy.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLineEdit, \
    QLabel, QHBoxLayout
from qtpy.QtCore import Qt, Slot, QRect
from siriushla import util
from siriushla.as_di_bpms.base import BaseWidget
from siriushla.as_di_bpms.main import BPMSummary


class SelectBPMs(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm_list=[]):
        super().__init__(parent=parent, prefix=prefix, bpm='')
        self.bpm_dict = {bpm: '' for bpm in bpm_list}
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        lab = QLabel('BPMs List')
        lab.setStyleSheet("font: 30pt \"Sans Serif\";\nfont-weight: bold;")
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab)
        vbl.addSpacing(20)

        search = QLineEdit(parent=self)
        search.setPlaceholderText("Search for BPMs...")
        search.textEdited.connect(self._filter_bpms)
        vbl.addWidget(search)

        scarea = QScrollArea(self)
        scarea.setSizeAdjustPolicy(scarea.AdjustToContents)
        scarea.setWidgetResizable(True)

        wid = QWidget()
        wid.setGeometry(QRect(0, 0, 521, 372))
        vbl2 = QVBoxLayout(wid)
        vbl2.setSpacing(15)
        for bpm in sorted(self.bpm_dict.keys()):
            widb = BPMSummary(wid, prefix=self.prefix, bpm=bpm)
            widb.setMinimumHeight(60)
            vbl2.addWidget(widb)
            self.bpm_dict[bpm] = widb

        vbl.addWidget(scarea)
        scarea.setMinimumWidth(400)
        scarea.setWidget(wid)
        self.scarea = scarea

    @Slot(str)
    def _filter_bpms(self, text):
        """Filter power supply widgets based on text inserted at line edit."""
        try:
            pattern = re.compile(text, re.I)
        except Exception as e:  # Ignore malformed patterns?
            pattern = re.compile("malformed")

        for bpm, wid in self.bpm_dict.items():
            wid.setVisible(bool(pattern.search(bpm)))
        # Sroll to top
        self.scarea.verticalScrollBar().setValue(0)


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    import sys

    app = SiriusApplication()
    util.set_style(app)
    wind = SiriusDialog()
    # wind.resize(1400, 1400)
    hbl = QHBoxLayout(wind)
    bpm_names = [
        'SI-07SP:DI-BPM-1', 'SI-07SP:DI-BPM-2',
        'SI-01M1:DI-BPM', 'SI-01M2:DI-BPM',
        'SI-02M1:DI-BPM', 'SI-02M2:DI-BPM',
        'SI-03M1:DI-BPM', 'SI-03M2:DI-BPM',
        'SI-04M1:DI-BPM', 'SI-04M2:DI-BPM',
        'SI-05M1:DI-BPM', 'SI-05M2:DI-BPM',
        'SI-06M1:DI-BPM', 'SI-06M2:DI-BPM',
        ]
    widm = SelectBPMs(prefix='ca://', bpm_list=bpm_names)
    hbl.addWidget(widm)
    wind.show()
    sys.exit(app.exec_())
