/*jshint esversion:8*/
/*jshint -W069*/
const functions = require("firebase-functions");
const admin = require("firebase-admin");

admin.initializeApp();

exports.dynamic = functions
    .runWith({
        // secrets: [
        //     "ROBOFLOW_KEY",
        //     "ROBOFLOW_PUBLISHABLE"
        // ]
    })
    .https.onRequest(require('./dynamic.js').app);
