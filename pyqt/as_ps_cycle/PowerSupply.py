#!/usr/bin/python3
import re
from epics import caget, caput

PREFIX = 'VAG-'

class PowerSupply:

    #Static Class Variables
    OFF = SLOWREF = REMOTE = DISABLED = 0
    ON = FASTREF = LOCAL = ENABLED = AUTOCORR = 1
    WAIT = WFMREF = MEASRESPMAT = 2
    SIGGEN = 3

    def __init__(self, dev_name):
        self.name = dev_name
        self.dev_name = PREFIX + dev_name
        if re.match("^[A-Z]{2}-\w{2,4}:PS-B", dev_name):
            self.element = "B"
            self.force = "Energy"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-QS", dev_name):
            self.element = "QS"
            self.force = "KL"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-Q", dev_name):
            self.element = "Q"
            self.force = "KL"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-S", dev_name):
            self.element = "S"
            self.force = "SL"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-C", dev_name):
            self.element = "C"
            self.force = "Angle"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-F", dev_name):
            self.element = "FC"
            self.force = "Angle"
        else:
            raise ValueError("Element '{}' not recognised".format(dev_name))

    def devName(self):
        return self.name

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

    def readForce(self):
        return caget(self.dev_name + ':' + self.force + '-RB')
