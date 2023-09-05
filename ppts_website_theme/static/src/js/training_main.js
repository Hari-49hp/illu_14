

$('#training-main-event-name').multiselect({
    templates: {
        button: '<button type="button" class="multiselect dropdown-toggle custom-select btn btn-default" data-toggle="dropdown"><span class="multiselect">Course Name</span></button>',
    },
    buttonTitle: function (options, select) {
        var labels = [];
        options.each(function () {
            labels.push($(this).text());
        });
        return labels.join(' - ');
    }
});


$('#training-main-event-level').multiselect({
    templates: {
        button: '<button type="button" class="multiselect dropdown-toggle custom-select btn btn-default" data-toggle="dropdown"><span class="multiselect">Levels</span></button>',
    },
    buttonTitle: function (options, select) {
        var labels = [];
        options.each(function () {
            labels.push($(this).text());
        });
        return labels.join(' - ');
    }
});

$('#training-main-event-platform').multiselect({
    templates: {
        button: '<button type="button" class="multiselect dropdown-toggle custom-select btn btn-default" data-toggle="dropdown"><span class="multiselect">Platform</span></button>',
    },
    buttonTitle: function (options, select) {
        var labels = [];
        options.each(function () {
            labels.push($(this).text());
        });
        return labels.join(' - ');
    },
    click: function (e) {
        e.stopPropagation();
    }
});


$('#training-main-event-country').multiselect({
    enableCaseInsensitiveFiltering: true,
    includeSelectAllOption: true,
    templates: {
        button: '<button type="button" class="multiselect dropdown-toggle custom-select btn btn-default" data-toggle="dropdown"><span class="multiselect"><img style="margin-left: -3px;margin-right: 4px;" src="/ppts_website_theme/static/src/img/location-icon.svg" width="24px" height="24px"/> Country </span></button>',

    },
    buttonTitle: function (options, select) {
        var labels = [];
        options.each(function () {
            labels.push($(this).text());
        });
        return labels.join(' - ');
    },
    click: function (e) {
        e.stopPropagation();
    }
});




$('#training-main-event-city').multiselect({
    enableCaseInsensitiveFiltering: true,
    includeSelectAllOption: true,
    templates: {
        button: '<button type="button" class="multiselect dropdown-toggle custom-select btn btn-default" data-toggle="dropdown"><span class="multiselect"><img style="margin-left: -3px;margin-right: 4px;" src="/ppts_website_theme/static/src/img/location-icon.svg" width="24px" height="24px"/> City </span></button>',
    },
    buttonTitle: function (options, select) {
        var labels = [];
        options.each(function () {
            labels.push($(this).text());
        });
        return labels.join(' - ');
    },
    click: function (e) {
        e.stopPropagation();
    }
});


$('#TraningMainDatePicker').datepicker({
    autoclose: true,
    todayHighlight: true
});

$(document).on("click", "#training-filter-btn-main", () => {
    console.log('Date --> ', $('.training_main_date_filter').val())
    $.ajax({
        url: "/training/main/filter",
        type: "POST",
        async: false,
        data: {
            multi_date: String($('.training_main_date_filter').val()),
            course_name: JSON.stringify($('#training-main-event-name').val()),
            levels: JSON.stringify($('#training-main-event-level').val()),
            platform: $('#training-main-event-platform').val(),
            country: JSON.stringify($('#training-main-event-country').val()),
            city: JSON.stringify($('#training-main-event-city').val()),
        },

        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            $(".calendar-eventlist-view-wrapper.main").empty();
            $(".table-body-main").empty();

            $.each(resultJSON, function (key, value) {

                $(".calendar-eventlist-view-wrapper.main").append(`
                    <div class="calenday-eventlist-item" data-aos="fade-up" data-aos-delay="100">
                        <div class="cal-event-img">
                                <img src="`+ value['image'] + `" />
                        </div>
                        <div class="eventfullinfos">
                            <div class="event-typoingo">
                                <div class="eventtitleinfos">
                                <h5>`+ value['name'] + `</h5>
                                    <p class="upsmtxt">
                                        `+ value['event_sub_categ_id'] + `
                                    </p>
                                </div>
                                <div class="eventinfos">
                                    <label style="color:#8A8A8A !important;">
                                        <img src="/ppts_website_theme/static/src/img/person-icon.svg" width="24px" height="24px"/>
                                        <a class="underline-a" style="color: #8A8A8A;" href="/team/therapists/`+ value['user_id'] + `">
                                        `+ value['user'] + `
                                        </a>
                                    </label>

                                    <label style="color:#8A8A8A !important;">
                                        <img src="/ppts_website_theme/static/src/img/calendar-icon.svg" width="24px" height="24px" />
                                        `+ value['date'] + `
                                    </label>

                                    <label style="color:#8A8A8A !important;">
                                        `+ value['type_event_img'] + `
                                        `+ value['platform'] + `
                                    </label>

                                    <label style="color:#8A8A8A !important;">
                                        <img src="/ppts_website_theme/static/src/img/location-icon.svg" width="24px" height="24px"/>
                                        `+ value['location'] + `
                                    </label>
                                </div>
                            </div>
                            <div class="event-listbtn">
                                <a class="fullbutton" id="selected-event-ID" data-event-id="`+ value['id'] + `" style="color: #ffff !important;">
                                    book for 
                                    `+ value['cost'] + `
                                    AED
                                </a>
                                <a href="#book_free_apt_snippet" style="text-decoration:none;" class="borderedbtn">Enquire Now</a>
                            </div>
                        </div>
                    </div>
                `);

                $(".table-body-main").append(`
                    <tr>
                        <td>
                            <p class="upsmtxt" style="color: #3A3A3A;">
                            `+ value['event_sub_categ_id'] + `
                            </p>
                        </td>
                        <td>
                            <label style="color:#8A8A8A !important;">
                                <img src="/ppts_website_theme/static/src/img/person-icon.svg" width="24px" height="24px"/>
                                <a class="underline-a" style="color: #8A8A8A !important;font-size: 14px;" t-att-title="list_event_id.get_facilitator_name()" t-attf-href="/team/therapists/{{list_event_id.facilitator_evnt_ids[0].id}}">
                                    <t t-esc="list_event_id.get_facilitator_name()"/>
                                </a>
                                <a class="underline-a" style="color: #8A8A8A;" href="/team/therapists/`+ value['user_id'] + `">
                                `+ value['user'] + `
                                </a>
                            </label>
                        </td>
                        <td>
                            <label class="training-list-label" style="color:#8A8A8A !important;">
                                <img src="/ppts_website_theme/static/src/img/calendar-icon.svg" width="24px" height="24px" />
                                `+ value['date'] + `
                            </label>
                        </td>
                        <td>
                            <label class="training-list-label" style="color:#8A8A8A !important;">
                            `+ value['type_event_img'] + `
                            `+ value['platform'] + `
                            </label>
                        </td>
                        <td>
                            <label class="training-list-label" style="color:#8A8A8A !important;">
                                <img src="/ppts_website_theme/static/src/img/location-icon.svg" width="24px" height="24px"/>
                                `+ value['location'] + `
                            </label>
                        </td>
                        <td>
                            <a href="#book_free_apt_snippet" style="text-decoration:none;">Enquire</a>
                        </td>
                        <td>
                            <a class="fullbutton" id="selected-event-ID" data-event-id="`+ value['id'] + `" style="color: #ffff !important;">
                                book for 
                                `+ value['cost'] + `
                                AED
                            </a>
                        </td>
                    </tr>
                `);


            });


        },
    });

});