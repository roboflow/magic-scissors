/*jshint esversion:6*/

const $ = require("jquery");
const page = require("page");
const swal = require("sweetalert2");
const _ = require("lodash");

$(function () {
    window.$ = $;

    _.mixin({
        getItem: function (k) {
            try {
                return localStorage.getItem(k);
            } catch (e) {
                return localStorageFallback[k] || null;
            }
        },
        setItem: function (k, v) {
            try {
                localStorage.setItem(k, v);
            } catch (e) {
                localStorageFallback[k] = v;
            }
        },
        removeItem: function (k) {
            try {
                localStorage.removeItem(k);
            } catch (e) {
                delete localStorageFallback[k];
            }
        },
        clear: function () {
            try {
                localStorage.clear();
            } catch (e) {
                localStorageFallback = {};
            }
        }
    });
});
