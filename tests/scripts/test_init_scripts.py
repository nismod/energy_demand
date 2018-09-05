"""testing
"""
from energy_demand.scripts import init_scripts

def test_sum_across_sectors_all_regs():
    """testing"""

    fuel_disagg_reg = {
        'regA': {
            'enduse': {'sectorA': 100, 'sectorB': 100}}}

    out = init_scripts.sum_across_sectors_all_regs(fuel_disagg_reg)

    assert out['regA'] == {'enduse': 200}
