// var startCarousel = () => {
//     var holistichealingtherapyteamlider = $("#holistichealingtherapyteamlider").owlCarousel({
//         responsive: {
//             0: {
//                 items: 1,
//                 autoplay: false,
//                 dots: true,
//                 loop: false,
//                 responsiveClass: true,
//                 margin: 20,
//                 stagePadding: 20,
//                 autoWidth: false,
//                 touchDrag: true,

//             },
//             400: {
//                 items: 2,
//                 autoplay: false,
//                 dots: true,
//                 loop: false,
//                 responsiveClass: true,
//                 margin: 20,
//                 stagePadding: 20,
//                 autoWidth: false,
//                 touchDrag: true,
//             },

//         }
//     });
//     holistichealingtherapyteamlider.owlCarousel();
// }

// var stopCarousel = () => {
//     var owl = $('.popularpost-caresole-mobile');
//     owl.trigger('destroy.owl.carousel');
//     owl.addClass('off');
// }



// $(window).resize(function () {
//     if (window.innerWidth < 600) {
//         startCarousel();
//     } else {
//         stopCarousel();
//     }
// });

$(document).ready(function () {
    $('#browse_helpHealing').val('all');
    $('#browse_platformHealing').val('all');
    $('#browse_qualifiedHealing').val('all');
    $('#browse_locationHealing').val('all');

    $('#HealingCatFilterSelect').val('all');
    $('#HealingSubFilterSelect').val('all');
    $('#multiselect-filter-tag_id').val();
    $("#multiselect-filter-tag_id").multiselect('clearSelection');




    // if (window.innerWidth < 1200) {
    // var holistichealingtherapyteamlider = $("#holistichealingtherapyteamlider").owlCarousel({
    //     autoplay: false,
    //     dots: true,
    //     loop: false,
    //     margin: 10,
    //     autoWidth: false,
    //     touchDrag: true,
    //     responsive: true,
    //     responsiveClass: true,
    // responsive: {
    //     0: {
    //         items: 1,
    //         margin: 10,
    //         stagePadding: 30,
    //     },
    //     768: {
    //         items: 2,
    //         margin: 10,
    //     },
    //     900: {
    //         items: 3
    //     },
    //     1400: {
    //         items: 4
    //     }
    // }
    // });

    // holistichealingtherapyteamlider.owlCarousel();

    // $('.aboutTherapist-team-right').click(function () {
    //     aboutTherapistImage_Sliderll.trigger('next.owl.carousel');
    // })
    // $('.aboutTherapist-team-left').click(function () {
    //     aboutTherapistImage_Sliderll.trigger('prev.owl.carousel', [300]);
    // })
    // }

    $("#multiselect-filter-tag_id").change(function () {
        filter_tag_id = $('#multiselect-filter-tag_id').val()
        if (filter_tag_id.length === 0) {
            filter_tag_id = '[]'
        }
        var HealingCatFilterSelect = document.getElementById("HealingCatFilterSelect")
        var HealingSubFilterSelect = document.getElementById("HealingSubFilterSelect")
        $.ajax({
            url: "/get/model/holistic-healing/filter/tag/" + HealingCatFilterSelect.value + '/' + HealingSubFilterSelect.value + '/' + filter_tag_id,
            type: "get",
            async: false,
            dataType: 'json',
            success: function (result) {
                $('#CategoryView').html(result.data);
            }
        });
    });

});
var HealingCatDiv = (id, type) => {
    filter_tag_id = $('#multiselect-filter-tag_id').val()
    if (filter_tag_id.length === 0) {
        filter_tag_id = '[]'
    }
    var HealingCatFilterSelect = document.getElementById("HealingCatFilterSelect").value
    var HealingSubFilterSelect = document.getElementById("HealingSubFilterSelect").value
    if (type == 'category') {
        HealingCatFilterSelect = id;
        $('#HealingCatFilterSelect').val(id);
    }
    $.ajax({
        url: "/get/model/holistic-healing/filter/" + type + '/' + HealingCatFilterSelect + '/' + HealingSubFilterSelect + '/' + filter_tag_id,
        type: "get",
        async: false,
        dataType: 'json',
        success: function (result) {
            $('#CategoryView').html(result.sub_cat);
            $('#HealingSubFilterSelect').html(result.filter);
        }
    });
}
function HealingCatFilter() {
    filter_tag_id = $('#multiselect-filter-tag_id').val()
    if (filter_tag_id.length === 0) {
        filter_tag_id = '[]'
    }
    var HealingCatFilterSelect = document.getElementById("HealingCatFilterSelect")
    var HealingSubFilterSelect = document.getElementById("HealingSubFilterSelect")
    $.ajax({
        url: "/get/model/holistic-healing/filter/category/" + HealingCatFilterSelect.value + '/' + HealingSubFilterSelect.value + '/' + filter_tag_id,
        type: "get",
        async: false,
        dataType: 'json',
        success: function (result) {
            $('#CategoryView').html(result.sub_cat);
            $('#HealingSubFilterSelect').html(result.filter);
        }
    });
}
function ServiceHealingCategoryFn() {
    var ServiceHealingCategory = document.getElementById("ServiceHealingCategory")
    $.ajax({
        url: "/get/model/holistic-healing/category/" + ServiceHealingCategory.value,
        type: "get",
        async: false,
        dataType: 'json',
        success: function (result) {
            $('#ServiceHealingSubCategory').html(result.data);
        }
    });
}
function HealingSubFilter() {
    filter_tag_id = $('#multiselect-filter-tag_id').val()
    if (filter_tag_id.length === 0) {
        filter_tag_id = '[]'
    }
    var HealingCatFilterSelect = document.getElementById("HealingCatFilterSelect")
    var HealingSubFilterSelect = document.getElementById("HealingSubFilterSelect")
    $.ajax({
        url: "/get/model/holistic-healing/filter/sub/" + HealingCatFilterSelect.value + '/' + HealingSubFilterSelect.value + '/' + filter_tag_id,
        type: "get",
        async: false,
        dataType: 'json',
        success: function (result) {
            $('#CategoryView').html(result.sub_cat);
        }
    });
}
function HealingSubDiv(id) {
    window.location.href = "/healing/" + id + "/register";
}
$('#multiselect-filter-tag_id').multiselect({
    enableCaseInsensitiveFiltering: true,
    includeSelectAllOption: true,
    // maxHeight: 400,
    // buttonWidth: '100%',
    dropUp: false,
    // templates: {
    //     button: '<button type="button" class="multiselect dropdown-toggle btn btn-default" style="text-align:left;" data-toggle="dropdown"><span class="multiselect">&nbspBy Struggle</span></button>',
    // },
    buttonText: function (options, select) {
        return ' By Struggle';
    },
    buttonTitle: function (options, select) {
        var labels = [];
        options.each(function () {
            labels.push($(this).text());
        });
        return labels.join(' - ');
    },
});

