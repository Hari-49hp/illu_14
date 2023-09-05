$(document).ready(function () {

    $('#blog-global-search , #blog-model-global-search').keypress(function (event) {

        var keycode = (event.keyCode ? event.keyCode : event.which);
        if (keycode == '13' && event.currentTarget.value.length > 2) {
            $('#searchmodel-popup').modal({
                keyboard: false,
                show: true,
                focus: true,
                backdrop: false
            })

            $('#blog-model-global-search').val(event.currentTarget.value);

            $.ajax({
                url: "/blog/global/search",
                type: "POST",
                async: false,
                data: { 'search': event.currentTarget.value },
                success: function (result) {
                    var resultJSON = jQuery.parseJSON(result);
                    $('.model-blog-search-result').empty();
                    $.each(resultJSON, function (key, value) {
                        $('.model-blog-search-result').append('<a href="' + value['url'] + '" onclick="blog_redirect_url(this)">' + value['name'] + '</a><br/>');
                    });
                }
            });

            $.ajax({
                url: "/blog/global/search/list/cards",
                type: "POST",
                async: false,
                data: { 'search': event.currentTarget.value },
                success: function (result) {
                    var resultJSON = jQuery.parseJSON(result);
                    $('.blog-recomen-list-model-cards').empty();
                    $.each(resultJSON, function (key, value) {
                        var tags = ''

                        $.each(value['tags'], function (key, value) {
                            tags += `<label> ` + value + `</label>`
                        })

                        $('.blog-recomen-list-model-cards').append(`
                                <div class="popularpost-list">
                                    <img src="` + value['img'] + `" />
                                    <div class="popular-typos">
                                        <h6>` + value['name'] + `</h6>
                                        <p>` + value['subtitle'] + `</p>
                                        <div class="oberlay-tags">` +
                            tags +
                            `</div>
                                    </div>
                                </div>
                        `);
                    });
                }
            });


            $('#blog-searchdata').empty();
            const removeDupliactes = (values) => {
                let concatArray = values.map(eachValue => {
                    return Object.values(eachValue).join('')
                })
                let filterValues = values.filter((value, index) => {
                    return concatArray.indexOf(concatArray[index]) === index

                })
                return filterValues
            }
            if (localStorage.searchHistory) {
                $.each(removeDupliactes(JSON.parse(localStorage.searchHistory)), function (key, value) {
                    $('#blog-searchdata').append('<p>' + value + '</p>');
                });
            }

        }

    });



});

document.addEventListener("DOMContentLoaded", function () {

    var filter_multiselect = $('#blog-tags-filter').multiselect({
        buttonText: function (options, select) {
            return 'Category';
        },
        buttonTitle: function (options, select) {
            var labels = [];
            options.each(function () {
                labels.push($(this).text());
            });
            return labels.join(' - ');
        },
    });

    $("#blog-tags-filter").change(function () {
        var selected = $(this).find("option:selected");
        var arrSelected = {};
        $('.latmonthfilterrow-left').empty();
        selected.each(function () {
            arrSelected[$(this).val()] = $(this).text()
        });
        $.each(arrSelected, function (key, value) {
            $('.latmonthfilterrow-left').append(`<a class="filterchipwithclose" data-tag-id="` + key + `">` + value + `<i id="closeiconchip" onclick="closeiconchipFunc(this)" class="closeiconchip"></i></a>`)
        });
        getDataAndFeed()
    });

    var blog_redirect_url = (self) => {
        var searchHistory = (localStorage.searchHistory) ? JSON.parse(localStorage.searchHistory) : [];
        searchHistory.push(self.innerText);
        localStorage.searchHistory = JSON.stringify(searchHistory);
    }

});

var arrayRemoveVal = (array, removeValue) => {
    var newArray = $.grep(array, (value) => { return value != removeValue; });
    return newArray;
}

var closeiconchipFunc = (e) => {
    let tag_closest = $(e).closest(".filterchipwithclose");
    let tag_id = tag_closest.attr('data-tag-id');
    let value_tag = $('.blog-tags-filter-div-whole :input[value="' + parseInt(tag_id) + '"]');
    value_tag.closest('.multiselect-option.dropdown-item.active').removeClass('active');
    value_tag.prop('checked', false);
    tag_closest.remove();
    let blog_val = $('#blog-tags-filter').val()
    blog_val = arrayRemoveVal(blog_val, tag_id)
    $('#blog-tags-filter').val(blog_val)
    getDataAndFeed()
}

var getDataAndFeed = () => {
    let blog_val = $('#blog-tags-filter').val()
    $.ajax({
        url: "/blog/latest/tag/filter",
        type: "POST",
        async: false,
        dataType: "json",
        // contentType: 'application/json; charset=utf-8',
        data: { 'filter': JSON.stringify(blog_val) },
        success: function (result) {
            // var resultJSON = jQuery.parseJSON(result);
            $('#high_views_post_ids').empty();
            $.each(result, function (key, value) {
                var tags = ''
                $.each(value['tags'], function (key, value) {
                    tags += `<label> ` + value + `</label>`
                })
                $('#high_views_post_ids').append(`
                <div class="col-xl-4 col-lg-6 col-md-6 col-sm-6 col-xs-12 featurecard-items" data-aos="fade-up" data-aos-delay="200">
                <div class="abt-title-img">
                    <img src="` + value['img'] + `" class="img-fluid" loading="lazy"/>
                </div>
                <div class="oberlay-tags tagsrelative">` + tags + `</div>
                <a href="` + value['url'] + `">
                    <h5>` + value['name'] + `</h5>
                </a>
            </div>
            `);
            });
        }
    });
}