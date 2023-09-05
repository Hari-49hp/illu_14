
odoo.define('pos_credit_payment.pos', function (require) {
	"use strict";

	var models = require('point_of_sale.models');
	var core = require('web.core');
	var rpc = require('web.rpc');
	

	var _t = core._t;

	var _super_posmodel = models.PosModel.prototype;
	models.PosModel = models.PosModel.extend({
		initialize: function (session, attributes) {
			var partner_model = _.find(this.models, function(model){ return model.model === 'res.partner'; });
			partner_model.fields.push('custom_credit');
			var journal_model = _.find(this.models, function(model){ return model.model === 'pos.payment.method'; });
			journal_model.fields.push('credit_jr','cash_journal_id');
			return _super_posmodel.initialize.call(this, session, attributes);

		},
		
		setdigit: function(amount, digit=0) {
        	return amount.toFixed(digit);
    	},
    	
    	_update_payment_info: function (order, return_ref) {
			rpc.query({
	                model: 'pos.order',
	                method: 'get_payment_info',
	                args: [order, return_ref],
	            }).then(function (result) {
	            	if (result[0]) {
	            		$(".pos-customer-payment-cheque").text(result[0].cheque);
	            		$(".pos-customer-payment-method").text(result[0].payment_method);
	            		$(".pos-customer-payment").show();
	            	} else {
	            		$(".pos-customer-payment").hide();
	            	}
	            })
	            
	   },
    	
    	
	});

	let OrderSuper = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function(attributes, options) {
			let res = OrderSuper.initialize.apply(this, arguments);
			let self = this;
			setInterval(function(){ 
				self.pos.load_new_partners();
			}, 5000);
		},
	});
});
