$(document).ready(function () {
    setTimeout(function () {
        const btmfixedbar = document.querySelector("#ourteamfilterpopup");
        for (let i = 0; i < btmfixedbar.length; i++) {
            btmfixedbar[i].click(function () {
                $('#outteamfilter').toggleClass("activeourteamfilterpopup");
                $('#outteamfilter').toggleClass("modal left fade show");
            });
        }

        const btmfixedbarl = document.querySelector("#ourteamfilterpopupoe");
        for (let i = 0; i < btmfixedbarl.length; i++) {
            btmfixedbarl[i].click(function () {
                $('#outteamfilter').toggleClass("activeourteamfilterpopup");
            });
        }
    }, 2000);

    $('#team-by-platform').multiselect({
        templates: {
            button: '<button type="button" class="multiselect dropdown-toggle btn btn-default" data-toggle="dropdown"><span class="multiselect">By Platform</span></button>',
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

    $('#team-by-support').multiselect({
        templates: {
            button: '<button type="button" class="multiselect dropdown-toggle btn btn-default" data-toggle="dropdown"><span class="multiselect">By Support</span></button>',
        },
        buttonTitle: function (options, select) {
            var labels = [];
            options.each(function () {
                labels.push($(this).text());
            });
            return labels.join(' - ');
        }
    });

    $('#team-by-solution').multiselect({
        templates: {
            button: '<button type="button" class="multiselect dropdown-toggle btn btn-default" data-toggle="dropdown"><span class="multiselect"><i class="fas fa-list-ul"></i> By Solution</span></button>',
        },
        buttonTitle: function (options, select) {
            var labels = [];
            options.each(function () {
                labels.push($(this).text());
            });
            return labels.join(' - ');
        }
    });

    $('#team-by-location').multiselect({
        templates: {
            button: '<button type="button" class="multiselect dropdown-toggle btn btn-default" data-toggle="dropdown"><span class="multiselect"><img style="margin-left: -3px;margin-right: 4px;" src="/ppts_website_theme/static/src/img/location-icon.svg" width="24px" height="24px"/> By Location</span></button>',
        },
        enableCaseInsensitiveFiltering: true,
        includeSelectAllOption: true,
        buttonTitle: function (options, select) {
            var labels = [];
            options.each(function () {
                labels.push($(this).text());
            });
            return labels.join(' - ');
        }
    });

    $("#apply-filter").click(function () {
        var by_support = JSON.stringify($('#team-by-support').val());
        var by_solution = JSON.stringify($('#team-by-solution').val());
        var by_location = JSON.stringify($('#team-by-location').val());
        $.ajax({
            url: "/team/filter",
            type: 'POST',
            async: false,
            data: {
                'only_available': $("input[name='show_available_therapist']").is(":checked"),
                'by_platform': $('#team-by-platform').val(),
                'by_support': by_support,
                'by_solution': by_solution,
                'by_location': by_location,
            },
            success: function (result) {
                var resultJSON = jQuery.parseJSON(result);
                $('#therapist-list-our-team').empty();
                $.each(resultJSON, function (key, value) {
                    $('#therapist-list-our-team').append(`
                        <div class="col-xl-4 col-lg-4 col-md-4 col-sm-6 col-xs-12" data-aos="fade-up" data-aos-delay="`+ value['aos_delay'] + `">
                        <a href="/team/therapists/`+ value['id'] +`">
                        <div class="therapest-list-container">
                            <img src="/web/image?model=hr.employee&id=`+ value['id'] + `&field=image_1920" />
                            <h5>`+ value['name'] + `</h5>
                            <p>`+ value['job_position'] + `</p>
                            <label class="therapestlocation">`+ value['company_name'] + `</label>
                            <a class="buttonwithbtnshape"> Book an appointment </a>
                        </div>
                        </a>
                    </div>
                    `);
                });
            },
        });

    });

    $("#clear-filter-btn").click(function () {

        // $('#team-by-platform').multiselect('select', ['all']);
        // $("input[name='show_available_therapist']").prop('checked', false);
        // $("#team-by-support").val([]).multiselect('refresh');
        // $("#team-by-solution").val([]).multiselect('refresh');
        // $("#team-by-location").val([]).multiselect('refresh');

        location.reload()

    });

});