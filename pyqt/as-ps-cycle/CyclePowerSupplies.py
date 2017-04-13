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

    def __init__(self, section, devices):
        self.power_supplies = []

        with open("ps_map/ps_%s_%s.txt" % (section, devices), 'r') as fd:
            for line in fd:
                self.power_supplies.append(PowerSupply(line.strip()))


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

    def setOn(self, ps):
        return ps.setPowerStateSelected(PowerSupply.ON)

    def setZeroCurrent(self, ps):
        return ps.setCurrentSetPoint(0)

    def setSigGen(self, ps):
        return ps.setOpModeSelected(PowerSupply.SIGGEN)

    def setToCycle(self):
        for ps in self.power_supplies:
            if not self.setOn(ps) or not self.setZeroCurrent(ps) or not self.setSigGen(ps):
                self.not_ready_ps.add(ps)

    def isReadyToCycle(self):
        for ps in self.power_supplies:
            if not self._isPSReadyToCycle(ps):
                self.not_ready_ps.add(ps)

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
