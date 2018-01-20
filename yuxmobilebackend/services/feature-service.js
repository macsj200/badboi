var dataService = require('./data-service.js');
var log = require('tracer').colorConsole({level:'info'});
var features = {tops: [], shorts: [], pants: [], shoes: []};
var comboFeatures = [];

function	getOutfitFeatures(req, callback) {
	if (comboFeatures.length > 0) {
		callback(comboFeatures);
	}
	else {
		dataService.getOutfitCombo(req, function(results) {
			log.info("retrieved oufit data from db");
			for (var i = 0; i < results.length; i++) {
				results[i].tops = results[i].tops.split(',').map(parseFloat);
				results[i].bottoms = results[i].bottoms.split(',').map(parseFloat);
				results[i].shoes = results[i].shoes.split(',').map(parseFloat);
			}
			comboFeatures = results;
			if (callback) {
				callback(results);
			}
		});
	}
}


var featureService = {
	getFeatures: function (req, segment, callback) {
		if(features[segment].length > 0) {
			log.info("in storage");
			if (callback) {
				callback(features[segment]);
			}
		}
		else {
			log.info("not in storage");
			dataService.getClothing(req, segment, function(results) {
				features[segment] = results;
				//console.log(results);	
				for (var i = 0; i < results.length; i++) {
					results[i].features = results[i].features.split(',').map(parseFloat);
				}
				log.info("returning data for %s", segment);
				if (callback) {
					callback(features[segment]);
				}
			});
		}
	},

	getClothingByIndex: function(segment, index) {
		return features[segment][index];
	},

	getNumberOfClothing: function(segment) {
		return features[segment].length;
	},

	getOutfitFeaturesBySegment: function(req, segment, callback) {
		if (segment == 'pants' || segment == 'shorts') {
			segment = 'bottoms';
		}

		var returnFeatures = function() {
			var data = [];
			for (var i = 0; i < comboFeatures.length; i++) {
				data.push({features: comboFeatures[i][segment]});
			}	
			callback(data);
		}

		if (comboFeatures.length > 0) {
			log.info("combo features exist");
			returnFeatures();
		}
		else {
			log.info("combo features missing, waiting or grab from db");
			getOutfitFeatures(req, function(results) {
				returnFeatures();
			});
		}
	},
	getOutfitByIndex: function(index) {
		return comboFeatures[index];
	}


};

module.exports = featureService;
