"""Define widget for controlling slow correctors."""
from .BasePSControlWidget import BasePSControlWidget


class SISlowCorrectorControlWidget(BasePSControlWidget):
    """Storage ring slow correctors."""

    def _getFilter(self, subsection=None):
        filt = {"sec": "SI", "sub": "\w{4}", "dev": "(CH|CV).*"}
        if subsection:
            filt.update({'sub': subsection})
        return filt

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [('Horizontal Slow Correctors', '-CH'),
                ('Vertical Slow Corretors', '-CV')]


class BoSlowCorrectorControlWidget(SISlowCorrectorControlWidget):
    """Booster slow corretors."""

    def _getFilter(self, subsection=None):
        filt = {"sec": "BO", "sub": "\w{3}", "dev": "(CH|CV).*"}
        if subsection:
            filt.update({'sub': subsection})
        return filt


class TBSlowCorrectorControlWidget(SISlowCorrectorControlWidget):
    """To booster transport line slow corrector."""

    def _getFilter(self, subsection=None):
        filt = {"sec": "TB", "sub": "\d{2}", "dev": "(CH|CV).*"}
        if subsection:
            filt.update({'sub': subsection})
        return filt

    def _hasScrollArea(self):
        return False


class TSSlowCorrectorControlWidget(SISlowCorrectorControlWidget):
    """To sirius transport line slow correctors."""

    def _getFilter(self, subsection=None):
        filt = {"sec": "TS", "sub": "\w{2}", "dev": "(CH|CV).*"}
        if subsection:
            filt.update({'sub': subsection})
        return filt

    def _hasScrollArea(self):
        return False


class LISlowCorrectorControlWidget(SISlowCorrectorControlWidget):
    """To booster transport line slow corrector."""

    def _getFilter(self, subsection=None):
        return {"sec": "LI", "sub": "\d{2}", "dev": "(CH|CV).*"}

    def _hasScrollArea(self):
        return False


class IDSlowCorrectorControlWidget(SISlowCorrectorControlWidget):
    """To booster transport line slow corrector."""

    def _getFilter(self, subsection=None):
        filt = {"sec": "SI", "sub": "\d{2}", "dev": "(CH|CV).*"}
        if subsection:
            filt.update({'sub': subsection})
        return filt

    def _hasScrollArea(self):
        return False

    def _getVisibleProps(self):
        return ['detail', 'state', 'intlk', 'strength_sp', 'strength_mon']
