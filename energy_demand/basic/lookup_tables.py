"""Lookup tables
"""

'''def get_sic_nr()

    lu_tabe = industrydemand_name_sic2007()'''


def industrydemand_name_sic2007():
    """Lookup table of industry energy demands and SIC letter and number

    Return
    ------
    lookup : dict
        name_used_in_model: {'SIC_2007_nr', 'SIC_2007_letter}
    Info
    ----
    https://unstats.un.org/unsd/cr/registry/regcst.asp?Cl=27
    """
    lookup = {
        'mining': {
            'sic_2007_nr': 8,
            'sic_2007_letter': 'B'},
        'food_production': {
            'sic_2007_nr': 10,
            'sic_2007_letter': 'C'},
        'beverages': {
            'sic_2007_nr': 11,
            'sic_2007_letter':'C'},
        'tobacco': {
            'sic_2007_nr': 12,
            'sic_2007_letter':'C'},
        'textiles': {
            'sic_2007_nr': 13,
            'sic_2007_letter': 'C'},
        'wearing_appeal': {
            'sic_2007_nr': 14,
            'sic_2007_letter': 'C'},
        'leather': {
            'sic_2007_nr': 15,
            'sic_2007_letter': 'C'},
        'wood': {
            'sic_2007_nr': 16,
            'sic_2007_letter': 'C'},
        'paper': {
            'sic_2007_nr': 17,
            'sic_2007_letter': 'C'},
        'printing': {
            'sic_2007_nr': 18,
            'sic_2007_letter': 'C'},
        'chemicals': {
            'sic_2007_nr': 20,
            'sic_2007_letter': 'C'},
        'pharmaceuticals': {
            'sic_2007_nr': 21,
            'sic_2007_letter': 'C'},
        'rubber_plastics': {
            'sic_2007_nr': 22,
            'sic_2007_letter': 'C'},
        'non_metallic_mineral_products': {
            'sic_2007_nr': 23,
            'sic_2007_letter': 'C'},
        'basic_metals': {
            'sic_2007_nr': 24,
            'sic_2007_letter': 'C'},
        'fabricated_metal_products': {
            'sic_2007_nr': 25,
            'sic_2007_letter': 'C'},
        'computer': {
            'sic_2007_nr': 26,
            'sic_2007_letter': 'C'},
        'electrical_equipment': {
            'sic_2007_nr': 27,
            'sic_2007_letter': 'C'},
        'machinery': {
            'sic_2007_nr': 28,
            'sic_2007_letter': 'C'},
        'motor_vehicles': {
            'sic_2007_nr': 29,
            'sic_2007_letter': 'C'},
        'other_transport_equipment': {
            'sic_2007_nr': 30,
            'sic_2007_letter': 'C'},
        'furniture': {
            'sic_2007_nr': 31,
            'sic_2007_letter': 'C'},
        'other_manufacturing': {
            'sic_2007_nr': 32,
            'sic_2007_letter': 'C'},
        'water_collection_treatment': {
            'sic_2007_nr': 36,
            'sic_2007_letter': 'E'},
        'waste_collection': {
            'sic_2007_nr': 38,
            'sic_2007_letter': 'E'}}

    return lookup

def basic_lookups():
    """Definition of basic lookup tables

    Return
    ------
    lookups : dict
        Lookup information
    """
    lookups = {}

    # Assign BESI categories to merged AddressPoint dataset
    lookups['building_cnt_lu'] = {
        "commercial_General": 1,
        "primary_Industry": 2,
        "public_Services": 3,
        "education": 4,
        "hospitality": 5,
        "community_arts_leisure": 6,
        "industrial": 7,
        "health": 8,
        "offices": 9,
        "retail": 10,
        "storage": 11,
        "residential": 12,
        "military": 13,
        'emergency_services': 8,
        'other': 14}

    lookups['dwtype'] = {
        0: 'detached',
        1: 'semi_detached',
        2: 'terraced',
        3: 'flat',
        4: 'bungalow'}

    lookups['fueltypes'] = {
        'solid_fuel': 0,
        'gas': 1,
        'electricity': 2,
        'oil': 3,
        'biomass': 4,
        'hydrogen': 5,
        'heat': 6}

    lookups['fueltypes_nr'] = int(len(lookups['fueltypes']))

    return lookups
