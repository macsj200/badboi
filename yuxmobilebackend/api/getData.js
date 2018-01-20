//var championService = require('../services/champion-service.js');
var dataService = require('../services/data-service.js');
var log = require('winston');

module.exports = {
	get: function (req, res, next) {
		dataService.getOutfitCombo(req, function(results) {
			res.json(results);
		});
	},
	post: function (req, res, next) {
		console.log(req.body);
		res.status(204).end();
	},
	delete: function (req, res, next) {
		championService.deleteChampionList('tops');
		championService.deleteChampionList('bottoms');
		championService.deleteChampionList('shoes');
		res.json(true);
	}
}
