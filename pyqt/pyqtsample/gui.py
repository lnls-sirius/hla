
import sys
from PyQt5 import QtWidgets, QtCore
import epics


class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)

        self.current = epics.PV('SIDI-CURRENT')
        self.lifetime = epics.PV('SIPA-LIFETIME')

        self.label = QtWidgets.QLabel("Nothing yet")
        self.timerlabel = QtWidgets.QLabel("Nothing yet")
        self.button = QtWidgets.QPushButton("Click here!")

        layout = QtWidgets.QVBoxLayout()

        hlayout1 = QtWidgets.QHBoxLayout()
        hlayout1.addWidget(QtWidgets.QLabel("SI Beam Current"))
        hlayout1.addWidget(self.label)

        hlayout2 = QtWidgets.QHBoxLayout()
        hlayout2.addWidget(QtWidgets.QLabel("SI Beam Lifetime"))
        hlayout2.addWidget(self.timerlabel)

        layout.addLayout(hlayout1)
        layout.addLayout(hlayout2)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.button.clicked.connect(self.button_clicked)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_timerlabel)
        self.timer.setInterval(1000.0)
        self.timer.start()

    def button_clicked(self):
        self.label.setText(str(self.current.get()))

    def update_timerlabel(self):
        self.timerlabel.setText(str(self.lifetime.get()))


def exec_(app):
    result = app.exec_()
    epics.ca.finalize_libca()
    return result


if __name__ == '__main__':
    epics.ca.initialize_libca()
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(exec_(app))
