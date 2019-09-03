"""Define factory class to get a control widget."""
from .DipoleControlWidget import \
    TBDipoleControlWidget, BODipoleControlWidget,\
    TSDipoleControlWidget, SIDipoleControlWidget
from .FamQuadrupoleControlWidget import \
    TBQuadrupoleControlWidget, BOFamQuadrupoleControlWidget,\
    TSQuadrupoleControlWidget, SIFamQuadrupoleControlWidget
from .FamSextupoleControlWidget import \
    BOFamSextupoleControlWidget, SIFamSextupoleControlWidget
from .SlowCorrectorControlWidget import \
    TBSlowCorrectorControlWidget, BoSlowCorrectorControlWidget, \
    TSSlowCorrectorControlWidget, SISlowCorrectorControlWidget
from .SkewQuadControlWidget import BOSkewQuadControlWidget, \
    SISkewQuadControlWidget
from .FastCorrectorControlWidget import \
    SIFastCorrectorControlWidget


class ControlWidgetFactory:
    """Return a control widget."""

    def __init__(self):
        """Static class."""
        pass

    @staticmethod
    def _device_not_found(section, device):
        raise AttributeError("{} not defined for {}".format(device, section))

    @staticmethod
    def factory(parent, section, discipline, device, orientation=0):
        if section == "TB":
            if device == "dipole":
                return TBDipoleControlWidget(dev_type=discipline,
                                             orientation=orientation,
                                             parent=parent)
            elif device == "quadrupole":
                return TBQuadrupoleControlWidget(dev_type=discipline,
                                                 orientation=orientation,
                                                 parent=parent)
            elif device == "corrector-slow":
                return TBSlowCorrectorControlWidget(dev_type=discipline,
                                                    orientation=orientation,
                                                    parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "BO":
            if device == "dipole":
                return BODipoleControlWidget(dev_type=discipline,
                                             orientation=orientation,
                                             parent=parent)
            elif device == "quadrupole":
                return BOFamQuadrupoleControlWidget(dev_type=discipline,
                                                    orientation=orientation,
                                                    parent=parent)
            elif device == "sextupole":
                return BOFamSextupoleControlWidget(dev_type=discipline,
                                                   orientation=orientation,
                                                   parent=parent)
            elif device == "corrector-slow":
                return BoSlowCorrectorControlWidget(dev_type=discipline,
                                                    orientation=orientation,
                                                    parent=parent)
            elif device == "quadrupole-skew":
                return BOSkewQuadControlWidget(dev_type=discipline,
                                               orientation=orientation,
                                               parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "TS":
            if device == "dipole":
                return TSDipoleControlWidget(dev_type=discipline,
                                             orientation=orientation,
                                             parent=parent)
            elif device == "quadrupole":
                return TSQuadrupoleControlWidget(dev_type=discipline,
                                                 orientation=orientation,
                                                 parent=parent)
            elif device == "corrector-slow":
                return TSSlowCorrectorControlWidget(dev_type=discipline,
                                                    orientation=orientation,
                                                    parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "SI":
            if device == "dipole":
                return SIDipoleControlWidget(dev_type=discipline,
                                             orientation=orientation,
                                             parent=parent)
            elif device == "quadrupole":
                return SIFamQuadrupoleControlWidget(dev_type=discipline,
                                                    orientation=orientation,
                                                    parent=parent)
            elif device == "sextupole":
                return SIFamSextupoleControlWidget(dev_type=discipline,
                                                   orientation=orientation,
                                                   parent=parent)
            elif device == "corrector-slow":
                return SISlowCorrectorControlWidget(dev_type=discipline,
                                                    orientation=orientation,
                                                    parent=parent)
            elif device == "corrector-fast":
                return SIFastCorrectorControlWidget(dev_type=discipline,
                                                    orientation=orientation,
                                                    parent=parent)
            elif device == "quadrupole-skew":
                return SISkewQuadControlWidget(dev_type=discipline,
                                               orientation=orientation,
                                               parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        else:
            raise AttributeError("{} does not exist".format(section))
