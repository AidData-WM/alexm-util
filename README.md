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
1. OSGEO
2. gdal2tiles.py (included)
3. ogr2ogr.py (included)

####Use
Usage:

Options:
  -h, --help            show this help message and exit
  -i FILE, --input=FILE
                        Input csv file path
  -a ALG, --alg=ALG     GDAL grid algorithm. Default is
                        'invdist:power=2.0:smoothing=1.0'
  -m ZOOM, --zoom=ZOOM  Zoom level in single quotes. Default is '1-3'
  -c COLOR1, --color1=COLOR1
                        RGB color for lowest level, Default '255 255 0' for
                        yellow
  -d COLOR2, --color2=COLOR2
                        RGB color for highest level, Default is '255 0 0' for
                        red
  -s STEPS, --steps=STEPS
                        Number of steps in the color relief. Default is 25
  -r ROWS, --rows=ROWS  Grid rows. Default is 1000
  -l COLS, --cols=COLS  Grid columns. Default is 1000
  -x LONGITUDE, --longitude=LONGITUDE
                        CSV longitude header. Default is 'longitude'
  -y LATITUDE, --latitude=LATITUDE
                        CSV latitude header. Default is 'latitude'
  -z ZFIELD, --zfield=ZFIELD
                        CSV z-field header

With all the default options explicitly declared, the command looks like:
```
./csv2mbtiles.py -i SCAD.csv -a 'invdist:power=2.0:smoothing=1.0' -m '1-3' -c '255 255 0' -d '255 0 0' -s 25 -r 1000 -l 1000 -x 'longitude' -y 'latitude' -z 'npart'
```

Or with the bare minimum of arguments (only creates sample, CSV must contain columns 'latitude' and 'longitude'):
```
./csv2mbtiles.py -i SCAD.csv -z 'npart'
```
