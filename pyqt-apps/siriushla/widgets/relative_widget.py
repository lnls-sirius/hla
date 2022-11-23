from qtpy.QtWidgets import QWidget, QHBoxLayout

class RelativeWidget(QWidget):
    ''' Widget that stays in a relative position in the window '''
    ''' Relative position and size are given
    as a percentage based on the size of the parents'''

    def __init__(self, parent=None, widget=None, relative_pos=None):
        """."""
        super().__init__(parent=parent)
        self.parent = parent
        lay = QHBoxLayout()
        lay.addWidget(widget)
        self.setLayout(lay)
        self.posX = relative_pos[0]
        self.posY = relative_pos[1]
        self.width = relative_pos[2]
        self.height = relative_pos[3]

    def relativeResize(self):
        ''' Resize and position in according to the relative position '''
        self.move(
            self.parent.geometry().width() * self.posX / 100,
            self.parent.geometry().height() * self.posY / 100)
        self.resize(
            self.parent.geometry().width() * self.width / 100,
            self.parent.geometry().height() * self.height / 100)
