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
import gdal2tiles
from gdal2tiles import Configuration

#Import OGR2OGR
import ogr2ogr

def main(argv):
    #Get input and output from command line args
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Input SHP file path", metavar="FILE")
    parser.add_option("-m", "--zoom", dest="zoom", default="1-3",
                      help="Zoom level in single quotes. Default is '1-3'")
    parser.add_option("-c", "--color1", dest="color1", default='255 255 0',
                      help="RGB color for lowest level, Default '255 255 0' for yellow")
    parser.add_option("-d", "--color2", dest="color2", default='255 0 0',
                      help="RGB color for highest level, Default is '255 0 0' for red")
    parser.add_option("-n", "--nearest", dest="nearest", default=False,
                      help="If true, raster values will be assigned to nearest step, rather than continuous. Default is continuous")
    parser.add_option("-r", "--rows", dest="rows", default=0.1,
                      help="Raster y resolution. Default is 0.1 for a quick sample")
    parser.add_option("-l", "--cols", dest="cols", default=0.1,
                      help="Raster y resolution. Default is 0.1 for a quick sample")
    parser.add_option("-z", "--zfield", dest="zfield",
                      help="CSV z-field header")
    parser.add_option("-o", "--output", dest="outfile", default="./tmp/output.mbtiles", metavar="FILE",
                      help="Output file path for MBtiles. Default is ./tmp/output.mbtiles")
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
    #Rasterize SHP
    print "Rasterizing..."
    rasterize = subprocess.Popen(["gdal_rasterize","-a",options.zfield,"-tr",str(options.rows),str(options.cols),"-l",inputname,options.inputfile,"./tmp/raster.tif"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    rOutput = rasterize.communicate()[0]
    print rOutput
    
    #Write color relief txt
    print "Writing color relief txt..."
    #Find min and max
    src_ds = gdal.Open("./tmp/raster.tif")
    srcband = src_ds.GetRasterBand(1)
    (tifMin, tifMax) = srcband.ComputeRasterMinMax()
    (tifMean, tifStd) = srcband.ComputeBandStats()
    colorTxt = open("./tmp/"+"color.txt","w")
    colorTxt.write(str(tifMin)+" "+options.color1+" \n")
    percent1R = str(((int(options.color1.split()[0])*(99))+(int(options.color2.split()[0])*1))/100)
    percent1G = str(((int(options.color1.split()[1])*(99))+(int(options.color2.split()[1])*1))/100)
    percent1B = str(((int(options.color1.split()[2])*(99))+(int(options.color2.split()[2])*1))/100)
    percent2R = str(((int(options.color1.split()[0])*(98))+(int(options.color2.split()[0])*2))/100)
    percent2G = str(((int(options.color1.split()[1])*(98))+(int(options.color2.split()[1])*2))/100)
    percent2B = str(((int(options.color1.split()[2])*(98))+(int(options.color2.split()[2])*2))/100)
    percent16R = str(((int(options.color1.split()[0])*(84))+(int(options.color2.split()[0])*16))/100)
    percent16G = str(((int(options.color1.split()[1])*(84))+(int(options.color2.split()[1])*16))/100)
    percent16B = str(((int(options.color1.split()[2])*(84))+(int(options.color2.split()[2])*16))/100)
    percent50R = str(((int(options.color1.split()[0]))+(int(options.color2.split()[0])))/2)
    percent50G = str(((int(options.color1.split()[1]))+(int(options.color2.split()[1])))/2)
    percent50B = str(((int(options.color1.split()[2]))+(int(options.color2.split()[2])))/2)
    percent84R = str(((int(options.color1.split()[0])*(16))+(int(options.color2.split()[0])*84))/100)
    percent84G = str(((int(options.color1.split()[1])*(16))+(int(options.color2.split()[1])*84))/100)
    percent84B = str(((int(options.color1.split()[2])*(16))+(int(options.color2.split()[2])*84))/100)
    percent98R = str(((int(options.color1.split()[0])*(2))+(int(options.color2.split()[0])*98))/100)
    percent98G = str(((int(options.color1.split()[1])*(2))+(int(options.color2.split()[1])*98))/100)
    percent98B = str(((int(options.color1.split()[2])*(2))+(int(options.color2.split()[2])*98))/100)
    percent99R = str(((int(options.color1.split()[0])*(1))+(int(options.color2.split()[0])*99))/100)
    percent99G = str(((int(options.color1.split()[1])*(1))+(int(options.color2.split()[1])*99))/100)
    percent99B = str(((int(options.color1.split()[2])*(1))+(int(options.color2.split()[2])*99))/100)
    colorTxt.write(str(tifMean-(3*tifStd))+" "+percent1R+" "+percent1G+" "+percent1B+" "+"\n")
    colorTxt.write(str(tifMean-(2*tifStd))+" "+percent2R+" "+percent2G+" "+percent2B+" "+"\n")
    colorTxt.write(str(tifMean-(tifStd))+" "+percent16R+" "+percent16G+" "+percent16B+" "+"\n")
    colorTxt.write(str(tifMean)+" "+percent50R+" "+percent50G+" "+percent50B+" "+"\n")
    colorTxt.write(str(tifMean+(tifStd))+" "+percent84R+" "+percent84G+" "+percent84B+" "+"\n")
    colorTxt.write(str(tifMean+(2*tifStd))+" "+percent98R+" "+percent98G+" "+percent98B+" "+"\n")
    colorTxt.write(str(tifMean+(3*tifStd))+" "+percent99R+" "+percent99G+" "+percent99B+" "+"\n")
    colorTxt.write(str(tifMax)+" "+options.color2)
    colorTxt.close()
    
    #Color the raster
    print "Colorizing raster..."
    if options.nearest:
       colorize = subprocess.Popen(["gdaldem", "color-relief","./tmp/raster.tif", "./tmp/color.txt", "./tmp/raster_color.tif","-nearest_color_entry","-alpha"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    else:
       colorize = subprocess.Popen(["gdaldem", "color-relief","./tmp/raster.tif", "./tmp/color.txt", "./tmp/raster_color.tif","-alpha"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    cOutput = colorize.communicate()[0]
    print cOutput
    
    #Warp for compression
    print "Warping raster..."
    warp = subprocess.Popen(["gdalwarp","-co","compress=deflate", "-co", "tiled=yes", "-r", "lanczos", "-srcnodata", options.color1, "./tmp/raster_color.tif", "./tmp/raster_final.tif"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    wOutput = warp.communicate()[0]
    print wOutput
    
    #Draw VRT for parallel gdal2tiles
    print "Building tile VRT..."
    buildVrt = subprocess.Popen(["gdalbuildvrt","./tmp/tiles.vrt", "./tmp/raster_final.tif"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    vOutput = buildVrt.communicate()[0]
    print vOutput
    
    #Draw png tiles
    print "Drawing tiles..."
    argv = gdal.GeneralCmdLineProcessor( ['./gdal2tiles.py','-z',options.zoom,'./tmp/tiles.vrt','./tmp/tiles'] )
    if argv:
       c1 = Configuration(argv[1:])
       tile=c1.create_tile()
       gdal2tiles.process(c1,tile)
        
    #Create MBtiles
    print "Generating MBtiles file..."
    mbtiles = subprocess.Popen(["mb-util","./tmp/tiles",options.outfile,"--scheme","tms"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    mOutput = mbtiles.communicate()[0]
    print mOutput
    print "Done."

if __name__ == "__main__":
   main(sys.argv[1:])
