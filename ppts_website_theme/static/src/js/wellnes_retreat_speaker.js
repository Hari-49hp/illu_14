$(document).ready(function () {

	// employee our experts

	$.ajax({
		url: "/wellness/retreat/speaker",
		type: "POST",
		async: false,
		data: {},
		success: function (result) {
			var resultJSON = jQuery.parseJSON(result);
			$("#speaker-expert-owl-carousel").empty();
			$.each(resultJSON, function (key, value) {
				$('#speaker-expert-owl-carousel').append(`
					<a href="/team/therapists/`+ value['id'] + `">
                        <div class="leadercont" data-aos="fade-left" data-aos-delay="750">
                            <img src="`+ value['image'] + `" />
                            <h5 style="font-size: 1.5rem !important;color: #585858 !important;max-width: 350px !important;line-height: 30px !important">`+ value['name'] + `</h5>
                            <p style="font-size: 1rem !important;color: #585858 !important;max-width: 350px !important;line-height: 30px !important"> `+ value['job'] + `</p>
                        </div></a>`);
			});
		}
	});

});






