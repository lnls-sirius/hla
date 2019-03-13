import re
from qtpy.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLineEdit, \
    QLabel, QHBoxLayout
from qtpy.QtCore import Qt, Slot
from siriushla.as_di_bpms.base import BaseWidget
from siriushla.as_di_bpms.main import BPMSummary


class SelectBPMs(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm_list=[]):
        super().__init__(parent=parent, prefix=prefix, bpm='')
        self.bpm_dict = {bpm: '' for bpm in bpm_list}
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        lab = QLabel('<h2>BPMs List</h2>', alignment=Qt.AlignCenter)
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
        vbl2 = QVBoxLayout(wid)
        vbl2.setSpacing(15)
        for bpm in sorted(self.bpm_dict.keys()):
            widb = BPMSummary(wid, prefix=self.prefix, bpm=bpm)
            vbl2.addWidget(widb)
            self.bpm_dict[bpm] = widb

        vbl.addWidget(scarea)
        scarea.setWidget(wid)
        self.scarea = scarea

        self.setObjectName('SelectBPMs')
        self.setStyleSheet("""#SelectBPMs{min-width:16em; min-height:12em;}""")

    @Slot(str)
    def _filter_bpms(self, text):
        """Filter power supply widgets based on text inserted at line edit."""
        try:
            pattern = re.compile(text, re.I)
        except Exception:  # Ignore malformed patterns?
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
    wind = SiriusDialog()
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
    widm = SelectBPMs(bpm_list=bpm_names)
    hbl.addWidget(widm)
    wind.show()
    sys.exit(app.exec_())
