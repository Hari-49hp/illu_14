odoo.define('pos_auto_invoice.pos', function (require) {
        "use strict";
var models = require('point_of_sale.models');

var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            let res = _super_Order.initialize.apply(this, arguments);
            if (this.pos.config.pos_auto_invoice) {
                this.to_invoice = true;
            }
            return res
        }
    });
})


