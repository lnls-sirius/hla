import pvs as _pvs
import time as _time

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)

__version__ = _pvs.__version__

class App:

    PVS_PREFIX = 'TEST-'

    def __init__(self):
        self._driver = None # This should latter be set by the Driver __init__ using driver.setter
        self._pvs_database = _pvs.pvs_database

    @property
    def pvs_database(self):
        return self._pvs_database

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self,value):
        self._driver = value

    def process(self,interval):
        _time.sleep(interval)

    def read(self,reason):
        value = None # this should be implemented.
        self.driver.updatePVs() # this should be used in case PV states have changed.
        return value

    def write(self,reason,value):
        return False # False: no write implemented.
