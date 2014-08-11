from osgeo import ogr
from osgeo import osr
from osgeo import gdal
from struct import pack
import sys

def density(pointsFile,outFile,x0,y0,x1,y1,samples,lines):
    
    deltax = (x1 - x0) / samples  
    deltay = (y1 - y0) / lines

    dsPoints = ogr.Open(pointsFile)
    if dsPoints is None:
       raise Exception('Could not open ' + pointsFile)
    
    pointsLayer = dsPoints.GetLayer()

    #Creating the output file

    driverName = "ESRI Shapefile"
    drv = ogr.GetDriverByName( driverName )
    
    srsPeticio = osr.SpatialReference()
    srsPeticio.ImportFromEPSG(4326)    
    srsProva = osr.SpatialReference()
    srsProva.ImportFromEPSG(900913)  

    transf = osr.CoordinateTransformation(srsPeticio,srsProva)

    driverName = gdal.GetDriverByName( 'GTiff' )
    dsOut = driverName.Create( outFile, samples, lines, 1, gdal.GDT_Float32)
    dsOut.SetProjection(srsPeticio.ExportToWkt())
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
        dataString = dataString + pack('f',density)
    
    #Writting the raster
    dsOut.GetRasterBand(1).WriteRaster( 0, 0, samples, lines, dataString ) 

    dsOut = None
    dsPoints = None
if __name__ == "__main__":
    points = sys.argv[1]
    outfile = sys.argv[2]
    x0=float(sys.argv[3])
    y0=float(sys.argv[4])
    x1=float(sys.argv[5])
    y1=float(sys.argv[6])
    samples=int(sys.argv[7])
    lines=int(sys.argv[8])

  
    density(points,outfile,x0,y0,x1,y1,samples,lines)

