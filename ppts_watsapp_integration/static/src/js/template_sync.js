odoo.define('ppts_watsapp_integration.action_whatsapp_def', function (require){
	"use strict";
	var core = require('web.core');
	var ListController = require('web.ListController');
	var rpc = require('web.rpc');
	var session = require('web.session');
	var _t = core._t;
	ListController.include({
		renderButtons: function($node) {
			this._super.apply(this, arguments);
			if (this.$buttons) {
				this.$buttons.find('.oe_action_whatsapp_sync').click(this.proxy('action_whatsapp_def'));
				this.$buttons.find('.oe_import_partner_mailing_def').click(this.proxy('import_partner_mailing_def'));
			}
		},

		action_whatsapp_def: function () {
			$.ajax({
				url: "/pos/whatsapp/template/sync",
				type: 'POST',
				async:false,
				data: {},
				success: function(result) {},
			});

		},

		import_partner_mailing_def: function () {
			$.ajax({
				url: "/mailing/list/partner/import",
				type: 'POST',
				async:false,
				data: {},
				success: function(result) {},
			});

		},

	});
});
