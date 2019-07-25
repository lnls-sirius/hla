from siriuspy.search import PSSearch, MASearch
from siriuspy.csdevice.pwrsupply import Const as _PSC


DEFAULT_CAP_BANK_VOLT = {
    'Default': 100,
    'BO-Fam:PS-B-1': 240,
    'BO-Fam:PS-B-2': 240,
    'BO-Fam:PS-QF': 300
}


def get_related_dclinks_data(manames):
    alldclinks = dict()
    for name in manames:
        if 'LI' in name:
            continue
        psnames = MASearch.conv_maname_2_psnames(name)
        dclinkparams = dict()
        for ps in psnames:
            dclinks = PSSearch.conv_psname_2_dclink(ps)
            if dclinks:
                for dcl in dclinks:
                    if PSSearch.conv_psname_2_psmodel(dcl) == 'FBP_DCLink':
                        ctrlloop = _PSC.OpenLoop.Open
                        capvolt = DEFAULT_CAP_BANK_VOLT['Default']
                    else:
                        ctrlloop = _PSC.OpenLoop.Closed
                        capvolt = DEFAULT_CAP_BANK_VOLT[ps]
                    dclinkparams.update({dcl: [ctrlloop, capvolt]})
        alldclinks.update(dclinkparams)
    return alldclinks
