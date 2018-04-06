"""testing
"""
from energy_demand.scripts import init_scripts

def test_convert_sharesdict_to_service_switches():
    """testing"""

    s_tech_switched_p = {'techA': 0.5, 'techB': 0.5}

    out = init_scripts.convert_sharesdict_to_service_switches(
        yr_until_switched=2050,
        enduse='heating',
        s_tech_switched_p=s_tech_switched_p,
        regions=False,
        regional_specific=False)

    for switch in out:
        if switch.technology_install == 'techA':
            assert switch.service_share_ey == 0.5
        if switch.technology_install == 'techB':
            assert switch.service_share_ey == 0.5

def test_sum_across_sectors_all_regs():
    """testing"""

    fuel_disagg_reg = {
        'regA': {
            'enduse': {'sectorA': 100, 'sectorB': 100}}}

    out = init_scripts.sum_across_sectors_all_regs(fuel_disagg_reg)

    assert out['regA'] == {'enduse': 200}
