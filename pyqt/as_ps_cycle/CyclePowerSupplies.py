#!/usr/bin/python3

from PowerSupply import PowerSupply
import qrc_resource

class CyclePowerSupplies:

    ANEL = 'si'
    TRANSPORTE = 'lt'
    LINAC = 'li'
    DIPOLOS = 'b'
    QUADRUPOLOS = 'q'
    SEXTUPOLOS = 's'
    CORRETORAS = 'c'

    not_ready_ps = set()

    def __init__(self):
        self.power_supplies = []
        self.ps_set = dict([("li_c", False), ("li_q", False), ("lt_b", False), \
                ("lt_q", False), ("lt_c", False), ("si_b", False), \
                ("si_q", False), ("si_s", False), ("si_c", False)])

    def addPsSet(self, devices):
        self.ps_set[devices] = True

    def removePsSet(self, devices):
        self.ps_set[devices] = False

    def _readPsSet(self, devices):
        with open("ps_map/ps_%s.txt" % (devices), 'r') as fd:
            for line in fd:
                self.power_supplies.append(PowerSupply(line.strip()))

    def readAllPs(self):
        devices = [key for key in self.ps_set.keys() if self.ps_set[key]]
        for device in devices:
            self._readPsSet(device)

    def _isPSInCycleState(self, ps):
        if ps.readOpModeStatus() == PowerSupply.SIGGEN:
            return True

        return False

    def _isPSCurrentZero(self, ps):
        if ps.readCurrent() == 0:
            return True

        return False

    def _isPSPowerOn(self, ps):
        if ps.readPowerStateStatus() == PowerSupply.ON:
            return True

        return False

    def _isPSReadyToCycle(self, ps):
        if self._isPSCurrentZero(ps) and self._isPSPowerOn(ps) and self._isPSInCycleState(ps):
            return True

        return False

    def _setOn(self, ps):
        return ps.setPowerStateSelected(PowerSupply.ON)

    def _setZeroCurrent(self, ps):
        return ps.setCurrentSetPoint(0)

    def _setSigGen(self, ps):
        return ps.setOpModeSelected(PowerSupply.SIGGEN)

    def setToCycle(self):
        self.not_ready_ps = list()
        self.readAllPs()
        for ps in self.power_supplies:
            if not self._setOn(ps) or not self._setZeroCurrent(ps) or not self._setSigGen(ps):
                self.not_ready_ps.add(ps)

        if len(self.not_ready_ps) > 0:
            return False

        return True

    def isReadyToCycle(self):
        self.not_ready_ps = list()
        for ps in self.power_supplies:
            if not self._isPSReadyToCycle(ps):
                self.not_ready_ps.add(ps)

        if len(self.not_ready_ps) > 0:
            return False

        return True

    def printBadPS(self):
        for ps in self.not_ready_ps:
            print(ps.devName())

    '''def prepareToCycle(self):
        self.setToCycle()
        self.isReadyToCycle()'''

if __name__ == '__main__':
    op = CyclePowerSupplies('fontes.txt')
    op.cycle()
    op.printBadPS()
