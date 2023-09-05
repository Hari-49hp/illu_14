$(document).ready(function () {
	odoo.define("website_sale.custom_website_sale", function (require) 
	{
	    "use strict";
	    $(".oe_website_sale").each(function () {
	     var oe_website_sale = this;
	        function onClickAdjustAdvance (event) {
	            $(".adjust_advance_grp").removeClass("d-none");
				$(".show_adjust_advance").addClass("d-none");
	        }
	        $(oe_website_sale).on("click", "a.show_adjust_advance",onClickAdjustAdvance );
	   });

	   $("#outstanding_payment_btn").click(function() {
			var partner_outstanding_payment = parseFloat(document.querySelector("#partner_outstanding_payment > td.text-xl-right.border-0 > span > span.oe_currency_value").innerText.replace(',', ''))
			var amount_total_order = parseFloat(document.querySelector("#order_total > td.text-xl-right > strong > span").innerText.replace(',', ''))
			var adjust_advance_field = parseFloat($(".adjust_advance_field").val())

			if (amount_total_order < adjust_advance_field){
				$(".outstanding_amt_alert").removeClass("oe_hidden");
				$(".adjust_for_pass_value").val("False");
				setTimeout(function(){ 
					$(".outstanding_amt_alert").addClass("oe_hidden");
				}, 15000);
			}
			else if (partner_outstanding_payment < adjust_advance_field){
				$(".outstanding_amt_alert_l").removeClass("oe_hidden");
				$(".adjust_for_pass_value").val("False");
				setTimeout(function(){ 
					$(".outstanding_amt_alert_l").addClass("oe_hidden");
				}, 15000);
			}
			else {
				$(".outstanding_amt_alert").addClass("oe_hidden");
				$(".outstanding_amt_alert_l").addClass("oe_hidden");
				$(".adjust_for_pass_value").val("True");
			}
		
		});
	});
	
});
