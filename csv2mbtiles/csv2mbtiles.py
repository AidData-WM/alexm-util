#!/usr/bin/env python

#Import system
import sys, os
from optparse import OptionParser
import shutil
import subprocess

#Import GDAL libraries
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst

#Import GDAL2Tiles
from gdal2tiles import GDAL2Tiles

#Import OGR2OGR
import ogr2ogr

def main(argv):
   #Get input and output from command line args
   parser = OptionParser()
   parser.add_option("-i", "--input", dest="inputfile",
                     help="Input csv file path", metavar="FILE")
   parser.add_option("-a", "--alg", dest="alg", default="invdist:power=2.0:smoothing=1.0",
                     help="GDAL grid algorithm. Default is 'invdist:power=2.0:smoothing=1.0'")
   parser.add_option("-m", "--zoom", dest="zoom", default="1-3",
                     help="Zoom level in single quotes. Default is '1-3'")
   parser.add_option("-c", "--color1", dest="color1", default='255 255 0',
                     help="RGB color for lowest level, Default '255 255 0' for yellow")
   parser.add_option("-d", "--color2", dest="color2", default='255 0 0',
                     help="RGB color for highest level, Default is '255 0 0' for red")
   parser.add_option("-s", "--steps", dest="steps", default=25,
                     help="Number of steps in the color relief. Default is 25")
   parser.add_option("-r", "--rows", dest="rows", default=1000,
                     help="Grid rows. Default is 1000")
   parser.add_option("-l", "--cols", dest="cols", default=1000,
                     help="Grid columns. Default is 1000")
   parser.add_option("-x", "--longitude", dest="longitude", default='longitude',
                     help="CSV longitude header. Default is 'longitude'")
   parser.add_option("-y", "--latitude", dest="latitude", default='latitude',
                     help="CSV latitude header. Default is 'latitude'")
   parser.add_option("-z", "--zfield", dest="zfield",
                     help="CSV z-field header")
   (options, args) = parser.parse_args()
   basename = os.path.basename(options.inputfile)
   inputname, inputextension = os.path.splitext(basename)
   #Clean up
   try:
      shutil.rmtree("./tmp")
   except:
      print "No cleanup required... Continuing..."
   #Write DBF
   os.makedirs("./tmp")
   ogr2ogr.main(["","-f","ESRI Shapefile","./tmp",options.inputfile])
   #Write VRT
   print "Writing VRT..."
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
   
   #Rasterize SHP
   print "Rasterizing..."
   rasterize = subprocess.Popen(["gdal_grid","-outsize",str(options.rows),str(options.cols),"-a","invdist:power=2.0:smoothing=1.0","-zfield",options.zfield,"./tmp/"+inputname+".shp","-l",inputname,"./tmp/"+inputname+".tif"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   rOutput = rasterize.communicate()[0]
   print rOutput
   
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
   outDataSource.Destroy()
   
   #Write color relief txt
   print "Writing color relief txt..."
   #Find min and max
   #src_ds = gdal.Open("./tmp/"+inputname+".tif")
   #srcband = src_ds.GetRasterBand(1)
   #(tifMin, tifMax) = srcband.ComputeRasterMinMax()
   steps = int(options.steps)
   colorTxt = open("./tmp/"+"color.txt","w")
   colorTxt.write("0 255 255 255 0\n")
   colorTxt.write("0% "+options.color1+"\n")
   percentStep = 100/steps
   for step in range(1,steps):
      percentR = str(((int(options.color1.split()[0])*(steps-step))+(int(options.color2.split()[0])*step))/steps)
      percentG = str(((int(options.color1.split()[1])*(steps-step))+(int(options.color2.split()[1])*step))/steps)
      percentB = str(((int(options.color1.split()[2])*(steps-step))+(int(options.color2.split()[2])*step))/steps)
      colorTxt.write(str(percentStep*step)+"% "+percentR+" "+percentG+" "+percentB+" "+"\n")
   colorTxt.write("100% "+options.color2)
   colorTxt.close()
   
   #Color the raster
   print "Colorizing raster..."
   colorize = subprocess.Popen(["gdaldem", "color-relief","./tmp/"+inputname+".tif", "./tmp/color.txt", "./tmp/"+inputname+"_color.tif", "-nearest_color_entry"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   cOutput = colorize.communicate()[0]
   print cOutput
   
   #Warp for compression and clip to convex hull
   print "Warping raster..."
   warp = subprocess.Popen(["gdalwarp","-co","compress=deflate", "-co", "tiled=yes", "-r", "lanczos", "-cutline", "./tmp/convexhull.shp", "-dstnodata", "0", "./tmp/"+inputname+"_color.tif", "./tmp/"+inputname+"_final.tif"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   wOutput = warp.communicate()[0]
   print wOutput
   
   #Draw png tiles
   print "Drawing tiles..."
   argv = gdal.GeneralCmdLineProcessor( ['./gdal2tiles.py','-z',options.zoom,'./tmp/'+inputname+'_final.tif','./tmp/'+inputname] )
   if argv:
       gdal2tiles = GDAL2Tiles( argv[1:] )
       gdal2tiles.process()
       
   #Create MBtiles
   print "Generating MBtiles file..."
   mbtiles = subprocess.Popen(["mb-util","./tmp/"+inputname,inputname+".mbtiles","--scheme","tms"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   mOutput = mbtiles.communicate()[0]
   print mOutput
   print "Done."

if __name__ == "__main__":
   main(sys.argv[1:])
