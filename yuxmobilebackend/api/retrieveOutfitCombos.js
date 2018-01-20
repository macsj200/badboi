var matchingService = require('../services/matching-service.js');
var request = require('request');

var api = {
	get: function (req, res, next) {
		console.log(req.query.imgurl);
		var result = { imgurl: req.query.imgurl };
		//GET Request to Flask App 'clasifyImage' Route with imgurl
		//Save response of clothing type and feature vector
		//Retrieve clothing objects from champion list of other clothing types
		//GET Request to ML studio
		//If results are satisfactory, return as response
		//Else Retrieve more clothings from database to compare
		//Return best result
		res.status(200).type('application/json').send(result);
	},
	post: function (req, res, next) {
		var PYTHON_SERVER = process.env.PYTHON_SERVER;
		request({
			url: PYTHON_SERVER + ':5000/analyse_image',
			method: 'POST',
			json: req.body
		}, function(err, classRes, body) {
			if (err) {
				console.log(err);
				res.status(500).end();
				return;
			}
			console.log(body);
			switch (body.vector.length) {
				case 66:
					body.type = "tops";
					break;
				case 58:
					body.type = "bottoms";
					break;
				case 48:
					body.type = "shoes";
					break;
				default:
					console.log("vector length error");
					res.stat(500).end();
					return;
			}
			matchingService.retrieveOutfit(req, body.type, body.vector, function(results) {
				res.json(results);
			});
		});
	}
}

module.exports = api;
