function contact_map_load(company_id) {
    console.log(company_id)

    $.ajax({
        url: "/get/company/address",
        type: "POST",
        async: false,
        data: {
            'company_id': company_id,
        },
        success: function (result) {
            $('#gmap_canvas').replaceWith(`
                <iframe id='gmap_canvas' width='600' height='400' frameborder='0' 
                scrolling='no' marginheight='0' marginwidth='0' src='https://maps.google.com/maps?&amp;q=` +
                encodeURIComponent(result) + `&amp;t=&amp;z=9&amp;ie=UTF8&amp;iwloc=&amp;output=embed'></iframe>`);

        }
    });


}


function onsubmit_contact_us_custom(el) {
    document.getElementsByClassName("chatbox-frm").fname.value = el.full_name.value;
    document.getElementsByClassName("chatbox-frm").email.value = el.email.value;
    document.getElementsByClassName("chatbox-frm").phone.value = el.phone.value;
    opn_live_chat();
    return false;
}

function initialize() {
    if (GBrowserIsCompatible()) {
        var map = new GMap2(
            document.getElementById('map'));
        map.setCenter(new GLatLng(37.4419, -122.1419), 13);
        map.setUIToDefault();

        map.addOverlay(new GMarker(new GLatLng(37.4419, -122.1419)));

    }
}

$(document).ready(() => {

    // // Card options
    // var myOptions = {
    //     center: new google.maps.LatLng(40.837067, 14.142821),
    //     zoom: 17,
    //     mapTypeId: google.maps.MapTypeId.ROADMAP,
    //     mapTypeControl: false
    // };

    // // Render card
    // var map = new google.maps.Map(document.getElementById("map"), myOptions);

    // // Append card when map renders
    // google.maps.event.addListener(map, 'idle', function (e) {

    //     // Prevents card from being added more than once (i.e. when page is resized and google maps re-renders)
    //     if ($(".place-card").length === 0) {
    //         $(".gm-style").append('<div style="position: absolute; right: 0px; top: 0px;"> <div style="margin: 10px; padding: 1px; -webkit-box-shadow: rgba(0, 0, 0, 0.298039) 0px 1px 4px -1px; box-shadow: rgba(0, 0, 0, 0.298039) 0px 1px 4px -1px; border-radius: 2px; background-color: white;"> <div> <div class="place-card place-card-large"> <div class="place-desc-large"> <div class="place-name"> Tenuta Cigliano </div><div class="address"> Contrada Pisciarelli, 80078 Napoli, Italy </div></div><div class="navigate"> <div class="navigate"> <a class="navigate-link" href="https://maps.google.com/maps?ll=40.837067,14.136834&amp;z=16&amp;t=m&amp;hl=en-US&amp;gl=PT&amp;mapclient=embed&amp;daddr=Tenuta%20Cigliano%20Contrada%20Pisciarelli%2080078%20Napoli%20Italy@40.837067,14.142821" target="_blank"> <div class="icon navigate-icon"></div><div class="navigate-text"> Directions </div></a> </div></div><div class="review-box"> <div class="" style="display:none"></div><div class="" style="display:none"></div><div class="" style="display:none"></div><div class="" style="display:none"></div><div class="" style="display:none"></div><div class="" style="display:none"></div><a href="https://plus.google.com/101643431012640484007/about?hl=en&amp;authuser=0&amp;gl=pt&amp;socpid=247&amp;socfid=maps_embed:placecard" target="_blank">1 review</a> </div><div class="saved-from-source-link" style="display:none"> </div><div class="maps-links-box-exp"> <div class="time-to-location-info-exp" style="display:none"> <span class="drive-icon-exp experiment-icon"></span><a class="time-to-location-text-exp" style="display:none" target="_blank"></a><a class="time-to-location-text-exp" style="display:none" target="_blank"></a> </div><div class="google-maps-link"> <a href="https://maps.google.com/maps?ll=40.837067,14.136834&amp;z=16&amp;t=m&amp;hl=en-US&amp;gl=PT&amp;mapclient=embed&amp;cid=2152474408176797502" target="_blank">View larger map</a> </div></div><div class="time-to-location-privacy-exp" style="display:none"> <div class="only-visible-to-you-exp"> Visible only to you. </div><a class="learn-more-exp" target="_blank">Learn more</a> </div></div></div></div></div>');
    //     }
    // });

    // var iterations = 0;
    // let initialize = () => {

    //     if (typeof GBrowserIsCompatible === 'undefined') {
    //         setTimeout(initialize, 1000);
    //         iterations++;//you want to do this finite number of times say 10.
    //     }
    //     else {
    //         if (GBrowserIsCompatible()) {
    //             //do your thing
    //         } else {
    //             var map = new GMap2(
    //                 document.getElementById('contact_gmap_canvas'));
    //             map.setCenter(new GLatLng(37.4419, -122.1419), 13);
    //             map.setUIToDefault();

    //             map.addOverlay(new GMarker(new GLatLng(37.4419, -122.1419)));
    //         }
    //     }

    // }

    // initialize()

    let contact_gmap_canvas;

    let initMap = () => {
        contact_gmap_canvas = new google.maps.Map(document.getElementById("contact_gmap_canvas"), {
            center: { lat: -34.397, lng: 150.644 },
            zoom: 8,
        });
    }

    initMap()

});