// $("#browse_help_Healing , #browse_platform_Healing , #browse_qualified_Healing , #browse_location_Healing").change(function () {
//     $.ajax({
//         url: "/employee/filter/details",
//         type: 'POST',
//         async: false,
//         data: {
//             'browse_help': $('#browse_help_Healing').val(),
//             'browse_qualified': $('#browse_qualified_Healing').val(),
//             'browse_location': $('#browse_location_Healing').val(),
//             'browse_platform': $('#browse_platform_Healing').val(),
//         },
//         success: function (result) {
//             var resultJSON = jQuery.parseJSON(result);
//             $('#holistichealingtherapyteamlider').empty();
//             $.each(resultJSON, function (key, value) {
//                 $('#holistichealingtherapyteamlider').append(`
//                             <div class="col-xl-3 col-lg-4 col-md-6 col-sm-6 col-xs-12 o_colored_level">
//                                 <div class="therapest-list-container">
//                                   <img src=`+ value['image'] + ` loading="lazy"/>
//                                   <h5 class="o_default_snippet_text">`+ value['name'] + `</h5>
//                                   <p class="o_default_snippet_text">` + value['job'] + ` </p>
//                                   <label class="therapestlocation o_default_snippet_text">` + value['location'] + `</label>
//                                   <a href="/contactus" class="buttonwithbtnshape o_default_snippet_text"> Book an appointment </a>
//                                 </div>
//                           </div>
//                         `);
//             });
//         },
//     });
// });


//
//if (window.innerWidth < 600) {
//    startCarousel();
//} else {
//    $('#therapyteamliderHealing').addClass('off');
//}
//
//$(window).resize(function () {
//    // footerwave();
//    // console.log($(window).width(), 'asd');
//    // console.log(window.innerWidth, 'a11111111sd');
//    if (window.innerWidth < 600) {
//        // alert("aone");
//        startCarousel();
//    } else {
//        stopCarousel();
//    }
//});
//
//
//function startCarousel() {
//    var popularpostlists = $("#therapyteamliderHealing").owlCarousel({
//
//        responsive: {
//            0: {
//                items: 1,
//                autoplay: false,
//                dots: true,
//                loop: false,
//                responsiveClass: true,
//                margin: 20,
//                stagePadding: 20,
//                autoWidth: false,
//                touchDrag: true,
//
//            },
//            400: {
//                items: 2,
//                autoplay: false,
//                dots: true,
//                loop: false,
//                responsiveClass: true,
//                margin: 20,
//                stagePadding: 20,
//                autoWidth: false,
//                touchDrag: true,
//            },
//
//        }
//    });
//}
//
//function stopCarousel() {
//    var owl = $('.popularpost-caresole-mobile');
//    owl.trigger('destroy.owl.carousel');
//    owl.addClass('off');
//}


