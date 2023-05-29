# #!/usr/bin/env python3
# """Soft IOC to test DCCT HLA."""

import time
import signal
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools


INTERVAL = 10
stop_event = False


def stop_now(signum, frame):
    """Stop signal."""
    global stop_event
    stop_event = True


class PCASDriver(_pcaspy.Driver):
    """Driver."""

    def __init__(self):
        """Init."""
        super().__init__()

    def read(self, reason):
        """Read."""
        return super().read(reason)

    def write(self, reason, value):
        """Write."""
        return super().write(reason, value)

    def process(self, interval):
        """Process."""
        time.sleep(INTERVAL)


def run():
    """Run."""
    signal.signal(signal.SIGINT, stop_now)
    db = {
        'ImgDVFStatus-Mon': {
            'type': 'int', 'value': 0b10101101,
        }
    }

    server = _pcaspy.SimpleServer()
    server.createPV('', db)
    pcas_driver = PCASDriver()

    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    while not stop_event:
        pcas_driver.process(INTERVAL)

    server_thread.stop()
    server_thread.join()


if __name__ == '__main__':
    run()
