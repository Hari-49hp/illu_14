$(document).ready(function(){ 

	var imagePos_client_top_wave = $('.client-about-illumincations').offset().top + 750;

	$(window).on("scroll", function() {
		
		// Client About Top View
		var imageHeight = $('.client-about-illumincations').height();
		var topOfWindow = $(window).scrollTop(); 

		if (imagePos_client_top_wave < topOfWindow + imageHeight && imagePos_client_top_wave + imageHeight > topOfWindow) {
			$('.client-about-illumincations').addClass("btm_wave_activate");
		} else {
			$('.client-about-illumincations').removeClass("btm_wave_activate");
		}
        // Client About Top View

    });

});