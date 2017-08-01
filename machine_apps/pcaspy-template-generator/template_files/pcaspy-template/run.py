#!/usr/bin/env python-sirius

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import signal as _signal
import main as _main


INTERVAL = 0.1
stop_event = False
PREFIX = ''


def _stop_now(signum, frame):
    print(' - SIGNAL received.')
    global stop_event
    stop_event = True


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, app=None):
        super().__init__()
        self.app = app or _main.App()
        self.app.driver = self

    def read(self, reason):
        value = self.app.read(reason)
        if value is None:
            return super().read(reason)
        else:
            return value

    def write(self, reason, value):
        app_ret = self.app.write(reason, value)
        if app_ret:
            self.setParam(reason, value)
        self.updatePVs()
        return app_ret


def run():
    """Run the IOC."""
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # create the application model
    app = _main.App()

    db = app.get_database()

    # create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    server.createPV(PREFIX, db)

    # create the driver
    pcas_driver = _PCASDriver(app)

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    # main loop
    # while not stop_event.is_set():
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    print('exiting...')
    # send stop signal to server thread
    server_thread.stop()
    server_thread.join()


if __name__ == '__main__':
    run()
