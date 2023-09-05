odoo.define('ppts_event_recurrent.oe_recurrent_btn', function (require) {
    "use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                let filter_button = this.$buttons.find('.oe_recurrent_btn');
                filter_button && filter_button.click(this.proxy('oe_recurrent_btn')) ;
            }
        },
        oe_recurrent_btn: function () {
            var rpc = require('web.rpc');
            $(document).delegate(".oe_recurrent_btn", "click", function(){
              rpc.query({
                model: 'base.recurrent',
                method: 'recurrent',       
                args: [[1]],
            }).then(function(val){
              location.reload(true);
          })
        });
        }
    });
});