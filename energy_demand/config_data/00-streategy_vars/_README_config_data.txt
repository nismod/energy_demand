The following inputs are necessary to manually define a parameters

sub_param_name   : str      Name of sub_parameter (only used for multidimensional parameters)

default_by       : float    Default value of parameter in base year

end_yr           : float    Value in start year of narrative

value_ey         : float    Value in end year of narrative

sector           : str      Affected sector. If left blank this value is replaced with TRUE, which means that the change applies across all sectors

diffusion_choice : str      Sigmoid or linear needs to be provided. If specific sigmoid input parameters want to be added, create new fields
                            sig_midpoint,sig_steepness and add values

---------------------------------
Specific arguments for parameter
---------------------------------
generic_fuel_switch     value_ey            float   Corresponds to 'fuel_share_switched_ey', i.e. the share of fuel to be switched
                        sub_param_name      str     Corresponds to enduse
                        default_by          float   Default value
                        fueltype_replace    str     Fueltype which is to be switched 
                        end_yr              float   End year of single narrative
                        sector              str     Affected sector


 