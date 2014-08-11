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
    parser.add_option("-c", "--color1", dest="color1", default='255 255 0',
                     help="RGB color for lowest level, Default '255 255 0' for yellow")
    parser.add_option("-d", "--color2", dest="color2", default='255 0 0',
                      help="RGB color for highest level, Default is '255 0 0' for red")
    parser.add_option("-n", "--nearest", dest="nearest", default=False,
                      help="If true, raster values will be assigned to nearest step, rather than continuous. Default is continuous. To be used in conjunction with -s")
    parser.add_option("-s", "--steps", dest="steps", default=10,
                      help="Number of steps in the color relief if specified and -n is 'True'. Default is 10")
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
    
    #Rasterize SHP
    print "Rasterizing..."
    
    # Define pixel_size and NoData value of new raster
    pixel_size = 0.002
    NoData_value = 0
    
    # Filename of the raster Tiff that will be created
    raster_fn = './tmp/clip.tif'
    
    # Open the data source and read in the extent
    x_min, x_max, y_min, y_max = clipLayer.GetExtent()
    
    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    
    # Close DataSource
    polyDataSource.Destroy()
    pointDataSource.Destroy()
    
    #Rasterize
    rasterize = subprocess.Popen(["gdal_rasterize","-b","1","-a", "Density", "-l","clip","-tr",str(x_res),str(y_res),"./tmp/clip.shp", "./tmp/clip.tif"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    rOutput = rasterize.communicate()[0]
    print rOutput
    
    #Write color relief txt
    print "Writing color relief txt..."
    steps = int(options.steps)
    colorTxt = open("./tmp/"+"color.txt","w")
    colorTxt.write("0% "+options.color1+"\n")
    percentStep = 100/steps
    for step in range(1,steps):
      percentR = str(((int(options.color1.split()[0])*(steps-step))+(int(options.color2.split()[0])*step))/steps)
      percentG = str(((int(options.color1.split()[1])*(steps-step))+(int(options.color2.split()[1])*step))/steps)
      percentB = str(((int(options.color1.split()[2])*(steps-step))+(int(options.color2.split()[2])*step))/steps)
      colorTxt.write(str(percentStep*step)+"% "+percentR+" "+percentG+" "+percentB+" "+"\n")
    colorTxt.write("100% "+options.color2)
    colorTxt.close()
        

if __name__ == "__main__":
   main(sys.argv[1:])