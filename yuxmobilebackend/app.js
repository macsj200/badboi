var express = require('express'),
    bodyParser = require('body-parser'),
    azureMobileApps = require('azure-mobile-apps');

var app = express();

var mobileApp = azureMobileApps({
    homePage: true, //enable the Azure Mobile Apps home page
    swagger: true //enable swagger support
});

// Set up large body content handling
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));


mobileApp.tables.import('./tables'); //configure the /tables endpoint
mobileApp.api.import('./api'); //configure the /api endpoint

// Initialize the database before listening for incoming requests
// The tables.initialize() method does the initialization asynchronously
// and returns a Promise.
mobileApp.tables.initialize()
    .then(function () {
        app.use(mobileApp);    // Register the Azure Mobile Apps middleware
        app.listen(process.env.PORT || 3000);   // Listen for requests
    });

