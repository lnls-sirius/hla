"""Horizontal Ruler Widget."""
from qtpy.QtWidgets import QFrame

class HorizontalRuler(QFrame):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        # self.setContentsMargins(0, 10, 0, 10)
        self.setFixedHeight(30)
        # self.setStyleSheet("""
        #     margin-top: 10px;
        # """)

    def setHeight(self, height):
        self.setFixedHeight(height)
