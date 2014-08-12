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
from math import ceil

def main(argv):
    #Parse options
    parser = OptionParser()
    parser.add_option("-p", "--polygoninput", dest="polyInput", default="./tmp/grid.shp",
                        help="Input polygon SHP. Default is a grid measured by -l and -r", metavar="FILE")
    parser.add_option("-i", "--pointinput", dest="pointInput",
                        help="Input csv file path", metavar="FILE")
    parser.add_option("-x", "--longitude", dest="longitude", default='longitude',
                        help="CSV longitude header. Default is 'longitude'")
    parser.add_option("-y", "--latitude", dest="latitude", default='latitude',
                        help="CSV latitude header. Default is 'latitude'")
    parser.add_option("-z", "--zfield", dest="zfield", default=False,
                        help="CSV attribute header to aggregate on. Default is raw count")
    parser.add_option("-l", "--cols", dest="cols", default=0.5,
                        help="Fraction of longitude for grid if -p is not supplied. Default is 0.1")
    parser.add_option("-r", "--rows", dest="rows", default=0.5,
                        help="Fraction of latitude for grid if -p is not supplied. Default is 0.1")
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
    inConShapefile = "./tmp/"+inputname+".shp"
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inConDataSource = inDriver.Open(inConShapefile, 0)
    inConLayer = inConDataSource.GetLayer()
    
    # Collect all Geometry
    geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
    for feature in inConLayer:
       geomcol.AddGeometry(feature.GetGeometryRef())
    
    # Calculate convex hull
    convexhull = geomcol.ConvexHull()
    
    # Save extent to a new Shapefile
    outConShapefile = "./tmp/convexhull.shp"
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    
    # Remove output shapefile if it already exists
    if os.path.exists(outConShapefile):
       outDriver.DeleteDataSource(outConShapefile)
    
    # Create the output shapefile
    outConDataSource = outDriver.CreateDataSource(outConShapefile)
    outConLayer = outConDataSource.CreateLayer("convexhull", geom_type=ogr.wkbPolygon)
    
    # Add an ID field
    idField = ogr.FieldDefn("id", ogr.OFTInteger)
    outConLayer.CreateField(idField)
    
    # Create the feature and set values
    featureDefn = outConLayer.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    feature.SetGeometry(convexhull)
    feature.SetField("id", 1)
    outConLayer.CreateFeature(feature)
    
    # Close DataSource
    inConDataSource.Destroy()
    
    #Create grid
    print "Creating grid..."
    #Get extent
    xmin, xmax, ymin, ymax = outConLayer.GetExtent()
    # convert sys.argv to float
    xmin = float(xmin)
    xmax = float(xmax)
    ymin = float(ymin)
    ymax = float(ymax)
    gridWidth = float(options.cols)
    gridHeight = float(options.rows)

    # get rows
    rows = ceil((ymax-ymin)/gridHeight)
    # get columns
    cols = ceil((xmax-xmin)/gridWidth)

    # start grid cell envelope
    ringXleftOrigin = xmin
    ringXrightOrigin = xmin + gridWidth
    ringYtopOrigin = ymax
    ringYbottomOrigin = ymax-gridHeight

    # create output file
    outDriver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists('./tmp/grid.shp'):
        os.remove('./tmp/grid.shp')
    outDataSource = outDriver.CreateDataSource('./tmp/grid.shp')
    outLayer = outDataSource.CreateLayer('./tmp/grid.shp',geom_type=ogr.wkbPolygon )
    featureDefn = outLayer.GetLayerDefn()

    # create grid cells
    countcols = 0
    while countcols < cols:
        countcols += 1

        # reset envelope for rows
        ringYtop = ringYtopOrigin
        ringYbottom =ringYbottomOrigin
        countrows = 0

        while countrows < rows:
            countrows += 1
            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(ringXleftOrigin, ringYtop)
            ring.AddPoint(ringXrightOrigin, ringYtop)
            ring.AddPoint(ringXrightOrigin, ringYbottom)
            ring.AddPoint(ringXleftOrigin, ringYbottom)
            ring.AddPoint(ringXleftOrigin, ringYtop)
            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)

            # add new geom to layer
            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(poly)
            outLayer.CreateFeature(outFeature)
            outFeature.Destroy

            # new envelope for next poly
            ringYtop = ringYtop - gridHeight
            ringYbottom = ringYbottom - gridHeight

        # new envelope for next poly
        ringXleftOrigin = ringXleftOrigin + gridWidth
        ringXrightOrigin = ringXrightOrigin + gridWidth

    # Close DataSources
    outDataSource.Destroy()
    
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
    polyLayer.Clip(outConLayer,clipLayer)
    outConDataSource.Destroy()
    pointDataSource = driver.Open(pointShapefile, 0)
    pointLayer = pointDataSource.GetLayer()
    aField = ogr.FieldDefn("Area", ogr.OFTReal)
    cField = ogr.FieldDefn("Count", ogr.OFTReal)
    sField = ogr.FieldDefn("SumAttr", ogr.OFTReal)
    dField = ogr.FieldDefn("CountDens", ogr.OFTReal)
    tField = ogr.FieldDefn("AttrDens",ogr.OFTReal)
    clipLayer.CreateField(aField)
    clipLayer.CreateField(cField)
    clipLayer.CreateField(sField)
    clipLayer.CreateField(dField)
    clipLayer.CreateField(tField)
    
    #Iterate over SHP features
    print "Calculating point density..."
    for feature in clipLayer:
        geom = feature.GetGeometryRef()
        area = geom.Area()
        pointLayer.SetSpatialFilter(geom)
        count = pointLayer.GetFeatureCount()
        density = count/area
        print density
        pointLayer.ResetReading()
        sumattr=0
        if options.zfield:
            for point in pointLayer:
                attr = point.GetField(options.zfield)
                try:
                    sumattr+=float(attr)
                except:
                    print "Invalid attr"
            attrdensity=sumattr/area
        else:
            attrdensity=density
        feature.SetField("Area",area)
        feature.SetField("Count",count)
        feature.SetField("SumAttr",sumattr)
        feature.SetField("CountDens",density)
        feature.SetField("AttrDens",attrdensity)
        clipLayer.SetFeature(feature)
        
    # Close DataSource
    polyDataSource.Destroy()
    pointDataSource.Destroy()
        

if __name__ == "__main__":
   main(sys.argv[1:])