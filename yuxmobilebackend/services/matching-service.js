var request = require('request');
var featureService = require('./feature-service.js');
var log = require('tracer').console();

var _idfTable = {tops: [], shorts: [], pants: [], shoes: []};
var _tfIdfTable = {tops: [], shorts: [], pants: [], shoes: [], bottoms:[]};
var _idfTableOutfits = {tops: [], bottoms: [], shoes: []};
var _tfIdfTableOutfits = {tops: [], bottoms: [], shoes: []};
var _championsTable = {tops: [], shorts: [], pants: [], shoes: []};
var categories = ['tops','shorts','pants','shoes'];
var categoriesForOutfits = ['tops','bottoms','shoes'];

function preprocess(req) {

	var bottomsData = {shorts: false, pants: false, data: []};
	categories.forEach(function(segment) {
		// Compute tf-idf table once
		featureService.getFeatures(req, segment, function(database) {
			log.info("for %s", segment);
			_idfTable[segment] = computeIdf(database);
			_tfIdfTable[segment] = computeTfIdf(database, _idfTable[segment]);
			log.info("num of features: %j", database[0].features.length); 

			for (var i = 0; i < database[0].features.length; i++){
				_championsTable[segment].push(getChampionList(_tfIdfTable[segment], i));
			}

			if (segment == "tops" || segment == "shoes") {
				featureService.getOutfitFeaturesBySegment(req, segment, function(outfit) {
					_tfIdfTableOutfits[segment] = computeTfIdf(outfit, _idfTable[segment]);
				});
			}
			else {
				bottomsData.data = bottomsData.data.concat(database);
				bottomsData[segment] = true;
				if (bottomsData.shorts && bottomsData.pants) {
					log.info("computing combined idf for bottoms");
					_idfTable.bottoms = computeIdf(bottomsData.data);

					log.info('calculating outfit tfidf for bottoms');
					featureService.getOutfitFeaturesBySegment(req, 'bottoms', function(outfit) {
						_tfIdfTableOutfits.bottoms = computeTfIdf(outfit, _idfTable.bottoms);
					});
				}
			}

		});
	});
	//log.info("after for each category");

	/*
	featureService.getFeatures(req, 'shorts', function(shorts) {
		featureService.getFeatures(req, 'pants', function(pants) {
			log.info("computing combined idf for bottoms");
			_idfTable.bottoms = computeIdf(shorts.concat(pants));

			// Compute tf-idf table once 
			log.info('calculating outfit tfidf for bottoms');
			featureService.getOutfitFeaturesBySegment(req, 'bottoms', function(database) {
				_tfIdfTableOutfits.bottoms = computeTfIdf(database, _idfTable.bottoms);
			});

		});
	});

	featureService.getFeatures(req, 'shorts', function(shorts) {
		featureService.getFeatures(req, 'pants', function(pants) {
			log.info("computing combined idf for bottoms");
			_idfTable.bottoms = computeIdf(shorts.concat(pants));

			categoriesForOutfits.forEach(function(segment) {
				// Compute tf-idf table once 
				log.info('calculating outfit tfidf for %s', segment);
				featureService.getOutfitFeaturesBySegment(req, segment, function(database) {
					log.info('outfit features for %s', segment);
					log.info(database);
					_tfIdfTableOutfits[segment] = computeTfIdf(database, _idfTable[segment]);
				});
			});

		});
	});
	*/
}


function computeIdf(data) {
	// threshold can be changed
	log.info("computing idf");
	var docNum = data.length;
	var attriNum = data[0].features.length;

	var idfTable = [];
	var threshold = 0.7; // Used as a threshold to consider as inside document

	for(var y = 0; y < attriNum; y++){ 
		var docf =0;
		for(var x = 0; x < docNum; x++){
			if (data[x].features[y] > threshold){
				docf += 1;
			}		
		} 
		var idf = Math.log(docNum/docf); //note log is natural logarithm

		//if frequency 0, unable to give relavant doc, set idf = 0 instead of infinity
		if (docf ==0){ idf = 0;}
		idfTable[y] = 1 + idf;  //CHANGE if necessary
	}
	return idfTable;
};

