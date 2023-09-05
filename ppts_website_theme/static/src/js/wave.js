$(document).ready(function(){ 
	var $win = $(window);

	jQuery.fn.visible = function(partial) {
		var $t = $(this),
		$w = $(window),
		viewTop = $w.scrollTop(),
		viewBottom = viewTop + $w.height(),
		_top = $t.offset().top,
		_bottom = _top + $t.height(),
		compareTop = partial === true ? _bottom : _top,
		compareBottom = partial === true ? _top : _bottom;

		return compareBottom <= viewBottom  && compareTop >= viewTop;
	};

	$(window).on("scroll", function() {
		$(".arrow-scroll").each(function(i, el) {
			var el = $(el);
			if (el.visible(true)) {
				el.addClass("active-arrowanim");
			} else {
				el.removeClass("active-arrowanim");
			}
		});

		$('.top-wave-svg').each(function (i, el) {
			var el = $(el);
			if (el.visible(true)) {
				el.addClass("top-wave-svg-activated");
			} 
			else {
				el.removeClass("top-wave-svg-activated");
			}
		});

		$('.bottom-wave-svg').each(function (i, el) {
			var el = $(el);
			if (el.visible(true)) {
				el.addClass("bottom-wave-svg-activated");
			} 
			else {
				el.removeClass("bottom-wave-svg-activated");
			}
		});
	});


	$("#wizard_web_login_btn").click(function(){
		$.ajax({
			url: "/wiz/web/login",
			type: 'POST',
			async:false,
			data: {
				'login': $('#login').val(),
				'password': $('#password').val(),
			},
			success: function(result) {
				var resultJSON = jQuery.parseJSON(result);
				if(resultJSON['login_success'] == 'false'){
					$('.alert-danger-login').removeClass('d-none');
				}
				else{
					$('.alert-danger-login').removeClass('d-none');
				}
			},
		});
	});

});