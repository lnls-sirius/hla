"""Report dialog."""
from qtpy.QtCore import QSize
from qtpy.QtWidgets import QLabel, QPushButton, QListWidget, QVBoxLayout, \
    QDialog


class ReportDialog(QDialog):
    """Show a list of items."""

    def __init__(self, items, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._items = items
        self._setup_ui()
        self.setWindowTitle('Report')

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        if self._items:
            self.header = QLabel('Failed PVs', self)
            self.layout.addWidget(self.header)
            self.items_list = QListWidget(self)
            self.items_list.addItems(self._items)
            self.layout.addWidget(self.items_list)
            self.setMinimumSize(QSize(600, 300))
        else:
            self.header = QLabel('Done', self)
            self.layout.addWidget(self.header)
            self.setMinimumSize(QSize(300, 100))
        self.ok_btn = QPushButton('Ok', self)
        self.layout.addWidget(self.ok_btn)

        self.ok_btn.clicked.connect(self.accept)
