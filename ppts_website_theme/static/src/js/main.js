$(document).ready(function () {

    $('.modal').on("show.bs.modal", function () {
        $("html").addClass('html-overflow-model');
    })
    // $("#span_button_select_multi_list").html("By Struggle");

    $('.modal').on("hide.bs.modal", function () {
        $("html").removeClass('html-overflow-model');
    })

    function aos_init() {
        AOS.init({
            duration: 1000,
            once: true
        });
    }

    aos_init();

    // AOS.init();
    // AOS.init({
    //     disable: true, // accepts following values: 'phone', 'tablet', 'mobile', boolean, expression or function
    //     startEvent: 'DOMContentLoaded', // name of the event dispatched on the document, that AOS should initialize on
    //     initClassName: 'aos-init', // class applied after initialization
    //     animatedClassName: 'aos-animate', // class applied on animation
    //     useClassNames: false, // if true, will add content of `data-aos` as classes on scroll
    //     disableMutationObserver: false, // disables automatic mutations' detections (advanced)
    //     debounceDelay: 50, // the delay on debounce used while resizing window (advanced)
    //     throttleDelay: 99, // the delay on throttle used while scrolling the page (advanced)
    //     // Settings that can be overridden on per-element basis, by `data-aos-*` attributes:
    //     offset: 120, // offset (in px) from the original trigger point
    //     once: true,
    //     duration: 900,
    //     anchorPlacement: 'bottom-bottom',
    // });

    // if(screen.availWidth >=1900 && screen.availWidth <=1930) { 
    // console.log("Available Wid", screen.availWidth);
    // $('body').removeClass('twentyzoom');
    // $('body').removeClass('fiftyzoom');
    // if (window.devicePixelRatio >= 1.20 && window.devicePixelRatio <= 1.30) {
    //     console.log("below 20 to 30", window.devicePixelRatio)
    //     $('body').addClass('twentyzoom');
    //     $('body').removeClass('fiftyzoom');
    //     // $('body').append(`

    //     // <div id="zoomOnload-Loader">

    //     // <img src="/ppts_website_theme/static/src/img/Ghost.gif" class="succlogo">

    //     // </div>

    //     // `)

    //     // setTimeout(() => {
    //     //     $('#zoomOnload-Loader').remove();
    //     // }, 2000);

    // } else if (window.devicePixelRatio >= 1.45 && window.devicePixelRatio <= 1.55) {
    //     console.log("below 45 to 55", window.devicePixelRatio)
    //     $('body').addClass('fiftyzoom');
    //     $('body').removeClass('twentyzoom');
    //     // $('body').append(`

    //     // <div id="zoomOnload-Loader">

    //     // <img src="/ppts_website_theme/static/src/img/Ghost.gif" class="succlogo">

    //     // </div>

    //     // `)

    //     // setTimeout(() => {
    //     //     $('#zoomOnload-Loader').remove();
    //     // }, 2000);
    // }


    // }
    //     setTimeout(function () {
    //         $('.owl-dots:not(:last-child)').remove();
    //     }, 3000);


    $(".awardlists li").hover(function () {
        $("#AwardSectionLiHoverVisible").show()
    }, function (e) {
        $("#AwardSectionLiHoverVisible").hide()
    })

    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })

    // if ($(window).width() < 750) {
    //     // stopCarouselSearchArticle();
    //     $('#searchresult-article').addClass('off');

    // }
    // else {
    //     startCarouselSearchArticle();
    // }

    // if ($(window).width() > 750 && $(window).width() < 1940) {
    //     $('#resolution-wholepage-popup').modal({
    //         backdrop: false
    //     });
    //     $('#resolution-wholepage-popup #current_res').text($(window).width() + 'x' + $(window).height());

    //     setTimeout(() => {
    //         $('#resolution-wholepage-popup').modal('hide');
    //     }, 10000);
    // }

    // location dropdown in contact us page feedback form
    $.ajax({
        url: "/contactus/feedback/location",
        type: "POST",
        async: false,
        data: {},
        success: function (result) {
            $('.location-drop-down').empty();
            $('.location-drop-down').append(result);
        }
    });

    // feedbackcategory dropdown in contact us page feedback form
    $.ajax({
        url: "/contactus/feedback/category",
        type: "POST",
        async: false,
        data: {},
        success: function (result) {
            $('.feedback-category-drop-down').append(result)
        }
    });


    // homepage featured in image
    $.ajax({
        url: "/home/featuredin/image",
        type: "POST",
        async: false,
        data: {},
        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            $(".featuredin-slider-caresole > div.owl-stage-outer > div").empty();
            $.each(resultJSON, function (key, value) {
                $('.featuredin-slider-caresole').append(`<div class="leadercont">
                                <img src="`+ value['image'] + `" />
                            </div>`);
            });



        }
    });

    // employee our experts
    // employee our experts
    $.ajax({
        url: "/home/client/about",
        type: "POST",
        async: false,
        data: {},
        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            $("#therapist-review-slider-home").empty();
            $.each(resultJSON, function (key, value) {
                $('#therapist-review-slider-home').append(`<div class="leadercont" >
                                <div class="textomin-user">
                                <img src="` + value['image'] + `" class="userimage" alt="" />
                                <h4>` + value['employee_id'] + `</h4>
                                </div>
                                <p> ` + value['name'] + `</p>
                            </div>`);
            });

        }
    });


    // Feature Blog Home Pgae
    $.ajax({
        url: "/homepage/feature/blog",
        type: "POST",
        async: false,
        data: {},
        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            var label1 = '';
            var label2 = '';
            var label3 = '';
            var label4 = '';
            var label5 = ''

            if (resultJSON[0]['blog_tag_ids'] !== undefined) {
                $.each(resultJSON[0]['blog_tag_ids'], function (key, value) {
                    label1 += `<label>` + value + `</label>`
                });
            }

            if (resultJSON[1]['blog_tag_ids'] !== undefined) {
                $.each(resultJSON[1]['blog_tag_ids'], function (key, value) {
                    label2 += `<label>` + value + `</label>`
                });
            }

            if (resultJSON[2]['blog_tag_ids'] !== undefined) {
                $.each(resultJSON[2]['blog_tag_ids'], function (key, value) {
                    label3 += `<label>` + value + `</label>`
                });
            }

            if (resultJSON[3]['blog_tag_ids'] !== undefined) {
                $.each(resultJSON[3]['blog_tag_ids'], function (key, value) {
                    label4 += `<label>` + value + `</label>`
                });
            }

            if (resultJSON[4]['blog_tag_ids'] !== undefined) {
                $.each(resultJSON[4]['blog_tag_ids'], function (key, value) {
                    label5 += `<label>` + value + `</label>`
                });
            }

            // $(".blog_homepage_feature").empty();
            $('.blog_homepage_feature').html(`<h2 data-aos="fade-up" data-aos-delay="100" class="aos-init aos-animate">Featured Posts</h2>
            <div class="row">
                <div class="col-xl-4 col-lg-6 col-md-6 col-sm-6 col-xs-12 featurecard-items">
                    <div class="oberlay-tags">` +
                label1 +
                `</div>
                    <img src="` + resultJSON[0]['image'] + `">
                    <a class="h5-blog" data-toggle="tooltip" data-placement="top" title="` + resultJSON[0]['name'] + `" href="` + resultJSON[1]['url'] + `">
                    ` + resultJSON[0]['name'] + `
                    </a>
                    <p class="subtitle-blog" data-toggle="tooltip" data-placement="top" title="` + resultJSON[0]['subtitle'] + `"> ` + resultJSON[0]['subtitle'] + `
                    </p>
                    <div class="post-infos"> <label class="views"> ` + resultJSON[0]['visits'] + `</label>
                        <label class="dates"> ` + resultJSON[0]['date'] + `</label>
                        <label class="user"> ` + resultJSON[0]['author_id'] + `</label> </div>
                </div>
                <div class="col-xl-4 col-lg-6 col-md-6 col-sm-6 col-xs-12 featurecard-items">
                    <div class="oberlay-tags">` + label2 + `</div>
                    <img src="` + resultJSON[1]['image'] + `">
                    <a class="h5-blog" data-toggle="tooltip" data-placement="top" title="` + resultJSON[1]['name'] + `" href="` + resultJSON[1]['url'] + `">
                    ` + resultJSON[1]['name'] + `
                    </a>
                    <p class="subtitle-blog" data-toggle="tooltip" data-placement="top" title="` + resultJSON[1]['subtitle'] + `"> ` + resultJSON[1]['subtitle'] + `
                    </p>
                    <div class="post-infos"> <label class="views"> ` + resultJSON[1]['visits'] + `</label>
                        <label class="dates"> ` + resultJSON[1]['date'] + `</label>
                        <label class="user"> ` + resultJSON[1]['author_id'] + `</label> </div>
                </div>
                <div class="col-xl-4 col-lg-12 col-md-12 col-sm-12 col-xs-12 popularpost-cont aos-init aos-animate" data-aos="fade-left" data-aos-delay="200">
                    <h5>Popular Posts</h5>
                    <div class="owl-carousel popularpost-caresole-mobile off">

                        <div class="popularpost-list">
                            <img src="` + resultJSON[2]['image'] + `">
                            <div class="popular-typos">
                            <a class="h6-blog" data-toggle="tooltip" data-placement="top" title="` + resultJSON[2]['name'] + `" href="` + resultJSON[2]['url'] + `"> ` + resultJSON[2]['name'] + `</a>
                                <p class="subtitle-blog" data-toggle="tooltip" data-placement="top" title="` + resultJSON[2]['subtitle'] + `">` + resultJSON[2]['subtitle'] + `
                                </p>
                                <div class="oberlay-tags">` + label3 + `</div>
                            </div>
                        </div>
                        <div class="popularpost-list">
                            <img src="` + resultJSON[3]['image'] + `">
                            <div class="popular-typos">
                            <a class="h6-blog" data-toggle="tooltip" data-placement="top" title="` + resultJSON[3]['name'] + `" href="` + resultJSON[3]['url'] + `">` + resultJSON[3]['name'] + `</a>
                                <p class="subtitle-blog" data-toggle="tooltip" data-placement="top" title="` + resultJSON[3]['subtitle'] + `">` + resultJSON[3]['subtitle'] + `
                                </p>
                                <div class="oberlay-tags">` + label4 + `</div>
                            </div>
                        </div>
                        <div class="popularpost-list">
                            <img src="` + resultJSON[4]['image'] + `">
                            <div class="popular-typos">
                            <a class="h6-blog" data-toggle="tooltip" data-placement="top" title="` + resultJSON[4]['name'] + `" href="` + resultJSON[4]['url'] + `">` + resultJSON[4]['name'] + `</a>
                                <p class="subtitle-blog" data-toggle="tooltip" data-placement="top" title="` + resultJSON[4]['subtitle'] + `">` + resultJSON[4]['subtitle'] + `
                                </p>
                                <div class="oberlay-tags">` + label5 + `</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div><div class="text-center">
            <a type="button" class="seeallpost-btns" href="/blog">See All Post</a>
        </div>`)
            // $.each(resultJSON['first_div_blog'], function (key, value) {
            //     $('.blog_featured_homepage_post').append(`
            //         <div class="col-xl-4 col-lg-6 col-md-6 col-sm-6 col-xs-12 featurecard-items">
            //             <div class="oberlay-tags">
            //                 <label>
            //                     `+value['blog_tag_ids']+`
            //                 </label>
            //             </div>
            //             <a t-attf-href="/blog/{{slug(first_blog_id.blog_id)}}/{{first_blog_id.id}}">
            //                 <img src="`+ value['image'] + `" class="userimage" alt=""  />
            //                 <h5>
            //                     `+value['name']+`
            //                 </h5>
            //                 <p>
            //                      `+value['subtitle']+`
            //                 </p>
            //                 <div class="post-infos">
            //                     <label class="views">
            //                         `+value['visits']+`
            //                     </label>
            //                     <label class="dates">
            //                         `+value['date']+`
            //                     </label>
            //                     <label class="user">
            //                          `+value['author_id']+`
            //                     </label>
            //                 </div>
            //             </a>
            //         </div>

            //     `);
            // });

            // $.each(resultJSON['second_div_blog'], function (key, value) {
            //     $('.second_blog_featured_homepage_post').append(`
            //         <div class="popularpost-list">
            //                 <img src="`+ value['image'] + `" class="userimage" alt=""  />
            //                 <div class="popular-typos">
            //                     <h6> `+value['name']+`</h6>
            //                     <p>`+value['subtitle']+`
            //                     </p>
            //                     <div class="oberlay-tags">
            //                         <label> `+value['blog_tag_ids']+` </label>

            //                     </div>
            //                 </div>
            //             </div>

            //     `);
            // });
        }




    });

    var ourExpertOwll = $(".exper-slider-caresole").owlCarousel({
        autoplay: false,
        dots: true,
        loop: false,
        margin: 26,
        stagePadding: 60,
        autoWidth: false,
        touchDrag: true,
        items: 2,
        responsive: {
            0: {
                items: 1,
                stagePadding: 20,
            },
            768: {
                items: 1,
                stagePadding: 20,
            },
            900: {
                items: 2,
                stagePadding: 40,
            },
        }
    });


    ourExpertOwll.owlCarousel();
    // Go to the next item
    $('.ourExpertNextBtn').click(function () {
        ourExpertOwll.trigger('next.owl.carousel');
    });
    // Go to the previous item
    $('.ourExpertPrevBtn').click(function () {
        ourExpertOwll.trigger('prev.owl.carousel', [300]);
    });

    var SpeakerExpertOwl = $("#speaker-expert-owl-carousel").owlCarousel({
        autoplay: false,
        dots: true,
        loop: true,
        margin: 26,
        stagePadding: 60,
        autoWidth: false,
        touchDrag: true,
        items: 2,
        responsive: {
            0: {
                items: 1,
                stagePadding: 20,
            },
            768: {
                items: 1,
                stagePadding: 20,
            },
            900: {
                items: 2,
                stagePadding: 40,
            },
        }
    });

    SpeakerExpertOwl.owlCarousel();

    $('#SpeakerourExpertNextBtn').click(() => {
        SpeakerExpertOwl.trigger('next.owl.carousel');
    });

    $('#SpeakerourExpertPrevBtn').click(() => {
        SpeakerExpertOwl.trigger('prev.owl.carousel', [300]);
    });


    // $('#SpeakerourExpertNextBtn').click(() => {
    //     ourExpertOwll.trigger('next.owl.carousel');
    // });
    // // Go to the previous item

    // $('#SpeakerourExpertPrevBtn').click(() => {
    //     ourExpertOwll.trigger('prev.owl.carousel', [300]);
    // });

    // featured in slider 

    var MostlikeThisSliderTherapist = $(".MostlikeThisSliderTherapist").owlCarousel({
        autoplay: false,
        dots: true,
        loop: false,
        margin: 26,
        stagePadding: 60,
        autoWidth: false,
        touchDrag: true,
        items: 2,
        responsive: {
            0: {
                items: 1,
                stagePadding: 40,
            },
            768: {
                items: 2,
                stagePadding: 40,
            },
            1024: {
                items: 3,
                stagePadding: 30,
            },

        }
    });

    MostlikeThisSliderTherapist.owlCarousel();
    $(document).on("click", "#MostlikeThisSliderTherapistNextBtn", () => {
        MostlikeThisSliderTherapist.trigger('next.owl.carousel');
    });

    $(document).on("click", "#MostlikeThisSliderTherapistPrevBtn", () => {
        MostlikeThisSliderTherapist.trigger('prev.owl.carousel', [300]);
    });


    var MostlikeThisSlider = $(".mostlike-this_slider").owlCarousel({
        autoplay: false,
        dots: true,
        loop: false,
        margin: 26,
        stagePadding: 60,
        autoWidth: false,
        touchDrag: true,
        items: 2,
        responsive: {
            0: {
                items: 1,
                stagePadding: 40,
            },
            768: {
                items: 2,
                stagePadding: 40,
            },
            1024: {
                items: 3,
                stagePadding: 30,
            },

        }
    });

    MostlikeThisSlider.owlCarousel();
    $(document).on("click", ".MostlikeThisSliderNextBtn , #MostlikeThisSliderNextBtn", () => {
        MostlikeThisSlider.trigger('next.owl.carousel');
    });

    $(document).on("click", ".MostlikeThisSliderPrevBtn, #MostlikeThisSliderPrevBtn", () => {
        MostlikeThisSlider.trigger('prev.owl.carousel', [300]);
    });

    if (window.innerWidth > 767) {
        var searchresultArticle = $("#searchresult-article").owlCarousel({
            autoplay: false,
            dots: true,
            loop: false,
            margin: 26,
            stagePadding: 60,
            autoWidth: false,
            touchDrag: true,
            items: 2,
            responsive: {
                0: {
                    items: 1,
                    stagePadding: 40,
                },
                768: {
                    items: 2,
                    stagePadding: 40,
                },
                1024: {
                    items: 3,
                    stagePadding: 30,
                },

            }
        });

        searchresultArticle.owlCarousel();
        $(document).on("click", ".searchresultArticleNextBtn", () => {
            searchresultArticle.trigger('next.owl.carousel');
        });

        $(document).on("click", ".searchresultArticlePrevBtn", () => {
            searchresultArticle.trigger('prev.owl.carousel', [300]);
        });

    }


    const SearchTherapistSlider = $(".search-therapist-this_slider").owlCarousel({
        autoplay: false,
        dots: true,
        loop: false,
        margin: 26,
        stagePadding: 60,
        autoWidth: false,
        touchDrag: true,
        items: 2,
        responsive: {
            0: {
                items: 1,
                stagePadding: 40,
            },
            768: {
                items: 2,
                stagePadding: 40,
            },
            1024: {
                items: 3,
                stagePadding: 30,
            },

        }
    });

    $('.SearchTherapistSliderNextBtn').click(function () {
        SearchTherapistSlider.trigger('next.owl.carousel');
    })
    // Go to the previous item
    $('.SearchTherapistSliderPrevBtn').click(function () {
        SearchTherapistSlider.trigger('prev.owl.carousel', [300]);
    });

    var featuredInOwli = $(".featuredin-slider-caresole").owlCarousel({
        autoplay: false,
        dots: true,
        loop: true,
        margin: 26,
        stagePadding: 60,
        autoWidth: false,
        touchDrag: true,
        responsive: {
            0: {
                items: 2,
                stagePadding: 50,
            },
            768: {
                items: 4,
                stagePadding: 0,
            },
            900: {
                items: 5,
                stagePadding: 0,

            },
            1400: {
                items: 5,
                stagePadding: 0,
            }
        }
    });


    featuredInOwli.owlCarousel();
    // Go to the next item
    $('.featuredin_NextBtn, .featuredin_NextBtant').click(function () {
        featuredInOwli.trigger('next.owl.carousel');
    })
    // Go to the previous item
    $('.featuredin_PrevBtn, .featuredin_PrevBtan').click(function () {
        featuredInOwli.trigger('prev.owl.carousel', [300]);
    });

    // featured in slider 

    var clientsaboutilluTestimonial = $(".clientsaboutillu-slider-caresole").owlCarousel({
        autoplay: false,
        dots: true,
        loop: false,
        autoWidth: true,
        touchDrag: true,
        responsive: {
            0: {
                items: 1,
                margin: 10,
                autoWidth: false,
                margin: 80,
            },
            768: {
                items: 1,
                margin: 10,
                autoWidth: false,
                margin: 150,
            },
            900: {
                items: 2,
                margin: 100,
            },
            1400: {
                items: 2,
                margin: 160,
            }
        }
    });


    clientsaboutilluTestimonial.owlCarousel();

    $(".clisneillum-left").click(function () {
        clientsaboutilluTestimonial.trigger('next.owl.carousel');
    });


    $(".clisneillum-right").click(function () {
        clientsaboutilluTestimonial.trigger('prev.owl.carousel', [300]);
    });


    var corporateclientsslidercaresole = $(".corporateclients-slider-caresole").owlCarousel({
        autoplay: false,
        dots: true,
        loop: true,
        autoWidth: true,
        touchDrag: true,
        responsive: {
            0: {
                items: 1,
                margin: 10,
                autoWidth: false,
                margin: 80,
            },
            768: {
                items: 1,
                margin: 10,
                autoWidth: false,
                margin: 150,
            },
            900: {
                items: 2,
                margin: 100,
            },
            1400: {
                items: 2,
                margin: 160,
            }
        }
    });


    corporateclientsslidercaresole.owlCarousel();

    $(".corporateclients_PrevBtn").click(function () {
        corporateclientsslidercaresole.trigger('next.owl.carousel');
    });


    $(".corporateclients_NextBtn").click(function () {
        corporateclientsslidercaresole.trigger('prev.owl.carousel', [300]);
    });



    // Popularpost caresole for mobile view start

    // Our Expert team slider
    var startCarousel_retreats_page_aboutsection = () => {
        var retreats_page_aboutsection = $("#retreats_page_aboutsection").owlCarousel({
            autoplay: false,
            dots: true,
            loop: false,
            margin: 26,
            stagePadding: 60,
            autoWidth: false,
            touchDrag: true,
            items: 2,
            responsive: {
                0: {
                    items: 1,
                    stagePadding: 20,
                },
                768: {
                    items: 1,
                    stagePadding: 20,
                },
                900: {
                    items: 2,
                    stagePadding: 40,
                },
            }
        });
    }

    if (window.innerWidth < 1200) {
        startCarousel();
        startCarousel_retreats_page_aboutsection();
    } else {
        $('.popularpost-caresole-mobile').addClass('off');
        $('#retreats_page_aboutsection').css('display', 'flex');
        $('#retreats_page_aboutsection').addClass('off');
    }


    $(window).resize(function () {
        if (window.innerWidth < 1200) {
            startCarousel();
            startCarousel_retreats_page_aboutsection();
        } else {
            stopCarousel();
            $('#retreats_page_aboutsection').css('display', 'flex');
            $('#retreats_page_aboutsection').addClass('off');
        }
    });

    function startCarousel() {
        var popularpostlists = $(".popularpost-caresole-mobile").owlCarousel({

            responsive: {
                0: {
                    items: 1,
                    autoplay: false,
                    dots: true,
                    loop: true,
                    responsiveClass: true,
                    margin: 20,
                    stagePadding: 20,
                    autoWidth: true,
                    touchDrag: true,
                    itemsDesktop: false,
                    itemsDesktopSmall: false,
                    itemsTablet: false,
                    itemsMobile: true,
                },
                768: {
                    items: 3,
                    autoplay: false,
                    dots: false,
                    loop: false,
                    responsiveClass: false,
                    autoWidth: false,
                    touchDrag: false,
                },

            }
        });
    }

    function stopCarousel() {
        var owl = $('.popularpost-caresole-mobile');
        owl.trigger('destroy.owl.carousel');
        owl.addClass('off');
    }
    // Popularpost caresole for mobile view end

    // Owl Caresole Script End

    // ****************************************


    // var retreats_page_accomadatiens_slider = $("#retreats_page_accomadatiens_slider").owlCarousel({
    //     autoplay: false,
    //     dots: true,
    //     loop: false,
    //     margin: 10,
    //     autoWidth: false,
    //     touchDrag: true,
    //     responsive: true,
    //     responsiveClass: true,
    //     responsive: {
    //         0: {
    //             items: 1,
    //             margin: 10,
    //             stagePadding: 30,
    //         },
    //         768: {
    //             items: 2,
    //             margin: 10,
    //         },
    //         900: {
    //             items: 3
    //         },
    //         1400: {
    //             items: 4
    //         }
    //     }
    // });

    // retreats_page_accomadatiens_slider.owlCarousel();


    var aboutTherapistImage_Sliderll = $("#aboutTherapist-image").owlCarousel({
        autoplay: false,
        dots: true,
        loop: false,
        margin: 10,
        autoWidth: false,
        touchDrag: true,
        responsive: true,
        responsiveClass: true,
        responsive: {
            0: {
                items: 1,
                margin: 10,
                stagePadding: 30,
            },
            768: {
                items: 2,
                margin: 10,
            },
            900: {
                items: 3
            },
            1400: {
                items: 4
            }
        }
    });


    aboutTherapistImage_Sliderll.owlCarousel();
    // Go to the next item
    $('.aboutTherapist-team-right').click(function () {
        aboutTherapistImage_Sliderll.trigger('next.owl.carousel');
    })
    // Go to the previous item
    $('.aboutTherapist-team-left').click(function () {
        aboutTherapistImage_Sliderll.trigger('prev.owl.carousel', [300]);
    })


    $('.clientsaboutillu_NextBtn').click(function () {
        aboutTherapistImage_Sliderll.trigger('next.owl.carousel');
    })
    // Go to the previous item
    $('.clientsaboutillu_PrevBtn').click(function () {
        aboutTherapistImage_Sliderll.trigger('prev.owl.carousel', [300]);
    })


    var aboutTherapistImage_Slider = $("#faqtabslider").owlCarousel({
        autoplay: false,
        dots: false,
        loop: true,
        margin: 00,
        autoWidth: true,
        touchDrag: true,
        responsive: true,
        responsiveClass: true,
        responsive: {
            0: {
                items: 1,
                margin: 10,

            },
            768: {
                items: 2,
                margin: 10,
            },
            900: {
                items: 3
            },
            1400: {
                items: 4
            }
        }
    });

    // featured in slider 

    var clientsaboutillu = $("#therapist-casestudy-slider").owlCarousel({
        autoplay: false,
        dots: true,
        loop: false,
        margin: 250,
        // stagePadding: 100,
        autoWidth: true,
        touchDrag: true,
        responsive: {
            0: {
                items: 1,
                margin: 10,
            },
            768: {
                items: 2,
                margin: 50,
            },
            900: {
                items: 2
            },
            1400: {
                items: 2
            }
        }
    });


    var clientsaboutillu = $("#therapy-youhaveaproblem-slider").owlCarousel({
        autoplay: false,
        dots: true,
        loop: false,
        // margin: 25,
        // stagePadding: 100,
        autoWidth: false,
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



    var curriculumlevels_slider = $("#curriculumlevels").owlCarousel({
        stagePadding: 60,
        loop: true,
        margin: 40,

        responsive: {
            0: {
                items: 2,

            },
            768: {
                items: 2,

            },
            900: {
                items: 3,


            },
            1000: {
                items: 5,


            }
        }
    });


    // our Experts background slide up js start
    $(window).scroll(function () {
        $('.animation-test').each(function () {
            var imagePos = $(this).offset().top;
            var imageHeight = $(this).height();
            var topOfWindow = $(document).scrollTop();

            if (imagePos < topOfWindow + imageHeight && imagePos + imageHeight > topOfWindow) {
                $('.ourexpert_more-container').addClass("slidetop-active");

                setTimeout(function () {
                    $('.ourexpert-wrapper').addClass("typochangecolors");

                }, 2000);
            } else {
                // $('.ourexpertsec').removeClass("slidetop");
            }
        });
    });
    // our Experts background slide up js end





    //  top position compare
    jQuery.fn.visible = function (partial) {
        var $t = $(this),
            $w = $(window),
            viewTop = $w.scrollTop(),
            viewBottom = viewTop + $w.height(),
            _top = $t.offset().top,
            _bottom = _top + $t.height(),
            compareTop = partial === true ? _bottom : _top,
            compareBottom = partial === true ? _top : _bottom;

        return compareBottom <= viewBottom && compareTop >= viewTop;
    };

    // arrow animation activeting
    $(window).scroll(function (event) {
        arrowanimationfunc();

    });


    function arrowanimationfunc() {
        $(".arrow-scroll").each(function (i, el) {
            var el = $(el);
            if (el.visible(true)) {
                el.addClass("active-arrowanim");
            } else {
                el.removeClass("active-arrowanim");
            }
        });
    };

    arrowanimationfunc();

    // SVG wave shapes wave activating
    $(document).scroll(function () {
        // top svg shape animation
        if (window.innerWidth > 767) {
            waveanimationsonhomepage();
        }

        $(window).resize(function () {
            // footerwave();
            // console.log($(window).width(), 'asd');
            // console.log(window.innerWidth, 'a11111111sd');
            if (window.innerWidth > 767) {
                // alert("aone");
                waveanimationsonhomepage();
            }
        });

        function waveanimationsonhomepage() {
            $('.top-wave-svg').each(function (i, el) {
                var el = $(el);
                if (el.visible(true)) {
                    el.addClass("top-wave-svg-activated");
                    setTimeout(function () {
                        el.addClass("top-wave-svg-activated-end");
                    }, 2000);

                } else {
                    // el.removeClass("active-arrowanim");
                    el.removeClass("top-wave-svg-activated");
                    el.removeClass("top-wave-svg-activated-end");
                }
            });

            // bottom svg active
            $('.bottom-wave-svg').each(function (i, el) {
                var el = $(el);
                if (el.visible(true)) {

                    el.addClass("bottom-wave-svg-activated");

                    setTimeout(function () {
                        el.addClass("bottom-wave-svg-activated-end");
                    }, 1000);

                } else {
                    // el.removeClass("active-arrowanim");
                    el.removeClass("bottom-wave-svg-activated");
                    el.removeClass("bottom-wave-svg-activated-end");
                }
            });
        }
    });






    const handleScroll = () => {
        if (!ref.current) return
        if (ref.current.getBoundingClientRect().y <= -580 || null) {
            console.log(ref.current.getBoundingClientRect().y);

            setSticky(true);
        } else {
            setSticky(false);
        }
    };

    if (document.getElementById("footersec")) {
        // Get the position on the page of the SVG - footer animatio active when visible
        var svgLocation = document.getElementById("footersec").getBoundingClientRect();

        // Scroll offset that triggers animation start.
        // In this case it is the bottom of the SVG.
        var offsetToTriggerAnimation = svgLocation.y + svgLocation.height;
    }





    // Function to handle the scroll event.
    // Add an event handler to the document for the "onscroll" event
    function scrollAnimTriggerCheck(evt) {
        var viewBottom = window.scrollY + window.innerHeight;
        if (viewBottom > offsetToTriggerAnimation) {
            // Start the SMIL animation
            document.getElementById("footwave").beginElement();
            // Remove the event handler so it doesn't trigger again
            document.removeEventListener("scroll", scrollAnimTriggerCheck);
        }
    }

    // Add an event handler to the document for the "onscroll" event
    document.addEventListener("scroll", scrollAnimTriggerCheck);


    // stickey top header script
    $(window).scroll(function () {
        // console.log($(window).scrollTop())
        if ($(window).scrollTop() > 20) {
            $('.top-menu-header-wrapper').addClass('navbar-fixed');
            navbar_height = document.querySelector('.navbar').offsetHeight;
            document.body.style.paddingTop = navbar_height + 'px';
        } else {
            $('.top-menu-header-wrapper').removeClass('navbar-fixed');
            document.body.style.paddingTop = '0';
        }
        if ($(window).scrollTop() < 64) {
            $('.top-menu-header-wrapper').removeClass('navbar-fixed');
        }
    });


    // $("body").easeScroll({
    //     frameRate: 60,
    //     animationTime: 5000,
    //     stepSize: 50,
    //     pulseAlgorithm: 10,
    //     pulseScale: 18,
    //     pulseNormalize: 1,
    //     accelerationDelta: 80,
    //     accelerationMax: 1,
    //     keyboardSupport: true,
    //     arrowScroll: 50,
    // });

    // Menu bar multi level dropdown menu script with megamenu
    $('.dropdown-menu a.dropdown-toggle').on('click', function (e) {
        if (!$(this).next().hasClass('show')) {
            $(this).parents('.dropdown-menu').first().find('.show').removeClass('show');
        }
        var $subMenu = $(this).next('.dropdown-menu');
        $subMenu.toggleClass('show');

        $(this).parents('li.nav-item.dropdown.show').on('hidden.bs.dropdown', function (e) {
            $('.dropdown-submenu .show').removeClass('show');
        });


        return false;
    });


    if (window.innerWidth < 600) {
        var holistichealingtherapyteamlider = $("#holistichealingtherapyteamlider").owlCarousel({
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
        holistichealingtherapyteamlider.owlCarousel();
    } else {
        $('#holistichealingtherapyteamlider').addClass('off');
    }

});