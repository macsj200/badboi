var matchingService = require('../services/matching-service.js');
var request = require('request');

var api = {
	get: function (req, res, next) {
		//console.log(req.query.imgurl);
		// var result = { imgurl: req.query.imgurl };
		// var result = "222";
		//GET Request to Flask App 'clasifyImage' Route with imgurl
		//Save response of clothing type and feature vector
		//Retrieve clothing objects from champion list of clothing type
		//Compute cosine similarity between feature vector and champion list
		//If results are satisfactory, return as response
		//Else Retrieve more clothings from database to compare
		//Return best result
		/*featureService.getFeaturesOfTops(req, function(results) {
		res.json(results);
	 });*/
		/*dataService.getTestByUuid("b8adac12-1b9e-4f8b-87e6-0969fa0a5d3f", req, function(results) {
		res.json(results);
	 });*/
		matchingService.retrieveWithRandomQuery(req, 'tops', function(results) {
			res.json(results);
		});
		//res.status(200).type('application/json').send(result);
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
					if (body.vector[33] > body.vector[34]) {
						body.type = "pants";
					}
					else {
						body.type = "shorts";
					}
					break;
				case 48:
					body.type = "shoes";
					break;
				default:
					console.log("vector length error");
					res.stat(500).end();
					return;
			}
			matchingService.retrieveWithQuery(req, body.type, body.vector, function(results) {
				res.json(results);
			});
		});
	}
};

module.exports = api;
