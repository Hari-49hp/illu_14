$(document).ready(function() {
    "use strict";
    $(".partner_set_type").change(function() {
        var value = $(".partner_set_type").val();
        if (value == 'appointment') {
            $(".appointment_val").removeClass("oe_hidden");
            $(".event_val").addClass("oe_hidden");
        } else if (value == 'event') {
            $(".event_val").removeClass("oe_hidden");
            $(".appointment_val").addClass("oe_hidden");
        } else {
            $(".event_val").addClass("oe_hidden");
            $(".appointment_val").addClass("oe_hidden");
        }

        var x = $('.partner_set_type').val();
        $.ajax({
            url: "/pos/event/details",
            type: 'POST',
            data: {
                "x": x
            },
            success: function(result) {
                var obj_result = JSON.parse(result);
                var htmlOptions = '';

                if (x == "event") {
                    htmlOptions = '<option value="">Select Event...</option>';
                } else if (x == "appointment") {
                    htmlOptions = '<option value="">Select Appointment...</option>';
                }
                $.each(obj_result, function(key, value) {
                    htmlOptions += '<option value="' + value.value + '">' + value.name + '</option>';
                });

                if (x == "event") {
                    $('.partner_event').html(htmlOptions);
                } else if (x == "appointment") {
                    $('.partner_appoinment').html(htmlOptions);
                }
            },
        });
    });

    $(".partner_event").change(function() {
        var x_partner_event = $('.partner_event').val();
        if (x_partner_event != '') {
            $(".select_customer_pos").show();
        } else {
            $(".select_customer_pos").hide();
        }
        $.ajax({
            url: "/pos/event/partner_event",
            type: 'POST',
            data: {
                "x": x_partner_event
            },
            success: function(result) {},
        });
    });

    $(".appointment_val").change(function() {
        var x_partner_appointment = $('.partner_appoinment').val();
        if (x_partner_appointment != '') {
            $(".select_customer_pos").show();
        } else {
            $(".select_customer_pos").hide();
        }
        $.ajax({
            url: "/pos/event/partner_appointment",
            type: 'POST',
            data: {
                "y": x_partner_appointment
            },
            success: function(result) {

            },
        });
    });

});