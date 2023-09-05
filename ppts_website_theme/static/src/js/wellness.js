$('#number-day-filter , #location-filter').change(function () {

    $.ajax({
        url: "/wellness/page/filter",
        type: 'POST',
        async: false,
        data: {
            'number-day-filter': $('#number-day-filter').val(),
            'location-filter': $('#location-filter').val(),
        },
        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            $('.calendar_twocardview').empty();

            $.each(resultJSON, function (key, value) {
                $(".calendar_twocardview").append(`<div class="calenday-eventlist-item">
                    <div class="cal-event-img">
                        <img src="`+ value['image'] + `" loading="lazy">
                    </div>
                    <div class="eventfullinfos">
                        <div class="event-typoingo">
                            <div class="eventtitleinfos">
                                <h5>
                                    `+ value['name'] + `
                                </h5>
                                <p class="upsmtxt">
                                `+ value['event_sub_categ_id'] + `
                                </p>
                            </div>
                            <div class="eventinfos">
                                <label>
                                    <i class="far fa-user"></i>
                                    `+ value['facilitator'] + `
                                </label>
                                <label>
                                    <i class="far fa-calendar-minus"></i>
                                    `+ value['date'] + `
                                </label>
                                <label>
                                    <img src="/ppts_website_theme/static/src/img/onsiteicon.svg" width="20px" loading="lazy">
                                    `+ value['platform'] + `
                                </label>
                                <label>
                                    <i class="fas fa-map-marker-alt"></i>
                                    `+ value['location_id'] + `
                                </label>
                            </div>

                        </div>
                        <div class="event-listbtn">
                            <button class="borderedbtn">Enquire Now</button>
                            <button class="fullbutton">
                            book for 
                            `+ value['price'] + `
                            AED
                            </button>
                        </div>
                    </div>
                </div>`
                );
            });



        },
    });



});
