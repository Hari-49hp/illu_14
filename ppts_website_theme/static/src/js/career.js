// $(function () {
$(document).ready(function () {
    $('#ResumeSubmit').bind("click", function () {
        var imgVal = $('#file_popup').val();
        if (imgVal == '') {
            alert("Please upload resume and continue.");
            return false;
        }
    });
});
$('#file_popup').on('change', function () {
    var fileInput = document.getElementById('file_popup');
    var filePath = fileInput.value;
    var allowedExtensions = /(\.doc|\.docx|\.pdf|\.xls|\.xlsx)$/i;
    if (!allowedExtensions.exec(filePath)) {
        alert('Invalid file type ! File extension must be in .pdf, .xls, .xlsx, .doc, .docx .');
        fileInput.value = '';
        return false;
    }
    const size =
        (this.files[0].size / 1024 / 1024).toFixed(2);

    if (size > 4) {
        alert("File must be lesser than size of 4 MB");
    } else {
        var i = $(this).prev('label').clone();
        var file = $('#file_popup')[0].files[0].name;
        $(this).prev('label').text(file);
    }
});

function onclickUpcoming() {
    //     $('#upcomingsection_mng').scrollTop($('#upcomingsection_mng').scrollTop()+20);;
    window.location.href = '#upcomingsection_mng';
}
function onclickPosition() {
    window.location.href = '#therapistOpen';
}

function onclickTherapistBtn() {
    window.location.href = '#therapistOpen';
}

var listviewoff = () => {
    var element = document.getElementsByClassName("positionlistview");
    var i;
    for (i = 0; i < element.length; i++) {
        element[i].className = ' calendar-eventlist-view-wrapper positionlistview '; // WITH space added
    }
    //    element.classList.remove("listviewmode");
    var dropdownMenuButtonGrid = document.getElementById("dropdownMenuButtonGrid");
    dropdownMenuButtonGrid.classList.add("d-none");
    var dropdownMenuButtonList = document.getElementById("dropdownMenuButtonList");
    dropdownMenuButtonList.classList.remove("d-none");
}

var gridviewoff = () => {
    var element = document.getElementsByClassName("positionlistview");
    var i;
    for (i = 0; i < element.length; i++) {
        element[i].className = ' calendar-eventlist-view-wrapper positionlistview listviewmode'; // WITH space added
    }
    document.getElementById("dropdownMenuButtonGrid").classList.remove("d-none");
    document.getElementById("dropdownMenuButtonList").classList.add("d-none");
}

var career_therapist = (job_id, address_id, tab) => {
    window.location.href = "/initial-application-form/" + job_id;
}

var career_management = (job_id, address_id, tab) => {
    $("#studentModalform").modal();
    $.ajax({
        url: "/get/model/recruitment/management",
        type: "POST",
        async: false,
        data: { 'job_id': job_id, 'type': 'career_therapist', 'address_id': address_id, 'tab': tab },
        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            $('#studentModalform #next_job_id').val(resultJSON['next_job']);
            if (resultJSON['next_job'] == false) {
                $('#studentModalform .hide_next_job_false').hide();
            } else {
                $('#studentModalform .hide_next_job_false').show();
            }
            $('#studentModalform #next_job_id_type').val('career_therapist');
            $('#studentModalform #current_partner_id').val(address_id);
            $('#studentModalform #current_tab').val(tab);
            $('#studentModalform .responsibilities-lst').empty();
            $('#studentModalform .qualifications-lst').empty();
            $('#studentModalform .career-management-title').text(resultJSON['title']);
            $('#studentModalform .Student-BottomNavigationBar').text(resultJSON['title']);
            $('#studentModalform .student-desc').text(resultJSON['description']);
            $.each(resultJSON['responsibilities'], function (key, value) {
                $('#studentModalform .responsibilities-lst').append('<li>' + value + '</li>');
            });
            $.each(resultJSON['qualifications'], function (key, value) {
                $('#studentModalform .qualifications-lst').append('<li>' + value + '</li>');
            });
            $('#studentModalform .recruitement-fill-form').attr('action', '/recruitement/application/submit/' + job_id)
        }
    });
}

var nxt_career = () => {
    $("#studentModalform").modal();
    var job_id = $("#next_job_id").val();
    var current_partner_id = $('#studentModalform #current_partner_id').val();
    var type = $('#studentModalform #next_job_id_type').val();
    var tab = $('#studentModalform #current_tab').val();
    $.ajax({
        url: "/get/model/recruitment/management",
        type: "POST",
        async: false,
        data: { 'job_id': job_id, 'type': type, 'address_id': current_partner_id, 'tab': tab },
        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            $('#studentModalform #next_job_id').val(resultJSON['next_job']);
            $('#studentModalform .career-management-title').text(resultJSON['title']);
            $('#studentModalform #next_job_id_type').val(type);
            $('#studentModalform #current_tab').val(tab);
            $('#studentModalform .Student-BottomNavigationBar').text(resultJSON['title']);
            $('#studentModalform .student-desc').text(resultJSON['description']);
            $('#studentModalform .responsibilities-lst').empty();
            $('#studentModalform .qualifications-lst').empty();
            $('#studentModalform #current_partner_id').val(current_partner_id);
            $.each(resultJSON['responsibilities'], function (key, value) {
                $('#studentModalform .responsibilities-lst').append('<li>' + value + '</li>');
            });
            $.each(resultJSON['qualifications'], function (key, value) {
                $('#studentModalform .qualifications-lst').append('<li>' + value + '</li>');
            });
            $('#studentModalform .recruitement-fill-form').attr('action', '/recruitement/application/submit/' + job_id)
        }
    });

}

// });