function computeTfIdf(data, idfTable) {
	log.info("computing tf-idf");
	var docNum = data.length;
	var attriNum = data[0].features.length;
	log.info("docNum: %d, attriNum: %d", docNum, attriNum);

	var tfIdfTable = [];
	var magTable = [];
	for(var x = 0; x < docNum; x++){
		tfIdfTable[x] = [];    
		magTable[x]= 0;
		for(var y = 0; y < attriNum; y++){ 
			tfIdfTable[x][y] = (1+Math.log(1+data[x].features[y])) * idfTable[y]; //tf-idf

			//this part edits the importance of certain vectors
			//Decrease importance of no secondary colours
			if(y == 32){ tfIdfTable[x][y] = tfIdfTable[x][y] * 0.1; }

			// //Increase importance of primary colours
			if(y < 16 ){ tfIdfTable[x][y] = tfIdfTable[x][y] * 3; }

			magTable[x] += tfIdfTable[x][y]* tfIdfTable[x][y];
		}    
	}

	//normalising step
	for(var x = 0; x < docNum; x++){
		magTable[x] = Math.sqrt(magTable[x]);
		for(var y = 0; y < attriNum; y++){ 
			tfIdfTable[x][y] =  tfIdfTable[x][y]/magTable[x] ;
		}
	}

	return tfIdfTable;
};

function normalizeQuery(query, idfTable) {
	log.info("normalizing query");
	var attriNum = idfTable.length;

	var queryMag = 0;
	var queryTable = [];

	for(var y = 0; y < attriNum; y++){ 
		queryTable[y] = query[y]*idfTable[y];  
		queryMag += queryTable[y]* queryTable[y];
	}  
	console.log("queryTable"); 
	console.log(queryTable); 
	queryMag = Math.sqrt(queryMag);

	//Normalizing step
	for(var y = 0; y < attriNum; y++){ 
		queryTable[y] =  queryTable[y]/queryMag ;
	}   

	return queryTable;
};

function selectBestK(queryTable, tfIdfTable, k, queryIndex) {
	log.info("selecting best k");
	var dimensions = [ tfIdfTable.length, tfIdfTable[0].length ];
	var docNum = dimensions[0];
	var attriNum = dimensions[1];
	log.info("docNum: %d, attriNum: %d", docNum, attriNum);
	
	var kSimTable = [];

	var cosSimTable = [];
	for(var x = 0; x < docNum; x++){
		cosSimTable[x]=0;
		for(var y = 0; y < attriNum; y++){ 
			cosSimTable[x] += queryTable[y] * tfIdfTable[x][y];
		}    
	} 

//	console.log("cosSimTable");
//	console.log(cosSimTable);

	var index = [];
	while(index.length < k){
	//for each document, take the largest cossim and store the index
		//var max_index = cosSimTable.indexOf(Math.max(...cosSimTable));
		var max_index = cosSimTable.indexOf(Math.max.apply(Math, cosSimTable));
		if (max_index != queryIndex){	//should not return itself
			index.push(max_index);
			//log the cosine similarity of max_index into a global var to show later on
         kSimTable.push(cosSimTable[max_index]);
		}

		cosSimTable[max_index]=-1;		//remove largest value and iterate again
	}  

	return index;
};

// Champions Function: Compute cosine similarity between query and documents, select the top k results
function champions_selectBestK(query, k, searchList, tfIdfTable, queryIndex){

	console.log("select best k from champion search list");
	var cosSimTable = [];
	var kSimTable = [];
	for(var x = 0; x < searchList.length; x++){
		var docIndexToCompare = searchList[x];
		cosSimTable[x]=0;
		for(var y = 0; y < query.length; y++){ 
			cosSimTable[x] += query[y] * tfIdfTable[docIndexToCompare][y];
		}    
	} 

	var index = [];
	while(index.length < k){
	//for each document, take the largest cossim and store the index
		var max_index_in_searchList = cosSimTable.indexOf(Math.max.apply(Math,cosSimTable));
		var max_index = searchList[max_index_in_searchList];
		if (max_index != queryIndex && index.indexOf(max_index) == -1){	//should not return itself
			index.push(max_index);
			//log the cosine similarity of max_index into a global var to show later on
         kSimTable.push(cosSimTable[max_index]);
		}

		cosSimTable[max_index_in_searchList]=-1;		//remove largest value and iterate again
	}  

	return index;
};

// Extracts out champion list for each clothing attribute
function getChampionList(tfIdfTable, attriNumReferenced){

	var championListSize = 0.01;   				// size of champion list relative to size of corpus
	var k = Math.ceil(championListSize*tfIdfTable.length);
	var championList = [];
	var tfIdfColumn = [];
	for (var i = 0; i < tfIdfTable.length; i++){
		tfIdfColumn[i] = tfIdfTable[i][attriNumReferenced];
	}

	for (var j = 0; j < k; j++){
		var max_index = tfIdfColumn.indexOf(Math.max.apply(Math,tfIdfColumn));
		championList[j] = max_index;
		tfIdfColumn[max_index]=-1;
	}
	return championList;
};

