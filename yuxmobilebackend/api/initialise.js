var matchingService = require('../services/matching-service.js');

var api = {
	get: function (req, res, next) {
		matchingService.preprocess(req);
		res.status(204).end();
	}
}

module.exports = api;
