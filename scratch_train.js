var csv = require('csv'),
fs = require('fs'),
natural = require('natural'),
stopwords = require('stopwords').english,
stopObj = {},
csvfile = "train_short.csv",
header = true,
tokenizer = new natural.WordTokenizer(),
batch = [],
totalInputs = {count:0,docs:0,data:{},booleanData:{}},
classifier = {data:{},idf:{}};

for(var i = 0;i<stopwords.length;i++){
	stopObj[stopwords[i]]=1;
};

//read the training file
csv().from.path(csvfile, { columns: true, delimiter: "\t" } )

// on each record, do this
.on('record', function (data, index) 
{
	if (header)
    {
    	//now I have read the header, discard it and move on
 		header = false;	
 	}else
 	{
		var strRow ='',
		act_code ='',
		title ='',
		short_desc ='',
		long_desc ='',
		project_id = '';
		for (key in data)
		{	
			data[key] = data[key].trim();
			if (key == 'act_code')
			{
				var act_code = data[key];    
			};
			 if (key == 'project_id')
			{
				var project_id = data[key];
			};
			if (key == 'title') 
			{
				var title = data[key];
			};
			if (key == 'short')
			{
				var short_desc = data[key];
			};
			if (key == 'long')
			{
				var long_desc = data[key];
			};  
		};
		
		//our data is here!
		var text = title+" "+short_desc+" "+long_desc,
		tokens = tokenizer.tokenize(text.toLowerCase());
		if (!batch[act_code]) {batch[act_code]={input:{},output:act_code,count:0};};
		for(var i=0;i<tokens.length;i++){
			if (!stopObj[tokens[i]]) {
				if (!batch[act_code].input[tokens[i]]) {batch[act_code].input[tokens[i]]=0};
				if (!totalInputs.data[tokens[i]]){totalInputs.data[tokens[i]]=0};
				batch[act_code].input[tokens[i]]+=1;
				batch[act_code].count+=1;
				totalInputs.data[tokens[i]]+=1;
				totalInputs.count+=1;
			};
		};
		for(var token in batch[act_code].input){
			if (!totalInputs.booleanData[token]){totalInputs.booleanData[token]=0};
			totalInputs.booleanData[token]+=1;
		};
		totalInputs.docs += 1;
		console.log("Adding: "+text+", "+act_code);
		
		//add the document to the classifier
	};
 })
 
 //when we are done, do this
 .on('end', function(count)
 {
	console.log("Done Reading. Training Classifier...");
	//train the classifier
	for(var act_code in batch){
		var inputs = batch[act_code].input,
		output = batch[act_code].output,
		inputCount = batch[act_code].count,
		inputObj = {pos:{},neg:JSON.parse(JSON.stringify(totalInputs.data))};
		for(var input in inputs){
			inputObj.pos[input]=inputs[input];
			inputObj.neg[input]-=inputs[input];
		};

		classifier.data[output] = inputObj;
	};
	classifier.idf.docs = totalInputs.docs;
	classifier.idf.freq = totalInputs.booleanData;
	console.log("Done Training. Writing file...");
	var jsonStr = JSON.stringify(classifier);
        fs.writeFile('scratchClassifier.js',jsonStr,function(err){if(err){throw err};});
	console.log("Done.");
 });
