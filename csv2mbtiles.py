#!/usr/bin/env python

#Import system
import sys, getopt, os

#Import CSV reader
import csv

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
   inputfile = ''
   outputfile = ''
   zoom = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:z:",["ifile=","ofile=", "zlevel="])
   except getopt.GetoptError:
      print 'test.py -i <inputfile> -o <outputfile> -z <zoom>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputfile> -o <outputfile> -z <zoom>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
         inputname, inputextension = os.path.splitext(inputfile)
      elif opt in ("-o", "--ofile"):
         outputfile = arg
      elif opt in ("-z", "--zlevel"):
         zoom = arg
    #Prompt user for lat/long columns
   with open(inputfile, 'rb') as csvfile:
    reader = csv.reader(csvfile,delimiter=',', quotechar='"')
    headers = reader.next()
    for item in enumerate(headers):
        print "[%d] %s" % item
    try:
        idx = int(raw_input("Choose latitude column number: "))
    except ValueError:
        print "Please type a number."
    try:
        latitude = headers[idx]
    except IndexError:
        print "Try a number in range next time."
    try:
        idy = int(raw_input("Choose longitude column number: "))
    except ValueError:
        print "Please type a number."
    try:
        longitude = headers[idy]
    except IndexError:
        print "Try a number in range next time."
    #Write VRT
    os.makedirs("./tmp")
    ogr2ogr.main(["","-f","ESRI Shapefile","./tmp",inputfile])
    vrt = open('./tmp/'+inputname+'.vrt','w')
    vrt.write("<OGRVRTDataSource>\n")
    vrt.write("\t<OGRVRTLayer name='"+inputname+"'>\n")
    vrt.write("\t\t<SrcDataSource relativeToVRT='1'>./</SrcDataSource>\n")
    vrt.write("\t\t<GeometryType>wkbPoint</GeometryType>\n")
    vrt.write("\t\t<LayerSRS>WGS84</LayerSRS>\n")
    vrt.write("\t\t<GeometryField encoding='PointFromColumns' x='"+longitude+"' y='"+latitude+"'/>\n")
    vrt.write("\t</OGRVRTLayer>\n")
    vrt.write("</OGRVRTDataSource>")
    vrt.close()
    ogr2ogr.main(["","-f","ESRI Shapefile","./tmp","./tmp/"+inputname+".vrt","-overwrite"])
    
    #argv = gdal.GeneralCmdLineProcessor( ['./gdal2tiles.py','-z',zoom,'./tmp/'+inputname+'.tiff',inputname] )
    #if argv:
    #    gdal2tiles = GDAL2Tiles( argv[1:] )
    #    gdal2tiles.process()

if __name__ == "__main__":
   main(sys.argv[1:])
