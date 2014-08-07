var request = require('request');
var cheerio = require('cheerio');
var fs = require('fs');
var pageUrl = "http://portfolio.usaid.gov/AidTrackerProjectListData?c=Angola%3A%3A%3AChad%3A%3A%3ADemocratic%20Republic%20of%20the%20Congo%3A%3A%3AEthiopia%3A%3A%3AGhana%3A%3A%3AKenya%3A%3A%3ALiberia%3A%3A%3AMali%3A%3A%3AMauritania%3A%3A%3AMozambique%3A%3A%3ANiger%3A%3A%3ANigeria%3A%3A%3ARwanda%3A%3A%3ASenegal%3A%3A%3ASouth%20Africa%3A%3A%3ASouth%20Sudan%3A%3A%3ATanzania%3A%3A%3AUganda%3A%3A%3AZimbabwe&r=search&l=&w=&m=&s=&v=list&f=948236669221&t=1405956229381";
var individualUrl = "http://portfolio.usaid.gov/PublicProjectDetail?id="
var mapDataUrl = "http://portfolio.usaid.gov/AidTrackerMapData?r=pd&id="
var recordLength = 0;
var records = {};
request(pageUrl,parseCallback);

function parseCallback(e,r,b) {
    if(e){throw e};
    var rawJson = b.substr(1,b.length-3);
    var data = JSON.parse(rawJson);
    recordLength+=data.length;
    for(var i = 0;i<data.length;i++){
        var id = data[i].Id;
        records[id]=data[i];
        request(individualUrl+id,parseDetails);
    };
};
function parseDetails(e,r,b){
    if(e){throw e};
    var id = r.request.uri.query.substr(3);
    var $ = cheerio.load(b,{normalizeWhitespace:true});
    records[id]["public_results"] = $('.mainContent p').last().text();
    records[id]["obligation"] = $('.content h3').last().text();
    request(mapDataUrl+id,parseMap);
};
function parseMap(e,r,b){
    if(e){throw e};
    var id = r.request.uri.query.substr(8);
    var rawJson = b.substr(1,b.length-3);
    var data = JSON.parse(rawJson);
    records[id]["locations"] = data;
    recordLength-=1;
    process.stdout.write(".");
    if (recordLength==0) {
        process.stdout.write('\n');
        console.log("Done.")
        var jsonStr = JSON.stringify(records);
        fs.writeFile('USAID.js',jsonStr,function(err){if(err){throw err};});
    };
};

