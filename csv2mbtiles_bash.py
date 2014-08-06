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
   parser.add_option("-o", "--output", dest="outputfile",
                     help="Output mbtiles file path", metavar="FILE")
   parser.add_option("-m", "--zoom", dest="zoom",
                     help="Zoom level in single quotes. E.g. '1-3'")
   parser.add_option("-c", "--color1", dest="color1",
                     help="RGB color for lowest level, E.g. '0 0 255' for blue")
   parser.add_option("-d", "--color2", dest="color2",
                     help="RGB color for highest level, E.g. '255 0 0' for red")
   parser.add_option("-r", "--rows", dest="rows",
                     help="Grid rows")
   parser.add_option("-l", "--cols", dest="cols",
                     help="Grid columns")
   parser.add_option("-x", "--longitude", dest="longitude",
                     help="CSV longitude header")
   parser.add_option("-y", "--latitude", dest="latitude",
                     help="CSV latitude header")
   parser.add_option("-z", "--zfield", dest="zfield",
                     help="CSV z-field header")
   (options, args) = parser.parse_args()
   inputname, inputextension = os.path.splitext(options.inputfile)
   #Clean up
   try:
      shutil.rmtree("./tmp")
   except:
      print "No cleanup required... Continuing..."
   #Write DBF
   os.makedirs("./tmp")
   ogr2ogr.main(["","-f","ESRI Shapefile","./tmp",options.inputfile])
   #Write VRT
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
   ogr2ogr.main(["","-f","ESRI Shapefile","./tmp","./tmp/"+inputname+".vrt","-overwrite"])
   
   #Rasterize SHP
   print "Rasterizing input..."
   rasterize = subprocess.Popen(["gdal_grid","-outsize",str(options.rows),str(options.cols),"-a","invdist:power=2.0:smoothing=1.0","-zfield",options.zfield,"./tmp/"+inputname+".shp","-l",inputname,"./tmp/"+inputname+".tif"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   Routput = rasterize.communicate()[0]
   print Routput
   
   #Warp for transparency and size
   print "Warping raster..."
   warp = subprocess.Popen(["gdalwarp","-co","compress=deflate", "-co", "tiled=yes", "-r", "lanczos", "-cutline", "./afr/africa_boundary.shp", "-srcnodata", "0", "-dstnodata", "0", "./tmp/"+inputname+".tif", "./tmp/"+inputname+"_idw.tif"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   Woutput = warp.communicate()[0]
   print Woutput
   
   #Write color relief txt
   
   #Color the raster
  
   
   
   #argv = gdal.GeneralCmdLineProcessor( ['./gdal2tiles.py','-z',zoom,'./tmp/'+inputname+'.tiff',inputname] )
   #if argv:
   #    gdal2tiles = GDAL2Tiles( argv[1:] )
   #    gdal2tiles.process()

if __name__ == "__main__":
   main(sys.argv[1:])
