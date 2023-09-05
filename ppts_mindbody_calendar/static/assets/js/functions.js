$("#consumerSearchQueryInput").on('focus', function () {
var selectedCountry = $("select.location-filter-drop-down").children("option:selected").val();
     console.log("BookinggggI",selectedCountry)
let customer
$.ajax({
    url: "/booking_activities/filter/customer_detail",
    type: "POST",
    async: false,
    data: {
        'selected_country_id_booking' : selectedCountry,
    },
    success: function (result) {
        customer = jQuery.parseJSON(result);
    },
});

$("#consumerSearchQueryInput").autocomplete({
    // source: customer,
    source: function (req, resp) {
        var results = [];
        $.each(customer, function (k, v) {
            if (v.label.indexOf(req.term) != -1) {
                results.push(v);
                return;
            }
            if (v.label.toLocaleLowerCase().indexOf(req.term) != -1) {
                results.push(v);
                return;
            }
            if (v.label.toLocaleUpperCase().indexOf(req.term) != -1) {
                results.push(v);
                return;
            }
            if (v.label.toLowerCase().indexOf(req.term) != -1) {
                results.push(v);
                return;
            }
            if (v.label.toUpperCase().indexOf(req.term) != -1) {
                results.push(v);
                return;
            }
            if (v.mobile.replace(/\s/g, "").indexOf(req.term) != -1) {
                results.push(v);
                return;
            }
            if (v.mobile.indexOf(req.term) != -1) {
                results.push(v);
                return;
            }
            if (v.email.indexOf(req.term) != -1) {
                results.push(v);
                return;
            }
            if (v.email.toLocaleLowerCase().indexOf(req.term) != -1) {
                results.push(v);
                return;
            }
            if (v.email.toLocaleUpperCase().indexOf(req.term) != -1) {
                results.push(v);
                return;
            }
            if (v.email.toLowerCase().indexOf(req.term) != -1) {
                results.push(v);
                return;
            }
            if (v.email.toLowerCase().indexOf(req.term) != -1) {
                results.push(v);
                return;
            }
            if (v.email.toUpperCase().indexOf(req.term) != -1) {
                results.push(v);
                return;
            }
        });
        resp(results);
    },
    minLength: 1,
    select: function (event, ui) {
        window.location = ui.item.url;
    },
    html: true,
    autoFocus: true,
    minLength: 0,
    open: function (event, ui) {
        $(".ui-autocomplete").css("z-index", 1000);
    },
    focus: function (event) {
        event.preventDefault(); // don't automatically select values on focus
    },
    delay: 200,
}).autocomplete("instance")._renderItem = function (ul, item) {
    return $(`<li>
        <div style="display: flex;">
        <div style="">
        <div style="display: block;line-height: 1;">
        <span style="color:#666;font-weight:bold">` + item.label + `</span>
        <br />
        <span style="font-size: 10px;">
        <span style="font-size:10px;font-weight:800;">Mobile:</span>` + item.mobile + `
        </span>
        <br />
        <span style="font-size: 10px;">
        <span style="font-size:10px;font-weight:800;">Email:</span>` + item.email + `</span>
        </div>
        </div>
        </div>
        </li> 
    `).appendTo(ul);
};

let hideSideBarMainBa = () => {
    var x = document.querySelector("#afterLoad > div.leftmenu-main");
    var afterLoad = document.querySelector("#afterLoad");
    var btmfixedbar = document.querySelector(".btmfixedbar");
    if (x.style.display === "none") {
        x.style.display = "block";
        afterLoad.style.display = "grid";
        btmfixedbar.style.left = "65px";

        x.style.visibility = 'visible';
        x.style.opacity = 1;
    } else {
        x.style.display = "none";
        afterLoad.style.display = "block"
        btmfixedbar.style.left = "0px"

        x.style.visibility = 'hidden';
        x.style.opacity = 0;
    }
}
});
