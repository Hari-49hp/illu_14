
// $(document).ready(function () {
    
//     setTimeout(function(){ 
                
//                 $("#list_view_partner_osc_create").click(function(){
                
//         window.location.href = "/web#action=665&cids=1&id=&menu_id=476&model=availability.availability&view_type=form";
//     });

//                  }, 3000);

    

// });


// odoo.define('custom_partner.action_button', function (require) {
// "use strict";
// var core = require('web.core');
// var ListController = require('web.ListController');
// var rpc = require('web.rpc');
// var session = require('web.session');
// var _t = core._t;
// ListController.include({
//    renderButtons: function($node) {
//    this._super.apply(this, arguments);
//        if (this.$buttons) {
//          this.$buttons.find('.oe_action_button').click(this.proxy('receive_invoice')) ;
//        }
//    },
// receive_invoice: function () {
//             var self = this
//             var user = session.uid;
            
//             self.do_action({
//                 name: _t('Contact'),
//                 type: 'ir.actions.act_window',
//                 res_model: 'res.partner',
//                 views: [[false, 'form']],
//                 view_mode: 'form',
//                 target: 'new',
//             });
//             window.location
//         });
// },
// odoo.define('custom_partner.dialer_button', function (require) {
// "use strict";
// const core = require('web.core');
// get the id of the template 07-09-22
function open_dialler_func(){
	document.getElementById('voip_dialler_ids').click();
}
