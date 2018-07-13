"""Append result to shapefile
"""
'''import logging
import shapefile

def write_result_shapefile(lad_geometry_shp, out_shape, field_names, csv_results):
    """
    Join result attributes to LAD geography with
    pyhape library

    Arguments
    ---------
    lad_geometry_shp : str
        Path to LAD shapefile
    out_shape : str
        Path to new shapefile
    field_names : list
        list with new attribute field name
    csv_results : list
        list with result dicts

    Info
    -----
    pip install pyshp
    https://github.com/GeospatialPython/pyshp#reading-shapefiles-from-file-like-objects

    http://www.qgistutorials.com/en/docs/performing_table_joins_pyqgis.html
    """
    # Read in our existing shapefile
    lad_geometry_shp_name = lad_geometry_shp[:-3]
    myshp = open(lad_geometry_shp_name + "shp", "rb")
    mydbf = open(lad_geometry_shp_name + "dbf", "rb")

    record = shapefile.Reader(shp=myshp, dbf=mydbf)

    # Create a new shapefile in memory
    writer = shapefile.Writer()

    # Copy over the existing fields
    writer.fields = list(record.fields)

    # --------------
    # Add new fields
    # --------------
    for field_name in field_names:
        writer.field(field_name, "F", decimal=10) #Float

    # Get position of field 'name' 
    position = 0
    for field_name in record.fields[1:]:
        if field_name[0] == 'name': #corresponds to LAD Geocode
            position_field_name = position
            break
        else:
            position += 1

    # --------------------------
    # Join fields programatically
    # --------------------------
    missing_recors = set()

    # Loop through each record, add a column and get results
    for rec in record.records():

        # Get geocode for row
        geo_code = rec[position_field_name]

        # Iterate result entries in list
        for result_per_field in csv_results:

            # Iterate result entries and add
            try:
                result_csv = result_per_field[geo_code]
            except KeyError:
                # No results
                result_csv = 0
                missing_recors.add(geo_code)

            # Add specific fuel result
            rec.append(result_csv)

        # Add the modified record to the new shapefile
        writer.records.append(rec)

    if missing_recors != []:
        logging.warning(
            "No result value for regions '%s' in joining shapefile",
            missing_recors)
    else:
        pass

    # Copy over the geometry without any changes
    writer._shapes.extend(record.shapes())

    # Save as a new shapefile (or write over the old one)
    writer.save(out_shape)
    logging.info("... finished writing shp")
    return'''
