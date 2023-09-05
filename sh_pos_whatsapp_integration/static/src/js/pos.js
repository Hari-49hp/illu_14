odoo.define("sh_pos_whatsapp_integration.WhatsappMessagePopup", function (require) {
    "use strict";

    const { useState, useSubEnv } = owl.hooks;
    const PosComponent = require("point_of_sale.PosComponent");
    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    const Registries = require("point_of_sale.Registries");

    class WhatsappMessagePopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            useSubEnv({ attribute_components: [] });
        }
    }
    WhatsappMessagePopup.template = "WhatsappMessagePopup";

    Registries.Component.add(WhatsappMessagePopup);

    return {
        WhatsappMessagePopup,
    };
});

odoo.define("sh_pos_whatsapp_integration.ReceiptScreen", function (require) {
    "use strict";
    const ReceiptScreen = require("point_of_sale.ReceiptScreen");
    const Registries = require("point_of_sale.Registries");
    const { useBarcodeReader } = require("point_of_sale.custom_hooks");
    const { useListener } = require("web.custom_hooks");

    const WPReceiptScreen = (ReceiptScreen) =>
    class extends ReceiptScreen {
        constructor() {
            super(...arguments);
            useListener("click-send_wp", this.on_click_send_wp);
            useListener("click-send_wp_dierct", this.on_click_send_wp_direct);
        }
        async on_click_send_wp_direct(event) {
            var message = "";
            var self = this;

            const partner = this.currentOrder.get_client();
            if (partner.mobile) {
                var mobile = partner.mobile;
                var order = this.currentOrder;
                var receipt = this.currentOrder.export_for_printing();
                var orderlines = this.currentOrder.get_orderlines();
                var paymentlines = this.currentOrder.get_paymentlines();
                message +=
                "Dear " +
                partner.name +
                "," +
                "%0A%0A" +
                "Here is the order " +
                "*" +
                receipt.name +
                "*" +
                " amounting in " +
                "*" +
                receipt.total_with_tax.toFixed(2) +
                "*" +
                "" +
                receipt.currency.symbol +
                " from " +
                receipt.company.name +
                "%0A%0A";
                if (receipt.orderlines.length > 0) {
                    message += "Following is your order details." + "%0A";
                    _.each(receipt.orderlines, function (orderline) {
                        message += "%0A" + "*" + orderline.product_name + "*" + "%0A" + "*Qty:* " + orderline.quantity + "%0A" + "*Price:* " + orderline.price + "" + receipt.currency.symbol + "%0A";
                        if (orderline.discount > 0) {
                            message += "*Discount:* " + orderline.discount + "%25" + "%0A";
                        }
                    });
                    message += "________________________" + "%0A";
                }
                message += "*" + "Total Amount:" + "*" + "%20" + receipt.total_with_tax.toFixed(2) + "" + receipt.currency.symbol;
                if (this.env.pos.user.sign) {
                    message += "%0A%0A%0A" + this.env.pos.user.sign;
                }
                $(".default-view").append('<a class="wp_url" target="blank" href=""><span></span></a>');
                var href = "https://web.whatsapp.com/send?l=&phone=" + mobile + "&text=" + message.replace('&','%26');
                $(".wp_url").attr("href", href);
                $(".wp_url span").trigger("click");
            }
        }
        async on_click_send_wp(event) {
            var message = "";
            var self = this;
            // $('#whatsapp_template_send').selectpicker();
            const partner = this.currentOrder.get_client();
            if (partner.mobile) {
                var mobile = partner.mobile;
                var order = this.currentOrder;
                var receipt = this.currentOrder.export_for_printing();
                var orderlines = this.currentOrder.get_orderlines();
                var paymentlines = this.currentOrder.get_paymentlines();


                // message +=
                // "Dear " +
                // partner.name +
                // "," +
                // "%0A%0A" +
                // "Here is the order " +
                // "*" +
                // receipt.name +
                // "*" +
                // " amounting in " +
                // "*" +
                // receipt.total_with_tax.toFixed(2) +
                // "*" +
                // "" +
                // receipt.currency.symbol +
                // " from " +
                // receipt.company.name +
                // "%0A%0A";
                // if (receipt.orderlines.length > 0) {
                //     message += "Following is your order details." + "%0A";
                //     _.each(receipt.orderlines, function (orderline) {
                //         message += "%0A" + "*" + orderline.product_name + "*" + "%0A" + "*Qty:* " + orderline.quantity + "%0A" + "*Price:* " + orderline.price + "" + receipt.currency.symbol + "%0A";
                //         if (orderline.discount > 0) {
                //             message += "*Discount:* " + orderline.discount + "%25" + "%0A";
                //         }
                //     });
                //     message += "________________________" + "%0A";
                // }
                // message += "*" + "Total Amount:" + "*" + "%20" + receipt.total_with_tax.toFixed(2) + "" + receipt.currency.symbol;
                // if (this.env.pos.user.sign) {
                //     message += "%0A%0A%0A" + this.env.pos.user.sign;
                // }
                setTimeout(function(){
                    $.ajax({
                        url: "/mail/whatsapp/template",
                        type: 'POST',
                        async:false,
                        data: {},
                        success: function(result) {
                            var resultJSON = jQuery.parseJSON(result);
                            $.each(resultJSON,function(key,value){
                                $('#whatsapp_template_send').append($('<option></option>').attr("value", key).text(value)); 
                            });
                        },
                    });
                }, 500);

                const { confirmed } = await this.showPopup("WhatsappMessagePopup", {
                    mobile_no: partner.mobile,
                    // message: message.replace('&','%26'),
                    confirmText: "Send",
                    cancelText: "Cancel",

                });
                if (confirmed) {

                    var text_msg = $('textarea[name="message"]').val();
                    var mobile = $(".mobile_no").val();

                    if (text_msg && mobile) {
                            // var href = "https://web.whatsapp.com/send?l=&phone=" + mobile + "&text=" + text_msg.replace('&','%26');
                            // $(".wp_url").attr("href", href);
                            // $(".wp_url span").trigger("click");
                            $.ajax({
                                url: "/pos/whatsapp/message",
                                type: 'POST',
                                async:false,
                                data: {
                                    "mobile":mobile,
                                    "text_msg":text_msg,
                                    "name":partner.name,
                                    "template_id":$("#whatsapp_template_send").val(),
                                },
                                success: function(result) {
                                    console.log(result);
                                    if (result === 'success' || result === 'true'){
                                        $.MessageBox("Message Send Successful");
                                    }
                                    else{
                                        $.MessageBox("Message Send Failed");
                                    }
                                },
                            });


                        } 
                        else if($("#whatsapp_template_send").val() != 'false'){
                            $.ajax({
                                url: "/pos/whatsapp/message",
                                type: 'POST',
                                async:false,
                                data: {
                                    "mobile":mobile,
                                    "text_msg":text_msg,
                                    "name":partner.name,
                                    "template_id":$("#whatsapp_template_send").val(),
                                },
                                success: function(result) {
                                    if (result === 'success'){
                                        $.MessageBox("Message Send Successful");
                                    }
                                    else{
                                        $.MessageBox("Message Send Failed");
                                    }
                                },
                            });
                        }
                        else {
                            $.MessageBox("Please Enter Message.");
                        }
                    }
                }
            }
        };

        Registries.Component.extend(ReceiptScreen, WPReceiptScreen);

        return ReceiptScreen;
    });
