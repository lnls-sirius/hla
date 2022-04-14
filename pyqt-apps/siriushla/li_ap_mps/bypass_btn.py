from qtpy.QtGui import QPalette, QColor
from ..widgets import SiriusPushButton


class BypassBtn(SiriusPushButton):

    def __init__(self, parent=None, init_channel=None):
        super().__init__(parent, init_channel=init_channel, pressValue=0)

    def value_changed(self, new_value):
        """Redefine value_changed."""

        if new_value == 1:
            # Bypass
            self.setText('Bypass')
            pal = self.palette()
            pal.setColor(QPalette.Button, QColor('blue'))
            pal.setColor(QPalette.ButtonText, QColor('white'))
            self.setPalette(pal)
            self.pressValue = 0
        else:
            #Active
            self.setText('Active')
            pal = self.palette()
            pal.setColor(QPalette.Button, QColor('#efefef'))
            pal.setColor(QPalette.ButtonText, QColor('black'))
            self.setPalette(pal)
            self.pressValue = 1

        return super().value_changed(new_value)
