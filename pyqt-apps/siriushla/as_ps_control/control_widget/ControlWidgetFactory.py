"""Define factory class to get a control widget."""
from ..detail_widget.DetailWidgetFactory import DetailWidgetFactory
from siriushla.as_ps_control.control_widget.DipoleControlWidget import *
from siriushla.as_ps_control.control_widget.FamQuadrupoleControlWidget import *
from siriushla.as_ps_control.control_widget.FamSextupoleControlWidget import *
from siriushla.as_ps_control.control_widget.SlowCorrectorControlWidget import *
from siriushla.as_ps_control.control_widget.FastCorrectorControlWidget import *
from siriushla.as_ps_control.control_widget.SkewQuadControlWidget import *


class ControlWidgetFactory:
    """Return a control widget."""

    def __init__(self):
        """Static class."""
        pass

    @staticmethod
    def _device_not_found(section, device):
        raise AttributeError("{} not defined for {}".format(device, section))

    @staticmethod
    def factory(parent, section, discipline, device, orientation=2):
        if section == "TB":
            if device == "dipole":
                # if discipline == 'MA':
                #     return DetailWidgetFactory.factory(
                #         "TB-Fam:MA-B", parent=parent)
                # else:
                return TBDipoleControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            elif device == "quadrupole":
                return TBQuadrupoleControlWidget(
                        dev_type=discipline, orientation=orientation, parent=parent)
            elif device == "corrector-slow":
                return TBSlowCorrectorControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "BO":
            if device == "dipole":
                # if discipline == 'MA':
                #     # return DetailWidgetFactory.factory("BO-Fam:MA-B")
                # else:
                return BODipoleControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            elif device == "quadrupole":
                return BOFamQuadrupoleControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            elif device == "sextupole":
                return BOFamSextupoleControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            elif device == "corrector-slow":
                return BoSlowCorrectorControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            elif device == "quadrupole-skew":
                return BOSkewQuadControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "TS":
            if device == "dipole":
                # if discipline == 'MA':
                #     return DetailWidgetFactory.factory("TS-Fam:MA-B")
                # else:
                return TSDipoleControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            elif device == "quadrupole":
                return TSQuadrupoleControlWidget(
                        dev_type=discipline, orientation=orientation, parent=parent)
            elif device == "corrector-slow":
                return TSSlowCorrectorControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "SI":
            if device == "dipole":
                # if discipline == 'MA':
                #     return DetailWidgetFactory.factory("SI-Fam:MA-B1B2")
                # else:
                return SIDipoleControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            elif device == "quadrupole":
                return SIFamQuadrupoleControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            elif device == "sextupole":
                return SIFamSextupoleControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            elif device == "corrector-slow":
                return SISlowCorrectorControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            elif device == "corrector-fast":
                return SIFastCorrectorControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            elif device == "quadrupole-skew":
                return SISkewQuadControlWidget(
                    dev_type=discipline, orientation=orientation, parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        else:
            raise AttributeError("{} does not exist".format(section))
