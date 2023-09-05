document.addEventListener("DOMContentLoaded", function () {

    var monthStringArrmS = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec",];
    var weekStringArrmS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    var weekStringTwoStringArr = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
    var active_selected_date;
    var calendarEl = document.getElementById("upComingEventCalendar");
    var displayDate = "";
    var countDate = 1;
    var navOpen = true;
    var isAddEventFlowOpen = false;
    var selectedStart = null;
    var selectedEnd = null;
    var resourceAvailableMap = {};
    var resources
    var events
    var isEventPopOverOpen = false;
    var previousEl = null;
    var viewChangeupdate = "resourceTimeGridDay";

    function getFilterDetails() {
        $.ajax({
            url: "/booking_activities/filter/company",
            type: "POST",
            async: false,
            data: {},
            success: function (result) {
                $('.location-filter-drop-down').append(result)
            }
        });

        $.ajax({
            url: "/booking_activities/filter/services",
            type: "POST",
            async: false,
            data: {},
            success: function (result) {
                $('.service-filter-drop-down').append(result)
            }
        });

        $.ajax({
            url: "/booking_activities/filter/instructors",
            type: "POST",
            async: false,
            data: {},
            success: function (result) {
                $('.intructor-filter-drop-down').append(result)
                $('.instructor-single-filter-drop-down').append(result)
            }
        });

        $('#multiselect').multiselect({
            buttonWidth: '140px',
            includeSelectAllOption: true,
            actionsBox: true,
            selectAllText: 'All Instructors',
            allSelectedText: 'All Instructors',
            nonSelectedText: 'All Instructors'
        }).multiselect('selectAll', false).multiselect('updateButtonText');

        $.ajax({
            url: "/booking_activities/filter/instructors",
            type: "POST",
            async: false,
            data: {},
            success: function (result) {
                $('.intructor-filter-drop-down').append(result)
                $('.instructor-single-filter-drop-down').append(result)
                $('#therapist_id').append(result)
            }
        });

    }

    CustomerAptBooking = (therapist_id) => {
        var customer
        $.ajax({
            url: "/booking_activities/filter/customer_detail",
            type: "POST",
            async: false,
            data: {},
            success: function (result) {
                var resultJSON = jQuery.parseJSON(result);
                customer = resultJSON;
            },
        });

        $("#client-advance-search-sidebar").autocomplete({
            source: customer,
            minLength: 1,
            select: function (event, ui) {
                addNewEventFlow()
                $('input[name=client_id]').val(ui.item.id)
                $('input[name=client_name]').val(ui.item.label)
                $('input[name=client_mobile]').val(ui.item.mobile)
                $('input[name=client_email]').val(ui.item.email)
            },
            html: true,
            open: function (event, ui) {
                $(".ui-autocomplete").css("z-index", 1000);
            }
        }).autocomplete("instance")._renderItem = function (ul, item) {
            return $('<li>' +
                '<div style="display: flex;">' +
                '<div>' +
                '<img src="' + item.img + '" style="margin-top: 8px;"/>' +
                '</div>' +
                '<div style="">' +
                '<div style="display: block;line-height: 1;">' +
                '<span style="color:#666;font-weight:bold">' + item.label + '</span><br/>' +
                '<span style="font-size: 10px;">' +
                '<span style="font-size:10px;font-weight:800;">Mobile:</span>' + item.mobile + '</span><br/>' +
                '<span style="font-size: 10px;"><span style="font-size:10px;font-weight:800;">Email:</span>' + item.email + '</span>' +
                '</span>' +
                '</div>' +
                '</div>' +
                '</div>' +
                '</li>').appendTo(ul);
        };

        $.ajax({
            url: "/booking_activities/get/service_categ",
            type: "POST",
            async: false,
            data: { 'therapist_id': therapist_id },
            success: function (result) {
                $('#service_categ_id').find('option').remove()
                $('#service_categ_id').append(result)
            },
        });


    }

    openNav = () => {
        navOpen = true;
        document.getElementById("leftsidenav").style.width = "350px";
        // document.getElementById("rightmain").style.marginLeft = "350px";
    }

    closeNav = () => {
        navOpen = false
        document.getElementById("leftsidenav").style.width = "0px";
        // document.getElementById("rightmain").style.marginLeft = "0px";
    }

    $('#recourcetooglenav').on('click', function () {
        navOpen ? closeNav() : openNav();
    });

    $('#datecalendartootle').on('click', function () {
        $(".datepickercontainer").toggleClass('opendatepicker');
    });

    $.ajax({
        url: "/booking_activities/availability",
        type: "POST",
        async: false,
        data: {},
        success: function (result) {
            var resultJSON = jQuery.parseJSON(result);
            events = resultJSON;
            console.log(events, 'lllllll-------------------');
        }
    });



    getFilterDetails()
    var calendar = new FullCalendar.Calendar(calendarEl, {
        schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
        plugins: ["dayGrid", "interaction", "timeGrid", "resourceDayGrid", "resourceTimeGrid", "timeGridWeek"],
        defaultView: "resourceTimeGridDay",
        selectable: true,
        nowIndicator: true,
        timeZone: 'local',
        timeFormat: 'H:mm',
        slotLabelFormat: {
            hour: 'numeric',
            minute: '2-digit',
            hour12: false
        },
        editable: true,
        eventResourceEditable: false,
        allDaySlot: false,
        eventTimeFormat: { // like '14:30:00'
            hour: '2-digit',
            minute: '2-digit',
            // meridiem: 'short'
            hour12: false
        },
        slotLabelInterval: "00:30",
        minTime: "08:00:00",
        aspectRatio: 1.605,
        refetchResourcesOnNavigate: true,
        columnHeaderFormat: {
            day: "numeric",
            month: "long",
            weekday: "short",
            omitCommas: true,
        },
        columnHeaderText: function (date) {
            if (countDate === 1) {
                displayDate =
                    monthStringArrmS[date.getMonth()] +
                    " " +
                    (date.getDate() > 9 ? date.getDate() : "0" + date.getDate()) +
                    " - ";
            }
            if (countDate <= 7) {
                if (countDate === 7) {
                    displayDate +=
                        (date.getDate() > 9 ? date.getDate() : "0" + date.getDate()) +
                        " " +
                        monthStringArrmS[date.getMonth()];
                    countDate = 1;
                } else {
                    countDate++;
                }
            }
            // const item = `
            // <div id="calenderViewSelectOption" class="calendarresourceheaderdrop">
            // <a class="" type="button" id="dropdownMenuButton"
            // data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            // <i class="fas fa-caret-down"></i> <span id="selectedView"></span>
            // </a>
            // <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
            // <a class="dropdown-item" value="day">Go to week view</a>
            // <a class="dropdown-item" value="day">Edit schedule</a>
            // <a class="dropdown-item" value="day">Add Unavailability</a>
            // <a class="dropdown-item" value="day">Assign Appointment type</a>
            // <a class="dropdown-item" value="week">View Profiles</a>
            // </div>
            // </div>
            // `;
            const div = document.createElement("div");
            div.classList.add("resource-header-title-container");
            // div.innerHTML = item;
            setTimeout(() => {
                const attDate = date.getFullYear() + '-' +
                    (date.getMonth() + 1 > 9 ? date.getMonth() + 1 : "0" + (date.getMonth() + 1)) + '-' +
                    (date.getDate() > 9 ? date.getDate() : "0" + date.getDate())
                const el = $("[data-date='" + attDate + "'");
                // console.log('data res', el);
                el[0].append(div)
            }, 300)
            return (
                (date.getDate() > 9 ? date.getDate() : "0" + date.getDate()) +
                " " +
                monthStringArrmS[date.getMonth()] +
                ", " +
                weekStringArrmS[date.getDay()]
            );
        },
        datesRender: (info) => {
            document.getElementById("currentCalendarWeekRange").innerText = info.view.title;
            var lastViewName;
            if (info.view.type === 'timeGridWeek' && lastViewName != info.view.type) {
                const newEvents = events.filter((event) => event.rendering !== 'background');
                events = newEvents;
                calendar.rerenderEvents();
            }
            lastViewName = info.view.type;

            $('.fc-axis').first().html('<a href="/booking/url/redirect/add_availability_view" data-toggle="tooltip" data-placement="top" title="" data-original-title="Add Availability" class="resourceHeader-label" style="margin-left: -4px;"><i class="fas fa-plus"></i>&nbsp;Add</a>');
            // console.log(info, 'kllklklklk');
        },
        dayRender: (info) => { },
        resourceRender: (renderInfo) => { },
        resourceText: (info) => { },
        eventRender: (eventInfo, element, view) => {
            if (eventInfo.event.rendering === 'background') {
                // console.log('available event', eventInfo);
                resourceAvailableMap[eventInfo.event.extendedProps.extendedPropsRId] = { start: eventInfo.event.start, end: eventInfo.event.end };
                // todo have to move this inside event listing ajax call or after event bind
                // for (let event of events) {
                // if (event.rendering === 'background') {
                // resourceAvailableMap[event.resourceId] = {start: event.start, end: event.end};
                // }
                // }

                // $(eventInfo.el).tooltip({
                //   title: " ",
                //   trigger: 'hover',
                //   placement: 'right',
                //   container: 'body',
                //   template: '<div class="tooltip-template" style="display:block;">' +
                //     '<div class="tooltip-header-event ' + eventInfo.event.extendedProps.tool_tip_className + '">' +
                //     '<p style="font-weight:bold;">' + eventInfo.event.extendedProps.partner_name + '</p>' +
                //     '<span>' + eventInfo.event.extendedProps.partner_seaquence + '</span>' +
                //     '</div><div class="tooltip-body"><div class="tooltip-font-color">' +
                //     '<span style="font-weight:bolder;color:#7F7F7F;font-size:12px;">' + eventInfo.event.extendedProps.tooltip_duration + '</span></div> </div>' +
                //     '<div class="greycontainer"><p>' + eventInfo.event.extendedProps.note + '</p> </div></div></div></div>'
                // });
            } else {
                if (!eventInfo.isMirror) {
                    payment_status = '<img class="EventCardPaymentStatus" src="https://static.mindbodyonline.com/a/asp/adm/images/unpaid-10px.png" border="0" alt="">'
                    var notes = ''
                    if (eventInfo.event.extendedProps.note != '') {
                        notes = '<div class="greycontainer"><p>' + eventInfo.event.extendedProps.note + '</p> </div>'
                    }
                    first_time = '<img src="https://static.mindbodyonline.com/a/asp/adm/images/first-appt-10px.png" style="margin-right: 2px !important;">'
                    resheduled = '<img src="https://static.mindbodyonline.com/a/asp/adm/images/icon-bm-schedule-overlay-calendar.png">'


                    $(eventInfo.el).tooltip({
                        title: " ",
                        trigger: 'hover',
                        placement: 'right',
                        container: 'body',
                        template: '<div class="tooltip-template" style="display:block;">' +
                            '<div class="tooltip-header-event ' + eventInfo.event.extendedProps.tool_tip_className + '">' +
                            '<p style="font-weight:bold;">' + eventInfo.event.extendedProps.partner_name + '</p>' +
                            '<span>' + eventInfo.event.extendedProps.partner_phone + '</span>' +
                            '</div><div class="tooltip-body"><div class="tooltip-font-color">' +
                            '<span style="font-weight:bolder;color:#7F7F7F;font-size:12px;">' + eventInfo.event.extendedProps.tooltip_duration + '</span>' +
                            '<div class="timeforflex" style="color:#7F7F7F;"> <small>' + eventInfo.event.extendedProps.service_category_name + '|' + eventInfo.event.extendedProps.sub_category_name + '</small> <div>' +
                            payment_status + first_time + resheduled + '</div> </div>' +
                            notes + '</div></div></div>'
                    });

                    $(eventInfo.el).popover({
                        title: "title",
                        placement: 'right',
                        trigger: 'manual',
                        container: 'body',
                        template: eventInfo.event.extendedProps.POP_OVER,
                    });
                }
            }

            if (eventInfo.event.classNames.indexOf("event-status-confirm") > -1 || eventInfo.event.classNames.indexOf("event-status-arrive") > -1 || eventInfo.event.classNames.indexOf("event-status-done") > -1 || eventInfo.event.classNames.indexOf("event-status-cancel") > -1 || eventInfo.event.classNames.indexOf("event-status-new") > -1 || eventInfo.event.classNames.indexOf("event-status-no-show") > -1) {
                payment_status = '<img class="EventCardPaymentStatus" src="https://static.mindbodyonline.com/a/asp/adm/images/unpaid-10px.png" border="0" alt="">'
                eventInfo.el.innerHTML = '<div class="fc-content">' +
                    '<div class="eventCard-Subcategory">' + eventInfo.event.extendedProps.sub_category_name + '</div>' +
                    '<div class="eventCard-PartnerName">' + payment_status + eventInfo.event.extendedProps.partner_name + '</div>' +
                    '<div class="eventCard-RoomName">' + eventInfo.event.extendedProps.room_name + '</div>' +
                    '</div><div class="fc-resizer fc-end-resizer"></div>'
            }


            $('.colorbox-booked').text($('.event-status-new').length)
            $('.colorbox-confirmed').text($('.event-status-confirm').length)
            $('.colorbox-arrived').text($('.event-status-arrive').length)
            $('.colorbox-no-show').text($('.event-status-no-show').length)
            $('.colorbox-completed').text($('.event-status-done').length)
            $('.colorbox-cancel').text($('.event-status-cancel').length)

            // console.log(eventInfo)
            if (eventInfo.view.type == "timeGridWeek") {
                return eventInfo.event.extendedProps.extendedPropsRId == $(".instructor-single-filter-drop-down").val() && ['all', eventInfo.event.extendedProps.sub_category_id].indexOf($('.service-filter-drop-down').val()) >= 0 && ['all', eventInfo.event.extendedProps.company_id].indexOf($('.location-filter-drop-down').val()) >= 0
            }
            else {
                if (eventInfo.event.extendedProps.state != 'availability') {
                    return ['all', eventInfo.event.extendedProps.sub_category_id].indexOf($('.service-filter-drop-down').val()) >= 0 && ['all', eventInfo.event.extendedProps.company_id].indexOf($('.location-filter-drop-down').val()) >= 0
                }
            }

        },
        eventClick: (info) => {
            $(info.el).tooltip('disable');
            $('.bs-tooltip-left').removeClass('show');
            $('.bs-tooltip-left').addClass('hide');
            $('.selected-popover-content').popover('hide');
            if (!isEventPopOverOpen) {
                isEventPopOverOpen = true;
                previousEl = info.el;
                setTimeout(() => {
                    $(info.el).popover('show');
                }, 300);
            } else {
                $(previousEl).tooltip('enable');
                $(previousEl).popover('hide');
                setTimeout(() => {
                    $(info.el).popover('show');
                    previousEl = info.el;
                }, 500);
            }
            setTimeout(() => {
                const elements = document.getElementsByClassName("popover-container-close-btn");
                for (let i = 0; i < elements.length; i++) {
                    elements[i].addEventListener('click', () => {
                        $('.bs-tooltip-right , .bs-tooltip-left').removeClass('disabled');
                        $(info.el).tooltip('enable');
                        if (isEventPopOverOpen) {
                            $(previousEl).popover('hide');
                        } else {
                            $(info.el).popover('hide');
                        }
                        isEventPopOverOpen = false;
                    }, false);
                }
            }, 500);
        },
        select: (selectedInfo) => {
            // if (selectedInfo.end.getTime() / 1000 - selectedInfo.start.getTime() / 1000 <= 1800) {

            if ($(selectedInfo.jsEvent.target)) {
                $('.popoverlist').popover('hide');
            }
            $(selectedInfo.jsEvent.target).popover({
                title: "title",
                placement: 'right',
                trigger: 'click',
                container: 'body',
                template: `
            <ul id="context-menu" class="popoverlist selected-popover-content context-menu context-right ctx-right POP-select-option while-event-available">
            <li><a class="popover-container-selected-Value"><i class="fas fa-times"></i></a></li>
            
            <li>
              <a href="#" class="checkout" title="" id="createNewAvailability">
                <span id="popover-edit-today-schedule"> <i class="fas fa-calendar-check"></i> Add Availability</span>
              </a>
            </li>
            
            <li>
              <a href="/booking/url/redirect/add_appointment_form_view" class="checkout" title=""> 
              <span id="popover-edit-today-schedule"> <i class="fas fa-clipboard-list"></i> Add Appointment</span>
              </a>
            </li>
            
            <li>
              <a href="#" class="checkout" id="markAsUnavailable"> 
                <span class="popover-add-availability"> <i class="fas fa-highlighter"></i> Mark as Unavailable </span>
              </a>
            </li>
            </ul>
            `
            });
            $('#addAavailabilityForm').addClass('display-none');
            $('#addAavailabilityForm').addClass('display-none');
            setTimeout(() => {
                $(selectedInfo.jsEvent.target).popover('show')
                const elements = document.getElementsByClassName("popover-container-selected-Value");
                for (let i = 0; i < elements.length; i++) {
                    elements[i].addEventListener('click', () => {
                        $(selectedInfo.jsEvent.target).popover('hide');
                        $('#selectContactForm').addClass('display-none');
                        $('#addUnavailabilityForm').addClass('display-none');

                        $('#bottomContainer').removeClass('display-none');
                        // closeNav()
                    }, false);
                }

                $("#markAsUnavailable").click(function () {
                    $('#selectContactForm').addClass('display-none');
                    $('#addUnavailabilityForm').removeClass('display-none');
                    $("#av_therapist_id").val(selectedInfo.resource.id);
                    $("#av_available_date").val(selectedInfo.startStr.split("T")[0]);
                    $("#av_start_date").val(selectedInfo.startStr.split("T")[0]);
                    $("#av_end_date").val(selectedInfo.endStr.split("T")[0]);
                    $("#av_start_time").val(selectedInfo.startStr.split("T")[1].split(':00+')[0]);
                    $("#av_end_time").val(selectedInfo.endStr.split("T")[1].split(':00+')[0]);
                });

                $("#createNewAvailability").click(function () {
                    $('#selectContactForm').addClass('display-none');
                    $('#addAavailabilityForm').removeClass('display-none');

                    $('#av_therapist_name').val(selectedInfo.resource.title)
                    $('#av_therapist_id').val(selectedInfo.resource.id)
                    $('#av_available_date').val(selectedInfo.startStr.split("T")[0])
                    $("#av_start_time").val(selectedInfo.startStr.split("T")[1].split(':00+')[0]);
                    $("#av_end_time").val(selectedInfo.endStr.split("T")[1].split(':00+')[0]);
                });


            }, 300)
            selectedStart = selectedInfo.start;
            selectedEnd = selectedInfo.end;
            isAddEventFlowOpen = true;
            $('#selectContactForm').removeClass('display-none');
            $('#appointmentClientBTM').removeClass('display-none');
            $('#bottomContainer').addClass('display-none');
            openNav()
            CustomerAptBooking(selectedInfo.resource._resource.id)
            $('#therapist_id').val(selectedInfo.resource._resource.id)
            $('#therapist_id_hidden').val(selectedInfo.resource._resource.id)
            $('#booking_date').val(selectedInfo.startStr.split("T")[0])

        },
        eventAllow: (dropInfo, draggedEvent) => {
            // console.log(dropInfo);
            const d = new Date();
            if (selectedViewType === 'week' || dropInfo.start < d) {
                return false;
            }
            let returnStatus = true
            if (resourceAvailableMap[dropInfo.resource.id]) {
                const availableStart = new Date(resourceAvailableMap[dropInfo.resource.id].start)
                const availableEnd = new Date(resourceAvailableMap[dropInfo.resource.id].end)
                if (dropInfo.start < availableStart || dropInfo.end < availableStart ||
                    dropInfo.start > availableEnd || dropInfo.end > availableEnd) {
                    returnStatus = false;
                }
            } else {
                returnStatus = false;
            }
            for (let event of events) {
                // console.log('evnt dropinfo', dropInfo, event, draggedEvent);
                const eventStart = new Date(event.start);
                const eventEnd = new Date(event.end);
                if (event?.start && event?.end && dropInfo.resource.id == event.resourceId &&
                    event.rendering !== 'background' &&
                    eventStart.getTime() !== new Date(draggedEvent.start).getTime() &&
                    eventEnd.getTime() !== new Date(draggedEvent.end).getTime() &&
                    dropInfo.start.getDate() === eventStart.getDate() && dropInfo.end.getDate() === eventEnd.getDate() &&
                    dropInfo.start.getMonth() === eventStart.getMonth() && dropInfo.end.getMonth() === eventEnd.getMonth() &&
                    dropInfo.start.getFullYear() === eventStart.getFullYear() && dropInfo.end.getFullYear() === eventEnd.getFullYear()) {
                    if ((eventStart <= dropInfo.start && eventEnd > dropInfo.start) ||
                        (eventStart < dropInfo.end && eventEnd >= dropInfo.end)) {
                        returnStatus = false;
                    }
                }
            }
            return returnStatus;
        },
        selectAllow: (selectedInfo) => {
            if (selectedViewType === 'week') {
                return false;
            }
            let returnStatus = false
            if (resourceAvailableMap[selectedInfo.resource.id]) {
                const availableStart = new Date(resourceAvailableMap[selectedInfo.resource.id].start)
                const availableEnd = new Date(resourceAvailableMap[selectedInfo.resource.id].end)
                if (selectedInfo.start < availableStart || selectedInfo.end < availableStart ||
                    selectedInfo.start > availableEnd || selectedInfo.end > availableEnd) {
                    returnStatus = true;
                }
            } else {
                returnStatus = true;
            }
            return returnStatus;
        },
        eventDrop: (dropInfo) => {
            if (selectedViewType === 'week') {
                dropInfo.revert();
            }
        },
        eventResize: (dropInfo) => {
            if (selectedViewType === 'week') {
                dropInfo.revert();
            }
            // else{
            console.log(dropInfo, 'lllllllllllllllll');

            dropInfo_start_time = dropInfo.event.start.toLocaleTimeString([], {
                hourCycle: 'h23',
                hour: '2-digit',
                minute: '2-digit'
            })
            dropInfo_end_time = dropInfo.event.end.toLocaleTimeString([], {
                hourCycle: 'h23',
                hour: '2-digit',
                minute: '2-digit'
            })

            let dateOne = new Date("01/01/2007 " + dropInfo_start_time);
            let dateTwo = new Date("01/01/2007 " + dropInfo_end_time);
            let msDifference = dateTwo - dateOne;
            let minutes = Math.floor(msDifference / 1000 / 60);

            console.log("Minutes between two dates =", minutes);


            let date_re = dropInfo.event.start.toLocaleDateString()

            console.log("Minutes between two dates =", date_re);
            // $.ajax({
            //   url: "/appointment/reschedule/" + String(dropInfo.event.extendedProps.appointment_id),
            //   type: "POST",
            //   async: false,
            //   data: {
            //     'apt_start': dropInfo_start_time,
            //     'apt_end': dropInfo_end_time,
            //     'duration': minutes,
            //   },
            //   success: function (result) { }
            // });
            $('#aptReschedule-model').modal('show');

            $('#re-apt_name').text(dropInfo.event._def.title);
            $('input[name="re_apt_id"]').val(dropInfo.event.extendedProps.appointment_id);
            $('input[name="re_date"]').val(date_re);
            $('input[name="re_start_time"]').val(dropInfo_start_time);
            $('input[name="re_end_time"]').val(dropInfo_end_time);
            $('input[name="re_duration"]').val(minutes);


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
            },
        },
        viewSkeletonRender: function (info) {
            // console.log(info,'view changeeee');
            if (info.view.type == "resourceTimeGridDay") {
                $(".instructor-single-filter-drop-down").addClass("d-none");
                $(".intructor-filter-drop-down").next().removeClass("d-none");
            }
            else {
                $(".instructor-single-filter-drop-down").removeClass("d-none");
                $(".intructor-filter-drop-down").next().addClass("d-none");
            }
        },
        resources: (fetchInfo, successCallback, failureCallback) => {
            // console.log(fetchInfo, 'fetchInfofsefvetchInfo');
            // console.log(fetchInfo.view, 'fetchInfofsefvetchInfo');
             console.log("RESORUCEEEEEEE")
            fetchResourcePy({
                start: fetchInfo.start,
                end: fetchInfo.end,
                timeZone: fetchInfo.timeZone,
            }, function (resources) {

                const filterInstructor = $('.intructor-filter-drop-down').val()
                const updatedResources = resources.filter((resource) => filterInstructor.findIndex(value => value == resource.id) !== -1);
                successCallback(updatedResources);

            });
        },
        events: '/booking_activities/availability'
    });

    setTimeout(() => {
        $('#BookingActivityLoaderCalendar').hide();
        $('#afterLoad').removeClass('d-none');
        calendar.render();
    }, 1000)

    $('.service-filter-drop-down').on('change', function () {
        calendar.rerenderEvents();
    })

    $('.location-filter-drop-down').on('change', function () {
        calendar.rerenderEvents();
    })

    $('.intructor-filter-drop-down').on('change', function () {
        calendar.refetchResources();
    })

    $('.instructor-single-filter-drop-down').on('change', function () {
        calendar.refetchResources();
    })

    resources_go_to_week_view = (res_id) => {
        $('.instructor-single-filter-drop-down').val(res_id);
        $('#upComingEventDateViewTypeWeek').click();
    }

    BookingeventRerender = () => {
        console.log('event rerender');
        BookingFormCancel()
        calendar.rerenderEvents();
    }

    changeClient = () => {
        BookingFormCancel()
    }

    BookingFormCancel = () => {
        $('.popoverlist').popover('hide');
        $('#selectContactForm').addClass('display-none');
        $('#appointmentClientBTM').addClass('display-none');
        $('#bottomContainer').removeClass('display-none');
        $('#AddBookingForm').addClass('display-none');
        $('#addUnavailabilityForm').addClass('display-none');
    }

    function fetchResourcePy({ start, end, timeZone }, successCallback) {

        $.ajax({
            url: "/booking_activities/resources",
            type: "POST",
            async: false,
            data: {
                date: start,
            },
            success: function (result) {
                var resultJSON = jQuery.parseJSON(result);
                resources = resultJSON;
                // if (viewChangeupdate == "resourceTimeGridDay") {
                // if (!resources?.length) {
                //   $('.eventresourcegridcalendar').addClass('d-none');
                //   $('#no-staff-container').removeClass('d-none');
                //   const monthStringArr = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"];
                //   const content = 'None of your staff members are available on ' +
                //     (start.getDate() > 9 ? start.getDate() : '0' + start.getDate()) +
                //     ' ' + monthStringArr[start.getMonth()] + ' ' + start.getFullYear() + '. Schedule availability or change the date range.'
                //   $('#no-staff-container-p').text(content);
                // } else {
                $('.eventresourcegridcalendar').removeClass('d-none');
                $('#no-staff-container').addClass('d-none');
                // }
                // }
                successCallback(resultJSON);
            },
        });
    }

    function unselect_event() {
        $('.popoverlist').popover('hide');
        $('#selectContactForm').addClass('display-none');
        $('#bottomContainer').removeClass('display-none');
        calendar.unselect()
    }

    weekViewAvailabilityBGColor = () => {
        setTimeout(() => {
            const elements = document.getElementsByClassName("fc-bgevent");
            // console.log('fc-bgevent', elements);
            for (let i = 0; i < elements.length; i++) {
                elements[i].style.backgroundColor = 'rgb(245 245 245 / 0%) !important';
            }
        }, 300)
    }

    $("#upComingEventDatepicker").datepicker({
        autoclose: true,
        gotoCurrent: true,
        changeMonth: true,
        changeYear: true,
        numberOfMonths: 2,
        showOtherMonths: true,
        selectOtherMonths: true,
    }).on("input change", function (e) {
        // console.log("Date changed: ", e.target.value);
        $('.popoverlist').popover('hide');
        if (e?.target.value) {
            monthViewEventsDisc = {};
            weekViewEventsDisc = {};
            var d = new Date(e.target.value);
            active_selected_date = new Date(e.target.value);
            calendar.gotoDate(d);
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
            weekViewAvailabilityBGColor();
        }
    });

    const initialListAction = () => {
        active_selected_date = active_selected_date || new Date();
    };

    setTimeout(function () {
        initialListAction();
        selectedViewType = "day";
        $('#AddBookingForm').addClass('display-none');
        $('#editAvailabilityForm').addClass('display-none');
        $('#createContactForm').addClass('display-none');
        $('#selectContactForm').addClass('display-none');
        $('#saveCancelbtm').addClass('display-none');
        $('#addClientbtm').addClass('display-none');
        // $('#bottomContainer').addClass('display-none');
    }, 100);

    service_categ_func = () => {
        $.ajax({
            url: "/booking_activities/get/sub_categ",
            type: "POST",
            async: false,
            data: {
                'therapist_id': $('#therapist_id').val(),
                'service_categ_id': $('#service_categ_id').val(),
            },
            success: function (result) {
                $('#sub_categ_id').find('option').remove()
                $('#sub_categ_id').append(result)
            }
        });
    }

    time_id_func = () => {
        $.ajax({
            url: "/booking_activities/get/time_id",
            type: "POST",
            async: false,
            data: {
                'therapist_id': $('#therapist_id').val(),
                'service_categ_id': $('#service_categ_id').val(),
                'sub_categ_id': $('#sub_categ_id').val(),
            },
            success: function (result) {
                $('#time_id').find('option').remove()
                $('#time_id').append(result)
            }
        });
    }

    time_slot_id_func = () => {
        $.ajax({
            // url: "http://illuminations14stage.pptssolutions.com/booking_activities/filter/instructors",
            url: "/booking_activities/get/time_slot_id",
            type: "POST",
            async: false,
            data: {
                'therapist_id': $('#therapist_id').val(),
                'service_categ_id': $('#service_categ_id').val(),
                'sub_categ_id': $('#sub_categ_id').val(),
                'time_id': $('#time_id').val(),
                'booking_date': $('#booking_date').val(),
            },
            success: function (result) {
                $('#time_slot_id').find('option').remove()
                $('#time_slot_id').append(result)
            }
        });
    }

    room_id_func = () => {
        $.ajax({
            url: "/booking_activities/get/room_id",
            type: "POST",
            async: false,
            data: {
                'therapist_id': $('#therapist_id').val(),
                'service_categ_id': $('#service_categ_id').val(),
                'sub_categ_id': $('#sub_categ_id').val(),
                'time_id': $('#time_id').val(),
                'booking_date': $('#booking_date').val(),
                'time_slot_id': $('#time_slot_id').val(),
            },
            success: function (result) {
                $('#room_id').find('option').remove()
                $('#room_id').append(result)
            }
        });
    }

    addNewClientFlow = () => {
        $('#selectContactForm').addClass('display-none');
        // enable view
        $('#createContactForm').removeClass('display-none');
        $('#addClientbtm').removeClass('display-none');
        $('#bottomContainer').addClass('display-none');
    }

    addNewClientFlowCancel = () => {
        $('#selectContactForm').removeClass('display-none');
        // disable view
        $('#createContactForm').addClass('display-none');
        $('#addClientbtm').addClass('display-none');
        $('#bottomContainer').addClass('display-none');
    }

    addNewEventFlow = () => {
        $('#selectContactForm').addClass('display-none');
        // enable add event
        $('#AddBookingForm').removeClass('display-none');
        $('#saveCancelbtm').removeClass('display-none');
        $('#bottomContainer').addClass('display-none');

    }

    function isInArray(value, array) {
        return array.indexOf(value) > -1;
    }


    document
        .getElementById("upComingEventDateGoToday")
        .addEventListener("click", () => {
            const d = new Date();
            calendar.gotoDate(d);
        });


    document
        .getElementById("currentCalendarWeekLeftArrow")
        .addEventListener("click", () => {
            calendar.prev(); // call method
            weekViewAvailabilityBGColor();
        });
    document
        .getElementById("currentCalendarWeekRightArrow")
        .addEventListener("click", () => {
            calendar.next(); // call method
            weekViewAvailabilityBGColor();
        });

    document
        .getElementById("upComingEventDateViewTypeDay")
        .addEventListener("click", () => {
            selectedViewType = "day";
            calendar.changeView("resourceTimeGridDay");
            viewChangeupdate = calendar.view.type
            calendar.refetchResources();
            calendar.rerenderEvents();
        });

    document
        .getElementById("upComingEventDateViewTypeWeek")
        .addEventListener("click", () => {
            selectedViewType = "week";
            calendar.changeView("timeGridWeek"); // call method
            calendar.editable = false;
            viewChangeupdate = calendar.view.type
            calendar.refetchResources();
            calendar.rerenderEvents();
        });

    $(document).on('click', function (e) {
        if (typeof $(e.target).data('original-title') == 'undefined' &&
            !$(e.target).parents().is('.popoverlist')) {
            $('.popoverlist').popover('hide');
            $('.selected-popover-content').popover('hide');
        };
        $(this).css('z-index', 8);
        $('.tooltipevent').remove();
    });

});

var serverTime = new Date();

function updateTime() {
    serverTime = new Date(serverTime.getTime() + 1000);
    $('.fc-now-indicator-arrow').html(serverTime.getHours() + ":" + (serverTime.getMinutes() < 10 ? '0' : '') + serverTime.getMinutes());
}

$(function () {
    updateTime();
    setInterval(updateTime, 1000);
});

$(function () {

    var doc = new jsPDF();
    var specialElementHandlers = {
        '#editor': function (element, renderer) {
            return true;
        }
    };

    $('#print-apt-pdf').click(function () {
        doc.fromHTML($('#upComingEventCalendar').html(), 15, 15, {
            'width': 170,
            'elementHandlers': specialElementHandlers
        });
        doc.save('sample-file.pdf');
    });

});