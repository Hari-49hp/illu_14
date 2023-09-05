//$(function () {


	function client_load_auto_complete() {
	
		$("#client-head-search").on('focus', function () {
		var website_name = $('.oe_topbar_name').text()
		var website_name1 = $('.location-filter-drop-down').text()
		console.log("HIIIIIIIIIIII",website_name1)
	    if (website_name){
	    var website_id=website_name
	    }
	    else{
	    website_id=null
	    }
		console.log("Website sss",website_id)
            var customer
            $.ajax({
                url: "/booking_activities/filter/customer_detail",
                type: "POST",
                async: false,
                data: {
                'website_id' : website_id,
                },
                success: function (result) {
                    var resultJSON = jQuery.parseJSON(result);
                    customer = resultJSON;
                },
            });

            $('#client-circle-tooltip').tooltip();

            $(this).autocomplete({
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
                delay: 0,
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
        });

        // $("#client-head-search").click(function () {
        //     $("#client-head-search").keydown();
        // });
		
	
	}
	
	client_load_auto_complete();
    setTimeout(function () {
    	client_load_auto_complete();
    }, 0);

    // <div class="add-customer-autocomplete" onclick="getElementById('client-head-search').value='';">\
    //     <a href="/booking/url/redirect/customer_create"><i class="fa fa-plus-circle"></i> Add customer</a>
    // </div>



// });