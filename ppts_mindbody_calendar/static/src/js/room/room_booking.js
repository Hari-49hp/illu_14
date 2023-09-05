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
				$('.optLocation').append($('<option></option>').attr("value", key).text(value));
				$('.header_location').append($('<option></option>').attr("value", key).text(value));
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
				$('.optTypeGroup').append($('<option></option>').attr("value", key).text(value)); 
				$('.header_services').append($('<option></option>').attr("value", key).text(value)); 
			});
		},
	});

	$.ajax({
		url: "/appointment/rooms",
		type: 'POST',
		async:false,
		data: {
		},
		success: function(result) {
			var resultJSON = jQuery.parseJSON(result);
			$.each(resultJSON,function(key,value){
				$('.roomselectfield').append($('<option></option>').attr("value", key).text(value)); 
			});
		},
	});

	$.ajax({
    url: "/event/calendar/partners_list",
    type: 'POST',
    async:false,
    data: {
      // "unavail_name": $(".side-bar-name").text()
    },
    success: function(result) {
      var resultJSON = jQuery.parseJSON(result);
      $.each(resultJSON,function(key,value){
       $('.optClient').append($('<option></option>').attr("value", key).text(value));
      });
    },
  });

	$.ajax({
		url: "/event/calendar/employee_list",
		type: 'POST',
		async:false,
		data: {
		},
		success: function(result) {
			var resultJSON = jQuery.parseJSON(result);
			$.each(resultJSON,function(key,value){
				$('.roomSupervisor').append($('<option></option>').attr("value", key).text(value)); 
			});
		},
	});

	$.ajax({
		url: "/event/calendar/app_type_list",
		type: 'POST',
		async:false,
		data: {
		},
		success: function(result) {
			var resultJSON = jQuery.parseJSON(result);
			$.each(resultJSON,function(key,value){
				$('.optAptType').append($('<option></option>').attr("value", key).text(value)); 
			});
		},
	});

});
