$(document).ready(function () {
	$.ajax({
		url: "/event/fasi/location",
		type: 'POST',
		async:false,
		data: {
		},
		success: function(result) {
			var resultJSON = jQuery.parseJSON(result);
			$.each(resultJSON, function(key, value) {   
				$('#facilitator_location').append($('<option></option>').attr("value", key).text(value));
			});
		},
	});
	
	$.ajax({
		url: "/availability/services/type",
		type: 'POST',
		async:false,
		data: {
		},
		success: function(result) {
			var resultJSON = jQuery.parseJSON(result);
			$.each(resultJSON,function(key,value){
				$('#services_type').append($('<option></option>').attr("value", key).text(value)); 
			});
		},
	});

	$.ajax({
		url: "/event/type/css",
		type: 'POST',
		async:true,
		data: {
			// "unavail_name": $(".side-bar-name").text()
		},
		success: function(result) {
			var resultJSON = jQuery.parseJSON(result);
			$.each(resultJSON, function(key, value) {   
				// $('#facilitator_location').append($('<option></option>').attr("value", key).text(value));
				$('.'+value).css({"background-color":key,"border-color":key});
			});
		},
	});

	$(".add-unavailability-ajax").click(function(){
		$.ajax({
			url: "/event/calendar/add-unavailability",
			type: 'POST',
			async:true,
			data: {
				"unavail_name": $(".side-bar-name").text()
			},
			success: function(result) {
				window.location.href = "/web#action=665&cids=1&id=&menu_id=476&model=availability.availability&view_type=form";
			},
		});
	});

	$(".add-view-profile-ajax").click(function(){
		$.ajax({
			url: "/event/calendar/view-profile",
			type: 'POST',
			async:true,
			data: {
				"unavail_name": $(".side-bar-name").text()
			},
			success: function(result) {
				window.location.href = result
			},
		});
	});

	$('.header_location').on('change',function(){
		console.log('sdgvf')
		$.ajax({
			url: "/event/calendar/resources/pass/session",
			type: 'POST',
			async:false,
			data: {
				"header_location": $(".header_location").val(),
			},
			success: function(result) {
			},
		});
	});
	// $(".fc-prev-button").click(function(){
	// 	localStorage.setItem("fullcalendar-date", $('#calendar-event-mindbody > div.fc-toolbar.fc-header-toolbar > div.fc-left > h2').text());
	// });

	// $(".fc-next-button").click(function(){
	// 	localStorage.setItem("fullcalendar-date", $('#calendar-event-mindbody > div.fc-toolbar.fc-header-toolbar > div.fc-left > h2').text());
	// });

	// $(".fc-today-button").click(function(){
	// 	localStorage.setItem("fullcalendar-date", "today");
	// });

	$("#searchbar-button").click(function(){
		$("#editAvail").css("display", "none");
		$("#editAvail-client-add").css("display", "block");
		$(".page-footer").css("display", "block");
		console.log(this);
		$.ajax({
			url: "/partner/list/search",
			type: 'POST',
			async:false,
			data: {
				"partner": $("#searchbar").val(),
			},
			success: function(result) {
				console.log(result,1111);
				var details = result.split("$$");
				$(".editAvail-client-name").text($("#searchbar").val());
				$("#editAvail-client-name-fi").val($("#searchbar").val());
				$(".editAvail-client-phone").text(details[0]);
				$("#editAvail-client-phone-fi").val(details[0]);
				// $(".editAvail-client-email").attr("href","mailto:"+details[1]);
				var datel = new Date($('#calendar-event-mindbody > div.fc-toolbar.fc-header-toolbar > div.fc-left > h2').text());
				var day = ("0" + datel.getDate()).slice(-2);
				var month = ("0" + (datel.getMonth() + 1)).slice(-2);
				var today = datel.getFullYear()+"-"+(month)+"-"+(day);
				$("#editAvail-client-date-fi").val(today);

				$("#editAvail-client-email-fi").val(details[1]);

				$("#editAvail-client-name-id").val(details[2]);
			},
		});
		// $("#editAvail-client-add").css("display", "none");
		$("#editAvail").css("display", "none");
		$(".DIV_PAST_1_DISABLE").css("display", "block");



		$.ajax({
			url: "/rebook/app/calendar",
			type: 'POST',
			async:false,
			data: {
				"partner": $("#searchbar").val(),
			},
			success: function(result) {
				
			},
		});


	});

	$("#tab-payment-balance").hover(function () {
		$(".tab-payment-balance-show").css("display", "block");
	}, function () {
		$(".tab-payment-balance-show").css("display", "none");
	});

	$("#tab-payment-status").hover(function () {
		$(".tab-payment-status-show").css("display", "block");
	}, function () {
		$(".tab-payment-status-show").css("display", "none");
	});

	$("#tab-pre-payment").hover(function () {
		$(".tab-pre-payment-show").css("display", "block");
	}, function () {
		$(".tab-pre-payment-show").css("display", "none");
	});


	$("#DIV_27 > svg,#SPAN_bottom_btn20").click(function(){
		$("#popper-wizard").css("display", "none");
		location.reload();
	});

	$(".promo-input-class").click(function(){
		$(".promo-input-class").css("display", "none");
		$(".promo-input-div").css("display", "block");
	});

	$("#promo-cancel-btn").click(function(){
		$(".promo-input-class").css("display", "flex");
		$(".promo-input-div").css("display", "none");
	});


	var location_option
	var services_option
	$.ajax({
		url: "/event/calendar/resources/location/resajax",
		type: 'POST',
		async: false,
		data: {},
		success: function(result) {
			var resultJSON = jQuery.parseJSON(result);
			$.each(resultJSON, function(key, value) {
				$('#header_location').append($('<option></option>').attr("value", key).text(value));
			});
		},
	});
	$.ajax({
		url: "/event/calendar/resources/services/resajax",
		type: 'POST',
		async: false,
		data: {},
		success: function(result) {
			var resultJSON = jQuery.parseJSON(result);
			$.each(resultJSON, function(key, value) {
				$('#header_services').append($('<option></option>').attr("value", key).text(value));
			});
		},
	});
	// $('#header_instructor-filter').multiselect('selectAll', false);

	$(".rebook_disable").click(function(){
		$(".DIV_PAST_1_DISABLE").css("display", "block");
		$(".DIV_PAST_1_ENABLE").css("display", "none");
	});

	$(".rebook_enable").click(function(){
		$(".DIV_PAST_1_DISABLE").css("display", "none");
		$(".DIV_PAST_1_ENABLE").css("display", "block");
	});

	$("#DIV_PAST_6 li").click(function(){
		$('#DIV_PAST_6 li').removeClass('DIV_PAST_6_active');
		$(this).addClass('DIV_PAST_6_active');
	});

	$(".add-client-set-addon-cancel").click(function(){
		$("#editAvail").css("display","none");
		$(".colorbysessiontype").css("display","block");
	});

	$('#services_type').multiselect({
		allSelectedText: 'All Services',
		// enableFiltering: true,
		includeSelectAllOption: true
		// dropUp: true
	});

	$("#addAvail > div.well.clean > ul > li:nth-child(2) > div > span > div > button").click(function(){
		$("#addAvail > div.well.clean > ul > li:nth-child(2) > div > span > div > div").css("position","inherit !important");
		$("#addAvail > div.well.clean > ul > li:nth-child(2) > div > span > div > div").css("top","-34px !important");
	});

	// $('.multipleSelect').fastselect();
	   //  max-height: 400px;
    // overflow: hidden auto;
    // position: inherit;
    // transform: translate3d(0px, 34px, 0px);
    // top: -34px;
    // left: 0px;
    // will-change: transform;

    // $('#services_type').selectpicker();




	$("#empty_star").click(function(){
		// $("#empty_star").css("display","none");
		// $("#gold_star").css("display","block");
		console.log("EMPTY STAR")
	});
	$("#gold_star").click(function(){
		// $("#gold_star").css("display","none");
		// $("#empty_star").css("display","block");
		console.log("GOLD STAR")
	});

});	