$(document).ready(function () {



	var imagePos_expert_top_wave = $('.ourexpertsec').offset().top;
	var imagePos_expert_slide_top_wave = $('.ourexpertsec').offset().top;
	$('.ourexpert_more-container').removeClass("slidetop-active");

	$(window).on("scroll", function () {

		// Expert Top View
		var imageHeight = $('.expert_top_wave').height();
		var topOfWindow = $(window).scrollTop();

		if (imagePos_expert_top_wave < topOfWindow + imageHeight && imagePos_expert_top_wave + imageHeight > topOfWindow) {
			$('.expert_top_wave').addClass("top_wave_activate");
		} else {
			$('.expert_top_wave').removeClass("top_wave_activate");
		}
		// Expert Top View


		if (imagePos_expert_slide_top_wave < topOfWindow + imageHeight && imagePos_expert_slide_top_wave + imageHeight > topOfWindow) {
			$('.ourexpert_more-container').addClass("slidetop-active");
			setTimeout(function () {
				$('.ourexpert-wrapper').addClass("typochangecolors");
			}, 2000);
		} else { }

	});

	// employee our experts

	$.ajax({
		url: "/home/our/excepts",
		type: "POST",
		async: false,
		data: {},
		success: function (result) {
			var resultJSON = jQuery.parseJSON(result);
			$(".exper-slider-caresole").empty();
			$.each(resultJSON, function (key, value) {
				$('.exper-slider-caresole').append(`
					<a href="/team/therapists/`+ value['id'] + `">
                        <div class="leadercont" data-aos="fade-left" data-aos-delay="450">
                            <img src="`+ value['image'] + `" />
                            <h5>`+ value['name'] + `</h5>
                            <p> `+ value['job'] + `</p>
                        </div></a>`);
			});
		}
	});

});


