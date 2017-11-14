"""Append result to shapefile
"""
import logging
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

    r = shapefile.Reader(shp=myshp, dbf=mydbf)

    # Create a new shapefile in memory
    w = shapefile.Writer()

    # Copy over the existing fields
    w.fields = list(r.fields)

    # --------------
    # Add new fields
    # --------------
    for field_name in field_names:
        w.field(field_name, "F", decimal=10) #Float

    # Get position of field 'geo_code'
    position = 0
    for field_name in r.fields[1:]:
        if field_name[0] == 'geo_code':
            position_field_name = position
        else:
            position += 1

    # --------------------------
    # Join fields programatically
    # --------------------------
    # Loop through each record, add a column and get results
    for rec in r.records():

        # Get geocode for row
        geo_code = rec[position_field_name]

        # Iterate result entries in list
        for result_per_field in csv_results:

            # Iterate result entries and add
            #for _ in result_per_field:
            try:
                result_csv = result_per_field[geo_code]
            except KeyError:
                # No results
                result_csv = 0
                logging.warning(
                    "No result value for region '%s' in joining shapefile", geo_code)

            # Add specific fuel result
            rec.append(result_csv)

        # Add the modified record to the new shapefile
        w.records.append(rec)

    # Copy over the geometry without any changes
    w._shapes.extend(r.shapes())

    # Save as a new shapefile (or write over the old one)
    w.save(out_shape)
    logging.info("... finished writing shp")
    return
