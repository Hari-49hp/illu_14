const FeaturedPostTeamSingle = $("#featured-post-team-single").owlCarousel({
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

FeaturedPostTeamSingle.owlCarousel();
$(document).on("click", "#FeaturedPostTeamSingleNextBtn", () => {
    FeaturedPostTeamSingle.trigger('next.owl.carousel');
});

$(document).on("click", "#FeaturedPostTeamSinglePrevBtn", () => {
    FeaturedPostTeamSingle.trigger('prev.owl.carousel', [300]);
});