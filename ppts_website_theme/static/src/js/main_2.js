function openNav() {
    $('#mySidenav').toggleClass("activemenu");
    $('html').toggleClass("menuopened");
}

if (window.innerWidth < 600) {
    startCarousel();
} else {
    $('#therapyteamlider').addClass('off');
}

$(window).resize(function () {
    // footerwave();
    // console.log($(window).width(), 'asd');
    // console.log(window.innerWidth, 'a11111111sd');
    if (window.innerWidth < 600) {
        // alert("aone");
        startCarousel();
    } else {
        stopCarousel();
    }
});


function startCarousel() {
    var popularpostlists = $("#therapyteamlider").owlCarousel({

        responsive: {
            0: {
                items: 1,
                autoplay: false,
                dots: true,
                loop: false,
                responsiveClass: true,
                margin: 20,
                stagePadding: 20,
                autoWidth: false,
                touchDrag: true,

            },
            400: {
                items: 2,
                autoplay: false,
                dots: true,
                loop: false,
                responsiveClass: true,
                margin: 20,
                stagePadding: 20,
                autoWidth: false,
                touchDrag: true,
            },

        }
    });


}

function stopCarousel() {
    var owl = $('.popularpost-caresole-mobile');
    owl.trigger('destroy.owl.carousel');
    owl.addClass('off');
}

if (window.innerWidth < 600) {
    var corporatewellness_therapyslider = $("#corporatewellness_therapyslider").owlCarousel({

        responsive: {
            0: {
                items: 1,
                autoplay: false,
                dots: true,
                loop: false,
                responsiveClass: true,
                margin: 20,
                stagePadding: 20,
                autoWidth: false,
                touchDrag: true,

            },
            400: {
                items: 2,
                autoplay: false,
                dots: true,
                loop: false,
                responsiveClass: true,
                margin: 20,
                stagePadding: 20,
                autoWidth: false,
                touchDrag: true,
            },

        }
    });

    corporatewellness_therapyslider.owlCarousel();
} else {
    // $('#corporatewellness_therapyslider').addClass('off');
}

var curriculumtabs = $('.curriculumlevel_tabs').owlCarousel({
    autoplay: false,
    dots: true,
    loop: false,
    margin: 0,
    // stagePadding: 40,
    autoWidth: true,
    touchDrag: true,
    DragEvent: true,
    mouseDrag: true,
    freeDrag: true,
    slideSpeed: 400,
    paginationSpeed: 400,

    responsive: {
        0: {
            items: 1,


        },
        600: {
            items: 1,


        },
        1000: {
            items: 5,

        }
    }
})

$('#curriculumlevel_tabs-right').click(function () {
    curriculumtabs.trigger('next.owl.carousel');
})
// Go to the previous item
$('#curriculumlevel_tabs-left').click(function () {
    curriculumtabs.trigger('prev.owl.carousel', [300]);
})

var li = $(".curriculumlevel_tabs .owl-item .nav-item a");
$(" .curriculumlevel_tabs .owl-item .nav-item").click(function () {
    li.removeClass('active');

});




function callist_table_view(viewmode) {
    if (viewmode == 0) {
        $("#calendar_listview").css("display", "none");
        $("#cal_tableview").css("display", "block");

        $("#dropdownMenuButtonList").removeClass("d-none");
        $("#dropdownMenuButtonGrid").addClass("d-none");

    }
    if (viewmode == 1) {
        $("#calendar_listview").css("display", "block");
        $("#cal_tableview").css("display", "none");

        $("#dropdownMenuButtonGrid").removeClass("d-none");
        $("#dropdownMenuButtonList").addClass("d-none");
    }

}

// $('#ourteamfilterpopup').on('click', function () {

// $('#outteamfilter').modal({
//   keyboard: false,
//   show: true,

//   focus: true
// }),
// $('#outteamfilter').toggleClass("activeourteamfilterpopup");
// });
$('#ourteamfilterpopup').on('click', function () {
    $('#outteamfilter').toggleClass("activeourteamfilterpopup");
    $('#outteamfilter').toggleClass("modal left fade show");
});
$('#ourteamfilterpopupoe').on('click', function () {
    $('#outteamfilter').toggleClass("activeourteamfilterpopup");
});

function Trainingsweofferslider() {
    var ourcourseslider = $("#ourcourse").owlCarousel({
        autoplay: false,
        dots: true,
        loop: false,
        margin: 40,
        // stagePadding: 40,
        autoWidth: true,
        touchDrag: true,
        responsive: {
            0: {
                items: 1,

            },
            768: {
                items: 1,

            },
            900: {
                items: 1,
                slideBy: 1

            },
            1400: {
                items: 1,
                slideBy: 1

            }
        }
    });

    $('#ourcourse-right').click(function () {
        ourcourseslider.trigger('next.owl.carousel');
    })
    // Go to the previous item
    $('#ourcourse-left').click(function () {
        ourcourseslider.trigger('prev.owl.carousel', [300]);
    })
}





