document.addEventListener("DOMContentLoaded", function () {

    Date.prototype.getWeek = function (dowOffset) {
        dowOffset = typeof dowOffset == "int" ? dowOffset : 0; //default dowOffset to zero
        var newYear = new Date(this.getFullYear(), 0, 1);
        var day = newYear.getDay() - dowOffset; //the day of week the year begins on
        day = day >= 0 ? day : day + 7;
        var daynum =
            Math.floor(
                (this.getTime() -
                    newYear.getTime() -
                    (this.getTimezoneOffset() - newYear.getTimezoneOffset()) * 60000) /
                86400000
            ) + 1;
        var weeknum;
        if (day < 4) {
            weeknum = Math.floor((daynum + day - 1) / 7) + 1;
            if (weeknum > 52) {
                nYear = new Date(this.getFullYear() + 1, 0, 1);
                nday = nYear.getDay() - dowOffset;
                nday = nday >= 0 ? nday : nday + 7;
                weeknum = nday < 4 ? 1 : 53;
            }
        } else {
            weeknum = Math.floor((daynum + day - 1) / 7);
        }
        return weeknum;
    };

    var monthStringArrmS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    var monthStringArrmSHalf = ["Jan", "Feb", "Mar", "Apr", "May", "June", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var weekStringArrmS = ["Su","Mo", "Tu", "We", "Th", "Fr", "Sa"];
    var weekStringTwoStringArr = ["Su","Mo", "Tu", "We", "Th", "Fr", "Sa"];
    var active_selected_date;

    var calendarEl = document.getElementById("upComingEventCalendar");
    var displayDate = "";
    var displayDatel = "";
    var selectedView = "";
    var countDate = 1;
    var selectedViewType = "";
    var weekViewType = "";
    var monthViewEventsDisc = {};
    var weekViewEventsDisc = {};
    const gridWeekViewCountLimit = 3;
    var globalInnerWidth = window.innerWidth;

    $(window).resize(function () {
        globalInnerWidth = window.innerWidth;
        console.log('resize', globalInnerWidth);
        upComingEventDateViewTypeWeekAction()
    });

    const upComingEventDateViewTypeWeekAction = () => {
        if (selectedViewType === 'week') {
            if (globalInnerWidth < 768 && globalInnerWidth > 300) {
                $("#calendar-mainwrap").addClass("weekly-mobileview");
                $("#calendar-mainwrap").removeClass("weekly-webview");
                $("#calendar-mainwrap").removeClass("month-webview");
                $("#calendar-mainwrap").removeClass("month-webview");
                $('.calendar-weeklybutton').css('display', 'block');
                weekViewType = 'listWeek';
                calendar.changeView('listWeek');
            } else {
                $("#calendar-mainwrap").addClass("weekly-webview");
                $("#calendar-mainwrap").removeClass("weekly-mobileview");
                $("#calendar-mainwrap").removeClass("month-webview");
                weekViewType = 'dayGridWeek';
                calendar.changeView('dayGridWeek');
            }
        }
    }

    var handleDateClick = (date) => {
        $(".fc-day-header").removeClass("dateactivebtn");
        $("[data-date='" + date + "'").addClass("dateactivebtn");
    };

    const rgbaToHex = (color) => {
        if (/^rgb/.test(color)) {
            const rgba = color.replace(/^rgba?\(|\s+|\)$/g, '').split(',');
            let hex = `#${((1 << 24) + (parseInt(rgba[0], 10) << 16) + (parseInt(rgba[1], 10) << 8) + parseInt(rgba[2], 10)).toString(16).slice(1)}`;
            if (rgba[4]) {
                const alpha = Math.round(0o1 * 255);
                const hexAlpha = (alpha + 0x10000).toString(16).substr(-2).toUpperCase();
                hex += hexAlpha;
            }
            return hex;
        }
        return color;
    };

    const colorShade = (col, amt) => {
        col = col.replace(/^#/, '')
        if (col.length === 3) col = col[0] + col[0] + col[1] + col[1] + col[2] + col[2]

        let [r, g, b] = col.match(/.{2}/g);
        ([r, g, b] = [parseInt(r, 16) + amt, parseInt(g, 16) + amt, parseInt(b, 16) + amt])

        r = Math.max(Math.min(255, r), 0).toString(16)
        g = Math.max(Math.min(255, g), 0).toString(16)
        b = Math.max(Math.min(255, b), 0).toString(16)

        const rr = (r.length < 2 ? '0' : '') + r
        const gg = (g.length < 2 ? '0' : '') + g
        const bb = (b.length < 2 ? '0' : '') + b

        return `#${rr}${gg}${bb}`
    }


    var eventJSON = [];
    var lastRequestedDate = '';

    $.ajax({
        url: "/theme/upcoming_event/render/reach",
        type: "POST",
        async: false,
        data: {
            calendar_domain: $('#calendar_domain').val(),
        },
        success: function (result) {
            eventJSON = jQuery.parseJSON(result);
        },
    });


    $('#calendar-multiselect-filter-location, #calendar-multiselect-filter-location-m').multiselect({
        // enableCaseInsensitiveFiltering: true,
        includeSelectAllOption: true,
        maxHeight: 400,
        dropUp: false,
        buttonText: function (options, select) {
            return 'All Locations';
        },
        buttonTitle: function (options, select) {
            var labels = [];
            options.each(function () {
                labels.push($(this).text());
            });
            return labels.join(' - ');
        },
    });

    $('#calendar-multiselect-filter-service , #calendar-multiselect-filter-service-m').multiselect({
        includeSelectAllOption: true,
        maxHeight: 400,
        dropUp: false,
        buttonText: function (options, select) {
            return 'Service';
        },
        buttonTitle: function (options, select) {
            var labels = [];
            options.each(function () {
                labels.push($(this).text());
            });
            return labels.join(' - ');
        },
    });



    // Start  
    var event_ticket_price_calcu_method = () => {
        var event_ticket_price_calcu = document.querySelectorAll('#data-ticket-price-id');
        var total_ticket_price = 0;
        event_ticket_price_calcu.forEach(element => {
            // total_ticket_price = parseInt(total_ticket_price) + parseInt(element.textContent);
        // change the ticket price formula based on website 13-07-22
            total_ticket_price =  parseInt(total_ticket_price)+parseInt(element.textContent);
        });
        $('#total-ticket-price').text(total_ticket_price/2);
    };
    //end	

    // Start  
    var event_ticket_qty_add_method = () => {
        var event_ticket_qty_add = document.querySelectorAll('#event-ticket-qty-add');
        event_ticket_qty_add.forEach(element => {
            element.addEventListener("click", (e) => {
                var ticket_id = e.currentTarget.getAttribute("data-ticket-id");
                var ticket_class = ".data-ticket-qty-" + ticket_id
                var ticket_price_class = "#data-ticket-price-" + ticket_id
                var ticket_price = $(ticket_price_class).val()
                var ticket_qty = parseInt($(ticket_class).html()) + 1;
                $(ticket_class).text(ticket_qty);
                var ticket_price_class = ".data-ticket-price-" + ticket_id
                $(ticket_price_class).text(ticket_price * ticket_qty);
                event_ticket_price_calcu_method();
            });
        });
    };
    //end


    // Start  
    var event_ticket_qty_sub_method = () => {
        var event_ticket_qty_sub = document.querySelectorAll('#event-ticket-qty-sub');
        event_ticket_qty_sub.forEach(element => {
            element.addEventListener("click", (e) => {
                var ticket_id = e.currentTarget.getAttribute("data-ticket-id");
                var ticket_class = ".data-ticket-qty-" + ticket_id
                var ticket_price_class = "#data-ticket-price-" + ticket_id
                var ticket_price = $(ticket_price_class).val()
                var ticket_qty = parseInt($(ticket_class).html()) - 1;
                if (ticket_qty < 0) {
                    $(ticket_class).text(0);
                    var ticket_price_class = ".data-ticket-price-" + ticket_id
                    $(ticket_price_class).text(ticket_price * 0);
                } else {
                    $(ticket_class).text(ticket_qty);
                    var ticket_price_class = ".data-ticket-price-" + ticket_id
                    $(ticket_price_class).text(ticket_price * ticket_qty);
                }
                event_ticket_price_calcu_method();
            });
        });

    };
    //end
    
    
    
     // Start  
    var selected_event_reserve_method = () => {

        // Start

        var selected_event_reserve = document.querySelectorAll('#event-reserve-click');

        selected_event_reserve.forEach(element => {

            element.addEventListener("click", (e) => {
            
            
	            var proceed = 1;
			
			if ($("#gift-event-other").prop('checked') == true) {
			
				if ($("#receiver_name").val() == null || $("#receiver_name").val() == '') {
					proceed = 0;
					$("#receiver_name").addClass("reservation-input");
				}
				else if ($("#receiver_email").val() == null || $("#receiver_email").val() == '') {
					proceed = 0;
					$("#receiver_email").addClass("reservation-input");
				}
				else if ($("#receiver_mobile").val() == null || $("#receiver_mobile").val() == '') {
					proceed = 0;
					$("#receiver_mobile").addClass("reservation-input");
				}
			}
				
				
				
		
			if (proceed == 1) {

               var event_id = $('#selected_event_id').val();
               
               

                $('#event-reservation-popup').modal('hide');


                var car_tlist_container = document.querySelectorAll('.cart-list');

                car_tlist_container.forEach(element => {

                    element.remove();

                });



                $.ajax({
                    url: "/event/details",
                    type: 'POST',
                    async: false,
                    data: {
                        'event_id': event_id,
                    },
                    success: function (result) {
                        var resultJSON = jQuery.parseJSON(result);
                        $('.cart-list-container').empty();

                        $.each(resultJSON, function (key, value) {
                            $('.cart-list-container').append(`
				
			                                
			                             <div class="cart-list">
							              <div class="cart-left-info">
							
							                <h5>`+ value['name'] + `
							                  <span> <label class=" chipsone">`+ value['platform'] + `</label> <label class="chipsone">Event</label></span>
							
							                </h5>
							                
							                  <h6>
							                	`+ value['ticket_name'] + `
							                  </h6>
							
							
							                <div class="eventinfos">
							                  <label><i class="fas fa-map-marker-alt"></i> `+ value['location'] + ` </label>
							                  <label><i class="far fa-clock"></i> `+ value['duration'] + ` </label>
							                  <label><i class="far fa-calendar-minus"></i>`+ value['event_date'] + `</label>
							                  <label><i class="far fa-user"></i> `+ value['facilitator'] + `</label>
							                </div>
							              </div>
							              
							              <div class="cart-right-detinfo">
							                <div class="cardcountsection">
							                  Ticket <a class="addsubbtn" data-ticket-id="`+ value['ticket_id'] + `" id="event-ticket-qty-sub">-</a><b data-ticket-id="` + value['ticket_id'] + `" id="data-ticket-qty-id" class="data-ticket-qty-` + value['ticket_id'] + `">1</b><a class="addsubbtn" data-ticket-id="` + value['ticket_id'] + `" id="event-ticket-qty-add">+</a> <a class="closeicon"><i
							                      class="fas fa-times"></i></a>
							              </div>
							                
							                <input hidden type="text" value="`+ value['price'] + `" id="data-ticket-price-` + value['ticket_id'] + `"/>
							                
							                <h4><b id="data-ticket-price-id" class="data-ticket-price-`+ value['ticket_id'] + `" >` + value['price'] + `</b>د.إ </h4>
							              </div>
							            </div>
			                                
			                                
			                                 
				
				                        `);
                        });

                    },
                });


                event_ticket_qty_add_method();
                event_ticket_qty_sub_method();
                event_ticket_price_calcu_method();
                
                

                $('#cart-popup').modal({
                    keyboard: false,
                    show: true,
                    focus: true
                })
                
                }

            });
        });

    };
    //end	



    // Start  
    var selected_event_ID_method = () => {

        // Start

        var selected_event_id = document.querySelectorAll('#selected-event-ID');

        selected_event_id.forEach(element => {

            element.addEventListener("click", (e) => {
                var event_id = e.currentTarget.getAttribute("data-event-id");
                

                $('#selected_event_id').val(event_id);


                $('.popover').popover('hide');


                var car_tlist_container = document.querySelectorAll('.cart-list');

                car_tlist_container.forEach(element => {

                    element.remove();

                });



                $.ajax({
                    url: "/event/details",
                    type: 'POST',
                    async: false,
                    data: {
                        'event_id': event_id,
                    },
                    success: function (result) {
                        var resultJSON = jQuery.parseJSON(result);
                        $('.cart-list-container').empty();

                        $.each(resultJSON, function (key, value) {
                            $('.cart-list-container').append(`
				
			                                
			                             <div class="cart-list">
							              <div class="cart-left-info">
							
							                <h5>`+ value['name'] + `
							                  <span> <label class=" chipsone">`+ value['platform'] + `</label> <label class="chipsone">Event</label></span>
							
							                </h5>
							                
							                  <h6>
							                	`+ value['ticket_name'] + `
							                  </h6>
							
							
							                <div class="eventinfos">
							                  <label><i class="fas fa-map-marker-alt"></i> `+ value['location'] + ` </label>
							                  <label><i class="far fa-clock"></i> `+ value['duration'] + ` </label>
							                  <label><i class="far fa-calendar-minus"></i>`+ value['event_date'] + `</label>
							                  <label><i class="far fa-user"></i> `+ value['facilitator'] + `</label>
							                </div>
							              </div>
							              
							              </div>
							            </div>
			                                
			                                
			                                 
				
				                        `);
                        });

                    },
                });
                
                
                
				$(".event-gift-info").hide();

                //event_ticket_qty_add_method();
                //event_ticket_qty_sub_method();
                //event_ticket_price_calcu_method();
                
              $("#gift-event-myself").prop('checked', true);
			  $("#gift-event-other").prop('checked', false);
			  $("#receiver_name").removeClass("reservation-input");
			  $("#receiver_email").removeClass("reservation-input");
			  $("#receiver_mobile").removeClass("reservation-input");
                
            selected_event_reserve_method()
                
            $('#event-reservation-popup').modal({
		            keyboard: false,
		            show: true,
		            focus: true
		        })
                
                
           /*

                $('#cart-popup').modal({
                    keyboard: false,
                    show: true,
                    focus: true
                })
                
                
            
                
            */

            });
        });

    };
    //end	

    var eventRenderAppend = (date) => {
        lastRequestedDate = date;
        $.ajax({
            url: "/theme/upcoming_event/render",
            type: "POST",
            async: false,
            data: {
                date: date,
                calendar_domain: $('#calendar_domain').val(),
            },
            success: function (result) {
                var resultJSON = jQuery.parseJSON(result);
                $("#upComingCalendarEventsContainer").empty();
                $("#upComingCalendarEventsContainer").append(`<div class="col-12 text-center upComingCalendarEventsContainer-rm-htxt" style="min-height:60px"><h3>No Events</h3></div>`);
                $.each(resultJSON, function (key, value) {
                    const event = value;
                    const filterLocation = $('#calendar-multiselect-filter-location').val()
                    const filterService = $('#calendar-multiselect-filter-service').val()
                    const filterEventType = $("select[name*='event_type']").val()

                    // switch ($('#calendar_domain').val()) {
                    //     case 'no_paid':
                    //         payment_status = '<img class="EventCardPaymentStatus" src="/ppts_mindbody_calendar/static/assets/img/unpaid-icon.png" border="0" alt="">'
                    //         break;
                    // }

                    let isValidEvent = false;
                    if (filterEventType === 'all' || event.type_event_str === filterEventType) {
                        if (filterService.length && filterLocation.findIndex(value => value == event.location_id) !== -1 && filterService.length && filterService.findIndex(value => value == event.service_category_id) !== -1) {
                            // eventJSON.push(event);
                            isValidEvent = true;
                        } else if (!filterLocation.length && filterService.length && filterService.findIndex(value => value == event.service_category_id) !== -1) {
                            // eventJSON.push(event);
                            isValidEvent = true;
                        } else if (!filterService.length && filterLocation.length && filterLocation.findIndex(value => value == event.location_id) !== -1) {
                            // eventJSON.push(event);
                            isValidEvent = true;
                        } else if (!filterLocation.length && !filterService.length) {
                            isValidEvent = true;
                        }
                    }

                    if (isValidEvent) {
                        $('.upComingCalendarEventsContainer-rm-htxt').remove();
                        $("#upComingCalendarEventsContainer").append(`<div class="calenday-eventlist-item" data-emp-id="` + value.employee_ids + `" data-service-id="` + value.service_category_id + `">
                        <div class="cal-event-img">
                        <label class="filtercatlabel">` + value.type + `</label>
                        <img src="`+ value.image + `" />
                        <div class="eventtag-imgoverlay chips-cont">
                        
                        <label class="training chipsone">` + value.event_category + `
                        </label><label class="meditation chipsone">` + value.sub_category + `</label>
                        </div>
                        </div>
                        <div class="eventfullinfos">
                        <div class="event-typoingo">
                        <div class="eventtitleinfos">
                        <h5><a href="` + value.evt_url + `">` + value.name + `</a></h5> <label class="training chipsone">` + value.event_category + `
                        </label><label class="meditation chipsone">` + value.sub_category + `</label>
                        </div>
                        <div class="eventinfos">
                        <label> <img src="/ppts_website_theme/static/src/img/location-icon.svg" width="24px" height="24px">` + value.location + `</label>
                        <label><img src="/ppts_website_theme/static/src/img/calendar-icon.svg" width="24px" height="24px">` + value.date + `</label>
                        <label><img src="/ppts_website_theme/static/src/img/time-icon.svg" width="24px" height="24px">` + value.time + `</label>
                        <label><img src="/ppts_website_theme/static/src/img/person-icon.svg" width="24px" height="24px"> 
                            <a style="text-decoration: underline !important;" href="/team/therapists/`+ value.facilitator_id + `">` + value.facilitator + `</a>
                        </label>
                        </div>
                        <div class="calc-list-event-price"><span>` + value.price + `</span><span> AED</span> </div>
                        </div>
                        <div class="event-listbtn">
                        `+ value.book_btn + `
                        </div>
                        </div>
                        </div>`);
                    }

                });
            },
        });


        selected_event_ID_method();

        switch ($('#calendar_domain').val()) {
            case 'team_therapist':
                $(".calenday-eventlist-item").each(function () {
                    const arr = $(this).data('emp-id');
                    if (arr.includes(parseInt($('#calendar_employee_id').val()))) {
                        $(this).removeClass('d-none');
                    } else {
                        $(this).addClass('d-none');
                    }
                });
                break;
            case 'meditation':
                $(".calenday-eventlist-item").each(function () {
                    if ($('#calendar_employee_id').val() === String($(this).data('service-id'))) {
                        $(this).removeClass('d-none');
                    } else {
                        $(this).addClass('d-none');
                    }
                });
                break;
        }


    };

    setTimeout(() => {
        var popOverSettings = {
            // placement: "bottom",
            container: "body",
            html: true,
            selector: '[rel="upComingEventCalendarPopover"]',
            title: () => {
                const selectedDate = event.target.getAttribute("data-date");
                const div = document.createElement("div");
                div.classList.add("popover-container-header");
                let date = new Date(selectedDate);
                let popoverHeader = `
          <span class="">` + date.getDate() + " " + monthStringArrmS[date.getMonth()] +
                    ", " + weekStringTwoStringArr[date.getDay()] + `</span>
          <a id="upComingEventCalendar-popover-close" class="calpopoverclose">X</a>`;
                div.innerHTML += popoverHeader;
                return div;
            },
            content: () => {
                const selectedDate = event.target.getAttribute("data-date");
                const selectedType = event.target.getAttribute("data-type");
                let selectedDateEvents = monthViewEventsDisc[selectedDate];
                if (selectedType === 'dayGridWeek') {
                    const val = new Array(...weekViewEventsDisc[selectedDate]);
                    selectedDateEvents = val.splice(0, (val.length - gridWeekViewCountLimit));
                }
                const div = document.createElement("div");
                div.classList.add("popover-container-content");
                for (let selectedDateEvent of selectedDateEvents) {
                    const eventData = selectedDateEvent.event;
                    let item = `<div class="colored-event-card-container" style="background: ` + eventData._def.extendedProps.background_color + `; border: 1px solid ` + eventData._def.extendedProps.background_color + `;">
                        <div class="event-card-header">
                            <span class="event-type" style="color:`+ colorShade(rgbaToHex(eventData._def.extendedProps.background_color), -70) + `;" title="` + eventData._def.extendedProps.event_category + `"> ` + eventData._def.extendedProps.event_category + ` </span>
                            <span class="therapestlocation"> ` + eventData._def.extendedProps.location_abbreviation + ` </span>
                        </div>
                        <div class="event-card-body">
                            <span class="timeevent">` + eventData._def.extendedProps.time + `</span>
                            <h6 class="eventheading" title="` + eventData._def.extendedProps.name + `"><a class="a-clr" href="` + eventData._def.extendedProps.evt_url + `">` + eventData._def.extendedProps.name + `</a></h6>

                            <div class="eventheading-priceitems">
                        <span class="user" title="` + eventData._def.extendedProps.facilitator + `">` + eventData._def.extendedProps.facilitator + `</span>
                        <span class="priceevent" title="` + eventData._def.extendedProps.price + ` AED">` + eventData._def.extendedProps.price + ` AED</span></div>
                        </div>
                        <div class="event-card-footer">
                            <a class="event-enquire" href="#book_free_apt_snippet">Enquire Now</a>
                            <a class="eventbook" id="selected-event-ID" data-event-id="`+ eventData._def.extendedProps.event_id + `">book now</a>
                        </div>
                        </div>`;
                    div.innerHTML += item;
                }
                setTimeout(() => {
                    const popoverArr = document.getElementsByClassName('popover');

                    selected_event_ID_method();

                    for (let i = 0; i < popoverArr.length; i++) {
                        popoverArr[i].className += " event-popover-card";
                    }
                });

                //selected_event_ID_method();
                $("#upComingEventCalendar-popover-close").click();
                return div;
            },
        };

        $("#upComingEventCalendar").popover(popOverSettings);



        $(document).on("click", "#upComingEventCalendar-popover-close", () => {
            $('.popover').popover('hide');
        });

    }, 3000);

    var calendar = new FullCalendar.Calendar(calendarEl, {
        plugins: ["dayGrid", "dayGridMonth", "dayGridWeek", "list"],
        defaultView: "dayGridWeek",
        // eventLimit: 2,
        columnHeaderFormat: {
            day: "numeric",
            month: "long",
            weekday: "short",
            omitCommas: true,
        },
        timeZone: 'local',
        columnHeaderText: function (date) {
            if (selectedView === "grid" && selectedViewType === "month") {
                if (countDate <= 7) {
                    if (countDate === 7) {
                        displayDate =
                            monthStringArrmSHalf[date.getMonth()] + " " + date.getFullYear();
                        document.getElementById("currentCalendarWeekRange").innerText =
                            displayDate;
                        countDate = 1;
                    } else {
                        countDate++;
                    }
                }
                return monthStringArrmS[date.getMonth()] + " " + date.getFullYear();
            } else {
                if (countDate === 1) {
                    displayDate =
                        (date.getDate() > 9 ? date.getDate() : "0" + date.getDate()) +
                        " - ";
                }
                if (countDate <= 7) {
                    if (countDate === 7) {
                        displayDate +=
                            (date.getDate() > 9 ? date.getDate() : "0" + date.getDate()) +
                            " " +
                            monthStringArrmSHalf[date.getMonth()];
                        document.getElementById("currentCalendarWeekRange").innerText =
                            displayDate;
                        countDate = 1;
                    } else {
                        countDate++;
                    }
                }
                return (                   
                    (date.getDate() > 9 ? date.getDate() : "0" + date.getDate()) +
                    " " +
                    monthStringArrmS[date.getMonth()] +
                    ", " +
                    weekStringArrmS[date.getDay()]                   
                );
            }
        },
        dayRender: (info) => {
            if (selectedView === "grid" && selectedViewType === "month") {
                const item =
                    info.date.getDate() +
                    " " +
                    monthStringArrmS[info.date.getMonth()] +
                    ", " +
                    weekStringTwoStringArr[info.date.getDay()];
                const div = document.createElement("div");
                // span.innerHtml(item);
                div.classList.add("month-fc-day-number");
                if (info.el.classList.value.search("fc-other-month") >= 0) {
                    div.classList.add("other-month-date");
                }
                div.innerHTML = item;
                info.el.appendChild(div);
            }
            // info;
            return "";
        },
        listDayFormat: (info) => {
            const date = info.date.marker;
            return weekStringTwoStringArr[date.getDay()];
        },
        listDayAltFormat: (info) => {
            const date = info.date.marker;
            return date.getDate() > 9 ? date.getDate() : "0" + date.getDate();
        },

        viewSkeletonRender: (info) => {
            console.log('viewSkeletonRender', info)
            // $('.fc-view.fc-dayGridMonth-view.fc-dayGrid-view  div.fc-content-skeleton > table > tbody > tr').slice(1).remove();
        },
        eventRender: (eventInfo) => {
            const filterLocation = $('#calendar-multiselect-filter-location').val()
            const filterService = $('#calendar-multiselect-filter-service').val()
            const filterEventType = $("select[name*='event_type']").val()
            const event = eventInfo.event.extendedProps

            let isValidEvent = false;
            if (filterEventType === 'all' || event.type_event_str === filterEventType) {
                if (filterService.length && filterLocation.findIndex(value => value == event.location_id) !== -1 && filterService.length && filterService.findIndex(value => value == event.service_category_id) !== -1) {
                    // eventJSON.push(event);
                    isValidEvent = true;
                } else if (!filterLocation.length && filterService.length && filterService.findIndex(value => value == event.service_category_id) !== -1) {
                    // eventJSON.push(event);
                    isValidEvent = true;
                } else if (!filterService.length && filterLocation.length && filterLocation.findIndex(value => value == event.location_id) !== -1) {
                    // eventJSON.push(event);
                    isValidEvent = true;
                } else if (!filterLocation.length && !filterService.length) {
                    isValidEvent = true;
                }
            }
            if (isValidEvent) {
                if (selectedView === "grid" && selectedViewType === "month") {
                    const startsAt = new Date(eventInfo.event.start);
                    const eventStart =
                        startsAt.getFullYear() +
                        "-" +
                        (startsAt.getMonth() + 1 > 9 ?
                            startsAt.getMonth() + 1 :
                            "0" + (startsAt.getMonth() + 1)) +
                        "-" +
                        (startsAt.getDate() > 9 ?
                            startsAt.getDate() :
                            "0" + startsAt.getDate());
                    if (!monthViewEventsDisc[eventStart]) {
                        monthViewEventsDisc[eventStart] = [eventInfo];
                    } else if (monthViewEventsDisc[eventStart]) {
                        monthViewEventsDisc[eventStart].push(eventInfo);
                    }
                    console.log('eventInfo.el.getElementsByTagName("div") ===> ', eventInfo.el)
                    // const exitingDiv = eventInfo.el.getElementsByTagName("div")[0];
                    const exitingDiv = eventInfo.el.getElementsByTagName("div")[0];

                    const eventText =
                        monthViewEventsDisc[eventStart].length === 1 ?
                            monthViewEventsDisc[eventStart].length + " event" :
                            monthViewEventsDisc[eventStart].length + " events";

                    console.log('count Test');

                    const item =
                        `
                    <div class="event-text" data-date=` +
                        eventStart +
                        ` rel="upComingEventCalendarPopover">` +
                        eventText +
                        `</div>
                    <div class="event-seeall-text " data-date=` +
                        eventStart +
                        ` rel="upComingEventCalendarPopover">
                    See All</div>`;

                    if (monthViewEventsDisc[eventStart].length == 1) {
                        exitingDiv.classList.add("event-text-container-month-view");
                        exitingDiv.innerHTML = item;
                    } else {
                        const currentDateFirstItem = monthViewEventsDisc[eventStart][0];
                        const currentDateFirstItemDiv =
                            currentDateFirstItem.el.getElementsByTagName("div")[0];
                        currentDateFirstItemDiv.innerHTML = item;
                        eventInfo.el.classList.add("display-none");
                    }

                } else if (selectedView === "grid" && selectedViewType === "week") {
                    if (weekViewType === "dayGridWeek") {
                        const startsAt = new Date(eventInfo.event.start);
                        const eventStart = startsAt.getFullYear() + "-" +
                            (startsAt.getMonth() + 1 > 9
                                ? startsAt.getMonth() + 1
                                : "0" + (startsAt.getMonth() + 1)) +
                            "-" +
                            (startsAt.getDate() > 9
                                ? startsAt.getDate()
                                : "0" + startsAt.getDate());
                        if (!weekViewEventsDisc[eventStart]) {
                            weekViewEventsDisc[eventStart] = [eventInfo];
                        } else if (weekViewEventsDisc[eventStart]) {
                            weekViewEventsDisc[eventStart].push(eventInfo);
                        }
                        if (weekViewEventsDisc[eventStart].length > gridWeekViewCountLimit) {
                            if (weekViewEventsDisc[eventStart].length > gridWeekViewCountLimit + 1) {
                                eventInfo.el.classList.add("display-none");
                            }
                            const eventText = 'See ' + (weekViewEventsDisc[eventStart].length - gridWeekViewCountLimit) + ' more events';
                            const item =
                                `<div style=" text-decoration: underline; margin: 10px;">
                                  <div class="event-text" data-type="dayGridWeek" data-date=` +
                                eventStart +
                                ` rel="upComingEventCalendarPopover">` +
                                eventText +
                                `</div></div>`;
                            const currentDateFirstItem = weekViewEventsDisc[eventStart][gridWeekViewCountLimit];
                            const currentDateFirstItemDiv =
                                currentDateFirstItem.el.getElementsByTagName("div")[0];
                            currentDateFirstItemDiv.innerHTML = item;
                        } else {
                            const exitingDiv = eventInfo.el.getElementsByTagName("div")[0];
                            let item = `
                            <div class="colored-event-card-container" style="background: ` + eventInfo.event.extendedProps.background_color + `; border: 1px solid ` + eventInfo.event.extendedProps.background_color + `;">
                            <div class="event-card-header">
                                <span class="event-type" style="color:`+ colorShade(rgbaToHex(eventInfo.event.extendedProps.background_color), -70) + `;" title="` + eventInfo.event.extendedProps.event_category + `"> ` + eventInfo.event.extendedProps.event_category + ` </span>
                                <span class="therapestlocation" title="` + eventInfo.event.extendedProps.location_abbreviation + `"> ` + eventInfo.event.extendedProps.location_abbreviation + ` </span>
                            </div>
                            <div class="event-card-body">
                                <span class="timeevent">` + eventInfo.event.extendedProps.time + `</span>
                                <h6 class="eventheading" title="` + eventInfo.event.extendedProps.name + `"><a class="a-clr" href="` + eventInfo.event.extendedProps.evt_url + `">` + eventInfo.event.extendedProps.name + `</a></h6>
    
                                <div class="eventheading-priceitems">
                            <span class="user" title="` + eventInfo.event.extendedProps.facilitator + `">` + eventInfo.event.extendedProps.facilitator + `</span>
                            <span class="priceevent" title="` + eventInfo.event.extendedProps.price + ` AED">` + eventInfo.event.extendedProps.price + ` AED</span></div>
                            </div>
                            <div class="event-card-footer">
                                <a class="event-enquire" href="#book_free_apt_snippet">Enquire Now</a>
                                <a class="eventbook" id="selected-event-ID" data-event-id="`+ eventInfo.event.extendedProps.event_id + `">book now</a>
                            </div>
                            </div>`;
                            exitingDiv.classList.add("event-text-container-week-view");
                            exitingDiv.innerHTML = item;
                        }
                    } else if (weekViewType === 'listWeek') {
                        const exitingTr = eventInfo.el.getElementsByTagName("td");
                        exitingTr[0].classList.add("event-text-container-list-week-view");
                        exitingTr[1].classList.add("display-none");
                        exitingTr[2].classList.add("display-none");
                        let item = `
                        <div class="colored-event-card-container" style="background: ` + eventInfo.event.extendedProps.background_color + `; border: 1px solid ` + eventInfo.event.extendedProps.background_color + `;">
                        <div class="event-card-header">
                            <span class="event-type" style="color:`+ colorShade(rgbaToHex(eventInfo.event.extendedProps.background_color), -70) + `;" title="` + eventInfo.event.extendedProps.event_category + `"> ` + eventInfo.event.extendedProps.event_category + ` </span>
                            <span class="therapestlocation" title="` + eventInfo.event.extendedProps.location_abbreviation + `"> ` + eventInfo.event.extendedProps.location_abbreviation + ` </span>
                        </div>
                        <div class="event-card-body">
                            <span class="timeevent">` + eventInfo.event.extendedProps.time + `</span>
                            <h6 class="eventheading" title="` + eventInfo.event.extendedProps.name + `"><a class="a-clr" href="` + eventInfo.event.extendedProps.evt_url + `">` + eventInfo.event.extendedProps.name + `</a></h6>

                            <div class="eventheading-priceitems">
                        <span class="user" title="` + eventInfo.event.extendedProps.facilitator + `">` + eventInfo.event.extendedProps.facilitator + `</span>
                        <span class="priceevent" title="` + eventInfo.event.extendedProps.price + ` AED">` + eventInfo.event.extendedProps.price + ` AED</span></div>
                        </div>
                        <div class="event-card-footer">
                            <a class="event-enquire" href="#book_free_apt_snippet">Enquire Now</a>
                            <a class="eventbook" id="selected-event-ID" data-event-id="`+ eventInfo.event.extendedProps.event_id + `">book now</a>
                        </div>
                        </div>`;
                        exitingTr[0].innerHTML = item;



                    }
                }
            } else {
                return false;
            }

            selected_event_ID_method();

        },
        header: {
            left: "",
            center: "",
            right: "",
        },
        views: {
            dayGridWeek: {
                dayHeaderFormat: {
                    day: "numeric",
                    month: "long",
                    weekday: "short",
                    omitCommas: true,
                },
                // eventLimit: 2
            },
            // dayGridMonth: {
            //     eventLimit: 1 // adjust to 6 only for timeGridWeek/timeGridDay
            // },
        },
        events: eventJSON,
    });

    calendar.render();

    $('#calendar-multiselect-filter-location-m').on('change', function () {
        $('#calendar-multiselect-filter-location').val($('#calendar-multiselect-filter-location-m').val())
    });

    $('#calendar-multiselect-filter-service-m').on('change', function () {
        $('#calendar-multiselect-filter-service').val($('#calendar-multiselect-filter-service-m').val())
    });

    $('#calendar-multiselect-filter-location, #calendar-multiselect-filter-location-m, #calendar-multiselect-filter-service, #calendar-multiselect-filter-service-m, select[name*="event_type"]').on('change', function () {
        if (selectedView === 'list') {
            eventRenderAppend(lastRequestedDate)
        } else {
            monthViewEventsDisc = {};
            weekViewEventsDisc = {};
            calendar.rerenderEvents();
        }

    });

    $("button#ClnToggleEventType").click(function () {
        $(".calendar-header-one-left > .filter-buttons-lists button").removeClass('selectedbtn');
        $(this).addClass('selectedbtn');
        $('select[name="event_type"]').val($(this).attr('event-data'));
        if (selectedView === 'list') {
            eventRenderAppend(lastRequestedDate)
        } else {
            monthViewEventsDisc = {};
            weekViewEventsDisc = {};
            calendar.rerenderEvents();
        }
    });


    $("#upComingEventDatepicker")
        .datepicker({
            autoclose: true,
            todayHighlight: true,
        })
        .on("changeDate", (e) => {
            if (e?.date) {
                monthViewEventsDisc = {};
                weekViewEventsDisc = {};
                var d = new Date(e.date);
                calendar.gotoDate(d);
                active_selected_date = new Date(e.date);
                var month = active_selected_date.getMonth() + 1;
                var day = active_selected_date.getDate();
                var output =
                    active_selected_date.getFullYear() +
                    "-" +
                    (("" + month).length < 2 ? "0" : "") +
                    month +
                    "-" +
                    (("" + day).length < 2 ? "0" : "") +
                    day;

                let outputl = (("" + day).length < 2 ? "0" : "") + day + '.' + (("" + month).length < 2 ? "0" : "") + month + '.' + active_selected_date.getFullYear()
                $("#upComingEventDatepicker > input").val(outputl);
                handleDateClick(output);
                eventRenderAppend(output);
                $('.datepicker').hide();
            }
        }).on('hide', function (e) {
            active_selected_date = new Date();
            var month = active_selected_date.getMonth() + 1;
            var day = active_selected_date.getDate();
            let outputl = (("" + day).length < 2 ? "0" : "") + day + '.' + (("" + month).length < 2 ? "0" : "") + month + '.' + active_selected_date.getFullYear()
            $("#upComingEventDatepicker > input").val(outputl);
        });

    const initialListAction = () => {

        $("#upComingEventCalendar > div.fc-header-toolbar")
            .children()
            .not(":first")
            .remove();
        $("#upComingEventCalendar > div.fc-view-container")
            .children()
            .not(":first")
            .remove();
        var active_date = active_selected_date || new Date();
        if (active_selected_date) {
            calendar.gotoDate(active_selected_date);
        }
        var month = active_date.getMonth() + 1;
        var day = active_date.getDate();
        let output =
            active_date.getFullYear() +
            "-" +
            (("" + month).length < 2 ? "0" : "") +
            month +
            "-" +
            (("" + day).length < 2 ? "0" : "") +
            day;
        handleDateClick(output);
        // let outputl =
        //     (("" + day).length < 2 ? "0" : "") +
        //     day +
        //     "." +
        //     (("" + month).length < 2 ? "0" : "") +
        //     month +
        //     "." + active_date.getFullYear();
        let outputl = (("" + day).length < 2 ? "0" : "") + day + '.' + (("" + month).length < 2 ? "0" : "") + month + '.' + active_date.getFullYear()

        // + "." + (("" + month).length < 2 ? "0" : "") + month + "." + active_selected_date.getFullYear();
        $("#upComingEventDatepicker > input").val(outputl);
        $("#upComingCalendarEventsContainer").empty();
        eventRenderAppend(output);

        $(".fc-day-header").click(function () {
            $(".fc-day-header").removeClass("dateactivebtn");
            $(this).addClass("dateactivebtn");
            var selected_date = $(this).attr("data-date");
            eventRenderAppend(selected_date);
        });

        $(".o_default_snippet_text").click(function () {
            $(".o_default_snippet_text").removeClass("selectedbtn");
            $(this).addClass("selectedbtn");
        });

        $("#upComingEventCalendar>div.fc-view-container>div>table>tbody").addClass("display-none");
    };

    setTimeout(() => {
        initialListAction();
        selectedView = "list";
        $("#listViewForCal").addClass("selectedbtn");
        $("#calendar-mainwrap").addClass("listviewcss");
        $("#gridViewForCal").removeClass("selectedbtn");

        $('#upComingEventCalendar .fc-toolbar.fc-header-toolbar').slice(1).remove();
        $('#upComingEventCalendar .fc-view-container').slice(1).remove();
    }, 100);

    document
        .getElementById("currentCalendarWeekLeftArrow")
        .addEventListener("click", () => {
            monthViewEventsDisc = {};
            weekViewEventsDisc = {};
            calendar.prev();
            if (selectedView === 'list') {
                $(".fc-day-header").click(function () {
                    $(".fc-day-header").removeClass("dateactivebtn");
                    $(this).addClass("dateactivebtn");
                    var selected_date = $(this).attr("data-date");
                    eventRenderAppend(selected_date);
                });
            }

        });

    document
        .getElementById("currentCalendarWeekRightArrow")
        .addEventListener("click", () => {
            monthViewEventsDisc = {};
            weekViewEventsDisc = {};
            calendar.next(); // call method
            if (selectedView === 'list') {
                $(".fc-day-header").click(function () {
                    $(".fc-day-header").removeClass("dateactivebtn");
                    $(this).addClass("dateactivebtn");
                    var selected_date = $(this).attr("data-date");
                    eventRenderAppend(selected_date);
                });
            }
        });

    [document.getElementById("upComingEventDateViewTypeWeek"), document.getElementById("upComingEventDateViewTypeWeekT")].forEach(item => {
        item.addEventListener("click", () => {
            monthViewEventsDisc = {};
            weekViewEventsDisc = {};
            selectedViewType = "week";
            $(".evnt-clss-view-tog-model #selectedView").empty();
            $(".evnt-clss-view-tog #selectedView").empty();
            // $("#selectedView").empty();
            $(".evnt-clss-view-tog-model #selectedView").append("Week");
            $(".evnt-clss-view-tog #selectedView").append("Week");
            // $("#selectedView").append("Week");
            upComingEventDateViewTypeWeekAction();
        });
    });

    [document.getElementById("upComingEventDateViewTypeMonth"), document.getElementById("upComingEventDateViewTypeMonthT")].forEach(item => {
        item.addEventListener("click", () => {
            monthViewEventsDisc = {};
            weekViewEventsDisc = {};
            selectedViewType = "month";
            $(".evnt-clss-view-tog-model #selectedView").empty();
            $(".evnt-clss-view-tog #selectedView").empty();
            // $("#selectedView").empty();
            // $("#selectedView").append("Month");
            $(".evnt-clss-view-tog-model #selectedView").append("Month");
            $(".evnt-clss-view-tog #selectedView").append("Month");
            $("#calendar-mainwrap").addClass("month-webview");
            $("#calendar-mainwrap").removeClass("weekly-mobileview");
            $("#calendar-mainwrap").removeClass("weekly-webview");
            calendar.changeView("dayGridMonth");
        });
    });


    [document.getElementById("gridViewForCal"), document.getElementById("gridViewForCalModel")].forEach(item => {
        item.addEventListener("click", () => {
            $(".evnt-clss-view-tog").removeClass("display-none");
            $(".evnt-clss-view-tog-model").removeClass("display-none");

            $("#listViewForCal").removeClass("selectedbtn");
            $("#listViewForCalModel").removeClass("selectedbtn");

            $("#calendar-mainwrap").removeClass("listviewcss");
            $("#calendar-mainwrap").addClass("gridviewcss");
            $("#calendar-mainwrap").addClass("month-webview");
            $("#calendar-mainwrap").removeClass("weekly-mobileview");
            $("#calendar-mainwrap").removeClass("weekly-webview");

            $("#gridViewForCal").addClass("selectedbtn");
            $("#gridViewForCalModel").addClass("selectedbtn");

            $("#upComingEventDatepicker").addClass("display-none");
            $("#upComingEventCalendar>div.fc-view-container>div>table>tbody").removeClass("display-none");

            monthViewEventsDisc = {};
            weekViewEventsDisc = {};
            selectedView = "grid";
            selectedViewType = "month";
            $("#upComingCalendarEventsContainer").empty();
            $(".evnt-clss-view-tog-model #selectedView").empty();
            $(".evnt-clss-view-tog #selectedView").empty();
            // $("#selectedView").empty();
            $(".evnt-clss-view-tog-model #selectedView").append("Month");
            $(".evnt-clss-view-tog #selectedView").append("Month");
            // $("#selectedView").append("Month");
            $('.calendar-weeklybutton').css('display', 'block');
            calendar.changeView("dayGridMonth");
        });

    });

    [document.getElementById("listViewForCal"), document.getElementById("listViewForCalModel")].forEach(item => {

        item.addEventListener("click", () => {
            $(".evnt-clss-view-tog").addClass("display-none");
            $(".evnt-clss-view-tog-model").addClass("display-none");
            $("#calendar-mainwrap").addClass("listviewcss");
            $("#calendar-mainwrap").removeClass("gridviewcss");
            $("#calendar-mainwrap").removeClass("month-webview");
            $("#calendar-mainwrap").removeClass("weekly-mobileview");
            $("#calendar-mainwrap").removeClass("weekly-webview");

            $("#listViewForCal").addClass("selectedbtn");
            $("#listViewForCalModel").addClass("selectedbtn");
            $("#upComingEventDatepicker").removeClass("display-none");
            $("#gridViewForCal").removeClass("selectedbtn");
            $("#gridViewForCalModel").removeClass("selectedbtn");
            $("#calenderViewSelectOption").addClass("display-none");
            $("#upComingEventCalendar>div.fc-view-container>div>table>tbody").addClass("display-none");
            // $('.calendar-weeklybutton').css('display', 'none');
            selectedView = "list";
            calendar.changeView("dayGridWeek");
            initialListAction();
        });

        $('#calendar-mbl-filter').on('click', function () {
            $('#outteamfilter').toggleClass("activeourteamfilterpopup");
            $('#outteamfilter').toggleClass("modal left fade show");
        });
        $('#calendar-mbl-filter').on('click', function () {
            $('#outteamfilter').toggleClass("activeourteamfilterpopup");
        });

    });

});


var GetPDFCalendar = () => {
    var HTML_Width = $(".upcomingsection").width();
    var HTML_Height = $(".upcomingsection").height();
    var top_left_margin = 15;
    var PDF_Width = HTML_Width + (top_left_margin * 2);
    var PDF_Height = (PDF_Width * 1.5) + (top_left_margin * 2);
    var canvas_image_width = HTML_Width;
    var canvas_image_height = HTML_Height;
    var totalPDFPages = Math.ceil(HTML_Height / PDF_Height) - 1;

    html2canvas($(".upcomingsection")[0]).then(function (canvas) {
        var imgData = canvas.toDataURL("image/jpeg", 1.0);
        var pdf = new jsPDF('p', 'pt', [PDF_Width, PDF_Height]);
        pdf.addImage(imgData, 'JPG', top_left_margin, top_left_margin, canvas_image_width, canvas_image_height);
        for (var i = 1; i <= totalPDFPages; i++) {
            pdf.addPage(PDF_Width, PDF_Height);
            pdf.addImage(imgData, 'JPG', top_left_margin, -(PDF_Height * i) + (top_left_margin * 4), canvas_image_width, canvas_image_height);
        }
        pdf.save("UpcomingEvents.pdf");
    });
}

var eventAllBookedModal = (event_id) => {
    $.getJSON('/get/event/modal/calendar', {
        'event_id': event_id,
    }).done(function (result) {
        var template = document.getElementById('EventTemplateForModalPreview').innerHTML;
        var compiled_template = Handlebars.compile(template);
        var rendered = compiled_template(result[0]);
        document.getElementById('EventTemplateForModalPreviewContent').innerHTML = rendered;
        $('#event-fullybooked-popup').modal();
    });
}

var eventJoinWaitingList = (event_id) => {
    var template = document.getElementById('event-join-waitinglist-popup-script').innerHTML;
    var compiled_template = Handlebars.compile(template);
    var rendered = compiled_template({ 'event_id': event_id });
    document.getElementById('event-join-waitinglist-popup-scriptContent').innerHTML = rendered;
    $(".modal").modal('hide');
    $('#event-join-waitinglist-popup').modal();
}

 


// $(document).ready(function() {
//     console.log( "ready!" );
//     $(".custom_popover_check").click(function(){
//     alert("ddddd")
//     if ( $("div").hasClass("popover")) {
//             alert("ddddd")
//          $('.popover').popover('hide');
//     }
//   });
// });