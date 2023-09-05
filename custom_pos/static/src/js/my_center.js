odoo.define('pos_customer_display.VDFPort', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    var session = require('web.session');
    var rpc = require('web.rpc');

    class MyCenter extends PosComponent {
        constructor() {
                super(...arguments);
                useListener('my_center', this.redirect_mycenter);
                console.log("My Center")
        }
        async redirect_mycenter() {
            console.log("redirect my center");
            rpc.query({
                model: 'pos.config',
                method: 'generate_crm_pipeline_link',
            }).then(function (url) {
//                return url;
                window.open(url,'_self');
            });
        }
    }

    MyCenter.template = 'my_center';

    Registries.Component.add(MyCenter);
    return {
        MyCenter:MyCenter,
    };
});