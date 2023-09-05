$(document).ready(function () {
	window.scrollTo({ top: 0, behavior: 'smooth' });
	// used to get the appointment type based on the url
        searchParams = new URLSearchParams(window.location.search)

	
});

                    
        var auto_select_function = function() {
        
        	if ($("#sub_categ_id").val()) {

				const service_platform_type_onload = document.querySelectorAll('#service_platform_type');
		
				service_platform_type_onload.forEach(element => {
		
						var platform = element.getAttribute("data-platform-type");
						var selected_platform = $("#sub_categ_id_type").val();
						if (platform  == selected_platform) {
								element.classList.add('tigger-now');
								$( ".tigger-now" ).trigger( "click" );
								
								if (platform != 'is_struggling') {
								
										const service_selected_onload = document.querySelectorAll('#service_selected');
				
										service_selected_onload.forEach(element_service => {
								
												var data_service_id = element_service.getAttribute("data-service-id");
												var selected_data_service_id = $("#sub_categ_id_type_id").val();
												if (data_service_id  == selected_data_service_id) {
														element_service.classList.add('tigger-now');
														$( ".tigger-now" ).trigger( "click" );
														
														
															const select_service_category_onload = document.querySelectorAll('#select_service_category');
				
															select_service_category_onload.forEach(element_category => {
													
																	var data_service_category_id = element_category.getAttribute("data-service-category");
																	var selected_data_service_category_id = $("#sub_categ_id").val();
																	if (data_service_category_id  == selected_data_service_category_id) {
																			element_category.classList.add('tigger-now');
																			element_category.classList.add('selected-service-platform');
																			$( ".tigger-now" ).css("background-color", "#00AEC7");
																			$( ".tigger-now" ).css("color", "#FFFFFF");
																			$( ".tigger-now" ).trigger( "click" );
																			
																			$( "#open_location_menu" ).trigger( "click" );
																			
																			
																			
																	}
															});
														
														
												}
										});
										
										
										
									} else {
									
												const category_struggling_id_onload = document.querySelectorAll('#category_struggling_id');
				
												category_struggling_id_onload.forEach(element_category => {
										
														var struggling_id = element_category.getAttribute("data-struggling-id");
														var selected_struggling_id = $("#sub_categ_id").val();
														if (struggling_id  == selected_struggling_id) {
																element_category.classList.add('tigger-now');
																$( ".tigger-now" ).trigger( "click" );
																$( "#open_location_menu" ).trigger( "click" );
																
														}
												});
									
									
									}
								
								
								
						}
				});
				
		}
}


function service_platform(platform) {

	$('#platform').val(platform)
	$('.service-platform').hide();
	$('.service-tag').show()
	$('.service-tag-back').show()

	$('.serviceseclowheight').empty();

	$('.serviceseclowheight').append(`
	

	                                        
	                                        
	                      <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" onclick="service_platform_type('holistic')">
	                                            <div class="service-lists-item">
	                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
	                                                    loading="lazy" />
	                                                    
	                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
	                                                    
	                                                <div class="service-svg-shapes-overlay">
	                                                    <div class="wrapper">
	                                                        <div class="side_side"> </div>
	                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
	                                                            y="200">
	                                                            <defs>
	                                                                <clipPath id="slopeclip">
	                                                                    <path class="st0"
	                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
	                                                                </clipPath>
	                                                            </defs>
	                                                        </svg>
	
	                                                    </div>
	                                                    <h4><span>Holistic Healing Sessions</span></h4>
	                                                </div>
	
	                                            </div>
	                                            <div class="service_hoveredcontainer">
	                                                <!-- <h5>Mind Science</h5>
	                                                <p>Hover effect here where, when you hover on any one of the services a
	                                                    small description.</p> -->
	                                                    
	                                                <span>Holistic Healing Sessions</span>
	                                            </div>
	                                        </div>
	                                        
	                                        
	                          <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-platform-type="is_struggling" id="service_platform_type">
	                                            <div class="service-lists-item">
	                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
	                                                    loading="lazy" />
	                                                    
	                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
	                                                    
	                                                <div class="service-svg-shapes-overlay">
	                                                    <div class="wrapper">
	                                                        <div class="side_side"> </div>
	                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
	                                                            y="200">
	                                                            <defs>
	                                                                <clipPath id="slopeclip">
	                                                                    <path class="st0"
	                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
	                                                                </clipPath>
	                                                            </defs>
	                                                        </svg>
	
	                                                    </div>
	                                                    <h4><span>What Are you Struggling with?</span></h4>
	                                                </div>
	
	                                            </div>
	                                            <div class="service_hoveredcontainer">
	                                                <!-- <h5>Mind Science</h5>
	                                                <p>Hover effect here where, when you hover on any one of the services a
	                                                    small description.</p> -->
	                                                    
	                                                <span>What Are you Struggling with?</span>
	                                            </div>
	                                        </div>
	                                        
	                                       
	                                        
	
	                        `);



}


function service_platform_type(type) {

	$('#selected_service_type').val(type)


	$.ajax({
		url: "/appointment/service/filter",
		type: 'POST',
		async: false,
		data: {

		},
		success: function (result) {
			var resultJSON = jQuery.parseJSON(result);
			$('.serviceseclowheight').empty();

			$.each(resultJSON, function (key, value) {
				$('.serviceseclowheight').append(`
	
	                 <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" onclick="service_selected(`+ value['id'] + `,'` + value['name'] + `')">
	                                            <div class="service-lists-item">
	                                                <img src=`+ value['image'] + ` loading="lazy"/>
	                                                    
	                                                <div class="service-svg-shapes-overlay">
	                                                    <div class="wrapper">
	                                                        <div class="side_side"> </div>
	                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
	                                                            y="200">
	                                                            <defs>
	                                                                <clipPath id="slopeclip">
	                                                                    <path class="st0"
	                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
	                                                                </clipPath>
	                                                            </defs>
	                                                        </svg>
	
	                                                    </div>
	                                                    <h4><span>`+ value['name'] + `</span></h4>
	                                                </div>
	
	                                            </div>
	                                            <div class="service_hoveredcontainer">
	                                                <!-- <h5>Mind Science</h5>
	                                                <p>Hover effect here where, when you hover on any one of the services a
	                                                    small description.</p> -->
	                                                    
	                                                <span>`+ value['maincateg_notes'] + `</span>
	                                            </div>
	                                        </div>
	
	                        `);
			});

		},
	});


}




// Service back button

function service_back_button() {

	$('.serviceseclowheight').empty();

	$('.service-tag').hide()
	$('.service-tag-back').hide()
	$('.service-platform').show();
	$('.service-category-header').hide();
	$('.service-category-list').hide();

	$('.serviceseclowheight').append(`
	
	                 <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" onclick="service_platform('online')">
	                                            <div class="service-lists-item">
	                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
	                                                    loading="lazy" />
	                                                    
	                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
	                                                    
	                                                <div class="service-svg-shapes-overlay">
	                                                    <div class="wrapper">
	                                                        <div class="side_side"> </div>
	                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
	                                                            y="200">
	                                                            <defs>
	                                                                <clipPath id="slopeclip">
	                                                                    <path class="st0"
	                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
	                                                                </clipPath>
	                                                            </defs>
	                                                        </svg>
	
	                                                    </div>
	                                                    <h4><span>Online</span></h4>
	                                                </div>
	
	                                            </div>
	                                            <div class="service_hoveredcontainer">
	                                                <!-- <h5>Mind Science</h5>
	                                                <p>Hover effect here where, when you hover on any one of the services a
	                                                    small description.</p> -->
	                                                    
	                                                <span>Online</span>
	                                            </div>
	                                        </div>
	                                        
	                                        <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" onclick="service_platform('onsite')">
	                                            <div class="service-lists-item">
	                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
	                                                    loading="lazy" />
	                                                    
	                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
	                                                    
	                                                <div class="service-svg-shapes-overlay">
	                                                    <div class="wrapper">
	                                                        <div class="side_side"> </div>
	                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
	                                                            y="200">
	                                                            <defs>
	                                                                <clipPath id="slopeclip">
	                                                                    <path class="st0"
	                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
	                                                                </clipPath>
	                                                            </defs>
	                                                        </svg>
	
	                                                    </div>
	                                                    <h4><span>Onsite</span></h4>
	                                                </div>
	
	                                            </div>
	                                            <div class="service_hoveredcontainer">
	                                                <!-- <h5>Mind Science</h5>
	                                                <p>Hover effect here where, when you hover on any one of the services a
	                                                    small description.</p> -->
	                                                    
	                                                <span>Onsite</span>
	                                            </div>
	                                        </div>
	                                        
	
	                        `);





}

// Service Selected on list

function service_selected(service_id, name) {


	$('#selected_service_id').val(service_id);
	$('#selected_service_categ_id').val('');

	$('.service-category-header').empty();

	$('.service-category-list').show();

	$('.service-category-header').append(`
		
	        <h5 class="bookappsubheading">Select a `+ name + ` Sub-Category</h5>
	 `);

	var selected_redirect_therapist_id = $('#selected_redirect_therapist_id').val();


	$.ajax({
		url: "/appointment/service/category/filter",
		type: 'POST',
		async: false,
		data: {
			'service_id': service_id,
			'therapist_id': selected_redirect_therapist_id,
		},
		success: function (result) {
			var resultJSON = jQuery.parseJSON(result);
			$('.service-category-list').empty();
			$.each(resultJSON, function (key, value) {
				$('.service-category-list').append(`
	                    
	                    	<button class="mindbtn" id="select_service_category" data-service-category="`+ value['id'] + `"> ` + value['name'] + `</button>
	                    	
	                    	
	
	
	                        `);
			});

		},
	});

	select_service_category_method();


}

// Select service category

function select_service_category(categ_id) {

	$('#selected_service_categ_id').val(categ_id)
}


// Open Location 

