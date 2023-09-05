function ClnToggleEventTypeHealing(e) {
    $(".ClassHealingFilter button").removeClass('selectedbtn');
    $(e).addClass('selectedbtn');
    var sub_cat_id = $('#subCategoryId').val();
    var type = $(e).attr('event-data');
    $.ajax({
        url: "/get/model/healing-approaches/data",
        type: "POST",
        async: false,
        data: { 'type': type, 'sub_cat_id': sub_cat_id},
        success: function(result) {
        $('#positionlistviewDiv').html(result);
    }
});
}