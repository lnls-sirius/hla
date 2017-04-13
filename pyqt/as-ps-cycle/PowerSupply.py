#!/usr/bin/python3

from epics import caget, caput

PREFIX = 'VAG-'

class PowerSupply:

    #Static Class Variables
    OFF = SLOWREF = REMOTE = DISABLED = 0
    ON = FASTREF = LOCAL = ENABLED = AUTOCORR = 1
    WAIT = WFMREF = MEASRESPMAT = 2
    SIGGEN = 3

    def __init__(self, dev_name):
        self.dev_name = PREFIX + dev_name

    def devName(self):
        return self.dev_name

    def readCurrent(self):
        return caget(self.dev_name + ':Current-RB')

    def readCurrentSetPoint(self):
        return caget(self.dev_name + ':Current-SP')

    def setCurrentSetPoint(self, value):
        return caput(self.dev_name + ':Current-SP ', value)

    def readPowerStateStatus(self):
        return caget(self.dev_name + ':PwrState-Sts')

    def readPowerStateSelected(self):
        return caget(self.dev_name + ':PwrState-Sel')

    def setPowerStateSelected(self, value):
        return caput(self.dev_name + ':PwrState-Sel', value)

    def readOpModeStatus(self):
        return caget(self.dev_name + ':OpMode-Sts')

    def readOpModeSelected(self):
        return caget(self.dev_name + ':OpMode-Sel')

    def setOpModeSelected(self, value):
        return caput(self.dev_name + ':OpMode-Sel', value)
