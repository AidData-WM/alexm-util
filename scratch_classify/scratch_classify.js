var fs = require('fs'),
natural = require('natural'),
tokenizer = new natural.WordTokenizer(),
classifierFile = "./scratchClassifier.js",
input = process.argv[2],
output = [],
explanation = [],
classifier = JSON.parse(fs.readFileSync(classifierFile,{encoding:'utf8'})),
inputTokens = tokenizer.tokenize(input.toLowerCase());

for(var act_code in classifier.data){
    var positive = classifier.data[act_code].pos,
    negative = classifier.data[act_code].neg,
    likelihood = 0;
    for(var i=0;i<inputTokens.length;i++){
        var token = inputTokens[i];
        if (!positive[token]){
            likelihood+=0;
        }else{
            likelihood+=positive[token];
            explanation.push({code:act_code,points:positive[token],token:token})
        };
        //if (!negative[token]){
        //    likelihood+=0;
        //}else{
        //    likelihood-=negative[token];
        //};
        if (!classifier.idf.freq[token]){
            likelihood+=0;
        }else{
            likelihood*=Math.log(classifier.idf.docs/classifier.idf.freq[token]);
        };
    };
    var outputObj = {code:act_code,similarity:likelihood};
    output.push(outputObj);
};

output.sort(function(a,b){
    var aKey = a.similarity,
    bKey = b.similarity;
    if(aKey<bKey){return 1};
    if(aKey>bKey){return -1};
    return 0;
});

explanation.sort(function(a,b){
    var aKey = a.points,
    bKey = b.points;
    if(aKey<bKey){return 1};
    if(aKey>bKey){return -1};
    return 0;
});

var i = 0,
j=0,
max = output[0].similarity;
while(i<1&&j<output.length){
    if (output[j+1]==undefined||output[j+1].similarity/max<0.5||output[j].similarity==undefined) {i+=1};
    console.log("Code: "+output[j].code+"; Score: "+output[j].similarity.toFixed(2))
    j+=1;
};
console.log("Why?")
var topChoice = output[0].code,
filteredExplain = explanation.filter(function(d){return d.code==topChoice});
for(var i = 0;i<filteredExplain.length;i++){
    console.log("'"+filteredExplain[i].token+"'"+" occurs "+filteredExplain[i].points+" times in "+filteredExplain[i].code +" and has an idf of "+Math.log(classifier.idf.docs/classifier.idf.freq[filteredExplain[i].token]).toFixed(2))    
};