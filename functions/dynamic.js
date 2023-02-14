const functions = require("firebase-functions");
const admin = require("firebase-admin");
const express = require("express");
const cookieParser = require("cookie-parser")();
const bodyParser = require("body-parser");

const cors = require("cors")({
    origin: true,
    methods: ["GET", "HEAD", "PUT", "PATCH", "POST", "PURGE", "DELETE"]
});

const app = express();
const async = require("async");
const moment = require("moment");
const _ = require("lodash");
const fs = require("fs");
const axios = require("axios");

var db = admin.firestore();

app.use(bodyParser.json());
app.use(
    bodyParser.urlencoded({
        extended: true
    })
);
app.use(bodyParser.text());
app.use(cookieParser);

app.get("/query/ping", function (req, res) {
    res.status(200).json({
        ping: "pong"
    });
});

exports.app = app;