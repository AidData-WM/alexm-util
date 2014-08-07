var fs = require('fs'),
csv = require('to-csv'),
S = require('string'),
USAID = JSON.parse(fs.readFileSync('./USAID.js','utf8')),
records = [];

for(var id in USAID){
    var startDate = USAID[id]["startDate"],
    sector = USAID[id]["sector"],
    partner = USAID[id]["partner"],
    org = USAID[id]["org"],
    name = USAID[id]["name"],
    endDate = USAID[id]["endDate"],
    publicResults = USAID[id]["public_results"],
    country = USAID[id]["country"],
    obligation = USAID[id]["obligation"],
    description = USAID[id]["description"],
    locations = USAID[id]["locations"];
    for(var i = 0;i < locations.length; i++){
        var obj = locations[i];
        obj.type = locations[i].attributes.type;
        obj.url = locations[i].attributes.url;
        delete obj["attributes"];
        obj.startDate = startDate!=''&&startDate!=null?startDate:'none';
        obj.sector = sector!=''&&sector!=null?sector:'none';
        obj.partner = partner!=''&&partner!=null?partner:'none';
        obj.org = org!=''&&org!=null?org:'none';
        obj.name = name!=''&&name!=null?name:'none';
        obj.endDate = endDate!=''&&endDate!=null?endDate:'none';
        obj.publicResults = publicResults!=''&&publicResults!=null?S(publicResults).stripPunctuation().s:'none';
        obj.country = country!=''&&country!=null?country:'none';
        obj.obligation = obligation!=''&&obligation!=null?obligation:'none';
        obj.description = description!=''&&description!=null?S(description).stripTags().stripPunctuation().s:'none';
        obj.id = id;
        records.push(obj);
    };
};
console.log(records.length)
fs.writeFile('USAID.csv',csv(records),function(err){if(err){throw err};});
console.log("Done.")