function open_location_menu() {

	$('#open-service-menu').removeClass("active")
	$('#open-content-service-menu').removeClass("show active")
	$('#open-location-menu').last().addClass("active");
	$('#open-content-location-menu').last().addClass("show active");

	var selected_redirect_therapist_id = $('#selected_redirect_therapist_id').val();


	$.ajax({
		url: "/appointment/location/filter",
		type: 'POST',
		async: false,
		data: {
			therapist_id: selected_redirect_therapist_id,
		},
		success: function (result) {
			var resultJSON = jQuery.parseJSON(result);
			$('.bookpackagecard-location').empty();

			$.each(resultJSON, function (key, value) {
				$('.bookpackagecard-location').append(`
	
	                 		<div class="sessionslistcard" onclick="select_service_location(`+ value['id'] + `)">
                                    <h4> `+ value['name'] + `  </h4>
                                </div>
                                
                                 
	
	                        `);
			});

		},
	});



}


// Select service Location

function select_service_location(locatio_id) {

	$('#selected_service_location_id').val(locatio_id)
}


// Location back button

function location_back_button() {

	$('#open-location-menu').removeClass("active")
	$('#open-content-location-menu').removeClass("show active")
	$('#open-service-menu').last().addClass("active");
	$('#open-content-service-menu').last().addClass("show active");

}


// Open Therapist 

function open_therapist_menu() {

	$('#open-location-menu').removeClass("active")
	$('#open-content-location-menu').removeClass("show active");
	$('#open-therapist-menu').last().addClass("active");
	$('#open-content-therapist-menu').last().addClass("show active");

	var service_id = $('#selected_service_id').val();


	$.ajax({
		url: "/appointment/service/therapist/filter",
		type: 'POST',
		async: false,
		data: {
			'company_id': $('#selected_service_location_id').val(),
			'service_id': service_id,
		},
		success: function (result) {
			var resultJSON = jQuery.parseJSON(result);
			$('.bookapp-choose-therapist').empty();

			$.each(resultJSON, function (key, value) {
				$('.bookapp-choose-therapist').append(`
	
	                 		<div class="col-xl-2 col-lg-3 col-md-12 col-sm-12 col-xs-12 therapychooslist" onclick="select_service_therapist(`+ value['id'] + `)">
                                    <div class="therapest-list-container">
                                        <img src=`+ value['image'] + ` loading="lazy"/>
                                        <h5>`+ value['name'] + `</h5>

                                        <a class="buttonwithbtnshape"> More info </a>
                                    </div>
                                </div>
                                
                         `);

			});


			$('.therapist-location-list').empty();
			$('.therapist-location-list').append(`
							<option value="" disabled="disabled" selected="selected">Choose Therapist</option>
                         `);


			$.each(resultJSON, function (key, value) {
				$('.therapist-location-list').append(`
							
							<option value="`+ value['id'] + `">` + value['name'] + `</option>
                                
                         `);

			});

		},
	});

}

// Select service Therapist

function select_service_therapist(therapist_id) {

	$('#selected_service_therapist_id').val(therapist_id);

	$('#open-content-sub-therapist-menu').addClass("d-none")
	$('.bookapp-choose-therapist').addClass("d-none")
	$('#therapist-profile-menu').removeClass("d-none");
	//$('#open-content-location-menu').last().addClass( "show active" );

	var service_id = $('#selected_service_id').val();
	var service_sub_id = $('#selected_service_categ_id').val();


	$.ajax({
		url: "/appointment/service/therapist/filter",
		type: 'POST',
		async: false,
		data: {
			'company_id': $('#selected_service_location_id').val(),
			'service_id': service_id,
			'service_sub_id': service_sub_id,
		},
		success: function (result) {
			var resultJSON = jQuery.parseJSON(result);

			$('.therapist-location-list').empty();
			$('.therapist-location-list').append(`
							<option value="" disabled="disabled">Choose Therapist</option>
                         `);


			$.each(resultJSON, function (key, value) {

				if (value['id'] == therapist_id) {
					$('.therapist-location-list').append(`
								
									<option value="`+ value['id'] + `" selected="selected">` + value['name'] + `</option>
	                         `);
				}
				else {
					$('.therapist-location-list').append(`
								
									<option value="`+ value['id'] + `">` + value['name'] + `</option>
	                         `);
				}

			});

		},
	});


	$.ajax({
		url: "/appointment/service/therapist/filter",
		type: 'POST',
		async: false,
		data: {
			'therapist_id': therapist_id,
		},
		success: function (result) {
			var resultJSON = jQuery.parseJSON(result);
			$('.therapist-profile').empty();

			$.each(resultJSON, function (key, value) {
				$('.therapist-profile').append(`
	
	                 		<div class="row bookapp-therapyinfo-innersec">
                                            <div class="col-xl-5=6 col-lg-6 col-md-6 col-sm-12 col-xs-12">
                                                <h5>`+ value['name'] + `</h5>
                                                <p><b>Languages Spoken:</b> `+ value['lang_ids'] + ` </p>
                                                <p><b>Nationality:</b> `+ value['country_id'] + `</p>
                                                <label class="therapestlocation">`+ value['location_id'] + `</label>
                                                <label class="onlinegobalicon">`+ value['platform'] + ` appointments</label>
                                            </div>
                                            <div class="col-xl-5=6 col-lg-6 col-md-6 col-sm-12 col-xs-12">
                                                <img src=`+ value['image'] + ` loading="lazy"/>
                                            </div>
                                        </div>
                                        <p>
                                        
                                        	`+ value['about_empolyee'] + `
                                        
                                        </p>
                                
                         `);

			});

		},
	});

}

$("#selection_therapist_id").change(function () {

	$('#selected_service_therapist_id').val($("#selection_therapist_id").val());


	//Calendar
	$('#selected_appointment_date').val('');
	$(".time-picker").addClass("display-none");
	$('#appointment-timepickerrows').empty();
	$("#selected_appointment_slot_id").val('');
	$(".timepickerbuttons").removeClass("timeshooseactive");
	$(".month-fc-day-number").removeClass("selectedDate");


	var therapist_id = $("#selection_therapist_id").val();

	$.ajax({
		url: "/appointment/service/therapist/filter",
		type: 'POST',
		async: false,
		data: {
			'therapist_id': therapist_id,
		},
		success: function (result) {
			var resultJSON = jQuery.parseJSON(result);
			$('.therapist-profile').empty();

			$.each(resultJSON, function (key, value) {
				$('.therapist-profile').append(`
	
	                 		<div class="row bookapp-therapyinfo-innersec">
                                            <div class="col-xl-5=6 col-lg-6 col-md-6 col-sm-12 col-xs-12">
                                                <h5>`+ value['name'] + `</h5>
                                                <p><b>Languages Spoken:</b> `+ value['lang_ids'] + ` </p>
                                                <p><b>Nationality:</b> `+ value['country_id'] + `</p>
                                                <label class="therapestlocation">`+ value['location_id'] + `</label>
                                                <label class="onlinegobalicon">`+ value['platform'] + ` appointments</label>
                                            </div>
                                            <div class="col-xl-5=6 col-lg-6 col-md-6 col-sm-12 col-xs-12">
                                                <img src=`+ value['image'] + ` loading="lazy"/>
                                            </div>
                                        </div>
                                        <p>
                                        
                                        	`+ value['about_empolyee'] + `
                                        
                                        </p>
                                
                         `);

			});

		},
	});



	//start
	// accessing the elements with same classname
	const select_service_therapist = document.querySelectorAll('#select_service_therapist');
	$(".therapychooslist").removeClass("select-therapest");

	// adding the event listener by looping
	select_service_therapist.forEach(element => {


		const selected_therapist_id = element.getAttribute("selected-therapist_id");

		if (therapist_id === selected_therapist_id) {

			element.classList.add('select-therapest');

		}


	});

	//end





});


// therapist back button

function therapist_back_button() {

	$('#open-therapist-menu').removeClass("active")
	$('#open-content-therapist-menu').removeClass("show active")
	$('#open-location-menu').last().addClass("active");
	$('#open-content-location-menu').last().addClass("show active");

}


function therapist_back_button_skip_sel_therapist() {

	$('#open-appointment-calendar-menu').removeClass("active")
	$('#open-content-appointment-calendar-menu').removeClass("show active")
	$('#open-location-menu').last().addClass("active");
	$('#open-content-location-menu').last().addClass("show active");

}


// therapist profile back button

function therapist_profile_back_button() {

	$('#open-content-sub-therapist-menu').removeClass("d-none")
	$('.bookapp-choose-therapist').removeClass("d-none")
	$('#therapist-profile-menu').addClass("d-none");
}


// Open Appointment Calendar

/*
method in bookappointmentfullcalender.js file
function open_appointment_calendar_menu() {
	
	$('#open-therapist-menu').removeClass( "active" )
	$('#open-content-therapist-menu').removeClass( "show active" );
	$('#open-appointment-calendar-menu').last().addClass( "active" );
	$('#open-content-appointment-calendar-menu').last().addClass( "show active" );
}*/


// Appointment Calendar back button

function appointment_calendar_back_button() {

	$('#open-appointment-calendar-menu').removeClass("active")
	$('#open-content-appointment-calendar-menu').removeClass("show active");
	$('#open-therapist-menu').last().addClass("active");
	$('#open-content-therapist-menu').last().addClass("show active");
}

