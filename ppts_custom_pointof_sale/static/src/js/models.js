odoo.define('ppts_custom_pointof_sale.models',function(require) {
    "use strict";

var models = require('point_of_sale.models');
var core = require("web.core");
var rpc = require("web.rpc");
var DB = require("point_of_sale.DB");
models.load_fields("res.partner", ["is_a_customer"]);
});