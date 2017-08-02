"""Main Module of the IOC Logic."""

import pvs as _pvs
import time as _time

__version__ = _pvs.__version__


class App:
    """Main Class of the IOC Logic."""

    pvs_database = _pvs.pvs_database

    def get_database(self):
        """Get the database."""
        db = dict()
        for pre, pvs in self.pvs_database.items():
            for pvname, info in pvs.items():
                db[pre + pvname] = info
        return db

    def __init__(self, driver=None):
        """Initialize the instance."""
        self._driver = driver

    @property
    def driver(self):
        """Set the driver of the App."""
        return self._driver

    @driver.setter
    def driver(self, driver):
        self._driver = driver

    def process(self, interval):
        """Trigger connection to external PVs in other classes."""
        _time.sleep(interval)

    def read(self, reason):
        """Read PV from database."""
        # implementation here
        # The default behavior is to return None and let the driver read
        # from the database.
        return None

    def write(self, reason, value):
        """Write PV in the model."""
        # implementation here
        # this should be used in case PV state change.
        return True  # return True for successful write and False otherwise.
