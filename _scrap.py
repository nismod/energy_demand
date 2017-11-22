
import shapely
from shapely.geometry import Point

from pyproj import Proj, transform

pnt = {
    'type': 'Feature',
    'geometry': {'type': 'Point', 'coordinates': (448106.78026545397, 530697.8232646097)},
    'properties': {'name': 'E06000001'}}

a = Point(pnt['geometry']['coordinates'])
a.name = pnt['properties']['name']

# OSGB_1936_British_National_Grid
inProj = Proj(init='epsg:27700')

# Transverse_Mercator
outProj = Proj(init='epsg:2157')

#WGS 84 projection #http://spatialreference.org/ref/epsg/wgs-84/
outProj = Proj(init='epsg:4326') 

x1,y1 = a.coords.xy
x2, y2 = transform(inProj, outProj, x1, y1)
print("-.....")
print(x2,y2)
print(".")

print(a.coords)
print(a.name)
print(a.coords.xy)
print(a)

'''

 # ----------------------
        #import shapely
        #from shapely.geometry import Point
        data['reg_coord'] = self.get_long_lat_decimal_degrees(reg_centroids)
        data['reg_coord'] = {}
        for centroid in reg_centroids:
            #pnt_centroid = Point(centroid['geometry']['coordinates'])
            #pnt_centroid.name = centroid['properties']['name']

            # OSGB_1936_British_National_Grid
            inProj = Proj(init='epsg:27700')

            #WGS 84 projection #http://spatialreference.org/ref/epsg/wgs-84/
            outProj = Proj(init='epsg:4326') 

            # Convert to decimal degrees
            long_dd, lat_dd = transform(
                inProj,
                outProj,
                centroid['geometry']['coordinates'][0], #longitude
                centroid['geometry']['coordinates'][1]) #latitude

            data['reg_coord'][centroid['properties']['name']] = {}
            data['reg_coord'][centroid['properties']['name']]['longitude'] = centroid['geometry']['coordinates'][0] #TODO: CHECK
            data['reg_coord'][centroid['properties']['name']]['latidue'] = centroid['geometry']['coordinates'][1]


'''
'''
import ogr, osr

driver = ogr.GetDriverByName('ESRI Shapefile')

shp = driver.Open('testpoint.shp', 0)
lyr = shp.GetLayer()

feat = lyr.GetNextFeature()
geom = feat.GetGeometryRef()

# Transform from Web Mercator to WGS84
sourceSR = lyr.GetSpatialRef()
targetSR = osr.SpatialReference()
targetSR.ImportFromEPSG(4326) # WGS84
coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
geom.Transform(coordTrans)

x = geom.GetX() 
y = geom.GetY() 

print x,y
'''