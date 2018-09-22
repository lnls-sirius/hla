from qtpy.QtCore import Slot
from qtpy.QtWidgets import QDialog, QLabel, QVBoxLayout, QProgressBar


class LoadingDialog(QDialog):
    def __init__(self, title,  maximum, parent=None):
        super(LoadingDialog, self).__init__(parent)
        #self.setAttribute(Qt.WA_DeleteOnClose)

        self._may_close = False

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Loading...", self))
        self.progress = QProgressBar(self)
        self.progress.setMinimum(0)
        self.progress.setMaximum(maximum)
        layout.addWidget(self.progress)

        self.setWindowTitle(title)
        self.setLayout(layout)

    @Slot(int)
    def update(self, value):
        self.progress.setValue(value)

    @Slot(int)
    def done(self, r):
        self._may_close = True
        super(LoadingDialog, self).done(r)

    def closeEvent(self, event):
        if self._may_close:
            super(LoadingDialog, self).closeEvent(event)
        else:
            event.ignore()
