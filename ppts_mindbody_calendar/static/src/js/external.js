function promo_add_to_order() {
	console.log("function wrksss");
	$.ajax({
		url: "/event/calendar/promo",
		type: 'POST',
		async:false,
		data: {
			"promo": $("input[name=promo]").val(),
			"order": $("input[name=order]").val(),
		},
		success: function(result) {
			if(result === 'nopromo'){
				$.MessageBox("Promo Code Not Found");
			}
			if(result === 'applied'){
				$(".koh-tab-content-body").remove();
				$.ajax({
					url: "/get/sale/order/details",
					type: 'POST',
					async: false,
					data: {
						"sale_id": $("input[name=order]").val(),
					},
					success: function (result) {
						var resultJSON = jQuery.parseJSON(result);
						var list
						$.each(resultJSON, function (key, value) {
							list += "<div class='koh-tab-content-body'><div class='koh-faq'><div class='koh-faq-question' onclick='order_line_expend()'><div class='line-item-pt-icon'><i class='fa fa-chevron-right'></i></div>" +
							"<div class='line-item-pt-name' sale-order-line='" + value.line_id + "'>" + value.product_name + "</div>" +
							"<div class='line-item-pt-price'>" + value.product_price + value.product_currency + "</div></div>" +
							"<div class='koh-faq-answer lt-lane-add'><div class='lt-lane-details'>" +
							"<div class='line-item-pt-desc'> Paying for 1 service </div></div>" +
							"<div class='lt-lane-rmv'><a class='line-item-pt-desc-ed ul-line' href='/web#id=" + value.line_id + "&action=811&model=sale.order.line&view_type=form&cids=1&menu_id=216'>Edit</a>" +
							"<div class='ul-line'><a class='ul-line ul-line-rmv' href='/sale/order/line/rmv/" + value.line_id + "'>Remove</a></div></div></div></div></div>"

							$("#DIV_651").text(value.date);
							$("#DIV_661").text(value.sales_person);
							$("#DIV_656").text(value.address);
							partner_id = value.partner_id
							order_id = value.order_id
							$("#promo-order-id").val(order_id)
							$("input[name=partner_promo_id]").val(partner_id)

							$("#DIV_690").text(value.subtotal + value.product_currency);
							$("#DIV_696").text(value.taxes + value.product_currency);
							$("#DIV_699").text(value.total + value.product_currency);
						});


						// if (!$("div").hasClass("DIV_CONTENT_1")) {
						// 	$(".add-cart-lst-itemms").append("<span class='no-item-crt'>No item in cart</span>");
						// }

						var tt = list.substr(9);
						$(".line-item-cart").append(tt)

					},
				});
				$("input[name=promo]").val("")
			}

		},
	});


}

function order_line_expend() {
	var x = $(this).next();
	console.log(x)
	// if ($(x).css('display') === 'none' ) {
		$(this).next().css('display','block');
	// }else{
		// $(x).css('display','none');
	// }
}

function close_btn_app() {
	$('.bs-popover-right , .bs-popover-left').removeClass('show');
	$('.bs-popover-right , .bs-popover-left').addClass('hide');
	if ($(".fc-time-grid-event").hasClass("border-popover-highlight")) {
		$(".fc-time-grid-event").removeClass("border-popover-highlight");
	}
}


var prev = 0;
var $window = $(window);
var nav = $('.closeButton');


