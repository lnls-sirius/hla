"""Dialog that handle thread that implement a task interface.

Task QThread Interface:
- itemDone: Signal
- size: method that return task size
- exit_task: set quit_thread flag True
"""
import time
from qtpy.QtCore import Signal, QThread
from qtpy.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, \
    QProgressBar


class ProgressDialog(QDialog):
    """Progress dialog.

    Parameters
    ----------
    label - string or list of strings
    task - QThread or list of QThread (implementing task interface)
    parent - QObject
    """

    canceled = Signal()

    def __init__(self, label, task, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._label = label
        self._task = task

        if (isinstance(self._label, (list, tuple)) and
                isinstance(self._task, (list, tuple)) and
                len(self._label) == len(self._task)) or \
                (isinstance(self._label, str) and
                 isinstance(self._task, QThread)):
            pass
        else:
            raise ValueError()

        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout()

        self.dlg_label = QLabel(self)
        self.cur_item_label = QLabel(self)
        self.progress_bar = QProgressBar(self)
        self.cancel = QPushButton('Cancel', self)

        self.layout.addWidget(self.dlg_label)
        self.layout.addWidget(self.cur_item_label)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.cancel)

        self.setLayout(self.layout)

        # Set initial value
        self.progress_bar.setValue(0)

        # Set progress bar limits and connect signals
        self.progress_bar.setMinimum(0)
        if hasattr(self._task, '__iter__'):
            self.dlg_label.setText(self._label[0])
            self._task[0].currentItem.connect(self.cur_item_label.setText)
            self._task[0].itemDone.connect(self.inc_value)
            pb_max = self._task[0].size()
            for i in range(1, len(self._task)):
                self._task[i].currentItem.connect(self.cur_item_label.setText)
                self._task[i].itemDone.connect(self.inc_value)
                self._task[i - 1].completed.connect(self._update_label)
                self._task[i - 1].completed.connect(self._task[i].start)
                pb_max += self._task[i].size()
            self.progress_bar.setMaximum(pb_max)
            self._task[-1].completed.connect(lambda: self._exit_dlg(1))
        else:
            self.dlg_label.setText(self._label)
            self._task.currentItem.connect(self.cur_item_label.setText)
            self._task.itemDone.connect(self.inc_value)
            self._task.completed.connect(lambda: self._exit_dlg(1))
            self.progress_bar.setMaximum(self._task.size())

        self.cancel.pressed.connect(self.canceled.emit)
        self.canceled.connect(lambda: self._exit_dlg(0))
        self.progress_bar.valueChanged.connect(self._is_finished)

    def _update_label(self):
        next_idx = self._label.index(self.dlg_label.text()) + 1
        if next_idx < len(self._label):
            self.dlg_label.setText(self._label[next_idx])

    def _exit_dlg(self, result):
        if hasattr(self._task, '__iter__'):
            for task in self._task:
                task.exit_task()
            self._wait_task(self._task[-1])
            self._task[-1].deleteLater()
        else:
            self._task.exit_task()
            self._wait_task(self._task)
            self._task.deleteLater()
        if result == 1:
            self.accept()
        elif result == 0:
            self.reject()

    def _wait_task(self, task):
        init = time.time()
        try:
            while task.isRunning():
                time.sleep(0.1)
                if time.time() - init > 10:
                    self._exit_dlg(0)
                    raise Exception('Thread will not leave')
        except RuntimeError:
            pass

    def _is_finished(self):
        if self.progress_bar.value() == self.progress_bar.maximum():
            self._exit_dlg(1)

    def set_value(self, value):
        """Set progress bar value."""
        self.progress_bar.setValue(value)

    def inc_value(self):
        """Increase value."""
        self.progress_bar.setValue(self.progress_bar.value()+1)

    def exec_(self):
        """Override."""
        if hasattr(self._task, '__iter__'):
            self._task[0].start()
        else:
            self._task.start()
        return super().exec_()
