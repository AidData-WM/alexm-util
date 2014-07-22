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