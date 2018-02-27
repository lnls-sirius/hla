"""Define factory class to get a control widget."""
from ..detail_widget.DetailWidgetFactory import DetailWidgetFactory
from .FamQuadrupoleControlWidget import *
from .FamSextupoleControlWidget import *
from .SlowCorrectorControlWidget import *
from .FastCorrectorControlWidget import *
from .SkewQuadControlWidget import *


class ControlWidgetFactory:
    """Return a control widget."""

    def __init__(self):
        """Static class."""
        pass

    @staticmethod
    def _device_not_found(section, device):
        raise AttributeError("{} not defined for {}".format(device, section))

    @staticmethod
    def factory(section, device, orientation=2):
        if section == "TB":
            if device == "dipole":
                return DetailWidgetFactory.factory("TB-Fam:MA-B")
            elif device == "corrector-slow":
                return TBSlowCorrectorControlWidget(orientation=orientation)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "BO":
            if device == "dipole":
                return DetailWidgetFactory.factory("BO-Fam:MA-B")
            elif device == "quadrupole":
                return BOFamQuadrupoleControlWidget(orientation=orientation)
            elif device == "sextupole":
                return BOFamSextupoleControlWidget(orientation=orientation)
            elif device == "corrector-slow":
                return BoSlowCorrectorControlWidget(orientation=orientation)
            elif device == "quadrupole-skew":
                return BOSkewQuadControlWidget(orientation=orientation)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "TS":
            if device == "dipole":
                return DetailWidgetFactory.factory("TS-Fam:MA-B")
            elif device == "corrector-slow":
                return TSSlowCorrectorControlWidget(orientation=orientation)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "SI":
            if device == "dipole":
                return DetailWidgetFactory.factory("SI-Fam:MA-B1B2")
            elif device == "quadrupole":
                return SIFamQuadrupoleControlWidget(orientation=orientation)
            elif device == "sextupole":
                return SIFamSextupoleControlWidget(orientation=orientation)
            elif device == "corrector-slow":
                return SISlowCorrectorControlWidget(orientation=orientation)
            elif device == "corrector-fast":
                return SIFastCorrectorControlWidget(orientation=orientation)
            elif device == "quadrupole-skew":
                return SISkewQuadControlWidget(orientation=orientation)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        else:
            raise AttributeError("{} does not exist".format(section))