document.addEventListener("DOMContentLoaded", function () {




	$('#appointment-warning').hide()

	appointment_type = $('#appointment_type').val()


	if (appointment_type === 'free') {

		$('.service-tag').show()
		$('.service-tag-back').hide()
		$('.service-tag-back-footer').hide()
		$('.service-platform').hide()


		$('#service_back_sub_menu_button').hide()
		$('#service_back_sub_menu_button_footer').hide()

		//$('#appointment_time_id').attr('readonly', 'readonly');
		$('#appointment_time_id').attr('disabled', true);


	} else {

		$('.service-tag').hide()
		$('.service-tag-back').hide()
		$('.service-tag-back-footer').hide()

		$('#service_back_sub_menu_button').hide()
		$('#service_back_sub_menu_button_footer').hide()
	}



	$('.service-category-struggling-header').hide()
	$('.service-category-struggling-list').hide()





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


				$('#customer_name').val(value['name']);
				$('#email').val(value['email']);
				$('#phone').val(value['phone']);
				$('#street').val(value['street']);

			});


		},
	});


	//end of ajax









	// Start Selected struggling
	var service_category_struggling_method = () => {

		// Start

		const category_struggling_id = document.querySelectorAll('#category_struggling_id');

		category_struggling_id.forEach(element => {

			element.addEventListener("click", (e) => {


				$('#appointment-warning').hide()

				//$(".service-lists-items-wrapper").removeClass("selected-service-platform");
				//e.currentTarget.classList.add('selected-service-platform');
				var struggling_id = e.currentTarget.getAttribute("data-struggling-id");

				$('#selected_service_categ_id').val(struggling_id)

				$(".category-struggling-ids").removeClass("selected-service-location");
				$(".strugglecards").removeClass("selected-service-location");
				e.currentTarget.classList.add('selected-service-location');

				var strugglecards = e.currentTarget.querySelectorAll('.strugglecards')

				strugglecards.forEach(strugglecard => {

					strugglecard.classList.add('selected-service-location');

				});





			});
		});

	};
	//end	


	// Start open_location_menu

	const open_location_menu = document.querySelectorAll('#open_location_menu');

	open_location_menu.forEach(element => {

		element.addEventListener("click", (e) => {

			window.scrollTo({ top: 0, behavior: 'smooth' });

			var check_platform = $('#platform').val();

			var check_appointment_type = $('#appointment_type').val();

			var check_service_categ_id = $('#selected_service_categ_id').val();



			if (check_appointment_type == "free") {

				check_platform = "free";

			}

			if (check_platform !== "" && check_service_categ_id !== "") {

				$('#open-service-menu').removeClass("active")
				$('#open-content-service-menu').removeClass("show active")
				$('#open-location-menu').last().addClass("active");
				$('#open-content-location-menu').last().addClass("show active");

				var selected_redirect_therapist_id = $('#selected_redirect_therapist_id').val();

				$.ajax({
					url: "/appointment/location/filter",
					type: 'POST',
					async: false,
					data: {
						therapist_id: selected_redirect_therapist_id,
					},
					success: function (result) {
						var resultJSON = jQuery.parseJSON(result);
						$('.bookpackagecard-location').empty();

						$.each(resultJSON, function (key, value) {
							$('.bookpackagecard-location').append(`
					
					                 		<div class="sessionslistcard sessionslist-service-location" data-service-location="`+ value['id'] + `" id="select_service_location">
				                                    <h4> `+ value['name'] + `  </h4>
				                                </div>
				                                
				                                 
					
					                        `);
						});

					},
				});

				select_service_location_method();

				$('#appointment-warning').hide()

			} else {

				if ((check_platform == "")) {
					$('#appointment-warning').text('Kindly select a platform to proceed.');
				} else {
					$('#appointment-warning').text('Kindly select a services and sub services to proceed.');
				}


				$('#appointment-warning').show()

			}




		});
	});

	//end	



	//start ------------------------

	var service_selected_method = () => {

		const service_selected = document.querySelectorAll('#service_selected');

		// adding the event listener by looping
		service_selected.forEach(element => {

			element.addEventListener("click", (e) => {
				window.scrollTo({ top: 400, behavior: 'smooth' });
				var service_selected_id = e.currentTarget.getAttribute("data-service-id");
				var service_name = e.currentTarget.getAttribute("data-service-name");



				$(".service-lists-items-wrapper").removeClass("selected-service-platform");
				$(".side_side").removeClass("selected-service-platform");

				// adding the event listener by looping
				service_selected.forEach(element => {

					var service_ele_id = element.getAttribute("data-service-id");

					if (service_ele_id === service_selected_id) {

						element.classList.add('selected-service-platform');
						var side_side = element.querySelectorAll('.side_side')

						side_side.forEach(side_side => {

							side_side.classList.add('selected-service-platform');

						});

						//elementChildren.classList.add('selected-service-platform');

					}


				});


				$('#selected_service_id').val(service_selected_id);
				$('#selected_service_categ_id').val('');

				$('.service-category-header').empty();
				$('.service-category-header').show();
				$('.service-category-list').show();

				$('.service-category-header').append(`
				
						<h5 class="bookappsubheading">Select a `+ service_name + ` Sub-Category</h5>
					 `);

				var selected_redirect_therapist_id = $('#selected_redirect_therapist_id').val();

				$.ajax({
					url: "/appointment/service/category/filter",
					type: 'POST',
					async: false,
					data: {
						'service_id': service_selected_id,
						'therapist_id': selected_redirect_therapist_id,
					},
					success: function (result) {
						var resultJSON = jQuery.parseJSON(result);
						$('.service-category-list').empty();
						$.each(resultJSON, function (key, value) {
							$('.service-category-list').append(`
						    
						    	<button class="mindbtn" id="select_service_category" data-service-category="`+ value['id'] + `"> ` + value['name'] + `</button>
						    	
						    	
				
				
							`);
						});

					},
				});


				select_service_category_method();






			});

		});
	};

	// end


	//start ------------------------

	var select_service_category_method = () => {

		const select_service_category = document.querySelectorAll('#select_service_category');

		// adding the event listener by looping
		select_service_category.forEach(element => {

			element.addEventListener("click", (e) => {
				window.scrollTo({ top: 600, behavior: 'smooth' });
				$('#appointment-warning').hide()

				var service_categ_selected_id = e.currentTarget.getAttribute("data-service-category");


				$('#selected_service_categ_id').val(service_categ_selected_id);


				$(".mindbtn").removeClass("selected-service-platform");

				// adding the event listener by looping
				select_service_category.forEach(element => {

					var service_ele_categ_id = element.getAttribute("data-service-category");

					if (service_ele_categ_id === service_categ_selected_id) {

						element.classList.add('selected-service-platform');

						//elementChildren.classList.add('selected-service-platform');

					}


				});






			});

		});
	};

	// end


	//start ------------------------

	var select_service_location_method = () => {

		const select_service_location = document.querySelectorAll('#select_service_location');

		// adding the event listener by looping
		select_service_location.forEach(element => {

			var location_selected_id = $('#selected_service_location_id').val();

			//$(".sessionslist-service-location").removeClass("selected-service-location");


			var service_ele_location_id = element.getAttribute("data-service-location");

			if (service_ele_location_id === location_selected_id) {

				element.classList.add('selected-service-location');

				//elementChildren.classList.add('selected-service-platform');

			}


			element.addEventListener("click", (e) => {
				window.scrollTo({ top: 400, behavior: 'smooth' });
				$('#appointment-warning').hide()

				var service_location_selected_id = e.currentTarget.getAttribute("data-service-location");


				$('#selected_service_location_id').val(service_location_selected_id);


				$(".sessionslist-service-location").removeClass("selected-service-location");

				// adding the event listener by looping
				select_service_location.forEach(element => {

					var service_ele_location_id = element.getAttribute("data-service-location");

					if (service_ele_location_id === service_location_selected_id) {

						element.classList.add('selected-service-location');

						//elementChildren.classList.add('selected-service-platform');

					}


				});






			});

		});
	};

	// end





	// Start Declaring platform type
	var service_platform_type_method = () => {

		// Start

		const service_platform_type = document.querySelectorAll('#service_platform_type');

		service_platform_type.forEach(element => {

			window.scrollTo({ top: 0, behavior: 'smooth' });
			var service_platform_type = $('#selected_service_type').val()

			$(".service-lists-items-wrapper").removeClass("selected-service-platform");


			var service_platform_type = $('#selected_service_type').val()
			var platform_type = element.getAttribute("data-platform-type");

			if (platform_type === service_platform_type) {

				element.classList.add('selected-service-platform');
				var side_side = element.querySelectorAll('.side_side')

				side_side.forEach(side_side => {

					side_side.classList.add('selected-service-platform');

				});


			}


			element.addEventListener("click", (e) => {

				$('#appointment-warning').hide()

				//$(".service-lists-items-wrapper").removeClass("selected-service-platform");
				//e.currentTarget.classList.add('selected-service-platform');
				var service_type = e.currentTarget.getAttribute("data-platform-type");


				var selected_conslt_type = e.currentTarget.getAttribute("data-conslt-type");

				if (selected_conslt_type === "free") {

					$('#appointment_time_id').attr('disabled', true);

				} else {

					$('#appointment_time_id').attr('disabled', false);
				}


				$('.service-tag-back').hide()
				$('.service-tag-back-footer').hide()
				$('#service_back_sub_menu_button').show()
				$('#service_back_sub_menu_button_footer').show()

				$('#selected_service_type').val(service_type)

				if (service_type == 'is_struggling') {

					//alert('is_struggling');

					$('.service-category-struggling-header').show()
					$('.service-category-struggling-list').show()

					$('.serviceseclowheight').empty();

					$('.service-tag').hide()

					var selected_redirect_therapist_id = $('#selected_redirect_therapist_id').val();

					$.ajax({
						url: "/appointment/service/struggling/filter",
						type: 'POST',
						async: false,
						data: {
							'service_type': service_type,
							'therapist_id': selected_redirect_therapist_id,
						},
						success: function (result) {
							var resultJSON = jQuery.parseJSON(result);
							$('.service-category-struggling-list').empty();

							$.each(resultJSON, function (key, value) {
								$('.service-category-struggling-list').append(`
														                    
														                    		<div class="col-xl-3 col-lg-3 col-md-4 col-sm-6 category-struggling-ids" data-struggling-id="`+ value['id'] + `" id="category_struggling_id">
												                                        <div class="strugglecards"> 
												                                                <img class="strugglimgcrop" src=`+ value['image'] + ` loading="lazy"/>
												                                            <div class="struhletypos">
												                                                <h5>`+ value['name'] + `</h5>
												                                            </div>
												                                        </div>
												                                    </div>
														
														
														                        `);
							});

						},
					});


					service_category_struggling_method();


				} else if (service_type == 'holistic') {

					$('.service-category-struggling-header').hide()
					$('.service-category-struggling-list').hide()
					$('.service-tag').show()

					var selected_redirect_therapist_id = $('#selected_redirect_therapist_id').val()


					$.ajax({
						url: "/appointment/service/filter",
						type: 'POST',
						async: false,
						data: {
							therapist_id: selected_redirect_therapist_id,
						},
						success: function (result) {
							var resultJSON = jQuery.parseJSON(result);
							$('.serviceseclowheight').empty();

							$.each(resultJSON, function (key, value) {
								$('.serviceseclowheight').append(`
																	
																	                 <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-service-id="`+ value['id'] + `" data-service-name="` + value['name'] + `" id="service_selected">
																	                 
																	                 
																	                                            <div class="service-lists-item">
																	                                                <img src=`+ value['image'] + ` loading="lazy"/>
																	                                                    
																	                                                <div class="service-svg-shapes-overlay">
																	                                                    <div class="wrapper">
																	                                                        <div class="side_side"> </div>
																	                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
																	                                                            y="200">
																	                                                            <defs>
																	                                                                <clipPath id="slopeclip">
																	                                                                    <path class="st0"
																	                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
																	                                                                </clipPath>
																	                                                            </defs>
																	                                                        </svg>
																	
																	                                                    </div>
																	                                                    <h4><span>`+ value['name'] + `</span></h4>
																	                                                </div>
																	
																	                                            </div>
																	                                            <div class="service_hoveredcontainer">
																	                                                <!-- <h5>Mind Science</h5>
																	                                                <p>Hover effect here where, when you hover on any one of the services a
																	                                                    small description.</p> -->
																	                                                    
																	                                                <span>`+ value['maincateg_notes'] + `</span>
																	                                            </div>
																	                                        </div>
																	
																	                        `);
							});

						},
					});

					service_selected_method();
					// if appointment type is free consultant mean auto select the free assesment and subcategory 
						// and go to the location select page

					if(searchParams.get('appointment_type')=='free')
					{
					
					$('[data-service-id="81"]').trigger('click')
					$('[data-service-category="407"]').trigger('click')
					$('#open_location_menu').trigger('click')
					 
					}

	




				} else if (service_type == 'free30_consult') {






					$('.serviceseclowheight').empty();

					$('.serviceseclowheight').append(`
											                                        
											                                        
											                      <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-conslt-type="free" data-platform-type="holistic" id="service_platform_type">
											                      
											                                            <div class="service-lists-item">
											                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
											                                                    loading="lazy" />
											                                                    
											                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
											                                                    
											                                                <div class="service-svg-shapes-overlay">
											                                                    <div class="wrapper">
											                                                        <div class="side_side"> </div>
											                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
											                                                            y="200">
											                                                            <defs>
											                                                                <clipPath id="slopeclip">
											                                                                    <path class="st0"
											                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
											                                                                </clipPath>
											                                                            </defs>
											                                                        </svg>
											
											                                                    </div>
											                                                    <h4><span>Holistic Healing Sessions</span></h4>
											                                                </div>
											
											                                            </div>
											                                            <div class="service_hoveredcontainer">
											                                                <!-- <h5>Mind Science</h5>
											                                                <p>Hover effect here where, when you hover on any one of the services a
											                                                    small description.</p> -->
											                                                    
											                                                <span>Holistic Healing Sessions</span>
											                                            </div>
											                                        </div>
											                                        
											                                        
											                          <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-conslt-type="free" data-platform-type="is_struggling" id="service_platform_type">
											                                            <div class="service-lists-item">
											                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
											                                                    loading="lazy" />
											                                                    
											                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
											                                                    
											                                                <div class="service-svg-shapes-overlay">
											                                                    <div class="wrapper">
											                                                        <div class="side_side"> </div>
											                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
											                                                            y="200">
											                                                            <defs>
											                                                                <clipPath id="slopeclip">
											                                                                    <path class="st0"
											                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
											                                                                </clipPath>
											                                                            </defs>
											                                                        </svg>
											
											                                                    </div>
											                                                    <h4><span>What Are you Struggling With?</span></h4>
											                                                </div>
											
											                                            </div>
											                                            <div class="service_hoveredcontainer">
											                                                <!-- <h5>Mind Science</h5>
											                                                <p>Hover effect here where, when you hover on any one of the services a
											                                                    small description.</p> -->
											                                                    
											                                                <span>What Are you Struggling with?</span>
											                                            </div>
											                                        </div>
											                                        
											                                       
											                                        
											
											                        `);


					service_platform_type_method();













				}

			});
		});

	};
	//end	



	// Start
	var appointment_service_platform_method = () => {

		// Start

		// appointment appointment_service_platform
		const appointment_service_platform = document.querySelectorAll('#appointment_service_platform');

		// adding the event listener by looping
		appointment_service_platform.forEach(element => {

			element.addEventListener("click", (e) => {

				$('#appointment-warning').hide();

				$(".service-lists-items-wrapper").removeClass("selected-service-platform");
				e.currentTarget.classList.add('selected-service-platform');
				var platform = e.currentTarget.getAttribute("data-platform");

				$('#platform').val(platform);
				$('.service-platform').hide();
				$('.service-tag').show()
				$('.service-tag-back').show()
				$('.service-tag-back-footer').show()

				$('.serviceseclowheight').empty();

				$('.serviceseclowheight').append(`
					                                        
					                      <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-conslt-type="" data-platform-type="holistic" id="service_platform_type">
					                      
					                                            <div class="service-lists-item">
					                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
					                                                    loading="lazy" />
					                                                    
					                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
					                                                    
					                                                <div class="service-svg-shapes-overlay">
					                                                    <div class="wrapper">
					                                                        <div class="side_side"> </div>
					                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
					                                                            y="200">
					                                                            <defs>
					                                                                <clipPath id="slopeclip">
					                                                                    <path class="st0"
					                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
					                                                                </clipPath>
					                                                            </defs>
					                                                        </svg>
					
					                                                    </div>
					                                                    <h4><span>Holistic Healing Sessions</span></h4>
					                                                </div>
					
					                                            </div>
					                                            <div class="service_hoveredcontainer">
					                                                <!-- <h5>Mind Science</h5>
					                                                <p>Hover effect here where, when you hover on any one of the services a
					                                                    small description.</p> -->
					                                                    
					                                                <span>Holistic Healing Sessions</span>
					                                            </div>
					                                        </div>
					                                        
					                                        
					                          <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-conslt-type="" data-platform-type="is_struggling" id="service_platform_type">
					                                            <div class="service-lists-item">
					                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
					                                                    loading="lazy" />
					                                                    
					                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
					                                                    
					                                                <div class="service-svg-shapes-overlay">
					                                                    <div class="wrapper">
					                                                        <div class="side_side"> </div>
					                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
					                                                            y="200">
					                                                            <defs>
					                                                                <clipPath id="slopeclip">
					                                                                    <path class="st0"
					                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
					                                                                </clipPath>
					                                                            </defs>
					                                                        </svg>
					
					                                                    </div>
					                                                    <h4><span>What Are you Struggling with?</span></h4>
					                                                </div>
					
					                                            </div>
					                                            <div class="service_hoveredcontainer">
					                                                <!-- <h5>Mind Science</h5>
					                                                <p>Hover effect here where, when you hover on any one of the services a
					                                                    small description.</p> -->
					                                                    
					                                                <span>What Are you Struggling with?</span>
					                                            </div>
					                                        </div>
					                                        
					                                       
					                                        
					
					                        `);
				



				service_platform_type_method();

				// Free Consultation

				if(searchParams.get('appointment_type')=='free')
					{
						$('[data-platform-type="holistic"]').trigger('click')
						

					}

				// Healing appointment
				if (searchParams.get('general') == 'booking')
					
				{
					var categ = searchParams.get('service_selected')
					var sub = searchParams.get('sub_categ_id')

					$('[data-platform-type="holistic"]').trigger('click')
					$(`[data-service-id=${categ}]`).trigger('click')
					$(`[data-service-category=${sub}]`).trigger('click')
					$('#open_location_menu').trigger('click')
					// $('#service_selected').data('data-service-id',11).trigger('click')

				}

				// Therapy appointment
				if (searchParams.get('general') == 'therapy')
					
				{
					var strug_id = searchParams.get('category_struggling_id')

					$('[data-platform-type="is_struggling"]').trigger('click')
					$(`[data-struggling-id=${strug_id}]`).trigger('click')
					$('#open_location_menu').trigger('click')

				}






			});
		});
		//end


	};
	//end





	appointment_service_platform_method();
	service_platform_type_method();
	service_category_struggling_method();





	//start
	const service_back_button = document.querySelectorAll('#service_back_button');

	// adding the event listener by looping
	service_back_button.forEach(element => {

		element.addEventListener("click", (e) => {

			$('.serviceseclowheight').empty();

			$('.service-tag').hide()
			$('.service-tag-back').hide()
			$('.service-tag-back-footer').hide()
			$('.service-platform').show();
			$('.service-category-header').hide();
			$('.service-category-list').hide();
			$('.service-category-struggling-header').hide()
			$('.service-category-struggling-list').hide()

			$('.serviceseclowheight').append(`
			
			                 <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-platform="online" id="appointment_service_platform" >
			                                            <div class="service-lists-item">
			                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
			                                                    loading="lazy" />
			                                                    
			                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
			                                                    
			                                                <div class="service-svg-shapes-overlay">
			                                                    <div class="wrapper">
			                                                        <div class="side_side"> </div>
			                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
			                                                            y="200">
			                                                            <defs>
			                                                                <clipPath id="slopeclip">
			                                                                    <path class="st0"
			                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
			                                                                </clipPath>
			                                                            </defs>
			                                                        </svg>
			
			                                                    </div>
			                                                    <h4><span>Online</span></h4>
			                                                </div>
			
			                                            </div>
			                                            <div class="service_hoveredcontainer">
			                                                <!-- <h5>Mind Science</h5>
			                                                <p>Hover effect here where, when you hover on any one of the services a
			                                                    small description.</p> -->
			                                                    
			                                                <span>Online</span>
			                                            </div>
			                                        </div>
			                                        
			                                        <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-platform="onsite" id="appointment_service_platform" >
			                                            <div class="service-lists-item">
			                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
			                                                    loading="lazy" />
			                                                    
			                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
			                                                    
			                                                <div class="service-svg-shapes-overlay">
			                                                    <div class="wrapper">
			                                                        <div class="side_side"> </div>
			                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
			                                                            y="200">
			                                                            <defs>
			                                                                <clipPath id="slopeclip">
			                                                                    <path class="st0"
			                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
			                                                                </clipPath>
			                                                            </defs>
			                                                        </svg>
			
			                                                    </div>
			                                                    <h4><span>Onsite</span></h4>
			                                                </div>
			
			                                            </div>
			                                            <div class="service_hoveredcontainer">
			                                                <!-- <h5>Mind Science</h5>
			                                                <p>Hover effect here where, when you hover on any one of the services a
			                                                    small description.</p> -->
			                                                    
			                                                <span>Onsite</span>
			                                            </div>
			                                        </div>
			                                        
			
			                        `);

			//Calling service platform
			appointment_service_platform_method();


			//start
			// accessing the elements with same classname
			const appointment_service_platform = document.querySelectorAll('#appointment_service_platform');

			$(".service-lists-items-wrapper").removeClass("selected-service-platform");

			// adding the event listener by looping
			appointment_service_platform.forEach(element => {

				var selected_platform = $("#platform").val();
				var platform = element.getAttribute("data-platform");

				if (platform === selected_platform) {

					element.classList.add('selected-service-platform');
					var side_side = element.querySelectorAll('.side_side')

					side_side.forEach(side_side => {

						side_side.classList.add('selected-service-platform');

					});

					//elementChildren.classList.add('selected-service-platform');

				}


			});

			//end



		});
	});

	// end



	//start
	const service_back_button_footer = document.querySelectorAll('#service_back_button_footer');

	// adding the event listener by looping
	service_back_button_footer.forEach(element => {

		element.addEventListener("click", (e) => {

			$('.serviceseclowheight').empty();

			$('.service-tag').hide()
			$('.service-tag-back').hide()
			$('.service-tag-back-footer').hide()
			$('.service-platform').show();
			$('.service-category-header').hide();
			$('.service-category-list').hide();
			$('.service-category-struggling-header').hide()
			$('.service-category-struggling-list').hide()

			$('.serviceseclowheight').append(`
			
			                 <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-platform="online" id="appointment_service_platform" >
			                                            <div class="service-lists-item">
			                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
			                                                    loading="lazy" />
			                                                    
			                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
			                                                    
			                                                <div class="service-svg-shapes-overlay">
			                                                    <div class="wrapper">
			                                                        <div class="side_side"> </div>
			                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
			                                                            y="200">
			                                                            <defs>
			                                                                <clipPath id="slopeclip">
			                                                                    <path class="st0"
			                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
			                                                                </clipPath>
			                                                            </defs>
			                                                        </svg>
			
			                                                    </div>
			                                                    <h4><span>Online</span></h4>
			                                                </div>
			
			                                            </div>
			                                            <div class="service_hoveredcontainer">
			                                                <!-- <h5>Mind Science</h5>
			                                                <p>Hover effect here where, when you hover on any one of the services a
			                                                    small description.</p> -->
			                                                    
			                                                <span>Online</span>
			                                            </div>
			                                        </div>
			                                        
			                                        <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-platform="onsite" id="appointment_service_platform" >
			                                            <div class="service-lists-item">
			                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
			                                                    loading="lazy" />
			                                                    
			                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
			                                                    
			                                                <div class="service-svg-shapes-overlay">
			                                                    <div class="wrapper">
			                                                        <div class="side_side"> </div>
			                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
			                                                            y="200">
			                                                            <defs>
			                                                                <clipPath id="slopeclip">
			                                                                    <path class="st0"
			                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
			                                                                </clipPath>
			                                                            </defs>
			                                                        </svg>
			
			                                                    </div>
			                                                    <h4><span>Onsite</span></h4>
			                                                </div>
			
			                                            </div>
			                                            <div class="service_hoveredcontainer">
			                                                <!-- <h5>Mind Science</h5>
			                                                <p>Hover effect here where, when you hover on any one of the services a
			                                                    small description.</p> -->
			                                                    
			                                                <span>Onsite</span>
			                                            </div>
			                                        </div>
			                                        
			
			                        `);

			//Calling service platform
			appointment_service_platform_method();


			//start
			// accessing the elements with same classname
			const appointment_service_platform = document.querySelectorAll('#appointment_service_platform');

			$(".service-lists-items-wrapper").removeClass("selected-service-platform");

			// adding the event listener by looping
			appointment_service_platform.forEach(element => {

				var selected_platform = $("#platform").val();
				var platform = element.getAttribute("data-platform");

				if (platform === selected_platform) {

					element.classList.add('selected-service-platform');
					var side_side = element.querySelectorAll('.side_side')

					side_side.forEach(side_side => {

						side_side.classList.add('selected-service-platform');

					});

					//console.log(side);
					//elementChildren.classList.add('selected-service-platform');

				}


			});

			//end



		});
	});

	// end




	//start
	const therapist_back_button_skip_sel_therapist = document.querySelectorAll('#therapist_back_button_skip_sel_therapist');

	// adding the event listener by looping
	therapist_back_button_skip_sel_therapist.forEach(element => {

		element.addEventListener("click", (e) => {


			$('#open-appointment-calendar-menu').removeClass("active")
			$('#open-content-appointment-calendar-menu').removeClass("show active")
			$('#open-location-menu').last().addClass("active");
			$('#open-content-location-menu').last().addClass("show active");
			
		});
	});

	// end
	
	
	//start
	const therapist_back_button = document.querySelectorAll('#therapist_back_button');

	// adding the event listener by looping
	therapist_back_button.forEach(element => {

		element.addEventListener("click", (e) => {


			$('#open-therapist-menu').removeClass("active")
			$('#open-content-therapist-menu').removeClass("show active")
			$('#open-location-menu').last().addClass("active");
			$('#open-content-location-menu').last().addClass("show active");



		});
	});

	// end


	//start
	const therapist_back_button_footer = document.querySelectorAll('#therapist_back_button_footer');

	// adding the event listener by looping
	therapist_back_button_footer.forEach(element => {

		element.addEventListener("click", (e) => {


			$('#open-therapist-menu').removeClass("active")
			$('#open-content-therapist-menu').removeClass("show active")
			$('#open-location-menu').last().addClass("active");
			$('#open-content-location-menu').last().addClass("show active");



		});
	});

	// end

	//start
	const therapist_profile_back_button = document.querySelectorAll('#therapist_profile_back_button');

	// adding the event listener by looping
	therapist_profile_back_button.forEach(element => {

		element.addEventListener("click", (e) => {


			$('#open-content-sub-therapist-menu').removeClass("d-none")
			$('.bookapp-choose-therapist').removeClass("d-none")
			$('#therapist-profile-menu').addClass("d-none");



		});
	});

	// end


	//start
	const therapist_profile_back_button_footer = document.querySelectorAll('#therapist_profile_back_button_footer');

	// adding the event listener by looping
	therapist_profile_back_button_footer.forEach(element => {

		element.addEventListener("click", (e) => {


			$('#open-content-sub-therapist-menu').removeClass("d-none")
			$('.bookapp-choose-therapist').removeClass("d-none")
			$('#therapist-profile-menu').addClass("d-none");



		});
	});

	// end


	//start
	const appointment_calendar_back_button = document.querySelectorAll('#appointment_calendar_back_button');

	// adding the event listener by looping
	appointment_calendar_back_button.forEach(element => {

		element.addEventListener("click", (e) => {

			$('#open_appointment_calendar_menu').text('Continue to Date');
			$('#open_appointment_calendar_menu').removeAttr('disabled');

			$('#open-appointment-calendar-menu').removeClass("active")
			$('#open-content-appointment-calendar-menu').removeClass("show active");
			$('#open-therapist-menu').last().addClass("active");
			$('#open-content-therapist-menu').last().addClass("show active");



		});
	});

	// end


	//start
	const appointment_calendar_back_button_footer = document.querySelectorAll('#appointment_calendar_back_button_footer');

	// adding the event listener by looping
	appointment_calendar_back_button_footer.forEach(element => {

		element.addEventListener("click", (e) => {

			$('#open-appointment-calendar-menu').removeClass("active")
			$('#open-content-appointment-calendar-menu').removeClass("show active");
			$('#open-therapist-menu').last().addClass("active");
			$('#open-content-therapist-menu').last().addClass("show active");

		});
	});

	// end





	//start
	const location_back_button = document.querySelectorAll('#location_back_button');

	// adding the event listener by looping
	location_back_button.forEach(element => {

		element.addEventListener("click", (e) => {


			$('#open-location-menu').removeClass("active")
			$('#open-content-location-menu').removeClass("show active")
			$('#open-service-menu').last().addClass("active");
			$('#open-content-service-menu').last().addClass("show active");


			//Calling service location
			//appointment_service_platform_method();



		});
	});

	// end


	//start
	const location_back_button_footer = document.querySelectorAll('#location_back_button_footer');

	// adding the event listener by looping
	location_back_button_footer.forEach(element => {

		element.addEventListener("click", (e) => {


			$('#open-location-menu').removeClass("active")
			$('#open-content-location-menu').removeClass("show active")
			$('#open-service-menu').last().addClass("active");
			$('#open-content-service-menu').last().addClass("show active");


			//Calling service location
			//appointment_service_platform_method();



		});
	});

	// end












	//start
	var service_back_sub_menu_button_method = () => {

		const service_back_sub_menu_button = document.querySelectorAll('#service_back_sub_menu_button');

		// adding the event listener by looping
		service_back_sub_menu_button.forEach(element => {

			element.addEventListener("click", (e) => {


				appointment_type = $('#appointment_type').val()

				if (appointment_type === 'free') {

					$('.service-tag-back').hide()
					$('.service-tag-back-footer').hide()


				} else {

					$('.service-tag-back').show()
					$('.service-tag-back-footer').show()
				}



				$('.service-tag').show()
				$('.service-category-header').hide();
				$('.service-category-list').hide();
				$('.service-category-struggling-header').hide()
				$('.service-category-struggling-list').hide()
				$('#service_back_sub_menu_button').hide()
				$('#service_back_sub_menu_button_footer').hide()


				$('.serviceseclowheight').empty();

				if (appointment_type != "free") {



					$('.serviceseclowheight').append(`
							
							                 <!-- <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-conslt-type="free" data-platform-type="free30_consult" id="service_platform_type">
							                                            <div class="service-lists-item">
							                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
							                                                    loading="lazy" />
							                                                    
							                                                    
							                                                <div class="service-svg-shapes-overlay">
							                                                    <div class="wrapper">
							                                                        <div class="side_side"> </div>
							                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
							                                                            y="200">
							                                                            <defs>
							                                                                <clipPath id="slopeclip">
							                                                                    <path class="st0"
							                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
							                                                                </clipPath>
							                                                            </defs>
							                                                        </svg>
							
							                                                    </div>
							                                                    <h4><span>Free 30 Mins Consultation</span></h4>
							                                                </div>
							
							                                            </div>
							                                            <div class="service_hoveredcontainer">
							                                                
							                                                    
							                                                <span>Free 30 Mins Consultation</span>
							                                            </div>
							                                        </div>-->
							                                        
							                                        
							                                       
							                                        
							
							                        `);

				}


				$('.serviceseclowheight').append(`
							
							                                        
							                      <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-conslt-type="`+ appointment_type + `" data-platform-type="holistic" id="service_platform_type">
							                      
							                                            <div class="service-lists-item">
							                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
							                                                    loading="lazy" />
							                                                    
							                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
							                                                    
							                                                <div class="service-svg-shapes-overlay">
							                                                    <div class="wrapper">
							                                                        <div class="side_side"> </div>
							                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
							                                                            y="200">
							                                                            <defs>
							                                                                <clipPath id="slopeclip">
							                                                                    <path class="st0"
							                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
							                                                                </clipPath>
							                                                            </defs>
							                                                        </svg>
							
							                                                    </div>
							                                                    <h4><span>Holistic Healing Sessions</span></h4>
							                                                </div>
							
							                                            </div>
							                                            <div class="service_hoveredcontainer">
							                                                <!-- <h5>Mind Science</h5>
							                                                <p>Hover effect here where, when you hover on any one of the services a
							                                                    small description.</p> -->
							                                                    
							                                                <span>Holistic Healing Sessions</span>
							                                            </div>
							                                        </div>
							                                        
							                                        
							                          <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-conslt-type="`+ appointment_type + `" data-platform-type="is_struggling" id="service_platform_type">
							                                            <div class="service-lists-item">
							                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
							                                                    loading="lazy" />
							                                                    
							                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
							                                                    
							                                                <div class="service-svg-shapes-overlay">
							                                                    <div class="wrapper">
							                                                        <div class="side_side"> </div>
							                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
							                                                            y="200">
							                                                            <defs>
							                                                                <clipPath id="slopeclip">
							                                                                    <path class="st0"
							                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
							                                                                </clipPath>
							                                                            </defs>
							                                                        </svg>
							
							                                                    </div>
							                                                    <h4><span>What Are you Struggling with?</span></h4>
							                                                </div>
							
							                                            </div>
							                                            <div class="service_hoveredcontainer">
							                                                <!-- <h5>Mind Science</h5>
							                                                <p>Hover effect here where, when you hover on any one of the services a
							                                                    small description.</p> -->
							                                                    
							                                                <span>What Are you Struggling with?</span>
							                                            </div>
							                                        </div>
							                                        
							                                       
							                                        
							
							                        `);


				service_platform_type_method();



			});
		});
	};
	// end

	service_back_sub_menu_button_method();



	//start
	var service_back_sub_menu_button_footer_method = () => {

		const service_back_sub_menu_button_footer = document.querySelectorAll('#service_back_sub_menu_button_footer');

		// adding the event listener by looping
		service_back_sub_menu_button_footer.forEach(element => {

			element.addEventListener("click", (e) => {


				appointment_type = $('#appointment_type').val()

				if (appointment_type === 'free') {

					$('.service-tag-back').hide()
					$('.service-tag-back-footer').hide()


				} else {

					$('.service-tag-back').show()
					$('.service-tag-back-footer').show()
				}



				$('.service-tag').show()
				$('.service-category-header').hide();
				$('.service-category-list').hide();
				$('.service-category-struggling-header').hide()
				$('.service-category-struggling-list').hide()
				$('#service_back_sub_menu_button').hide()
				$('#service_back_sub_menu_button_footer').hide()



				$('.serviceseclowheight').empty();

				if (appointment_type != "free") {



					$('.serviceseclowheight').append(`
							
							                 <!--<div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-conslt-type="free" data-platform-type="free30_consult" id="service_platform_type">
							                                            <div class="service-lists-item">
							                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
							                                                    loading="lazy" />
							                                                    
							                                                    
							                                                <div class="service-svg-shapes-overlay">
							                                                    <div class="wrapper">
							                                                        <div class="side_side"> </div>
							                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
							                                                            y="200">
							                                                            <defs>
							                                                                <clipPath id="slopeclip">
							                                                                    <path class="st0"
							                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
							                                                                </clipPath>
							                                                            </defs>
							                                                        </svg>
							
							                                                    </div>
							                                                    <h4><span>Free 30 Mins Consultation</span></h4>
							                                                </div>
							
							                                            </div>
							                                            <div class="service_hoveredcontainer">
							                                                <p>Hover effect here where, when you hover on any one of the services a
							                                                    small description.</p> -->
							                                                    
							                                                <span>Free 30 Mins Consultation</span>
							                                            </div>
							                                        </div>-->
							                                        
							                                        
							                                       
							                                        
							
							                        `);

				}


				$('.serviceseclowheight').append(`
							
							                                        
							                      <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-conslt-type="`+ appointment_type + `" data-platform-type="holistic" id="service_platform_type">
							                      
							                                            <div class="service-lists-item">
							                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
							                                                    loading="lazy" />
							                                                    
							                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
							                                                    
							                                                <div class="service-svg-shapes-overlay">
							                                                    <div class="wrapper">
							                                                        <div class="side_side"> </div>
							                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
							                                                            y="200">
							                                                            <defs>
							                                                                <clipPath id="slopeclip">
							                                                                    <path class="st0"
							                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
							                                                                </clipPath>
							                                                            </defs>
							                                                        </svg>
							
							                                                    </div>
							                                                    <h4><span>Holistic Healing Sessions</span></h4>
							                                                </div>
							
							                                            </div>
							                                            <div class="service_hoveredcontainer">
							                                                <!-- <h5>Mind Science</h5>
							                                                <p>Hover effect here where, when you hover on any one of the services a
							                                                    small description.</p> -->
							                                                    
							                                                <span>Holistic Healing Sessions</span>
							                                            </div>
							                                        </div>
							                                        
							                                        
							                          <div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" data-conslt-type="`+ appointment_type + `" data-platform-type="is_struggling" id="service_platform_type">
							                                            <div class="service-lists-item">
							                                                <img src="/ppts_website_theme/static/src/img/service1.jpg" alt="serviceimageone"
							                                                    loading="lazy" />
							                                                    
							                                                <!-- <img t-if="service_id.image" t-att-src="'data:image/png;base64,%s' % to_text(service_id['image'])" loading="lazy"/> -->
							                                                    
							                                                <div class="service-svg-shapes-overlay">
							                                                    <div class="wrapper">
							                                                        <div class="side_side"> </div>
							                                                        <svg class="side_wave" id="gt" height="0" width="0" x="200"
							                                                            y="200">
							                                                            <defs>
							                                                                <clipPath id="slopeclip">
							                                                                    <path class="st0"
							                                                                        d="M453,0c-7,0.4-84.1-1.7-112.1,6.7c-39.4,11.8-71.2,43.4-100.5,69.2c-37.2,32.8-44.9,44.1-139.9,44.1l0,0H453" />
							                                                                </clipPath>
							                                                            </defs>
							                                                        </svg>
							
							                                                    </div>
							                                                    <h4><span>What Are you Struggling with?</span></h4>
							                                                </div>
							
							                                            </div>
							                                            <div class="service_hoveredcontainer">
							                                                <!-- <h5>Mind Science</h5>
							                                                <p>Hover effect here where, when you hover on any one of the services a
							                                                    small description.</p> -->
							                                                    
							                                                <span>What Are you Struggling with?</span>
							                                            </div>
							                                        </div>
							                                        
							                                       
							                                        
							
							                        `);


				service_platform_type_method();



			});
		});
	};
	// end

	service_back_sub_menu_button_footer_method();





	// Open Therapist 

	const open_therapist_menu = document.querySelectorAll('#open_therapist_menu');

	// adding the event listener by looping
	open_therapist_menu.forEach(element => {

		element.addEventListener("click", (e) => {
			window.scrollTo({ top: 0, behavior: 'smooth' });

			var check_service_location_id = $('#selected_service_location_id').val();

			if (check_service_location_id !== "") {

				$('#appointment-warning').hide()

				$('#open-location-menu').removeClass("active")
				$('#open-content-location-menu').removeClass("show active");
				$('#open-therapist-menu').last().addClass("active");
				$('#open-content-therapist-menu').last().addClass("show active");

				var service_id = $('#selected_service_id').val();
				var service_sub_id = $('#selected_service_categ_id').val();

				var queryString = window.location.search;

				var urlParams = new URLSearchParams(queryString);

				var queryString_therapist_id = parseInt(urlParams.get('therapist_id'));



				$.ajax({
					url: "/appointment/service/therapist/filter",
					type: 'POST',
					async: false,
					data: {
						'company_id': $('#selected_service_location_id').val(),
						'service_id': service_id,
						'service_sub_id': service_sub_id,
					},
					success: function (result) {
						var resultJSON = jQuery.parseJSON(result);
						$('.bookapp-choose-therapist').empty();

						$.each(resultJSON, function (key, value) {

							if (queryString_therapist_id) {


								if (queryString_therapist_id === value['id']) {

									$('.bookapp-choose-therapist').append(`
					
								                 		<div class="col-xl-2 col-lg-3 col-md-12 col-sm-12 col-xs-12 therapychooslist" id="select_service_therapist" selected-therapist_id="`+ value['id'] + `">
							                                    <div class="therapest-list-container">
							                                        <img src=`+ value['image'] + ` loading="lazy"/>
							                                        <h5>`+ value['name'] + `</h5>
							
							                                        <a class="buttonwithbtnshape"> More info </a>
							                                    </div>
							                                </div>
							                                
							                         `);

								}


							} else {

								$('.bookapp-choose-therapist').append(`
					
						                 		<div class="col-xl-2 col-lg-3 col-md-12 col-sm-12 col-xs-12 therapychooslist" id="select_service_therapist" selected-therapist_id="`+ value['id'] + `">
					                                    <div class="therapest-list-container">
					                                        <img src=`+ value['image'] + ` loading="lazy"/>
					                                        <h5>`+ value['name'] + `</h5>
					
					                                        <a class="buttonwithbtnshape"> More info </a>
					                                    </div>
					                                </div>
					                                
					                         `);


							}


						});




						$('.therapist-location-list').empty();
						$('.therapist-location-list').append(`
											<option value="" disabled="disabled" selected="selected">Choose Therapist</option>
				                         `);


						$.each(resultJSON, function (key, value) {


							if (queryString_therapist_id) {

								if (queryString_therapist_id === value['id']) {

									$('.therapist-location-list').append(`
																
																<option value="`+ value['id'] + `">` + value['name'] + `</option>
									                                
									                         `);

								}

							} else {

								$('.therapist-location-list').append(`
																
																<option value="`+ value['id'] + `">` + value['name'] + `</option>
									                                
									                         `);



							}





						});







					},
				});




				// Open select service Therapist 

				const select_service_therapist = document.querySelectorAll('#select_service_therapist');

				// adding the event listener by looping
				select_service_therapist.forEach(element => {

					element.addEventListener("click", (e) => {

						window.scrollTo({ top: 300, behavior: 'smooth' });
						//var searchParams = new URLSearchParams(window.location.search);
						//searchParams.set("therapist_id", "");
						//window.location.search = searchParams.toString();


						//$(".timepickerbuttons").removeClass("timeshooseactive");
						//$(this).addClass("selectedDate");
						//e.currentTarget.classList.add('timeshooseactive');
						//const slot_id = e.currentTarget.getAttribute("data-slot-id");
						//$("#selected_appointment_slot_id").val(slot_id);

						//Calendar
						$('#selected_appointment_date').val('');
						$(".time-picker").addClass("display-none");
						$('#appointment-timepickerrows').empty();
						$("#selected_appointment_slot_id").val('');
						$(".timepickerbuttons").removeClass("timeshooseactive");


						$(".therapychooslist").removeClass("select-therapest");
						e.currentTarget.classList.add('select-therapest');

						const therapist_id = e.currentTarget.getAttribute("selected-therapist_id");

						$('#selected_service_therapist_id').val(therapist_id);

						$('#open-content-sub-therapist-menu').addClass("d-none")
						$('.bookapp-choose-therapist').addClass("d-none")
						$('#therapist-profile-menu').removeClass("d-none");

						var service_id = $('#selected_service_id').val();
						var service_sub_id = $('#selected_service_categ_id').val();


						$.ajax({
							url: "/appointment/service/therapist/filter",
							type: 'POST',
							async: false,
							data: {
								'company_id': $('#selected_service_location_id').val(),
								'service_id': service_id,
								'service_sub_id': service_sub_id,
							},
							success: function (result) {
								var resultJSON = jQuery.parseJSON(result);

								$('.therapist-location-list').empty();
								$('.therapist-location-list').append(`
													<option value="" disabled="disabled">Choose Therapist</option>
						                         `);


								$.each(resultJSON, function (key, value) {

									if (value['id'] == therapist_id) {
										$('.therapist-location-list').append(`
																		
																			<option value="`+ value['id'] + `" selected="selected">` + value['name'] + `</option>
											                         `);
									}
									else {
										$('.therapist-location-list').append(`
																		
																			<option value="`+ value['id'] + `">` + value['name'] + `</option>
											                         `);
									}

								});

							},
						});


						$.ajax({
							url: "/appointment/service/therapist/filter",
							type: 'POST',
							async: false,
							data: {
								'therapist_id': therapist_id,
							},
							success: function (result) {
								var resultJSON = jQuery.parseJSON(result);
								$('.therapist-profile').empty();

								$.each(resultJSON, function (key, value) {
									$('.therapist-profile').append(`
							
							                 		<div class="row bookapp-therapyinfo-innersec">
						                                            <div class="col-xl-5=6 col-lg-6 col-md-6 col-sm-12 col-xs-12">
						                                                <h5>`+ value['name'] + `</h5>
						                                                <p><b>Languages Spoken:</b> `+ value['lang_ids'] + ` </p>
						                                                <p><b>Nationality:</b> `+ value['country_id'] + `</p>
						                                                <label class="therapestlocation">`+ value['location_id'] + `</label>
						                                                <label class="onlinegobalicon">`+ value['platform'] + ` appointments</label>
						                                            </div>
						                                            <div class="col-xl-5=6 col-lg-6 col-md-6 col-sm-12 col-xs-12">
						                                                <img src=`+ value['image'] + ` loading="lazy"/>
						                                            </div>
						                                        </div>
						                                        <p>
						                                        
						                                        	`+ value['about_empolyee'] + `
						                                        
						                                        </p>
						                                
						                         `);

								});

							},
						});






					});


					var therapist_id = $('#selected_service_therapist_id').val();

					var service_ele_therapist_id = element.getAttribute("selected-therapist_id");

					if (service_ele_therapist_id === therapist_id) {

						element.classList.add('select-therapest');


					}


				});


			} else {

				$('#appointment-warning').text('Kindly select your location to proceed!')
				$('#appointment-warning').show()


			}










		});









	});







	// accessing the elements with same classname
	// open_appointment_number_session_menu
	const open_appointment_number_session_menu = document.querySelectorAll('#open_appointment_number_session_menu');

	// adding the event listener by looping
	open_appointment_number_session_menu.forEach(element => {

		element.addEventListener("click", (e) => {

			window.scrollTo({ top: 0, behavior: 'smooth' });
			var check_slot_id = $("#selected_appointment_slot_id").val();

			if (check_slot_id !== "") {

				$('#appointment-warning').hide()

				$('#open-appointment-calendar-menu').removeClass("active")
				$('#open-content-appointment-calendar-menu').removeClass("show active");

				$('#open-numbers-sessions-menu').last().addClass("active");
				$('#open-content-number-session-menu').last().addClass("show active");


				var therapist_id = $('#selected_service_therapist_id').val();
				var selected_service_id = $('#selected_service_id').val();
				var selected_service_categ_id = $('#selected_service_categ_id').val();
				var time_id = $('#appointment_time_id').val();




				//start of ajax

				$.ajax({
					url: "/appointment/service/session/filter",
					type: 'POST',
					async: false,
					data: {
						'therapist_id': therapist_id,
						'service_id': selected_service_id ,
						'service_categ_id': selected_service_categ_id,
						'time_id': time_id,
					},
					success: function (result) {
						var resultJSON = jQuery.parseJSON(result);
						$('#bookpackagecard-sessionslistcard').empty();


						$.each(resultJSON, function (key, value) {
							$('#bookpackagecard-sessionslistcard').append(`
				                    
				                    	<div class="sessionslistcard" id="sessionslistcard-appointment" data-session-id="`+ value['id'] + `" data-session-type="` + value['type'] + `">
		                                    <h4>`+ value['name'] + `</h4>
		                                    <p>`+ value['discount_text'] + `</p>
		                                </div>
				
			                         `);

						});

					},
				});




				//end of ajax

				//start of function


				// accessing the elements with same classname

				const sessionslistcard_appointment = document.querySelectorAll('#sessionslistcard-appointment');

				// adding the event listener by looping
				sessionslistcard_appointment.forEach(element => {

					element.addEventListener("click", (e) => {

						window.scrollTo({ top: 600, behavior: 'smooth' });
						$(".sessionslistcard").removeClass("select-sessionslistcard");
						e.currentTarget.classList.add('select-sessionslistcard');

						var single_session_id;
						var session_type;
						var package_session_id;
						single_session_id = e.currentTarget.getAttribute("data-session-id");
						session_type = e.currentTarget.getAttribute("data-session-type");
						package_session_id = e.currentTarget.getAttribute("data-session-id");

						$('#selected_appointment_session_type').val(session_type);
						$('#selected_appointment_single_session_id').val(single_session_id);
						$('#selected_appointment_package_session_id').val(package_session_id);



					});
				});


				//end of function


			} else {


				$('#appointment-warning').text('No slots were selected!');
				$('#appointment-warning').show();


			}
			// if appointment type is free consultant mean auto select the single session type
			if(searchParams.get('appointment_type')=='free')
				{
					$('[data-session-type="single"]').trigger('click')
					$('#open_appointment_customer_menu').trigger('click')
					 
				}







		});
		
	});














	//start
	// accessing the elements with same classname

	// appointment_number_session_button
	const appointment_number_session_button = document.querySelectorAll('#appointment_number_session_button');

	// adding the event listener by looping
	appointment_number_session_button.forEach(element => {

		element.addEventListener("click", (e) => {

			$('#open-numbers-sessions-menu').removeClass("active")
			$('#open-content-number-session-menu').removeClass("show active");

			$('#open-appointment-calendar-menu').last().addClass("active");
			$('#open-content-appointment-calendar-menu').last().addClass("show active");

		});
	});

	//end

	//start
	// accessing the elements with same classname

	// appointment_number_session_button
	const appointment_number_session_button_footer = document.querySelectorAll('#appointment_number_session_button_footer');

	// adding the event listener by looping
	appointment_number_session_button_footer.forEach(element => {

		element.addEventListener("click", (e) => {

			$('#open-numbers-sessions-menu').removeClass("active")
			$('#open-content-number-session-menu').removeClass("show active");

			$('#open-appointment-calendar-menu').last().addClass("active");
			$('#open-content-appointment-calendar-menu').last().addClass("show active");

		});
	});

	//end





	// open Customer menu
	const open_appointment_customer_menu = document.querySelectorAll('#open_appointment_customer_menu');
	$("#open_appointment_customer_menu").click(function () {
		window.scrollTo({ top: 0, behavior: 'smooth' });
	});
	// adding the event listener by looping
	open_appointment_customer_menu.forEach(element => {

		element.addEventListener("click", (e) => {


			var check_session_type = $('#selected_appointment_session_type').val();

			if (check_session_type !== "") {

				$('#appointment-warning').hide();

				$('#open-numbers-sessions-menu').removeClass("active")
				$('#open-content-number-session-menu').removeClass("show active");

				$('#open-appointment-cuustomer-menu').last().addClass("active");
				$('#open-content-customer-menu').last().addClass("show active");

			} else {

				$('#appointment-warning').text('Kindly select your package to proceed!');
				$('#appointment-warning').show();


			}






		});
	});

	// end










	//start
	// accessing the elements with same classname

	// appointment customer button
	const appointment_customer_button = document.querySelectorAll('#appointment_customer_button');

	// adding the event listener by looping
	appointment_customer_button.forEach(element => {

		element.addEventListener("click", (e) => {

			$('#open-appointment-cuustomer-menu').removeClass("active")
			$('#open-content-customer-menu').removeClass("show active");

			$('#open-numbers-sessions-menu').last().addClass("active");
			$('#open-content-number-session-menu').last().addClass("show active");




		});
	});

	//end


	//start
	// accessing the elements with same classname

	// appointment customer button
	const appointment_customer_button_footer = document.querySelectorAll('#appointment_customer_button_footer');

	// adding the event listener by looping
	appointment_customer_button_footer.forEach(element => {

		element.addEventListener("click", (e) => {

			$('#open-appointment-cuustomer-menu').removeClass("active")
			$('#open-content-customer-menu').removeClass("show active");

			$('#open-numbers-sessions-menu').last().addClass("active");
			$('#open-content-number-session-menu').last().addClass("show active");




		});
	});

	//end



	//start

	// Create Appointment
	const submit_appointment = document.querySelectorAll('#submit-appointment');

	// adding the event listener by looping
	// submit_appointment.forEach(element => {

	// 	element.addEventListener("click", (e) => {

	// 		var check_name = $("#customer_name").val();
	// 		var check_email = $("#email").val();
	// 		var check_phone = $("#phone").val();
	// 		var check_appointment_country_id = $("#appointment_country_id").val();
	// 		var check_appointment_city_id = $("#appointment_city_id").val();
	// 		var check_street = $("#street").val();

	// 		if (check_name !== "" && check_email !== "" && check_phone !== "" && check_appointment_country_id !== "" && check_appointment_city_id !== "" && check_street !== "" && check_appointment_country_id !== null && check_appointment_city_id !== null) {

	// 			if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(check_email)) {

	// 				$('#appointment-warning').hide();

	// 				appointemt = [];
	// 				var data = {};

	// 				$("input").each(function () {
	// 					var input_field = $(this);
	// 					data[input_field.attr('id')] = input_field.val()
	// 				});

	// 				$("select").each(function () {
	// 					var input_field = $(this);
	// 					data[input_field.attr('id')] = input_field.val()
	// 				});

	// 				$.ajax({
	// 					url: "/appointment/service/create",
	// 					type: 'POST',
	// 					async: false,
	// 					data: {
	// 						'data': data,
	// 					},
	// 					success: function (result) {
	// 						var resultJSON = jQuery.parseJSON(result);
	// 						$.each(resultJSON, function (key, value) {
	// 							$('#customer_appointment_id').val(value['customer_appointment_id']);
	// 							$('#customer_name').attr('readonly', 'readonly');
	// 							$('#email').attr('readonly', 'readonly');
	// 							$('#phone').attr('readonly', 'readonly');
	// 							$('#appointment_country_id').attr('readonly', 'readonly');
	// 							$('#appointment_city_id').attr('readonly', 'readonly');
	// 							$('#street').attr('readonly', 'readonly');
	// 							$('#submit-appointment').attr('disabled', 'disabled');
	// 						});
	// 					},
	// 				});

	// 				var customer_appointment_id = $('#customer_appointment_id').val();
	// 				$.ajax({
	// 					url: "/appointment/checkout/shop/cart",
	// 					type: 'POST',
	// 					async: false,
	// 					data: {
	// 						'appointment_id': customer_appointment_id,
	// 					},
	// 					success: function (result) {
	// 						// var resultJSON = jQuery.parseJSON(result);
	// 					},
	// 				});


	// 				//end of ajax

	// 				// var newForm = document.createElement('form');
	// 				// newForm.setAttribute("method", "post"); // set it to post
	// 				// newForm.hidden = true; // hide it
	// 				// newForm.innerHTML = ""; // put the html sent by the server inside the form
	// 				// var url = window.location.origin;
	// 				// var action_url = url + "/appointment/checkout/shop/cart";
	// 				// newForm.setAttribute("action", action_url); // set the action url

	// 				// var appointment_id_ele = document.createElement("input");
	// 				// appointment_id_ele.setAttribute("type", "text");
	// 				// appointment_id_ele.setAttribute("name", "appointment_id");
	// 				// appointment_id_ele.setAttribute("value", customer_appointment_id);


	// 				// newForm.appendChild(appointment_id_ele);
	// 				// $(document.getElementsByTagName('body')[0]).append(newForm); // append the form to the body
	// 				// newForm.submit();

	// 			} else {
	// 				$('#appointment-warning').text('Invalid Email ID!')
	// 				$('#appointment-warning').show();
	// 			}

	// 		} else {
	// 			$('#appointment-warning').text('Some mandatory fields are empty!')
	// 			$('#appointment-warning').show();
	// 		}

	// 	});
	// });
	//end	


	$("#submit-appointment").click(function () {
		//$("#submit-appointment").html(`
				//<i class="fa fa-spinner fa-spin"></i>Loading`)
		// $("#submit-appointment").attr('disabled', 'disabled');

		setTimeout(function () {
			var check_name = $("#customer_name").val();
			var check_email = $("#email").val();
			var check_phone = $("#phone").val();
			var check_appointment_country_id = $("#appointment_country_id").val();
			var check_appointment_city_id = $("#appointment_city_id").val();
			var check_street = $("#street").val();


			if (check_name !== "" && check_email !== "" && check_phone !== "" && check_appointment_country_id !== "" && check_appointment_city_id !== "" && check_street !== "" && check_appointment_country_id !== null && check_appointment_city_id !== null) {

				if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(check_email)) {

					$('#appointment-warning').hide();

					appointemt = [];
					var data = {};

					$("input").each(function () {
						var input_field = $(this);
						data[input_field.attr('id')] = input_field.val()
					});

					$("select").each(function () {
						var input_field = $(this);
						data[input_field.attr('id')] = input_field.val()
					});

					$.ajax({
						url: "/appointment/service/create",
						type: 'POST',
						async: false,
						data: {
							'data': data,
						},
						success: function (result) {
							var resultJSON = jQuery.parseJSON(result);
							$.each(resultJSON, function (key, value) {
								$('#customer_appointment_id').val(value['customer_appointment_id']);
								$('#customer_name').attr('readonly', 'readonly');
								$('#email').attr('readonly', 'readonly');
								$('#phone').attr('readonly', 'readonly');
								$('#appointment_country_id').attr('readonly', 'readonly');
								$('#appointment_city_id').attr('readonly', 'readonly');
								$('#street').attr('readonly', 'readonly');
								$('#submit-appointment').attr('disabled', 'disabled');
							});
						},
					});

					var customer_appointment_id = $('#customer_appointment_id').val();
					var newForm = document.createElement('form');
					newForm.setAttribute("method", "post"); // set it to post
					newForm.hidden = true; // hide it
					newForm.innerHTML = ""; // put the html sent by the server inside the form
					var url = window.location.origin;
					var action_url = url + "/appointment/checkout/shop/cart";
					newForm.setAttribute("action", action_url); // set the action url

					var appointment_id_ele = document.createElement("input");
					appointment_id_ele.setAttribute("type", "text");
					appointment_id_ele.setAttribute("name", "appointment_id");
					appointment_id_ele.setAttribute("value", customer_appointment_id);


					newForm.appendChild(appointment_id_ele);
					$(document.getElementsByTagName('body')[0]).append(newForm); // append the form to the body
					newForm.submit();

				} else {
					$('#appointment-warning').text('Invalid Email ID!')
					$('#appointment-warning').show();
				}

			} else {
				$('#appointment-warning').text('Some mandatory fields are empty!')
				$('#appointment-warning').show();
			}

		}, 1000);




	});




window.addEventListener("load", auto_select_function);

});

// checkout fcity filter based on country
$("#appointment_country_id").change(function () {
	const country_id = $('#appointment_country_id').val()
	    $.ajax({
	        url: "/checkout/city/filter",
	        type: 'POST',
	        async: false,
	        data: {
	            'browse_country': country_id,
	        },
	        success: function (result) {
		    var resultJSON = jQuery.parseJSON(result);
		     $('.check_out_filters_id').empty();
			$('.check_out_filters_id').append(`
				<option value="" disabled="disabled" selected="selected">Select a City/Town</option>
                         `);

			$.each(resultJSON, function (key, value) {
				$('.check_out_filters_id').append(`
							
			<option value="`+ value['id'] + `">` + value['name'] + `</option>
                                
                         `);

			});


        },
    });


});






