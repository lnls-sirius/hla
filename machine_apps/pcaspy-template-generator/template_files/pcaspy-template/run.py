#!/usr/bin/env python3

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import pvs as _pvs
import multiprocessing as _multiprocessing
import signal as _signal
import main as _main

INTERVAL = 0.1
stop_event = _multiprocessing.Event()


def stop_now(signum, frame):
    print(' - SIGINT received.')
    return stop_event.set()


class PCASDriver(_pcaspy.Driver):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.app.driver = self

    def read(self, reason):
        return super().read(reason)

    def write(self, reason, value):
        return super().write(reason, value)


def run():

    # define abort function
    _signal.signal(_signal.SIGINT, stop_now)

    # create application object
    app = _main.App()

    # create a new simple pcaspy server and driver to responde client's requests
    server = _pcaspy.SimpleServer()
    server.createPV(_main.App.PVS_PREFIX, app.pvs_database)
    pcas_driver = PCASDriver(app)

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    # main loop
    while not stop_event.is_set():
        app.process(INTERVAL)

    print('exiting...')
    # sends stop signal to server thread
    server_thread.stop()


if __name__ == '__main__':
    run()
