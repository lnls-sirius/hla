import time
from .task import EpicsTask


class EpicsWait(EpicsTask):
    """."""

    def __init__(self, pvs, wait_time=1.0, parent=None):
        """."""
        super().__init__(pvs, None, None, parent=parent)
        self.wait_time = wait_time

    def run(self):
        """."""
        if not self._quit_task:
            t0 = time.time()
            siz = self.size()
            if siz:
                for _ in range(siz):
                    dt = time.time() - t0
                    self.currentItem.emit(
                        'Waiting for {:3.2f} s...'.format(self.wait_time - dt))
                    time.sleep(self.wait_time/siz)
                    self.itemDone.emit()
            else:
                time.sleep(self.wait_time)
        self.completed.emit()