odoo.define("sh_pos_whatsapp_integration.ClientListScreen", function (require) {
    "use strict";
    const ClientListScreen = require("point_of_sale.ClientListScreen");
    const Registries = require("point_of_sale.Registries");
    const { useBarcodeReader } = require("point_of_sale.custom_hooks");
    const { useListener } = require("web.custom_hooks");

    const WPClientListScreen = (ClientListScreen) =>
    class extends ClientListScreen {
        constructor() {
            super(...arguments);
            useListener("click-send_wp", this.on_click_send_wp);
        }
        async on_click_send_wp(event) {
            var message = "";
            var self = this;
            if (this.env.pos.user.sign) {
                message += "%0A%0A%0A" + this.env.pos.user.sign;
            }
            const partner = event.detail;

            const { confirmed } = await this.showPopup("WhatsappMessagePopup", {
                mobile_no: partner.mobile,
                message: message.replace('&','%26'),
                confirmText: "Send",
                cancelText: "Cancel",
            });
            if (confirmed) {
                var text_msg = $('textarea[name="message"]').val();
                var mobile = $(".mobile_no").val();
                if (text_msg && mobile) {
                    var href = "https://web.whatsapp.com/send?l=&phone=" + mobile + "&text=" + text_msg.replace('&','%26');
                    $(".wp_url").attr("href", href);
                    $(".wp_url span").trigger("click");
                } else {
                    alert("Please Enter Message.");
                }
            }
        }
    };

    Registries.Component.extend(ClientListScreen, WPClientListScreen);

    return ClientListScreen;
});

