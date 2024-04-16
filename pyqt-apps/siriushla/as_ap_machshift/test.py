import sys

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel

from siriushla.widgets import SiriusMainWindow, SiriusFrame
from siriushla.sirius_application import SiriusApplication


class Test(SiriusMainWindow):
    """Frame test Window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Frame test')
        self._setupUi()

    def _setupUi(self):
        self.title = QLabel('<h2>Machine Shift Values</h2>',
                            alignment=Qt.AlignCenter)

        color_dict = {
            'Users': SiriusFrame.Yellow,
            'Commissioning': SiriusFrame.MediumBlue,
            'Conditioning': SiriusFrame.DarkCyan,
            'Injection': SiriusFrame.LightSalmon,
            'MachineStudy': SiriusFrame.LightBlue,
            'Maintenance': SiriusFrame.MediumGreen,
            'Standby': SiriusFrame.LightGray,
            'Shutdown': SiriusFrame.DarkGray,
            'MachineStartup': SiriusFrame.MediumBlue,
        }

        cw = QWidget()
        lay = QVBoxLayout(cw)
        lay.addWidget(self.title)
        for i, shift in enumerate(color_dict):
            frame = SiriusFrame(
                self, 'FAKE:'+str(i), color_list=list(color_dict.values()),
                is_float=False)
            frame.setEnabled(True)
            frame.value_changed(i)
            label = QLabel(
                '<h4>'+shift+'</h4>', self, alignment=Qt.AlignCenter)
            frame.add_widget(label)
            lay.addWidget(frame)
        self.setCentralWidget(cw)


if __name__ == '__main__':
    app = SiriusApplication()
    app.open_window(Test, parent=None)
    sys.exit(app.exec_())
