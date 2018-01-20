var azureMobileApps = require('azure-mobile-apps');
var table = azureMobileApps.table();

//Defines the list of columns
table.columns = {
  "name": "string",
  "description": "string",
  "category": "string",
  "imageUrl": "string",
  "predictedTags": "string",
  "price": "number",
  "websiteUrl": "string"
}

table.seed = [
  {name: "addidas superstart", description: "bestshoe4va"},
  {name: "addidas superstart", description: "bestshoe4va"}
]

module.exports = table;
