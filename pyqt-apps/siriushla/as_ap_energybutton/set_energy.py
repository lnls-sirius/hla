"""."""
from time import sleep
import epics as _epics
from siriuspy.search.ma_search import MASearch as _MASearch
import siriuspy.magnet.data as _mdata
from siriuspy.namesys import SiriusPVName as _SiriusPVName


_TIMEOUT = 0.05


def init_section(section):
    """."""
    dipole, magnets = _create_objects(section)
    _create_pvs(dipole, magnets)
    return dipole, magnets


def set_energy(energy, dipole, magnets):
    """."""
    # store normalized values
    fail_list = _store_normalized(dipole, magnets)
    if fail_list:
        return list(set(fail_list))
    # set dipole energy
    if not dipole['pv_sp'].connected:
        fail_list += ['set:'+dipole['pv_sp'].pvname]
        return list(set(fail_list))
    dipole['pv_sp'].value = energy
    dipole['sp_value'] = energy
    sleep(0.5)
    # restore normalized values
    fail_list = _restore_normalized(dipole, magnets)
    if fail_list:
        return list(set(fail_list))
    sleep(0.5)
    # check values set
    fail_list = _check_values(dipole, magnets)
    return list(set(fail_list))


def _magfunc(madata):
    """."""
    psnames = madata.psnames
    return madata.magfunc(psnames[0])


def _fail_list(dipole, magnets):
    """."""
    fail_list = []
    if not dipole['pv_sp'].connected:
        fail_list.append(dipole['pv_sp'].pvname)
    for m in magnets:
        if not m['pv_sp'].connected:
            fail_list.append(m['pv_sp'].pvname)
    return fail_list


def _create_objects(section):
    """."""
    dipnames = {
        'TB': 'TB-Fam:MA-B',
        'BO': 'BO-Fam:MA-B',
        'SI': 'BO-Fam:MA-B1B2'
    }
    dipname = dipnames[section]
    manames = _MASearch.get_manames()
    magnets = []
    for maname in manames:
        maname = _SiriusPVName(maname)
        if maname.sec != section:
            continue
        if maname.dev == 'FC':
            continue
        if maname.sub != 'Fam' and ('SD' in maname.dev or 'SF' in maname.dev):
            continue
        if maname.dis == 'PM':
            continue
        print(maname)
        madata = _mdata.MAData(maname=maname)
        mfunc = _magfunc(madata)
        if mfunc == 'dipole':
            continue
        dstruc = {
            'maname': maname,
            'madata': madata,
        }
        magnets.append(dstruc)
    dipole = {
        'maname': dipname,
        'madata': _mdata.MAData(maname=dipname),
    }
    return dipole, magnets


def _create_pvs(dipole, magnets):
    """."""
    maname = dipole['maname']
    dipole['pv_sp'] = _epics.PV(maname + ':Energy-SP')
    for d in magnets:
        maname = d['maname']
        madata = d['madata']
        magf = _magfunc(madata)
        if 'corrector' in magf:
            d['pv_sp'] = _epics.PV(maname + ':Kick-SP', connection_timeout=_TIMEOUT)
        elif 'quadrupole' in magf:
            d['pv_sp'] = _epics.PV(maname + ':KL-SP', connection_timeout=_TIMEOUT)
        elif 'sextupole' in magf:
            d['pv_sp'] = _epics.PV(maname + ':SL-SP', connection_timeout=_TIMEOUT)


def _check_values(dipole, magnets):
    fail_list = []
    if abs(dipole['pv_sp'].value - dipole['sp_value']) > 1e-5:
        # print(dipole['pv_sp'].pvname, dipole['pv_sp'].value, dipole['sp_value'])
        fail_list.append(dipole['pv_sp'].pvname)
    for m in magnets:
        if abs(m['pv_sp'].value - m['sp_value']) > 1e-5:
            # print(m['pv_sp'].pvname, m['pv_sp'].value, m['sp_value'])
            fail_list.append(m['pv_sp'].pvname)
    return fail_list


def _store_normalized(dipole, magnets):
    """."""
    fail_list = _fail_list(dipole, magnets)
    if fail_list:
        return fail_list
    for m in magnets:
        if m['pv_sp'].connected:
            m['sp_value'] = m['pv_sp'].value
        else:
            fail_list.append(m['pv_sp'].pvname)
            m['sp_value'] = None
    return fail_list


def _restore_normalized(dipole, magnets):
    """."""
    fail_list = _fail_list(dipole, magnets)
    if fail_list:
        return fail_list
    for m in magnets:
        value = m['sp_value']
        if value is not None and m['pv_sp'].connected:
            m['pv_sp'].value = value
            pass
        else:
            fail_list.append(m['pv_sp'].pvname)
    return fail_list
