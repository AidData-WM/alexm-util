#!/usr/bin/env python

#Import
from osgeo import ogr
from osgeo import osr
import sys, os
from optparse import OptionParser
import shutil
import ogr2ogr
import gdal
import subprocess

def main(argv):
    #Parse options
    parser = OptionParser()
    parser.add_option("-p", "--polygoninput", dest="polyInput",
                        help="Input shp", metavar="FILE")
    parser.add_option("-i", "--pointinput", dest="pointInput",
                        help="Input csv file path", metavar="FILE")
    parser.add_option("-x", "--longitude", dest="longitude", default='longitude',
                        help="CSV longitude header. Default is 'longitude'")
    parser.add_option("-y", "--latitude", dest="latitude", default='latitude',
                        help="CSV latitude header. Default is 'latitude'")
    (options, args) = parser.parse_args()
    basename = os.path.basename(options.pointInput)
    inputname, inputextension = os.path.splitext(basename)
    #Clean up
    try:
      shutil.rmtree("./tmp")
    except:
      print "No cleanup required... Continuing..."
    #Write DBF
    os.makedirs("./tmp")
    ogr2ogr.main(["","-f","ESRI Shapefile","./tmp",options.pointInput])
    #Write VRT
    print "Writing CSV VRT..."
    vrt = open('./tmp/'+inputname+'.vrt','w')
    vrt.write("<OGRVRTDataSource>\n")
    vrt.write("\t<OGRVRTLayer name='"+inputname+"'>\n")
    vrt.write("\t\t<SrcDataSource relativeToVRT='1'>./</SrcDataSource>\n")
    vrt.write("\t\t<GeometryType>wkbPoint</GeometryType>\n")
    vrt.write("\t\t<LayerSRS>WGS84</LayerSRS>\n")
    vrt.write("\t\t<GeometryField encoding='PointFromColumns' x='"+options.longitude+"' y='"+options.latitude+"'/>\n")
    vrt.write("\t</OGRVRTLayer>\n")
    vrt.write("</OGRVRTDataSource>")
    vrt.close()
    #Write SHP
    print "Converting to SHP..."
    ogr2ogr.main(["","-f","ESRI Shapefile","./tmp","./tmp/"+inputname+".vrt","-overwrite"])
    
    #Convex hull
    # Get a Layer
    print "Calculating convex hull..."
    inShapefile = "./tmp/"+inputname+".shp"
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()
    
    # Collect all Geometry
    geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
    for feature in inLayer:
       geomcol.AddGeometry(feature.GetGeometryRef())
    
    # Calculate convex hull
    convexhull = geomcol.ConvexHull()
    
    # Save extent to a new Shapefile
    outShapefile = "./tmp/convexhull.shp"
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    
    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
       outDriver.DeleteDataSource(outShapefile)
    
    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer("convexhull", geom_type=ogr.wkbPolygon)
    
    # Add an ID field
    idField = ogr.FieldDefn("id", ogr.OFTInteger)
    outLayer.CreateField(idField)
    
    # Create the feature and set values
    featureDefn = outLayer.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    feature.SetGeometry(convexhull)
    feature.SetField("id", 1)
    outLayer.CreateFeature(feature)
    
    # Close DataSource
    inDataSource.Destroy()
    
    #Clip poly SHP by data convex hull
    print "Clipping polygon SHP by convex hull..."
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    polyShapefile = options.polyInput
    pointShapefile = "./tmp/"+inputname+".shp"
    driver = ogr.GetDriverByName("ESRI Shapefile")
    polyDataSource = driver.Open(polyShapefile, 0)
    polyLayer = polyDataSource.GetLayer()
    clipData = driver.CreateDataSource("./tmp")
    clipLayer = clipData.CreateLayer("clip",spatialReference,ogr.wkbPolygon)
    polyLayer.Clip(outLayer,clipLayer)
    outDataSource.Destroy()
    pointDataSource = driver.Open(pointShapefile, 0)
    pointLayer = pointDataSource.GetLayer()
    field = ogr.FieldDefn("Density", ogr.OFTReal)
    clipLayer.CreateField(field)
    
    #Iterate over SHP features and calculate density
    print "Calculating point density..."
    for feature in clipLayer:
        geom = feature.GetGeometryRef()
        area = geom.Area()
        pointLayer.SetSpatialFilter(geom)
        count = pointLayer.GetFeatureCount()
        density = count/area
        print density
        feature.SetField("Density",density)
        clipLayer.SetFeature(feature)
        
    # Close DataSource
    polyDataSource.Destroy()
    pointDataSource.Destroy()
        

if __name__ == "__main__":
   main(sys.argv[1:])