function getTops(req, callback) {
	var query = {
		sql: 'SELECT * FROM Tops'
	};
	req.azureMobile.data.execute(query)
		.then(function (results) {
			callback(results);
		});
};

function getBottoms(req, callback) {
	var query = {
		sql: 'SELECT * FROM Bottoms'
	};
	req.azureMobile.data.execute(query)
		.then(function (results) {
			callback(results);
		});
};

function getShoes(req, callback) {
	var query = {
		sql: 'SELECT * FROM Shoes'
	};
	req.azureMobile.data.execute(query)
		.then(function (results) {
			callback(results);
		});
};

var dataService = {
	getClothing: function (req, segment, callback) {
		var query = {
			sql: 'SELECT * FROM '.concat(segment)
		};
		req.azureMobile.data.execute(query)
			.then(function (results) {
				callback(results);
			});
	},
	getTopsByUuid: function (uuid, req, callback) {
		//console.log(uuid);
		var queryString = "SELECT * FROM Tops WHERE id = '";
		queryString = queryString.concat(uuid).concat("'");
		//console.log(queryString);
		var query = {
			sql: queryString
		};
		req.azureMobile.data.execute(query)
			.then(function (results) {
				callback(results);
			});
	},
	getOutfitCombo: function (req, callback) {
		req.azureMobile.data.execute({sql: 'SELECT * FROM Outfits'})
			.then(function (results) {
				callback(results);
			});
	}

};
module.exports = dataService;
