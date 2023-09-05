$(document).ready(function () {

	if ($("#event-multiselect-filter-location").length > 0) {
		$('#event-multiselect-filter-location').multiselect({
			// enableCaseInsensitiveFiltering: true,
			includeSelectAllOption: true,
			maxHeight: 400,
			dropUp: false,
			buttonContainer: '<div id="example-selected-parents-container"></div>',
			buttonText: function (options, select) {
				console.log(options, 'optionsoptionsoptionsoptions', select);

				return 'All Locations';
			},
			buttonTitle: function (options, select) {
				var labels = [];
				options.each(function () {
					labels.push($(this).text());
				});
				return labels.join(' - ');
			},
		});

		$("#event-multiselect-filter-location").multiselect('clearSelection');
		$("#event-multiselect-filter-location").change(function () {
			filter_ids = $('#event-multiselect-filter-location').val()
			if (filter_ids.length === 0) {
				filter_ids = '[]'
			}
			$.ajax({
				url: "/get/event/filter/popular/" + filter_ids,
				type: "get",
				async: false,
				dataType: 'json',
				success: function (result) {
					$('#MostPopularEvent').html(result.data);
				}
			});
					});

	}

});

function ClnToggleEventType(e) {
	$(".filter-buttons-lists button").removeClass('selectedbtn');
	$(e).addClass('selectedbtn');
	$('select[name="event_type"]').val($(e).attr('event-data'));
}






// Added by jana

