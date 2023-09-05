$('input.flexRadioDefaultGender').on('change', function () {
    $('input.flexRadioDefaultGender').not(this).prop('checked', false);
});
$('input.facilitator').on('change', function () {
    $('input.facilitator').not(this).prop('checked', false);
});
$('input.relocate').on('change', function () {
    $('input.relocate').not(this).prop('checked', false);
});
$('input.type').on('change', function () {
    $('input.type').not(this).prop('checked', false);
});
var treeObject = []
$.ajax({
    url: "/initial-application-form/category",
    type: "get",
    async: false,
    dataType: 'json',
    success: function (result) { treeObject = result.data }
});
var tw = new TreeView(
    treeObject,
    { showAlwaysCheckBox: true, fold: true });

document.getElementById("treeview_new").appendChild(tw.root)
function firstCall() {
    var spans = document.getElementById('treeview_new').getElementsByTagName('span')
    var Options = [];
    $('#DivInitialFormAnswer input[type=checkbox]:checked').each(function () {
        if ($(this).data("parent") !== null) {
            var parent_id = $(this).data("parent");
            var data_id = $(this).data('id');
            Options.push({ parent_id: parseInt(parent_id), data_id: parseInt(data_id) })
        }
    });
    obj = [];
    for (var i = 0, l = spans.length; i < l; i++) {
        var check_value = spans[i].getAttribute("check-value");
        if (spans[i].getAttribute("data-parent_id") !== null && check_value === "1") {
            var parent_id = spans[i].getAttribute("data-parent_id")
            var data_id = spans[i].getAttribute("data-id")
            obj.push({ parent_id: parseInt(parent_id), data_id: parseInt(data_id) })
        }
    }
    var input = $("<input>").attr({ "type": "hidden", "name": "approaches" }).val(JSON.stringify(obj));
    $('#InitialApplicationSubmit').append(input);
    var input = $("<input>").attr({ "type": "hidden", "name": "question_options" }).val(JSON.stringify(Options));
    $('#InitialApplicationSubmit').append(input);
}
$(document).ready(function () {
    $("#btn-apply-initial").click(function () {
        firstCall()
    });
});

function preview_image() {
    var fileInput = document.getElementById('app_file');
    var filePath = fileInput.value;
    var _validFileExtensions = [".jpg", ".jpeg", ".bmp", ".gif", ".png"];
    var allowedExtensions = /(\.jpg|\.jpeg|\.bmp|\.gif|\.png)$/i;
    if (!allowedExtensions.exec(filePath)) {
        alert('Invalid file type ! File extension must be in .jpg, .jpeg, .bmp, .gif, .png .');
        fileInput.value = '';
        return false;
    } else {
        const size = (fileInput.files[0].size / 1024 / 1024).toFixed(2);
        if (size > 4) {
            alert("File must be lesser than size of 4 MB");
        } else {
            $('#ImagePreviewSpan').removeClass('d-none');
            var form_data = new FormData();
            var total_file = document.getElementById("app_file").files.length;
            var odd_even = 0;
            $('#ImagePreview').html('');
            for (var i = 0; i < total_file; i++) {
                form_data.append("file[]", document.getElementById('app_file').files[i]);
                if (odd_even % 2 === 0) {
                    $('#ImagePreview').append("<img name='images' src='" + URL.createObjectURL(event.target.files[i]) + "'>");
                }
                else { $('#ImagePreview').append("<img name='images' src='" + URL.createObjectURL(event.target.files[i]) + "'><br/>"); }
                odd_even++;
            }
        }
    }
}
$("#country_id").change(function () {
    var id = $(this).val();
    $('select#city_id>option').each(function () {
        var text = $(this).val();
        if (text === id) {
            $(this).show();
        }
        else {
            $(this).hide();
        }
    });
});
