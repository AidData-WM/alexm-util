AlexM-Util
==========

Alex Miller's utilities and scratch code

##Utilities

###1. getLERN.js
A node Javascript web scraper for http://www.lern.ushahidi.com/

####Dependencies
1. Request - https://www.npmjs.org/package/request
2. Cheerio - https://www.npmjs.org/package/cheerio
3. WGS84-Util - https://www.npmjs.org/package/wgs84-util

####Use
To run, change your working directory to where you wish to save the LERN geoJSON and then:

```
node getLERN.js
```

###2. getUSAID.js
A node Javascript web scraper for http://portfolio.usaid.gov/

####Dependencies
1. Request - https://www.npmjs.org/package/request
2. Cheerio - https://www.npmjs.org/package/cheerio

####Use
To run, change your working directory to where you wish to save the USAID JSON and then:

```
node getUSAID.js
```

###3. convertUSAID.js
A node Javascript CSV converter for the output from getUSAID.js

####Dependencies
1. To-CSV - https://www.npmjs.org/package/to-csv
2. String - https://www.npmjs.org/package/string

####Use
To run, change your working directory to where USAID.js is saved and then:

```
node convertUSAID.js
```

###4. scratch_train.js and scratch_classify.js
Playing around with building a classifier in node

####Dependencies
1. CSV@0.3.7 - https://www.npmjs.org/package/csv
2. Natural - https://www.npmjs.org/package/natural
3. Stopwords - https://www.npmjs.org/package/stopwords

####Use
To run, change your working directory to where train_short.csv is saved and then:

```
node scratch_train.js
node scratch_classify.js "Training refugees in sustainable agriculture methodology"
```

###5. csv2mbtiles.py
CSV to mbtiles converter utilizing Albert's bash script. Converts point data to grid.

####Dependencies
1. Python
2. OSGEO
3. multi-core gdal2tiles.py (included)
4. ogr2ogr.py (included)
5. gdal_grid installed and accessable in bash by the command 'gdal_grid'
6. gdaldem installed and accessable in bash by the command 'gdaldem'
7. gdalwarp installed and accessable in bash by the command 'gdalwarp'
8. gdalbuildvrt installed and accessable in bash by the command 'gdalbuildvrt'
9. mb-util installed and accessable in bash by the command 'mb-util'

####Use
First, make sure that there is nothing in ./tmp that you want to save; the script uses this path and will overwrite whatever you have saved there. Second, ensure that you have write permissions for the folder from which you're running the script.

Help:
```
./csv2mbtiles.py -h
```

With all the default options explicitly declared, the command looks like:
```
./csv2mbtiles.py -i SCAD.csv -a 'invdist:power=2.0:smoothing=1.0' -m '1-3' -c '255 255 0' -d '255 0 0' -s 10 -r 1000 -l 1000 -x 'longitude' -y 'latitude' -z 'npart' -p '.tmp/convexhull.shp'
```

Also included is an example CSV and shapefile, to create an mbtile clipped to the continent of Africa, run:
```
./csv2mbtiles.py -i SCAD.csv -z 'npart' -p ./afr/africa_boundary.shp
```

Or with the bare minimum of arguments (only creates sample, CSV must contain columns 'latitude' and 'longitude'):
```
./csv2mbtiles.py -i SCAD.csv -z 'npart'
```

###6. attributes2density.py
A density field calculator that takes a CSV (and optionally a shapefile), and returns a SHP.

####Dependencies
1. Python
2. OSGEO
3. ogr2ogr.py (included)

####Use
First, make sure that there is nothing in ./tmp that you want to save; the script uses this path and will overwrite whatever you have saved there. Second, ensure that you have write permissions for the folder from which you're running the script.

Help:
```
./attributes2density.py -h
```

To create a density grid based on aggregating the field 'npart' (with latitude and longitude fields named 'latitude' and 'longitude'):
```
./attributes2density.py -i SCAD.csv -z npart
```

To create a density map based on an ADM2 shapefile and raw point counts (with latitude and longitude fields named 'latitude' and 'longitude'):
```
./attributes2density.py -i SCAD.csv -p ADM2.shp
```

###7. attributes2density_multi.py
A distributed density field calculator that takes a CSV (and optionally a shapefile), and returns a SHP.

####Dependencies
1. Python
2. OSGEO
3. ogr2ogr.py (included)

####Use
First, make sure that there is nothing in ./tmp that you want to save; the script uses this path and will overwrite whatever you have saved there. Second, ensure that you have write permissions for the folder from which you're running the script. Third, don't try and keyboard interrupt the script... This makes the computer mad. If you need to kill it, I recommend first opening it in a Screen session and then using CTRL+a and k to kill the whole window.

Help:
```
./attributes2density_multi.py -h
```

To use all CPUs to create a density grid based on aggregating the field 'npart' (with latitude and longitude fields named 'latitude' and 'longitude'):
```
./attributes2density_multi.py -i SCAD.csv -z npart
```

To use one CPU create a density map based on an ADM2 shapefile and raw point counts (with latitude and longitude fields named 'latitude' and 'longitude'):
```
./attributes2density_multi.py -i SCAD.csv -p ADM2.shp -c 1
```