document.addEventListener("DOMContentLoaded", function () {

	$('#event-warning').hide()


	function queryStringToObject(queryString) {
		const pairs = queryString.substring(1).split('&');
		// → ["foo=bar", "baz=buzz"]

		var array = pairs.map((el) => {
			const parts = el.split('=');
			return parts;
		});
		// → [["foo", "bar"], ["baz", "buzz"]]

		return Object.fromEntries(array);
		// → { "foo": "bar", "baz": "buzz" }
	}



	//start

	// Create Event
	const submit_appointment = document.querySelectorAll('#event-submit-appointment');

	// adding the event listener by looping
	submit_appointment.forEach(element => {

		element.addEventListener("click", (e) => {


			var check_name = $("#event_customer_name").val();
			var check_email = $("#event_email").val();
			var check_phone = $("#event_phone").val();
			var check_appointment_country_id = $("#event_appointment_country_id").val();
			var check_appointment_city_id = $("#event_appointment_city_id").val();
			var check_street = $("#event_street").val();

			if (check_name !== "" && check_email !== "" && check_phone !== "" && check_appointment_country_id !== "" && check_appointment_city_id !== "" && check_street !== "" && check_appointment_country_id !== null && check_appointment_city_id !== null) {


				if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(check_email)) {


					appointemt = [];
					var data = {};

					$("input").each(function () {

						var input_field = $(this);

						//alert('Type: ' + input_field.attr('type') + 'Name: ' + input_field.attr('id') + 'Value: ' + input_field.val());

						//var id = $(this).attr("title");
						//var email = $(this).val();

						data[input_field.attr('id')] = input_field.val()

					});

					$("select").each(function () {

						var input_field = $(this);

						data[input_field.attr('id')] = input_field.val()

					});

					var queryString = window.location.search;

					var pairs = queryStringToObject(queryString)



					//appointemt.push(data);


					//start of ajax

					$.ajax({
						url: "/event/ticket/create",
						type: 'POST',
						async: false,
						data: {
							'data': data,
							'queryString': pairs,
						},
						success: function (result) {


							var resultJSON = jQuery.parseJSON(result);

							$.each(resultJSON, function (key, value) {

								$('#customer_sale_id').val(value['customer_sale_id']);
								$('#customer_event_id').val(value['customer_event_id']);

							});


						},
					});


					//end of ajax

					var customer_event_id = $('#customer_event_id').val();
					var customer_sale_id = $('#customer_sale_id').val();

					//Odoo payment redirect page
					var newForm = document.createElement('form');
					newForm.setAttribute("method", "post"); // set it to post
					newForm.hidden = true; // hide it
					newForm.innerHTML = ""; // put the html sent by the server inside the form
					var url = window.location.origin;
					var action_url = url + "/event/checkout/shop/cart";
					newForm.setAttribute("action", action_url); // set the action url

					var event_id_ele = document.createElement("input");
					event_id_ele.setAttribute("type", "text");
					event_id_ele.setAttribute("name", "customer_event_id");
					event_id_ele.setAttribute("value", customer_event_id);

					var sale_id_ele = document.createElement("input");
					sale_id_ele.setAttribute("type", "text");
					sale_id_ele.setAttribute("name", "customer_sale_id");
					sale_id_ele.setAttribute("value", customer_sale_id);


					newForm.appendChild(event_id_ele);
					newForm.appendChild(sale_id_ele);
					$(document.getElementsByTagName('body')[0]).append(newForm); // append the form to the body
					newForm.submit();



				} else {

					$('#event-warning').text('Invalid Email ID!')
					$('#event-warning').show();

				}

			} else {

				$('#event-warning').text('Some mandatory fields are empty!')
				$('#event-warning').show();

			}


		});
	});
	//end	




	//start of ajax

	$.ajax({
		url: "/appointment/user/list",
		type: 'POST',
		async: false,
		data: {
		},
		success: function (result) {


			var resultJSON = jQuery.parseJSON(result);


			$.each(resultJSON, function (key, value) {


				$('#event_customer_name').val(value['name']);
				$('#event_email').val(value['email']);
				$('#event_phone').val(value['phone']);
				//$('#street').val(value['street']);

			});


		},
	});


	//end of ajax





	// Start

	var event_checkout_cart = document.querySelectorAll('#event-checkout-cart');

	event_checkout_cart.forEach(element => {

		element.addEventListener("click", (e) => {
		
				var data = {};
	
				var queryString = ""
	
				var event_id = $('#selected_event_id').val();
				var receiver_name = $('#receiver_name').val();
				var receiver_email = $('#receiver_email').val();
				var receiver_mobile = $('#receiver_mobile').val();
	
				var data_ticket_qty_id = document.querySelectorAll('#data-ticket-qty-id');
	
				data_ticket_qty_id.forEach(element => {
	
					data['ticket_id_' + element.getAttribute("data-ticket-id")] = element.textContent;
					queryString = queryString + "&ticket_id_" + element.getAttribute("data-ticket-id") + "=" + element.textContent
	
				});
	
	
				//alert(data);
				console.log(data);
				var url = window.location.origin;
	
	
				//var queryString = Object.keys(params).map(key => key + '=' + params[key]).join('&');
	
	
				url = url + "/event/checkout?event_id=" + event_id + queryString + '&receiver_name=' +receiver_name + '&receiver_email=' +receiver_email + '&receiver_mobile=' +receiver_mobile
				$(window.location)[0].replace(url);
				



		});
	});

	//end	




	// Start  
	var event_ticket_price_calcu_method = () => {

		// Start

		var event_ticket_price_calcu = document.querySelectorAll('#data-ticket-qty-id');
		var total_ticket_price = 0;
		event_ticket_price_calcu.forEach(element => {

			console.log(element.textContent)
			
			
			total_ticket_price += parseInt(element.getAttribute("data-ticket-qty-price")) * parseInt(element.textContent);
			// change the ticket price formula based on website 13-07-22
		// total_ticket_price =parseInt(element.textContent);

		});

		$('#total-ticket-price').text(total_ticket_price/2);



	};
	//end	





	// Start  
	var event_ticket_qty_add_method = () => {

		// Start

		var event_ticket_qty_add = document.querySelectorAll('#event-ticket-qty-add');

		event_ticket_qty_add.forEach(element => {

			element.addEventListener("click", (e) => {

				var ticket_id = e.currentTarget.getAttribute("data-ticket-id");
				var ticket_class = ".data-ticket-qty-" + ticket_id
				var ticket_price_class = "#data-ticket-price-" + ticket_id
				var ticket_price = $(ticket_price_class).val()

				var ticket_qty = parseInt($(ticket_class).html()) + 1;

				//alert(ticket_qty);

				$(ticket_class).text(ticket_qty);

				var ticket_price_class = ".data-ticket-price-" + ticket_id

				//$(ticket_price_class).text(ticket_price * ticket_qty);


				event_ticket_price_calcu_method();


			});
		});

	};
	//end	


	// Start  
	var event_ticket_qty_sub_method = () => {

		// Start

		var event_ticket_qty_sub = document.querySelectorAll('#event-ticket-qty-sub');

		event_ticket_qty_sub.forEach(element => {

			element.addEventListener("click", (e) => {

				var ticket_id = e.currentTarget.getAttribute("data-ticket-id");
				var ticket_class = ".data-ticket-qty-" + ticket_id
				var ticket_price_class = "#data-ticket-price-" + ticket_id
				var ticket_price = $(ticket_price_class).val()

				var ticket_qty = parseInt($(ticket_class).html()) - 1;

				//alert(ticket_qty);

				if (ticket_qty < 0) {

					$(ticket_class).text(0);

					var ticket_price_class = ".data-ticket-price-" + ticket_id

					//$(ticket_price_class).text(ticket_price * 0);

				} else {

					$(ticket_class).text(ticket_qty);

					var ticket_price_class = ".data-ticket-price-" + ticket_id

					//$(ticket_price_class).text(ticket_price * ticket_qty);

				}


				event_ticket_price_calcu_method();




			});
		});

	};
	//end
	
	
	// Start  
    var selected_event_reserve_method = () => {

        // Start

        var selected_event_reserve = document.querySelectorAll('#event-reserve-click');

        selected_event_reserve.forEach(element => {

            element.addEventListener("click", (e) => {
            
            
	            var proceed = 1;
			
			if ($("#gift-event-other").prop('checked') == true) {
			
				if ($("#receiver_name").val() == null || $("#receiver_name").val() == '') {
					proceed = 0;
					$("#receiver_name").addClass("reservation-input");
				}
				else if ($("#receiver_email").val() == null || $("#receiver_email").val() == '') {
					proceed = 0;
					$("#receiver_email").addClass("reservation-input");
				}
				else if ($("#receiver_mobile").val() == null || $("#receiver_mobile").val() == '') {
					proceed = 0;
					$("#receiver_mobile").addClass("reservation-input");
				}
				
			}
				
				
				
		
			if (proceed == 1) {

               var event_id = $('#selected_event_id').val();
               
               

                $('#event-reservation-popup').modal('hide');


                var car_tlist_container = document.querySelectorAll('.cart-list');

                car_tlist_container.forEach(element => {

                    element.remove();

                });



                $.ajax({
                    url: "/event/details",
                    type: 'POST',
                    async: false,
                    data: {
                        'event_id': event_id,
                    },
                    success: function (result) {
                        var resultJSON = jQuery.parseJSON(result);
                        $('.cart-list-container').empty();

                        $.each(resultJSON, function (key, value) {
                            $('.cart-list-container').append(`
				
			                                
			                             <div class="cart-list">
							              <div class="cart-left-info">
							
							                <h5>`+ value['ticket_name'] + `
							                  <span> <label class=" chipsone">`+ value['platform'] + `</label> <label class="chipsone">Event</label></span>
							
							                </h5>
							                
							                 
							
							                <div class="eventinfos">
							                  <label><i class="fas fa-map-marker-alt"></i> `+ value['location'] + ` </label>
							                  <label><i class="far fa-clock"></i> `+ value['duration'] + ` </label>
							                  <label><i class="far fa-calendar-minus"></i>`+ value['event_date'] + `</label>
							                  <label><i class="far fa-user"></i> `+ value['facilitator'] + `</label>
							                </div>
							              </div>
							              
							              <div class="cart-right-detinfo">
							                <div class="cardcountsection">
							                  Ticket <a class="addsubbtn" data-ticket-id="`+ value['ticket_id'] + `" id="event-ticket-qty-sub">-</a><b data-ticket-id="` + value['ticket_id'] + `" id="data-ticket-qty-id" data-ticket-qty-price="`+value['price']+`" class="data-ticket-qty-` + value['ticket_id'] + `">0</b><a class="addsubbtn" data-ticket-id="` + value['ticket_id'] + `" id="event-ticket-qty-add">+</a> <a class="closeicon"><i
							                      class="fas fa-times"></i></a>
							              </div>
							                
							                <input hidden type="text" value="`+ value['price'] + `" id="data-ticket-price-` + value['ticket_id'] + `"/>
							                
							                <h4 style="display:none"><b id="data-ticket-price-id" class="data-ticket-price-`+ value['ticket_id'] + `" >` + value['price'] + `</b>د.إ </h4>
							                <h4 ><b id="data-ticket-price-id_event" `+ value['ticket_id'] + `" >` + value['ticket_price'] + `</b>د.إ </h4>
							              </div>
							            </div>
			                                
			                                
			                                 
				
				                        `);
                        });

                    },
                });


                event_ticket_qty_add_method();
                event_ticket_qty_sub_method();
                event_ticket_price_calcu_method();
                
                

                $('#cart-popup').modal({
                    keyboard: false,
                    show: true,
                    focus: true
                })
                
                }

            });
        });

    };
    //end	


    
	// Start  
	var selected_upcoming_event_ID_method = () => {

		// Start

		var selected_event_id = document.querySelectorAll('#selected-upcoming-event-ID');

		selected_event_id.forEach(element => {

			element.addEventListener("click", (e) => {
				var event_id = e.currentTarget.getAttribute("data-event-id");
				
				

				$('#selected_event_id').val(event_id);


				var car_tlist_container = document.querySelectorAll('.cart-list');

				car_tlist_container.forEach(element => {

					element.remove();

				});

			

				$.ajax({
					url: "/event/details",
					type: 'POST',
					async: false,
					data: {
						'event_id': event_id,
					},
					success: function (result) {
						var resultJSON = jQuery.parseJSON(result);
						$('.cart-list-container').empty();

						$.each(resultJSON, function (key, value) {
							$('.cart-list-container').append(`
				
			                             <div class="cart-list">
							              <div class="cart-left-info">
							
							                <h5>`+ value['ticket_name'] + `
							                  <span> <label class=" chipsone">`+ value['platform'] + `</label> <label class="chipsone">Event</label></span>
							
							                </h5>
							                
							               
							
							                <div class="eventinfos">
							                  <label><i class="fas fa-map-marker-alt"></i> `+ value['location'] + ` </label>
							                  <label><i class="far fa-clock"></i> `+ value['duration'] + ` </label>
							                  <label><i class="far fa-calendar-minus"></i>`+ value['event_date'] + `</label>
							                  <label><i class="far fa-user"></i> `+ value['facilitator'] + `</label>
							                </div>
							              </div>
							              
							              </div>
							            </div>
			                                
			                                
			                                 
				
				                        `);
						});

					},
				});




				$(".event-gift-info").hide();

				//event_ticket_qty_add_method();
				//event_ticket_qty_sub_method();
				//event_ticket_price_calcu_method();
				
				$("#gift-event-myself").prop('checked', true);
				$("#gift-event-other").prop('checked', false);
				$("#receiver_name").removeClass("reservation-input");
				$("#receiver_email").removeClass("reservation-input");
				$("#receiver_mobile").removeClass("reservation-input");
				
				selected_event_reserve_method()
				
				$('#event-reservation-popup').modal({
		            keyboard: false,
		            show: true,
		            focus: true
		        })
		        
		        


			/* 
				$('#cart-popup').modal({
					keyboard: false,
					show: true,
					focus: true
				})

			*/




			});
		});

	};
	selected_upcoming_event_ID_method()
	//end	






	// Start  
	var selected_event_ID_method = () => {

		// Start

		var selected_event_id = document.querySelectorAll('#selected-event-ID');

		selected_event_id.forEach(element => {

			element.addEventListener("click", (e) => {
				var event_id = e.currentTarget.getAttribute("data-event-id");
				
				

				$('#selected_event_id').val(event_id);


				var car_tlist_container = document.querySelectorAll('.cart-list');

				car_tlist_container.forEach(element => {

					element.remove();

				});

			

				$.ajax({
					url: "/event/details",
					type: 'POST',
					async: false,
					data: {
						'event_id': event_id,
					},
					success: function (result) {
						var resultJSON = jQuery.parseJSON(result);
						$('.cart-list-container').empty();

						$.each(resultJSON, function (key, value) {
							$('.cart-list-container').append(`
				
			                             <div class="cart-list">
							              <div class="cart-left-info">
							
							                <h5>`+ value['ticket_name'] + `
							                  <span> <label class=" chipsone">`+ value['platform'] + `</label> <label class="chipsone">Event</label></span>
							
							                </h5>
							                
							               
							
							                <div class="eventinfos">
							                  <label><i class="fas fa-map-marker-alt"></i> `+ value['location'] + ` </label>
							                  <label><i class="far fa-clock"></i> `+ value['duration'] + ` </label>
							                  <label><i class="far fa-calendar-minus"></i>`+ value['event_date'] + `</label>
							                  <label><i class="far fa-user"></i> `+ value['facilitator'] + `</label>
							                </div>
							              </div>
							              
							              </div>
							            </div>
			                                
			                                
			                                 
				
				                        `);
						});

					},
				});




				$(".event-gift-info").hide();

				//event_ticket_qty_add_method();
				//event_ticket_qty_sub_method();
				//event_ticket_price_calcu_method();
				
				$("#gift-event-myself").prop('checked', true);
				$("#gift-event-other").prop('checked', false);
				$("#receiver_name").removeClass("reservation-input");
				$("#receiver_email").removeClass("reservation-input");
				$("#receiver_mobile").removeClass("reservation-input");
				
				selected_event_reserve_method()
				
				$('#event-reservation-popup').modal({
		            keyboard: false,
		            show: true,
		            focus: true
		        })
		        
		        


			/* 
				$('#cart-popup').modal({
					keyboard: false,
					show: true,
					focus: true
				})

			*/




			});
		});

	};
	//end	

	selected_event_ID_method();
	
	
	// Start
	var gift_event_myself = document.querySelectorAll('#gift-event-myself');

	gift_event_myself.forEach(element => {

			element.addEventListener("click", (e) => {
			
			
				$("#gift-event-other").prop('checked', false);
					
				$(".event-gift-info").hide();
				$('#receiver_name').val('');
				$('#receiver_email').val('');
				$('#receiver_mobile').val('');


			});

	});
	//end
	
	
	// Start
	var gift_event_other = document.querySelectorAll('#gift-event-other');

	gift_event_other.forEach(element => {

			element.addEventListener("click", (e) => {
				
				$("#gift-event-myself").prop('checked', false);
				$('#receiver_name').val('');
				$('#receiver_email').val('');
				$('#receiver_mobile').val('');
				$(".event-gift-info").show();



			});

	});
	//end		
	
	
	

});

// Event checkout city filter based on country
$("#event_appointment_country_id").change(function () {
	    $.ajax({
	        url: "/event_checkout/city/filter",
	        type: 'POST',
	        async: false,
	        data: {
	            'event_browse_country': $('#event_appointment_country_id').val(),
	        },
	        success: function (result) {
		    var resultJSON = jQuery.parseJSON(result);
		     $('.event_check_out_filters_id').empty();
			$('.event_check_out_filters_id').append(`
				<option value="" disabled="disabled" selected="selected">Select a City/Town</option>
                         `);

			$.each(resultJSON, function (key, value) {
				$('.event_check_out_filters_id').append(`
							
			<option value="`+ value['id'] + `">` + value['name'] + `</option>
                                
                         `);

			});


        },
    });


});


