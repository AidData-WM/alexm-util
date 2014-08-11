from osgeo import ogr
from osgeo import osr
import sys


def density(pointsFile,polygonsFile,outFile):
    #Opening the input files
    dsPolygons = ogr.Open(polygonsFile)
    if dsPolygons is None:
       raise Exception('Could not open ' + pointsFile)
    dsPoints = ogr.Open(pointsFile)
    if dsPoints is None:
       raise Exception('Could not open ' + pointsFile)
    
    polygonsLayer = dsPolygons.GetLayer()
    pointsLayer = dsPoints.GetLayer()


    #Creating the output file

    driverName = "ESRI Shapefile"
    drv = ogr.GetDriverByName( driverName )
    dsOut = drv.CreateDataSource( outFile )  
    outLayer = dsOut.CreateLayer('DENSITY', None, ogr.wkbPolygon)  
    field = ogr.FieldDefn( "Density", ogr.OFTReal )
    outLayer.CreateField ( field )
    field = ogr.FieldDefn( "Name", ogr.OFTString )
    outLayer.CreateField ( field )
    field = ogr.FieldDefn( "State_name", ogr.OFTString )
    outLayer.CreateField ( field )
    
    #Preparing the coordinate transformation
    srsPeticio = osr.SpatialReference()
    srsPeticio.ImportFromEPSG(4326)    
    srsProva = osr.SpatialReference()
    srsProva.ImportFromEPSG(900913)  

    transf = osr.CoordinateTransformation(srsPeticio,srsProva)

    #Iterating all the polygons
    polygonFeature = polygonsLayer.GetNextFeature()
    k=0
    while polygonFeature:
        k = k + 1
        print  "processing " + polygonFeature.GetField("NAME") + " ("+polygonFeature.GetField("STATE_NAME")+") - " + str(k) + " of " + str(polygonsLayer.GetFeatureCount())
         
        geometry = polygonFeature.GetGeometryRef()
        numCounts = 0.0
        pointsLayer.ResetReading()
        pointFeature = pointsLayer.GetNextFeature()
        #Iterating all the points
        while pointFeature:
            if pointFeature.GetGeometryRef().Within(geometry):
                numCounts = numCounts + 1
            pointFeature = pointsLayer.GetNextFeature()
        
        #Calculating the actual area
        geometryArea = geometry.Clone()
        geometryArea.Transform(transf)
        polygonArea = geometryArea.GetArea()/(1000000.0)
        density = numCounts/polygonArea

        #Writting the fields in the output layer
        feature = ogr.Feature( outLayer.GetLayerDefn())
        feature.SetField( "Density",feature.GetFID, density )
        feature.SetField( "Name", polygonFeature.GetField("NAME") )
        feature.SetField( "State_name", polygonFeature.GetField("STATE_NAME") )

        feature.SetGeometry(geometry)
        outLayer.CreateFeature(feature)        

        polygonFeature = polygonsLayer.GetNextFeature()

    dsOut = None
    dsPolygons = None
    dsPoints = None


if __name__ == "__main__":
    points = sys.argv[1]
    polygons = sys.argv[2]
    outfile = sys.argv[3]

    density(points,polygons,outfile)

