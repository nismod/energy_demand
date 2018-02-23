from energy_demand.geography import spatial_diffusion

'''def test_calc_regional_services():



        print("oooooooooooooo")
        _scrap = 0
        for reg in sd_cont['rs_fuel_disagg']:
            print(reg)
            print(np.sum(sd_cont['rs_fuel_disagg'][reg]['rs_space_heating']))
            _scrap += np.sum(sd_cont['rs_fuel_disagg'][reg]['rs_space_heating'])

        print("oooooooooooooo")
        print(_scrap)
        print("_-")
        print(rs_reg_enduse_tech_p_ey['S12000013']['rs_space_heating']['heat_pumps_electricity'])
        print(np.sum(sd_cont['rs_fuel_disagg']['S12000013']['rs_space_heating']))
        print(rs_reg_enduse_tech_p_ey['E07000135']['rs_space_heating']['heat_pumps_electricity'])
        print(np.sum(sd_cont['rs_fuel_disagg']['E07000135']['rs_space_heating']))

        _a = rs_reg_enduse_tech_p_ey['S12000013']['rs_space_heating']['heat_pumps_electricity'] * np.sum(sd_cont['rs_fuel_disagg']['S12000013']['rs_space_heating'])
        _b = rs_reg_enduse_tech_p_ey['E07000135']['rs_space_heating']['heat_pumps_electricity'] * np.sum(sd_cont['rs_fuel_disagg']['E07000135']['rs_space_heating'])
        print("===========")
        print(_a)
        print(_b)
        print("--")
        print(_a + _b)
        print("_--")
        print(switches_cont['rs_share_s_tech_ey_p']['rs_space_heating']['heat_pumps_electricity'])
        print(_scrap * switches_cont['rs_share_s_tech_ey_p']['rs_space_heating']['heat_pumps_electricity'])


'''