odoo.define('pos_coupon.orderlineoption', function (require) {
    'use strict';

    const models = require('point_of_sale.models');
    const rpc = require('web.rpc');
    const session = require('web.session');
    const concurrency = require('web.concurrency');
    const { Gui } = require('point_of_sale.Gui');


    var _order_super = models.Order.prototype;
    models.Order = models.Order.extend({



    });
    });