function TrainingsweoffersliderstopCarousel() {

    ourcourseslider.trigger('destroy.owl.carousel');
    ourcourseslider.addClass('off');
}


if (window.innerWidth > 767) {

    Trainingsweofferslider();
} else {
    // TrainingsweoffersliderstopCarousel();


}

$(window).resize(function () {
    if (window.innerWidth > 767) {
        Trainingsweofferslider();
    } else {

        // TrainingsweoffersliderstopCarousel();
    }
});

var snapshottraining = $("#snapoftraining").owlCarousel({
    stagePadding: 60,
    loop: true,
    margin: 40,

    responsive: {
        0: {
            items: 1,
            loop: false,
            autoWidth: true,
            margin: 20,
            stagePadding: 20,
        },
        768: {
            items: 2,
        },
        900: {
            items: 3,
        },
        1400: {
            items: 2,
        }
    }
});

// Go to the next item
$('#snapoftraining-right').click(function () {
    snapshottraining.trigger('next.owl.carousel');
})
// Go to the previous item
$('#snapoftraining-left').click(function () {
    snapshottraining.trigger('prev.owl.carousel', [300]);
})


$("#browse_help , #browse_qualified , #browse_location , #browse_platform").change(function () {


    $.ajax({
        url: "/employee/filter",
        type: 'POST',
        async: false,
        data: {
            'browse_help': $('#browse_help').val(),
            'browse_qualified': $('#browse_qualified').val(),
            'browse_location': $('#browse_location').val(),
            'browse_platform': $('#browse_platform').val(),
        },
        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            $('#therapyteamlider').empty();

            $.each(resultJSON, function (key, value) {
                $('#therapyteamlider').append(`

                <div class="col-xl-3 col-lg-4 col-md-6 col-sm-6 col-xs-12 o_colored_level">
                    <div class="therapest-list-container">
                      <img src=`+ value['image'] + ` loading="lazy"/>
                      <h5 class="o_default_snippet_text">`+ value['name'] + `</h5>
                      <p class="o_default_snippet_text">` + value['job'] + ` </p>
                      <label class="therapestlocation o_default_snippet_text">` + value['location'] + `</label>
                      <a class="buttonwithbtnshape o_default_snippet_text"> Book an appointment </a>
                    </div>
              </div>

                        `);
            });

        },
    });


});


$("#categ_browse_help , #categ_browse_qualified , #categ_browse_location , #categ_browse_platform").change(function () {


    $.ajax({
        url: "/employee/categ/filter",
        type: 'POST',
        async: false,
        data: {
            'categ_browse_help': $('#categ_browse_help').val(),
            'categ_browse_qualified': $('#categ_browse_qualified').val(),
            'categ_browse_location': $('#categ_browse_location').val(),
            'categ_browse_platform': $('#categ_browse_platform').val(),
        },
        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            $('#therapycategoryslider').empty();

            $.each(resultJSON, function (key, value) {
                $('#therapycategoryslider').append(`

                <div class="col-xl-3 col-lg-4 col-md-6 col-sm-6 col-xs-12 o_colored_level">
                    <div class="therapest-list-container">
                      <img src=`+ value['image'] + ` loading="lazy"/>
                      <h5 class="o_default_snippet_text">`+ value['name'] + `</h5>
                      <p class="o_default_snippet_text">` + value['job'] + ` </p>
                      <label class="therapestlocation o_default_snippet_text">` + value['location'] + `</label>
                      <a class="buttonwithbtnshape o_default_snippet_text"> Book an appointment </a>
                    </div>
              </div>

                        `);
            });

        },
    });


});

// Healing page filters 21-11-22


$("#browse_help_Healing , #browse_platform_Healing , #browse_qualified_Healing , #browse_location_Healing").change(function () {
    $.ajax({
        url: "/employee/filter/details",
        type: 'POST',
        async: false,
        data: {
            'browse_help': $('#browse_help_Healing').val(),
            'browse_qualified': $('#browse_qualified_Healing').val(),
            'browse_location': $('#browse_location_Healing').val(),
            'browse_platform': $('#browse_platform_Healing').val(),
        },
        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            $('#holistichealingtherapyteamlider').empty();
            $.each(resultJSON, function (key, value) {
                $('#holistichealingtherapyteamlider').append(`
                            <div class="col-xl-3 col-lg-4 col-md-6 col-sm-6 col-xs-12 o_colored_level">
                                <div class="therapest-list-container">
                                  <img src=`+ value['image'] + ` loading="lazy"/>
                                  <h5 class="o_default_snippet_text">`+ value['name'] + `</h5>
                                  <p class="o_default_snippet_text">` + value['job'] + ` </p>
                                  <label class="therapestlocation o_default_snippet_text">` + value['location'] + `</label>
                                  <a href="/contactus" class="buttonwithbtnshape o_default_snippet_text"> Book an appointment </a>
                                </div>
                          </div>
                        `);
            });
        },
    });
});



