"""Define factory class to get a control widget."""
from .DipoleControlWidget import LISpectControlWidget, \
    TBDipoleControlWidget, BODipoleControlWidget,\
    TSDipoleControlWidget, SIDipoleControlWidget
from .FamQuadrupoleControlWidget import LIQuadrupoleControlWidget, \
    TBQuadrupoleControlWidget, BOFamQuadrupoleControlWidget,\
    TSQuadrupoleControlWidget, SIFamQuadrupoleControlWidget
from .FamSextupoleControlWidget import \
    BOFamSextupoleControlWidget, SIFamSextupoleControlWidget
from .SlowCorrectorControlWidget import LISlowCorrectorControlWidget, \
    TBSlowCorrectorControlWidget, BoSlowCorrectorControlWidget, \
    TSSlowCorrectorControlWidget, SISlowCorrectorControlWidget
from .SkewQuadControlWidget import BOSkewQuadControlWidget, \
    SISkewQuadControlWidget
from .TrimAllControlWidget import SITrimAllControlWidget
from .SolenoidControlWidget import LISolenoidControlWidget
from .LensControlWidget import LILensControlWidget, ITLensControlWidget
from .FastCorrectorControlWidget import \
    SIFastCorrectorControlWidget
from .SeptFFCorrectorControlWidget import SISeptFFCorrectorControlWidget


class ControlWidgetFactory:
    """Return a control widget."""

    def __init__(self):
        """Static class."""

    @staticmethod
    def _device_not_found(section, device):
        raise AttributeError("{} not defined for {}".format(device, section))

    @staticmethod
    def factory(parent, section, device, subsection=None, orientation=0):
        if section == "LI":
            if device == "spectrometer":
                return LISpectControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "lens":
                return LILensControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "corrector-slow":
                return LISlowCorrectorControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "solenoid":
                return LISolenoidControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "quadrupole":
                return LIQuadrupoleControlWidget(
                    orientation=orientation, parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "TB":
            if device == "dipole":
                return TBDipoleControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "quadrupole":
                return TBQuadrupoleControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "corrector-slow":
                return TBSlowCorrectorControlWidget(
                    subsection=subsection, orientation=orientation,
                    parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "BO":
            if device == "dipole":
                return BODipoleControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "quadrupole":
                return BOFamQuadrupoleControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "sextupole":
                return BOFamSextupoleControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "corrector-slow":
                return BoSlowCorrectorControlWidget(
                    subsection=subsection, orientation=orientation,
                    parent=parent)
            elif device == "skew-quadrupole":
                return BOSkewQuadControlWidget(
                    subsection=subsection, orientation=orientation,
                    parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "TS":
            if device == "dipole":
                return TSDipoleControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "quadrupole":
                return TSQuadrupoleControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "corrector-slow":
                return TSSlowCorrectorControlWidget(
                    subsection=subsection, orientation=orientation,
                    parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "SI":
            if device == "dipole":
                return SIDipoleControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "quadrupole":
                return SIFamQuadrupoleControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "sextupole":
                return SIFamSextupoleControlWidget(
                    orientation=orientation, parent=parent)
            elif device == "corrector-slow":
                return SISlowCorrectorControlWidget(
                    subsection=subsection, orientation=orientation,
                    parent=parent)
            elif device == "corrector-fast":
                return SIFastCorrectorControlWidget(
                    subsection=subsection, orientation=orientation,
                    parent=parent)
            elif device == "corrector-septff":
                return SISeptFFCorrectorControlWidget(
                    subsection=subsection, orientation=orientation,
                    parent=parent)
            elif device == "skew-quadrupole":
                return SISkewQuadControlWidget(
                    subsection=subsection, orientation=orientation,
                    parent=parent)
            elif device == "trim-quadrupole":
                return SITrimAllControlWidget(
                    subsection=subsection, orientation=orientation,
                    parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        elif section == "IT":
            if device == "lens":
                return ITLensControlWidget(
                    orientation=orientation, parent=parent)
            else:
                ControlWidgetFactory._device_not_found(section, device)
        else:
            raise AttributeError("{} does not exist".format(section))