odoo.define("sh_pos_whatsapp_integration.screens", function (require) {
    "use strict";

    var models = require("point_of_sale.models");

    var core = require("web.core");
    var rpc = require("web.rpc");
    var DB = require("point_of_sale.DB");

    models.load_fields("res.users", ["sign"]);
    models.load_fields("res.partner", ["lang", "mobile"]);
    //
    //    var WhatsappMessagePopup = PopupWidget.extend({
    //        template: 'WhatsappMessagePopup',
    //        init: function(parent, args) {
    //            this._super(parent, args);
    //
    //        },
    //        show: function(options){
    //
    //        	this.partner_id = options.partner_id || "";
    //        	this.mobile = options.mobile || "";
    //        	this.message = options.message || "";
    //            options = options || {};
    //            this._super(options);
    //
    //            var self = this;
    //            $('input[name="mobile_no"]').val(this.mobile);
    //            $('textarea[name="message"]').val(this.message);
    //
    //            this.$('.confirm').click(function(e) {
    //                e.preventDefault();
    //                var text_msg = $('textarea[name="message"]').val()
    //                if(text_msg){
    //
    //                    var href = "https://web.whatsapp.com/send?l=&phone="+self.mobile+"&text=" +text_msg
    //                    self.$('.wp_url').attr("href",href);
    //                    self.$('.wp_url span').trigger('click');
    //
    //                }else{
    //                	alert("Please Enter Message.")
    //                }
    //
    //            });
    //
    //        }
    //    });
    //    gui.define_popup({name:'send_whatsapp_message', widget: WhatsappMessagePopup});
    //
    //
    //    screens.ClientListScreenWidget.include({
    //    	 show: function(){
    //    	        var self = this;
    //    	        this._super();
    //    	        this.$('.client-list-contents').delegate('.send_wp','click',function(event){
    //    	        	 self.wp_line_select(event,parseInt($(this).data('id')));
    //    	        });
    //    	 },
    //    	 wp_line_select: function(event,id){
    //    		var partner = this.pos.db.get_partner_by_id(id);
    //    		var self = this;
    //    		var message = '';
    //    		if(self.pos.user.sign){
    //				 message += "%0A%0A%0A"+self.pos.user.sign
    //			}
    //
    //        	self.gui.show_popup('send_whatsapp_message',{
    //        		'partner_id':id,
    //        		'mobile':partner.mobile,
    //        		'message':message
    //        	});
    //    	 },
    //
    //    });
    //    screens.ReceiptScreenWidget.include({
    //
    //    	 renderElement: function() {
    //    		 var self = this;
    //    	     this._super();
    //    	     this.$('.button.send_wp').click(function(){
    //    	    	 if(self.pos.get_order() &&  self.pos.get_order().get_client()){
    //    	    		 var partner = self.pos.get_order().get_client()
    //    	    		 if(partner.mobile){
    //    	    			 var mobile = partner.mobile
    //    	    			 var order = self.pos.get_order()
    //    	    			 var receipt= order.export_for_printing();
    //    	    			 var orderlines=order.get_orderlines();
    //    	    			 var paymentlines=order.get_paymentlines();
    //    	    			 var message = '';
    //    	    			 var language_arr = ['es_AR','es_BO','es_CL','es_CO','es_CR','es_DO','es_EC','es_GT','es_MX','es_PA','es_PE','es_PY','es_UY','es_VE','es_ES'];
    //    	    			 var is_lng_found = language_arr.indexOf(partner.lang);
    //
    //    	    			 if(is_lng_found != (-1)){
    //    	    				 message = "Estimado "+receipt.client+","+"%0A%0A"+"Resumen de su pedido: %0A"+'*'+receipt.name+'*'+" por un total de "+'*'+(receipt.total_with_tax).toFixed(2)+'*'+""+receipt.currency.symbol+" en "+receipt.company.name+"%0A%0A"
    //        	    			 if(receipt.orderlines.length >0){
    //        	    				 message += "Detalle de su orden: "+"%0A"
    //        	    				 _.each(receipt.orderlines, function (orderline) {
    //        	    					 message += "%0A"+"*"+orderline.product_name+"*"+"%0A"+"*Cantidad:* "+orderline.quantity+"%0A"+"*Precio:* "+orderline.price+""+receipt.currency.symbol+"%0A"
    //        	     	    			if(orderline.discount>0){
    //        	     	    				message+= "*Descuento:* "+orderline.discount+"%25"+"%0A"
    //        	     	    			}
    //        	    			       });
    //        	    				 message += "________________________"+"%0A"
    //        	    			 }
    //        	    			 message += "*"+"Total:"+"*"+"%20"+(receipt.total_with_tax).toFixed(2)+""+receipt.currency.symbol
    //        	    			 if(self.pos.user.sign){
    //        	    				 message += "%0A%0A%0A"+self.pos.user.sign
    //        	    			 }
    //    	    			 }else{
    //    	    				 message = "Dear "+receipt.client+","+"%0A%0A"+"Here is the order "+'*'+receipt.name+'*'+" amounting in "+'*'+(receipt.total_with_tax).toFixed(2)+'*'+""+receipt.currency.symbol+" from "+receipt.company.name+"%0A%0A"
    //        	    			 if(receipt.orderlines.length >0){
    //        	    				 message += "Following is your order details."+"%0A"
    //        	    				 _.each(receipt.orderlines, function (orderline) {
    //        	    					 message += "%0A"+"*"+orderline.product_name+"*"+"%0A"+"*Qty:* "+orderline.quantity+"%0A"+"*Price:* "+orderline.price+""+receipt.currency.symbol+"%0A"
    //        	     	    			if(orderline.discount>0){
    //        	     	    				message+= "*Discount:* "+orderline.discount+"%25"+"%0A"
    //        	     	    			}
    //        	    			       });
    //        	    				 message += "________________________"+"%0A"
    //        	    			 }
    //        	    			 message += "*"+"Total Amount:"+"*"+"%20"+(receipt.total_with_tax).toFixed(2)+""+receipt.currency.symbol
    //        	    			 if(self.pos.user.sign){
    //        	    				 message += "%0A%0A%0A"+self.pos.user.sign
    //        	    			 }
    //    	    			 }
    //
    //
    //        	    		 self.gui.show_popup('send_whatsapp_message',{
    //         	        		'partner_id':partner.id,
    //         	        		'mobile':partner.mobile,
    //         	        		'message':message
    //         	        	});
    //    	    		 }else{
    //    	    			 alert("Mobile Number Not Found !")
    //    	    		 }
    //
    //    	    	 }
    //
    //    	     });
    //    	     this.$('.button.send_wp_direct').click(function(){
    //
    //
    //
    //
    //    	    	 if(self.pos.get_order() &&  self.pos.get_order().get_client()){
    //    	    		 var partner = self.pos.get_order().get_client()
    //    	    		 if(partner.mobile){
    //    	    			 var mobile = partner.mobile
    //    	    			 var order = self.pos.get_order()
    //    	    			 var receipt= order.export_for_printing();
    //    	    			 var orderlines=order.get_orderlines();
    //    	    			 var paymentlines=order.get_paymentlines();
    //    	    			 var message = '';
    //    	    			 var language_arr = ['es_AR','es_BO','es_CL','es_CO','es_CR','es_DO','es_EC','es_GT','es_MX','es_PA','es_PE','es_PY','es_UY','es_VE','es_ES'];
    //    	    			 var is_lng_found = language_arr.indexOf(partner.lang);
    //
    //    	    			 if(is_lng_found != (-1)){
    //    	    				 message = "Estimado "+receipt.client+","+"%0A%0A"+"Resumen de su pedido: %0A"+'*'+receipt.name+'*'+" por un total de "+'*'+(receipt.total_with_tax).toFixed(2)+'*'+""+receipt.currency.symbol+" en "+receipt.company.name+"%0A%0A"
    //        	    			 if(receipt.orderlines.length >0){
    //        	    				 message += "Detalle de su orden: "+"%0A"
    //        	    				 _.each(receipt.orderlines, function (orderline) {
    //        	    					 message += "%0A"+"*"+orderline.product_name+"*"+"%0A"+"*Cantidad:* "+orderline.quantity+"%0A"+"*Precio:* "+orderline.price+""+receipt.currency.symbol+"%0A"
    //        	     	    			if(orderline.discount>0){
    //        	     	    				message+= "*Descuento:* "+orderline.discount+"%25"+"%0A"
    //        	     	    			}
    //        	    			       });
    //        	    				 message += "________________________"+"%0A"
    //        	    			 }
    //        	    			 message += "*"+"Total:"+"*"+"%20"+(receipt.total_with_tax).toFixed(2)+""+receipt.currency.symbol
    //        	    			 if(self.pos.user.sign){
    //        	    				 message += "%0A%0A%0A"+self.pos.user.sign
    //        	    			 }
    //    	    			 }else{
    //    	    				 message = "Dear "+receipt.client+","+"%0A%0A"+"Here is the order "+'*'+receipt.name+'*'+" amounting in "+'*'+(receipt.total_with_tax).toFixed(2)+'*'+""+receipt.currency.symbol+" from "+receipt.company.name+"%0A%0A"
    //        	    			 if(receipt.orderlines.length >0){
    //        	    				 message += "Following is your order details."+"%0A"
    //        	    				 _.each(receipt.orderlines, function (orderline) {
    //        	    					 message += "%0A"+"*"+orderline.product_name+"*"+"%0A"+"*Qty:* "+orderline.quantity+"%0A"+"*Price:* "+orderline.price+""+receipt.currency.symbol+"%0A"
    //        	     	    			if(orderline.discount>0){
    //        	     	    				message+= "*Discount:* "+orderline.discount+"%25"+"%0A"
    //        	     	    			}
    //        	    			       });
    //        	    				 message += "________________________"+"%0A"
    //        	    			 }
    //        	    			 message += "*"+"Total Amount:"+"*"+"%20"+(receipt.total_with_tax).toFixed(2)+""+receipt.currency.symbol
    //        	    			 if(self.pos.user.sign){
    //        	    				 message += "%0A%0A%0A"+self.pos.user.sign
    //        	    			 }
    //    	    			 }
    //
    //    	    			 self.$('.centered-content').append('<a class="wp_url" target="blank" href=""><span></span></a>');
    //    	    		     var href = "https://web.whatsapp.com/send?l=&phone="+mobile+"&text=" +message
    //   	    		      	 self.$('.wp_url').attr("href",href);
    //    	    		     self.$('.wp_url span').trigger('click');
    //
    //
    //    	    		 }else{
    //    	    			 alert("Mobile Number Not Found !")
    //    	    		 }
    //
    //    	    	 }
    //    	     });
    //    	 },
    //    });
    //
});
