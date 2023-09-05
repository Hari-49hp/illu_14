odoo.define('pos_order_remove_line.pos_order_line', function(require) {
    "use strict";

    var models = require('point_of_sale.models');



    models.Orderline = models.Orderline.extend({

        remove_line_btn: function(ev) {
            console.log(ev);
            console.log(this);
            console.log(this.env);
            console.log(this.env);
            // console.log(this.env.pos.get_order());
            // ev.delegateTarget.parentElement.orderline.set_quantity("remove");
        },

    });

    // require("point_of_sale.screens").OrderWidget.include({
    //     // render_orderline: function() {
    //     //     var node = this._super.apply(this, arguments);

    //     //     $(node)
    //     //         .find(".remove-line-button")
    //     //         .on("click", null, this.remove_line.bind(this));

    //     //     return node;
    //     // },
    //     remove_line_btn: function(ev) {
    //         ev.delegateTarget.parentElement.orderline.set_quantity("remove");
    //     },
    // });

});

