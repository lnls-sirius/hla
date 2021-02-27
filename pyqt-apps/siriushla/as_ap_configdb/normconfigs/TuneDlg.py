from qtpy.QtWidgets import QDialog, QDialogButtonBox, \
    QGridLayout, QLabel
from siriushla.widgets import QDoubleSpinBoxPlus


class TuneDlg(QDialog):
    def __init__(self, parent=None):
        super(TuneDlg, self).__init__(parent)

        self._setupUi()

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def _setupUi(self):
        self.layout = QGridLayout()

        self.tune_x_label = QLabel("\u0394\u03bd<sub>x</sub>", self)
        self.tune_y_label = QLabel("\u0394\u03bd<sub>y</sub>", self)
        self.tune_x = QDoubleSpinBoxPlus(self)
        self.tune_x.setSingleStep(0.1)
        self.tune_y = QDoubleSpinBoxPlus(self)
        self.tune_y.setSingleStep(0.1)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok|QDialogButtonBox.Cancel)

        self.layout.addWidget(self.tune_x_label, 0, 0)
        self.layout.addWidget(self.tune_x, 0, 1)
        self.layout.addWidget(self.tune_y_label, 1, 0)
        self.layout.addWidget(self.tune_y, 1, 1)
        self.layout.addWidget(self.button_box, 2, 0, 1, 2)

        self.setWindowTitle("Tune Dialog")
        self.setLayout(self.layout)
