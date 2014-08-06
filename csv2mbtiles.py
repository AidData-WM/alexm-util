#!/usr/bin/env python

#Import system
import sys, os
from optparse import OptionParser

#Import CSV reader
import csv

#Import GDAL libraries
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst
from struct import pack

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
   parser.add_option("-z", "--zoom", dest="zoom",
                     help="Zoom level in single quotes. E.g. '1-3'")
   (options, args) = parser.parse_args()
   inputname, inputextension = os.path.splitext(options.inputfile)
   #Prompt user for lat/long columns
   with open(options.inputfile, 'rb') as csvfile:
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
   vrt.write("\t\t<GeometryField encoding='PointFromColumns' x='"+longitude+"' y='"+latitude+"'/>\n")
   vrt.write("\t</OGRVRTLayer>\n")
   vrt.write("</OGRVRTDataSource>")
   vrt.close()
   #Write SHP
   ogr2ogr.main(["","-f","ESRI Shapefile","./tmp","./tmp/"+inputname+".vrt","-overwrite"])
   
   #Rasterize SHP inputs
   NoData_value=0
   pointsFile="./tmp/"+inputname+".shp"
   outFile="./tmp/"+inputname+".tif"
   samples = 10
   lines = 10
   color1 = '255 255 255' #white
   color2 = '255 0 0' #red
   
   # Open the data source and read in the extent
   driver = ogr.GetDriverByName('ESRI Shapefile')
   source_ds = driver.Open(pointsFile,0)
   source_layer = source_ds.GetLayer()
   x0, x1, y0, y1 = source_layer.GetExtent()
   
   #Main Grid process
   deltax = (x1 - x0) / samples  
   deltay = (y1 - y0) / lines
   maxDensity = 0
   minDensity = 10000000

   dsPoints = ogr.Open(pointsFile)
   if dsPoints is None:
      raise Exception('Could not open ' + pointsFile)
   
   pointsLayer = dsPoints.GetLayer()

   #Creating the output file

   driverName = "ESRI Shapefile"
   drv = ogr.GetDriverByName( driverName )
   
   srsQuery = osr.SpatialReference()
   srsQuery.ImportFromEPSG(4326)    
   srsArea = osr.SpatialReference()
   srsArea.ImportFromEPSG(900913)  

   transf = osr.CoordinateTransformation(srsQuery,srsArea)

   driverName = gdal.GetDriverByName( 'GTiff' )
   dsOut = driverName.Create( outFile, samples, lines, 1, gdal.GDT_Float32)
   #dsOut.SetProjection(srsPeticio.ExportToWkt())
   dsOut.SetGeoTransform([x0,deltax,0,y0,0,deltay])

   #Iterating all the pixels to write the raster values
   dataString = ''
   for j in range(0,lines):
      for i in range(0,samples):
         print "sample " + str(i) + " line " + str(j)
         px = x0 + deltax * i
         py = y0 + deltay * j
         #The pixel geometry must be created to execute the within method, and to calculate the actual area
         wkt = "POLYGON(("+str(px)+" "+str(py)+","+str(px + deltax)+" "+str(py)+","+str(px + deltax)+" "+str(py+deltay)+","+str(px)+" "+str(py+deltay)+","+str(px)+" "+str(py)+"))"
         
         geometry = ogr.CreateGeometryFromWkt(wkt)
         
         numCounts = 0.0
         pointsLayer.ResetReading()
         pointFeature = pointsLayer.GetNextFeature()
         
         #Iterating all the points
         while pointFeature:
             if pointFeature.GetGeometryRef().Within(geometry):
                 numCounts = numCounts + 1
             pointFeature = pointsLayer.GetNextFeature()
         
         geometryArea = geometry.Clone()
         geometryArea.Transform(transf)
         polygonArea = geometryArea.GetArea()/(1000000.0)
         density = numCounts/polygonArea
         if density>maxDensity:
            maxDensity = density
         if density<minDensity:
            minDensity=density
         dataString = dataString + pack('f',density)
   
   #Writing the raster
   band = dsOut.GetRasterBand(1)
   band.SetNoDataValue(NoData_value)
   band.WriteRaster( 0, 0, samples, lines, dataString )
   dsOut = None
   dsPoints = None

   #Write color relief txt
   colorTxt = open('./tmp/'+"color_"+inputname+'.txt','w')
   colorTxt.write(str(minDensity)+" "+color1+"\n")
   colorTxt.write(str(maxDensity)+" "+color2)
   colorTxt.close()
   
   #Color the raster
  
   
   
   #argv = gdal.GeneralCmdLineProcessor( ['./gdal2tiles.py','-z',zoom,'./tmp/'+inputname+'.tiff',inputname] )
   #if argv:
   #    gdal2tiles = GDAL2Tiles( argv[1:] )
   #    gdal2tiles.process()

if __name__ == "__main__":
   main(sys.argv[1:])
