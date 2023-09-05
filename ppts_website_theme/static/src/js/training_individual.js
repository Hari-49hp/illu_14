

$('#training-individual-event-name').multiselect({
    templates: {
        button: '<button type="button" class="multiselect dropdown-toggle btn btn-default" data-toggle="dropdown"><span class="multiselect">Course Name</span></button>',
    },
    buttonTitle: function (options, select) {
        var labels = [];
        options.each(function () {
            labels.push($(this).text());
        });
        return labels.join(' - ');
    }
});


$('#training-individual-event-level').multiselect({
    templates: {
        button: '<button type="button" class="multiselect dropdown-toggle btn btn-default" data-toggle="dropdown"><span class="multiselect">Levels</span></button>',
    },
    buttonTitle: function (options, select) {
        var labels = [];
        options.each(function () {
            labels.push($(this).text());
        });
        return labels.join(' - ');
    }
});

$('#training-individual-event-platform').multiselect({
    templates: {
        button: '<button type="button" class="multiselect dropdown-toggle btn btn-default" data-toggle="dropdown"><span class="multiselect">Platform</span></button>',
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


$('#training-individual-event-country').multiselect({
    enableCaseInsensitiveFiltering: true,
    includeSelectAllOption: true,
    templates: {
        button: '<button type="button" class="multiselect dropdown-toggle btn btn-default" data-toggle="dropdown"><span class="multiselect">Country</span></button>',
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




$('#training-individual-event-city').multiselect({
    enableCaseInsensitiveFiltering: true,
    includeSelectAllOption: true,
    templates: {
        button: '<button type="button" class="multiselect dropdown-toggle btn btn-default" data-toggle="dropdown"><span class="multiselect">City</span></button>',
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


$('#TraningIndividualDatePicker').datepicker({
    autoclose: true, 
    todayHighlight: true
});

$(document).on("click", "#training-filter-btn", () => {


    $.ajax({
        url: "/training/individual/filter",
        type: "POST",
        async: false,
        data: {
            course_name: JSON.stringify($('#training-individual-event-name').val()),
            levels: JSON.stringify($('#training-individual-event-level').val()),
            platform: $('#training-individual-event-platform').val(),
            country: JSON.stringify($('#training-individual-event-country').val()),
            city: JSON.stringify($('#training-individual-event-city').val()),
            // date: $('#training-date').val(),
        },

        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            $(".calendar-eventlist-view-wrapper").empty();
            $(".table-body-training").empty();

            $.each(resultJSON, function (key, value) {

                $(".calendar-eventlist-view-wrapper").append(`
                    <div class="calenday-eventlist-item aos-init aos-animate" data-aos="fade-up" data-aos-delay="100">
                    <div class="cal-event-img">
                    <img src="`+value['image']+`">
                    </div>
                    <div class="eventfullinfos">
                    <div class="event-typoingo">
                    <div class="eventtitleinfos">
                    <h5>`+value['name']+`</h5>
                    <p class="upsmtxt">Basic DNA</p>
                    </div>
                    <div class="eventinfos">
                    <label><i class="far fa-user"></i>`+value['user']+`</label>

                    <label><i class="far fa-calendar-minus"></i>`+value['date']+`</label>
                    <label> <img src="/ppts_website_theme/static/src/img/onsiteicon.svg" width="20px" loading="lazy">
                    `+value['platform']+`</label>

                    <label><i class="fas fa-map-marker-alt"></i> `+value['location']+`</label>

                    </div>

                    </div>
                    <div class="event-listbtn">
                    <button class="fullbutton">book for `+value['cost']+` AED</button>
                    <a href="#general_enquiry" style="text-decoration:none;" class="borderedbtn">Enquire Now</a>
                    </div>
                    </div>
                    </div>
                    `);

                $(".table-body-training").append(`
                    <tr>
                    <td>
                    <p class="upsmtxt">Basic DNA</p>
                    </td>
                    <td> <label><i class="far fa-user"></i> `+value['user']+`</label> </td>
                    <td> <label><i class="far fa-calendar-minus"></i>`+value['date']+`</label> </td>
                    <td> <label><i class="far fa-clock"></i></label>`+value['platform']+` </td>
                    <td> <label><i class="fas fa-map-marker-alt"></i> `+value['location']+`</label>
                    </td>
                    <td> <a>Enquire</a> </td>
                    <td> <button class="fullbutton">book for `+value['cost']+`  AED</button> </td>
                    </tr>
                    `);


            });


        },
    });


});


