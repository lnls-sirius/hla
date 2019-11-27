"""."""
from siriuspy.search import MASearch as _MASearch
from siriuspy.namesys import SiriusPVName as _SiriusPVName


_TIMEOUT = 0.05


def init_section(section):
    """."""
    dipole, magnets = _create_objects(section)
    dipole, magnets = _create_pvs(dipole, magnets)
    return dipole, magnets


def _magfunc(maname):
    """."""
    func = _MASearch.conv_maname_2_magfunc(maname)
    return list(func.values())[0]


def _create_objects(section):
    """."""
    dipnames = {
        'TB': _SiriusPVName('TB-Fam:MA-B'),
        'BO': _SiriusPVName('BO-Fam:MA-B'),
        'TS': _SiriusPVName('TS-Fam:MA-B'),
        'SI': _SiriusPVName('SI-Fam:MA-B1B2')}
    dipname = dipnames[section]
    manames = _MASearch.get_manames()
    magnets = []
    for maname in manames:
        maname = _SiriusPVName(maname)
        if maname.sec != section:
            continue
        if maname.dev.startswith('FC'):
            continue
        if maname.sub != 'Fam' and maname.dev.startswith(('SF', 'SD')):
            continue
        mfunc = _magfunc(maname)
        if mfunc == 'dipole':
            dipole = {'maname': dipname, 'mafunc': mfunc}
            continue
        dstruc = {'maname': maname, 'mafunc': mfunc}
        magnets.append(dstruc)
    return dipole, magnets


def _create_pvs(dipole, magnets):
    """."""
    maname = dipole['maname']
    dip = [maname.substitute(propty_name='Energy', propty_suffix='SP')]
    mags = set()
    for d in magnets:
        maname = d['maname']
        magf = d['mafunc']
        if 'corrector' in magf:
            mags.add(maname.substitute(
                propty_name='Kick', propty_suffix='SP'))
        elif 'quadrupole' in magf:
            mags.add(maname.substitute(
                propty_name='KL', propty_suffix='SP'))
        elif 'sextupole' in magf:
            mags.add(maname.substitute(
                propty_name='SL', propty_suffix='SP'))
    return dip, sorted(mags)
