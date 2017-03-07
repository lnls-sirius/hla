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

    pvs_database = _pvs.pvs_database

    def __init__(self,driver):
        self._driver = driver

    @property
    def driver(self):
        return self._driver

    def process(self,interval):
        _time.sleep(interval)

    def read(self,reason):
        value = None # implementation here
        #self.driver.updatePVs() # this should be used in case PV states change.
        return value

    def write(self,reason,value):
        # implementation here
        #self.driver.updatePVs() # this should be used in case PV states change.
        return True # when returning True super().write of PCASDrive is invoked
