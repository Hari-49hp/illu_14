odoo.define('pos_sale_item_info.point_of_sale', function (require) {
"use strict";

var models = require('point_of_sale.models');
var _super_posmodel = models.PosModel.prototype;

models.PosModel = models.PosModel.extend({
    initialize: function(session, attributes) {
        var product_model = _.find(this.models, function (model) {
            return model.model === "product.product";
        });
        product_model.fields.push('qty_available');
        product_model.fields.push('type');
        return _super_posmodel.initialize.call(this,session,attributes);
    },
})

});

