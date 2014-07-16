var request = require('request');
var cheerio = require('cheerio');
var fs = require('fs');
var wgs84 = require('wgs84-util');
var LERNgeoJSON={};
var uniqueObj = {};
LERNgeoJSON.type = "FeatureCollection";
LERNgeoJSON.features = [];
console.log("Pulling primary data...");
request('http://www.lern.ushahidi.com/json/cluster?z=14',parseCallback);
function parseCallback(e,r,b){
	var data = JSON.parse(b),
		LERN = [];
	for(var i = 0; i<data.features.length;i++){
	        var obj = {},
	        record = data.features[i],
	        url = record.properties.link,
	        lat = record.geometry.coordinates[1],
	        lng = record.geometry.coordinates[0],
	        count = record.properties.count;
	        obj.url = url;
	        obj.lat = lat;
	        obj.lng = lng;
	        obj.count = count;
		LERN.push(obj);
	};
	requestURLs(LERN);
};

function requestURLs(data){
	console.log("Redirecting data URLs to parsers...");
	for(var i = 0;i<data.length;i++){
		if(data[i].count==1){
                        process.stdout.write(".");
			request(data[i].url,parseOne);
		}else{
			request(data[i].url,parseMany);
		};
	};
};

function parseOne(e,r,b){
	var obj = {};
	var $ = cheerio.load(b,{normalizeWhitespace:true});
	obj.title = $('h1.report-title').text().trim();
	obj.date = new Date(Date.parse($('span.r_date').text()));
	obj.geoname = $('span.r_location').text().trim();
	obj.categories = [];
	if ($('span.r_cat-box').length>0) {
		var cats = $('span.r_cat-box').parent();
		for(var i = 0;i<cats.length;i++){
			obj.categories.push($(cats[i]).text().trim())
		};
	};
	obj.group = $('div.report-category-list div a').text().trim();
	var coordStart = $('div.report-category-list').text().indexOf('UTM Zone');
	var coordEnd = $('div.report-category-list').text().indexOf('Group')>-1?$('div.report-category-list').text().indexOf('Group'):$('div.report-category-list').text().length
	obj.coord = $('div.report-category-list').text().substr(coordStart,coordEnd-coordStart).trim();
	var descStart = $('div.report-description-text').text().indexOf('Description') + 11;
	var descEnd = $('div.report-description-text').text().indexOf('Credibility');
	obj.description = $('div.report-description-text').text().substr(descStart,descEnd-descStart).trim();
	var credStart = $('div.report-description-text').text().indexOf('Credibility:')+13;
	obj.credibility = parseInt($('div.report-description-text').text().substr(credStart));
	obj.verified = $('p.r_verified').length==1
        var concatCat = "";
        for(var j = 0;j<obj.categories.length;j++){
            concatCat += obj.categories[j].toLowerCase()+" "    
        };
        var filterStr = obj.title.toLowerCase()+" "+obj.description.toLowerCase()+" "+concatCat;
        if(filterStr.indexOf("china")>-1 || filterStr.indexOf("chinese")>-1){
            var a = obj,
            zone = a.coord.substr(10,a.coord.indexOf(' Easting')-10),
            zoneLetter = zone.substr(-1),
            zoneNumber = parseFloat(zone.substr(0,zone.length-1)),
            easting = a.coord.substr(a.coord.indexOf('Easting')+9,a.coord.indexOf(' Northing')-(a.coord.indexOf('Easting')+9)),
            northing = a.coord.substr(a.coord.indexOf('Northing: ')+10),
            UTM = {};
            UTM.type = 'Feature';
            UTM.geometry = {};
            UTM.geometry.type = 'Point';
            UTM.geometry.coordinates = [];
            UTM.geometry.coordinates[0] = easting;
            UTM.geometry.coordinates[1] = northing;
            UTM.properties = {};
            UTM.properties.title = a.title;
            UTM.properties.date = a.date;
            UTM.properties.geoname = a.geoname;
            UTM.properties.categories = a.categories;
            UTM.properties.group = a.group;
            UTM.properties.description = a.description;
            UTM.properties.credibility = a.credibility;
            UTM.properties.verified = a.verified;
            UTM.properties.zoneLetter = zoneLetter;
            UTM.properties.zoneNumber = zoneNumber;
            
            var feature = UTM;
            feature.geometry = wgs84.UTMtoLL(UTM);
            feature.geometry.coordinates = feature.geometry.coordinates.reverse();
	    var uniqueStr = feature.properties.date+feature.properties.title+feature.geometry.coordinates[0]+feature.geometry.coordinates[0];
	    if (!uniqueObj[uniqueStr]) {
		uniqueObj[uniqueStr] = true;
		LERNgeoJSON.features.push(feature);
		process.stdout.write('\n');
		console.log(LERNgeoJSON.features.length+". "+feature.properties.title)
		var jsonStr = "var LERNdata = "+JSON.stringify(LERNgeoJSON);
		fs.writeFile('geoLERN.js',jsonStr,function(err){if(err){throw err};});
	    }else{process.stdout.write('\n');console.log("Tossing duplicate...");};
        };
};

function parseMany(e,r,b){
	var $ = cheerio.load(b,{normalizeWhitespace:true});
	var pages = parseInt($('ul.pager li').last().text());
	if(pages==1){
		parsePage(e,r,b);
	}else{
		parsePage(e,r,b);
		for(var i = 1;i<pages;i++){
			var pageIndex = $("ul.pager li a:not(.active)").first().attr('href').indexOf('&page')
			var baseURL = $("ul.pager li a:not(.active)").first().attr('href').substr(0,pageIndex)
			var pageURL = baseURL + "&page=" + i
			request(pageURL,parsePage);  	
		};
	};
};

function parsePage(e,r,b){
	var $ = cheerio.load(b,{normalizeWhitespace:true});
	var links = $('a.r_title');
	if(links.length>1){
        	for(var i = 0;i<links.length;i++){
                	var link = $('a.r_title')[i];
                	var singleURL = $(link).attr('href');
                        process.stdout.write(".");
                	request(singleURL,parseOne);
        	};
	}else{
		var singleURL = $('a.r_title').attr('href');
                process.stdout.write(".");
		request(singleURL,parseOne);
	};
};