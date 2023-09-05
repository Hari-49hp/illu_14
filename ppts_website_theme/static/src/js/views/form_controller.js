odoo.define('ppts_website_theme.FormController', function (require) {
"use strict";

var core = require('web.core');
var FormController = require('web.FormController');
var FormRenderer = require('web.FormRenderer');
var session = require('web.session');
var _t = core._t;
var ListRenderer = require('web.ListRenderer');

localStorage.setItem("open_log","0");

// window.onload = function(){ 
// 			setTimeout( 
// 				function(){ 
// 				session.user_has_group('ppts_custom_event_mgmt.group_admin').then(function(has_group) {
// 						if (has_group) {
						
// 							if ($("body").hasClass("o_home_menu_background") == false) {
// 								$(".header-client-add-btn").show()
// 							} else {
// 								$(".header-client-add-btn").hide()
// 							}
						
// 						} else {
// 							$(".header-client-add-btn").hide()
// 						}
// 					});
// 				}, 2500); 
// 			}

FormController.include({
	_onEdit: function () {
    	localStorage.setItem("open_log","edit");
    	this._super.apply(this, arguments);
    },
	saveRecord: async function () {
		if (localStorage.getItem("open_log") == "edit") {
				localStorage.setItem("open_log","1");
			}
		return this._super.apply(this, arguments);
	},
});

ListRenderer.include({
	 _onRowClicked: function (ev) {
	 	localStorage.setItem("open_log","0");
        this._super.apply(this, arguments);
    },
});

FormRenderer.include({
		 _updateView: function () {
            this._super.apply(this, arguments);
            var self = this;
            session.user_has_group('ppts_custom_event_mgmt.group_admin').then(function(has_group) {
           		// if (has_group) {
           		// 	self.$el.find('.o_FormRenderer_chatterContainer').find('.o_ChatterTopbar_actions').show() 
           		// 	$(".header-client-add-btn").show()
           		// } else {
           		// 	self.$el.find('.o_FormRenderer_chatterContainer').find('.o_ChatterTopbar_actions').hide() 
           		// 	$(".header-client-add-btn").hide()
           		// }
            });
            
            if (this.state.model == "res.partner") {
            	
            	if (this.state.res_id) {
            			this.$el.find('.o_FormRenderer_chatterContainer').show();
            			localStorage.setItem("open_log", "0");
		            } else {
		            	this.$el.find('.o_FormRenderer_chatterContainer').hide();
		            	$(".toggle_btn_chatter").hide()
	            	} 
            	
            
            } else {
            
	             if (localStorage.getItem("open_log") == "0" || localStorage.getItem("open_log") == "edit") {
	            	this.$el.find('.o_FormRenderer_chatterContainer').hide();
	            	$(".toggle_btn_chatter").hide()
		            } else {
		            	if(localStorage.getItem("open_log") == "1"){
		            		localStorage.setItem("open_log", "0");
		            		}
		            	this.$el.find('.o_FormRenderer_chatterContainer').show();
	            	} 
            
            }
           
        },
});

});