// Champions Function:  Gets the search list from championsTable according to queryVector
function champions_getSearchList(segment, queryVector){

	log.info("getting search list");
	var searchList = [];
	var attriNum = queryVector.length;
	var listNum = _championsTable[segment][0].length;
	var threshold = 0.7;
	var maxColIndex;
	var colMag = 0;
	for (var i = 0; i < 16; i++){
		if (queryVector[i] >= colMag){
			colMag = queryVector[i];
			maxColIndex = i;
		}
	}
	searchList = searchList.concat(_championsTable[segment][maxColIndex]);


	for (var i = 16; i < attriNum; i++){
		// Based on confidence of each attribute, get length of the championsList to use
		if (queryVector[i] >= threshold){
			searchList = searchList.concat(_championsTable[segment][i]);
		}    
	}
	return searchList;
};



function getCorpusByIndexes(segment, indexes, isMatchOutfit) {
	var corpus = [];
	for (var i = 0; i < indexes.length; i++) {
		if (isMatchOutfit) {
			corpus.push(featureService.getOutfitByIndex(indexes[i]));
		}
		else {
			corpus.push(featureService.getClothingByIndex(segment, indexes[i]));
		}
	}
	return corpus;
};

function randomIntFromInterval(min,max) {
	return Math.floor(Math.random()*(max-min+1)+min);
};

function retrieveSimilarClothing(req, segment, queryObj, isMatchOutfit, callback){
	log.info("in retrieve similar clothing");

	var doRetrieval = function(data) {
		log.info("getting ready to do matching");
		var idfTable = _idfTable[segment];
		var queryTable = normalizeQuery(queryObj.vector, idfTable);

		var k = 3;
		var indexes;

		//use champions list only when retrieveing similar clothing
		if(isMatchOutfit) {
			k = 1;
			var tfIdfTable = _tfIdfTableOutfits[segment];
			indexes = selectBestK(queryTable, tfIdfTable, k, queryObj.index);
		}
		else {
			var tfIdfTable = _tfIdfTable[segment];
			var searchList = champions_getSearchList(segment, queryObj.vector);
			indexes = champions_selectBestK(queryTable, k, searchList, tfIdfTable, queryObj.index);
		}

		/*
		console.log(indexes);
		*/

		var matches = getCorpusByIndexes(segment, indexes, isMatchOutfit);
		console.log("matching clothings");
		console.log(matches);

		if (callback) {
			callback(matches);
		}
	}
	if (isMatchOutfit) {
		log.info("finding outfits");
		featureService.getOutfitFeaturesBySegment(req, segment, doRetrieval);
	}
	else {
		log.info("finding similar clothings");
		featureService.getFeatures(req, segment, doRetrieval);
	}
};

var matchingService = {

	retrieveWithRandomQuery: function(req, segment, callback) {
		featureService.getFeatures(req, segment, function(data) {
			var i = randomIntFromInterval(0,featureService.getNumberOfClothing(segment)-1);
			var clothing = featureService.getClothingByIndex(segment, i);
			log.info('Using %s as query', clothing.img_url);
			var queryObj = {
				index: i,
				vector: clothing.features
			};
			if (queryObj.vector.length == 0) {
				log.error("DATA NOT INITIALISED");
				if (callback) {
					callback(false);
				}
				return;
			}
			retrieveSimilarClothing(req, segment, queryObj, false, function (matches) {
				if (callback) {
					callback({randomQuery: clothing.img_url, results: matches});
				}
			});
		});
	},

	retrieveWithQuery: function(req, segment, queryVector, callback) {
		var queryObj = {
			index: -1,
			vector: queryVector
		};
		retrieveSimilarClothing(req, segment, queryObj, false, function (matches) {
			if (callback) {
				callback({results: matches});
			}
		});
	},

	retrieveOutfit: function(req, segment, queryVector, callback) {
		if (segment == 'pants' || segment == 'shorts') {
			segment = 'bottoms';
		}
		var queryObj = {
			index: -1,
			vector: queryVector
		};
		retrieveSimilarClothing(req, segment, queryObj, true, function (match) {
			var results = {outfit: match[0], matches: {tops:[], bottoms:[], shoes:[]}};
			categoriesForOutfits.forEach(function(category) {
				if (category != segment) {
					var retrieveCat;
					if (category == "bottoms") {
						if (match[0].bottoms[33] > match[0].bottoms[34]) {
							retrieveCat = "pants";
						}
						else {
							retrieveCat = "shorts";
						}
					}
					else {
						retrieveCat = category;
					}
					matchingService.retrieveWithQuery(req, retrieveCat, match[0][category], function(part) {
						results.matches[category] = part;
					});
				}
			});
			if (callback) {
				callback(results);
			}
		});
	},

	preprocess: function(req) {
		preprocess(req);
	}

};

request({
	url: 'http://yuxmobilebackend.azurewebsites.net/api/initialise',
	method: 'GET'
}, function(err, res, body) {
});

module.exports = matchingService;


