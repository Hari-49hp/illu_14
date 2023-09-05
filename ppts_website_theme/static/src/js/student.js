var StudentModel = (emp_id) => {
    $("#studentModalEmp").modal();
    $.ajax({
        url: "/get/model/student/data",
        type: "POST",
        async: false,
        data: { 'emp_id': emp_id, 'type': 'all' },
        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            $('#studentModalEmp #next_emp_id').val(resultJSON['next_emp']);
            if (resultJSON['next_emp'] == false) {
                $('#studentModalEmp .hide_next_emp_false').hide();
            } else {
                $('#studentModalEmp .hide_next_emp_false').show();
            }
            $('#studentModalEmp #student-certification-list').empty();
            $('#studentModalEmp #studentModalLabel').text(resultJSON['title']);
            $("#studentModalEmp #studentModalImage").attr('src', resultJSON['image']);
            $('#studentModalEmp #studentModalBottomTitle').text(resultJSON['title']);
            $('#studentModalEmp #studentModalDes').html(resultJSON['about']);
            $.each(resultJSON['certifications'], function (key, value) {
                $('#studentModalEmp #student-certification-list').append('<li>' + value + '</li>');
            });
        }
    });
}

$(document).ready(function () {
    $("#multiselect-filter-locations_id-new").multiselect('clearSelection');
    $("#multiselect-filter-certification_id-new").multiselect('clearSelection');
    $('#multiselect-filter-locations_id-new').change(function () {
        filter_id = $('#multiselect-filter-locations_id-new').val()
        if (filter_id.length === 0) {
            filter_id = '[]'
        }
        filter_id1 = $('#multiselect-filter-certification_id-new').val()
        if (filter_id1.length === 0) {
            filter_id1 = '[]'
        }
        $.ajax({
            url: "/get/model/student/filter/" + filter_id + "/" + filter_id1,
            type: "get",
            async: false,
            dataType: 'json',
            success: function (result) {
                $('#StudentListDetails').html(result.html);
            }
        });
    });

    $('#multiselect-filter-certification_id-new').change(function () {
        filter_id = $('#multiselect-filter-locations_id-new').val()
        if (filter_id.length === 0) {
            filter_id = '[]'
        }
        filter_id1 = $('#multiselect-filter-certification_id-new').val()
        if (filter_id1.length === 0) {
            filter_id1 = '[]'
        }
        $.ajax({
            url: "/get/model/student/filter/" + filter_id + "/" + filter_id1,
            type: "get",
            async: false,
            dataType: 'json',
            success: function (result) {
                $('#StudentListDetails').html(result.html);
            }
        });
    });

});
$('#multiselect-filter-locations_id-new').multiselect({
    enableCaseInsensitiveFiltering: true,
    includeSelectAllOption: true,
    maxHeight: 400,
    buttonWidth: '100%',
    dropUp: false,
    buttonText: function (options, select) {
        return 'Region';
    },
    buttonTitle: function (options, select) {
        var labels = [];
        options.each(function () {
            labels.push($(this).text());
        });
        return labels.join(' - ');
    },
});
$('#multiselect-filter-certification_id-new').multiselect({
    enableCaseInsensitiveFiltering: true,
    includeSelectAllOption: true,
    maxHeight: 400,
    buttonWidth: '100%',
    dropUp: false,
    buttonText: function (options, select) {
        return 'Certification';
    },
    buttonTitle: function (options, select) {
        var labels = [];
        options.each(function () {
            labels.push($(this).text());
        });
        return labels.join(' - ');
    },
});

var nxt_career = () => {
    //    $("#studentModalform").modal();
    var emp_id = $("#next_emp_id").val();
    $.ajax({
        url: "/get/model/student/data",
        type: "POST",
        async: false,
        data: { 'emp_id': emp_id, 'type': 'next' },
        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            $('#studentModalEmp #next_emp_id').val(resultJSON['next_emp']);
            if (resultJSON['next_emp'] == false) {
                $('#studentModalEmp .hide_next_emp_false').hide();
            } else {
                $('#studentModalEmp .hide_next_emp_false').show();
            }
            $('#studentModalEmp #student-certification-list').empty();
            $('#studentModalEmp #studentModalLabel').text(resultJSON['title']);
            $("#studentModalEmp #studentModalImage").attr('src', resultJSON['image']);
            $('#studentModalEmp #studentModalBottomTitle').text(resultJSON['title']);
            $('#studentModalEmp #studentModalDes').text(resultJSON['about']);
            $.each(resultJSON['certifications'], function (key, value) {
                $('#studentModalEmp #student-certification-list').append('<li>' + value + '</li>');
            });
        }
    });

}