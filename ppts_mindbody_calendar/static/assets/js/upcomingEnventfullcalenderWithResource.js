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
  let AddBookingPopOver = false;
  var location_custom = $("select.location-filter-drop-down").children("option:selected").val();



  let getFilterDetails = () => {
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
      data: {
            'location_custom_non_all': location_custom,
      },
      success: function (result) {
        $('.service-filter-drop-down').append(result)
      }
    });

    $.ajax({
      url: "/booking_activities/filter/instructors",
      type: "POST",
      async: false,
      data: {
//        'selected_location':'location_custom',
        'location_custom_non_all': location_custom,
      },
      success: function (result) {
        $('.intructor-filter-drop-down').append(result)
        $('.instructor-single-filter-drop-down').append(result)
        console.log("custommm_alll",result)
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

//    $.ajax({
//      url: "/booking_activities/filter/instructors",
//      type: "POST",
//      async: false,
//      data: {
//      'location_custom_non_all': location_custom,
//      },
//      success: function (result) {
//        $('.intructor-filter-drop-down').append(result)
//        $('.instructor-single-filter-drop-down').append(result)
//        $('#therapist_id').append(result)
//        console.log("Third",result)
//      }
//    });

  }
  $("select.location-filter-drop-down").change (function () {
        $("select.intructor-filter-drop-down").children("option").remove();
        $("select.instructor-single-filter-drop-down").children("option").remove();
        $("select.service-filter-drop-down").children("optgroup").remove();
        location_custom = $("select.location-filter-drop-down").children("option:selected").val();
        console.log("Bookingggglocation",location_custom)
        $.ajax({
          url: "/booking_activities/filter/instructors",
          type: "POST",
          async: false,
          data: {
              'location_custom_non_all': location_custom,
          },
          success: function (result) {
            $('.intructor-filter-drop-down').append(result)
            console.log("reusltttt1",result)
            $('.instructor-single-filter-drop-down').append(result)
            $('#multiselect').multiselect({
          buttonWidth: '140px',
          includeSelectAllOption: true,
          actionsBox: true,
          selectAllText: 'All Instructors',
          allSelectedText: 'All Instructors',
          nonSelectedText: 'All Instructors'
        }).multiselect('selectAll', false).multiselect('updateButtonText');

          }
        });
        $.ajax({
          url: "/booking_activities/filter/services",
          type: "POST",
          async: false,
          data: {
                'location_custom_non_all': location_custom,
          },
          success: function (result) {
            $('.service-filter-drop-down').append(result)
          }
        });


  });

  CustomerAptBooking = (therapist_id,date_appointment,start_time,end_time,time_slot_id) => {

//    var selectedCountry = $('select.location-filter-drop-down option:selected').text();
//		$("select.location-filter-drop-down").change (function () {
//            var selectedCountry1 = $(this).children("option:selected").val();
//
//
//        });
    $("#client-advance-search-sidebar").on('focus', function () {
      var selectedCountry = $("select.location-filter-drop-down").children("option:selected").val();
     console.log("BookinggggI",selectedCountry)
    var customer
    $.ajax({
      url: "/booking_activities/filter/customer_detail",
      type: "POST",
      async: false,
      data: {
        'therapist_id': therapist_id,
        'booking_date': date_appointment,
        'start_time':start_time,
        'end_time': end_time,
        'time_slot_id' : time_slot_id,
        'selected_country_id' : selectedCountry,
      },
      success: function (result) {
        var resultJSON = jQuery.parseJSON(result);
        customer = resultJSON;
      },
    });

    $("#client-advance-search-sidebar").autocomplete({
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
        addNewEventFlow()
        $('input[name=client_id]').val(ui.item.id)
        $('input[name=client_name]').val(ui.item.label)
        $('input[name=client_mobile]').val(ui.item.mobile)
        $('input[name=client_email]').val(ui.item.email)
        rebookPastVisitData(ui.item.id)
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

    });

    AppendServiceCateg(therapist_id,date_appointment)
  }

  openNav = () => {
    navOpen = true;
    document.getElementById("leftsidenav").style.width = "350px";
  }
  
  closeNav = () => {
    navOpen = false
    document.getElementById("leftsidenav").style.width = "0px";
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
      events = jQuery.parseJSON(result);
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
    unselectAuto: false,
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
      const div = document.createElement("div");
      div.classList.add("resource-header-title-container");
      // div.innerHTML = item;
      setTimeout(() => {
        const attDate = date.getFullYear() + '-' +
          (date.getMonth() + 1 > 9 ? date.getMonth() + 1 : "0" + (date.getMonth() + 1)) + '-' +
          (date.getDate() > 9 ? date.getDate() : "0" + date.getDate())
        const el = $("[data-date='" + attDate + "'");
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
    },
    dayRender: (info) => { },
    resourceRender: (renderInfo) => { },
    resourceText: (info) => { },
    eventRender: (eventInfo, element, view) => {
      var info = eventInfo
      if (eventInfo.event.rendering === 'background') {
        if (resourceAvailableMap[eventInfo.event.extendedProps.extendedPropsRId] &&
          !resourceAvailableMap[eventInfo.event.extendedProps.extendedPropsRId].availability) {
          resourceAvailableMap[eventInfo.event.extendedProps.extendedPropsRId]['availability'] = { start: eventInfo.event.start, end: eventInfo.event.end };
        } else {
          resourceAvailableMap[eventInfo.event.extendedProps.extendedPropsRId] = {
            availability: { start: eventInfo.event.start, end: eventInfo.event.end }
          }
        }
        // resourceAvailableMap[eventInfo.event.extendedProps.extendedPropsRId] = {availability: { start: eventInfo.event.start, end: eventInfo.event.end }};
        // todo have to move this inside event listing ajax call or after event bind
        // for (let event of events) {
        // if (event.rendering === 'background') {
        // resourceAvailableMap[event.resourceId] = {start: event.start, end: event.end};
        // }
        // }
      } else {
        if (!eventInfo.isMirror) {
          var payment_status
          switch (eventInfo.event.extendedProps.payment_status) {
            case 'no_paid':
              payment_status = '<img class="EventCardPaymentStatus" src="/ppts_mindbody_calendar/static/assets/img/unpaid-icon.png" border="0" alt="">'
              break;
            case 'payment_received':
              payment_status = '<img class="EventCardPaymentStatus" src="https://logodix.com/logo/1007462.png" width="12px" border="0" alt="">'
              break;
            case 'paid':
              payment_status = '<img class="EventCardPaymentStatus" src="/ppts_mindbody_calendar/static/assets/img/icon_green_circle.png" border="0" alt="">'
              break;
            case 'partially_paid':
              payment_status = '<img class="EventCardPaymentStatus" src="/ppts_mindbody_calendar/static/assets/img/icon_green_circle.png" border="0" alt="">'
              break;
          }

          var notes = cancellation_notes = ''
          if (eventInfo.event.extendedProps.note != '') {
            notes = '<div class="greycontainer"><p>' + eventInfo.event.extendedProps.note + '</p> </div>'
          }

          if (eventInfo.event.extendedProps.state == 'cancel') {
            notes = `<div class="greycontainer"><p>
            
            ${eventInfo.event.extendedProps.cancel_notes.replaceAll(',', function (x) {
              return '<br/>';
            })}

            </p> </div>`
          }
          if (eventInfo.event.extendedProps.isfavourite)
          {
            first_time = '<img src="/ppts_mindbody_calendar/static/assets/img/first-appt-10px.png" style="margin-right: 2px !important;">'
          } 
          else{
            first_time = ''
          }
          
          resheduled = '<img src="/ppts_mindbody_calendar/static/assets/img/icon-bm-schedule-overlay-calendar.png">'
          // backend appointment 
          if (eventInfo.event.extendedProps.event_type === 'appointment' &&  eventInfo.event.extendedProps.booking_mode != 'online'){
            $(eventInfo.el).tooltip({
              title: " ",
              trigger: 'hover',
              placement: 'right',
              container: 'body',
              template: `<div class="tooltip-template" style="display:block;">
                            <div class="tooltip-header-event ${eventInfo.event.extendedProps.tool_tip_className}">
                                <p style="font-weight:bold;">${eventInfo.event.extendedProps.partner_name}</p>
                                <span>${eventInfo.event.extendedProps.partner_phone}</span>
                            </div>
                            <div class="tooltip-body">
                                <div class="tooltip-font-color">
                                    <span style="font-weight:bolder;color:#7F7F7F;font-size:12px;">${eventInfo.event.extendedProps.tooltip_duration}</span>
                                    <div class="timeforflex" style="color:#7F7F7F;">
                                        <small>${eventInfo.event.extendedProps.service_category_name}|${eventInfo.event.extendedProps.sub_category_name}</small>
                                        <div>
                                        ${payment_status}
                                        ${first_time}
                                        ${resheduled} 
                                        </div>
                                    </div>
                                    <div class="timeforflex" style="color:#7F7F7F;">
                                        <small><b>Rooms:</b> ${eventInfo.event.extendedProps.room_name} </small>
                                    </div>
                                    ${notes}
                                    ${cancellation_notes}
                                </div>
                            </div>
                        </div>`
            });
          }
          // online appointment
          if (eventInfo.event.extendedProps.event_type === 'appointment' &&  eventInfo.event.extendedProps.booking_mode === 'online'){
            $(eventInfo.el).tooltip({
              title: " ",
              trigger: 'hover',
              placement: 'right',
              container: 'body',
              template: `<div class="tooltip-template" style="display:block;">
                            <div class="tooltip-header-event ${eventInfo.event.extendedProps.tool_tip_className}">
                                <p style="font-weight:bold;"> <i class="fa fa-globe"></i> ${eventInfo.event.extendedProps.partner_name}</p>
                                <span>${eventInfo.event.extendedProps.partner_phone}</span>
                            </div>
                            <div class="tooltip-body">
                                <div class="tooltip-font-color">
                                    <span style="font-weight:bolder;color:#7F7F7F;font-size:12px;">${eventInfo.event.extendedProps.tooltip_duration}</span>
                                    <div class="timeforflex" style="color:#7F7F7F;">
                                        <small>${eventInfo.event.extendedProps.service_category_name}|${eventInfo.event.extendedProps.sub_category_name}</small>
                                        <div>
                                        ${payment_status}
                                        ${first_time}
                                        ${resheduled} 
                                        </div>
                                    </div>
                                    <div class="timeforflex" style="color:#7F7F7F;">
                                        <small><b>Rooms:</b> ${eventInfo.event.extendedProps.room_name} </small>
                                    </div>
                                    ${notes}
                                    ${cancellation_notes}
                                </div>
                            </div>
                        </div>`
            });
          }


          $(eventInfo.el).popover({
            // title: "title",
            placement: 'right',
            trigger: 'manual',
            html: true,
            content: eventInfo.event.extendedProps.POP_OVER,
          }).on('show.bs.popover', function () {
            $(eventInfo.el).closest('.fc-event-container').append("<div id='overlay-calendar'></div>");
            editAppointment(info);
            $('#leftsidenav').css('z-index', '100');
            $(eventInfo.el).css('z-index', '100');
            $('.fc-head-container.fc-widget-header').css('z-index', '0');
            $('.fc-event-container').css('z-index', '1');
            $(eventInfo.el).parent('.fc-event-container').css('z-index', '4');

          }).on('hide.bs.popover', function () {
            $("#overlay-calendar").remove();
            back_to_normal();
            $(eventInfo.el).css('z-index', '1');
            $('#leftsidenav').css('z-index', '0');
            $('.fc-head-container.fc-widget-header').css('z-index', '2');
            $('.fc-event-container').css('z-index', '4');
          });
        }
      }
// online appointment 
if (eventInfo.event.extendedProps.booking_mode === 'online'){
      if (eventInfo.event.classNames.indexOf("event-status-confirm") > -1 || eventInfo.event.classNames.indexOf("event-status-arrive") > -1 || eventInfo.event.classNames.indexOf("event-status-done") > -1 || eventInfo.event.classNames.indexOf("event-status-cancel") > -1 || eventInfo.event.classNames.indexOf("event-status-new") > -1 || eventInfo.event.classNames.indexOf("event-status-no-show") > -1) {
        eventInfo.el.innerHTML = '<div class="fc-content">' +
          '<div class="eventCard-Subcategory"> <i class="fa fa-globe"></i> ' + eventInfo.event.extendedProps.sub_category_name + '</div>' +
          '<div class="eventCard-PartnerName">' + payment_status + eventInfo.event.extendedProps.partner_name + '</div>' +
          '<div class="eventCard-RoomName">' + eventInfo.event.extendedProps.room_name + '</div>' +
          '</div><div class="fc-resizer fc-end-resizer"></div>'
      }
    }
// backend appointment
if (eventInfo.event.extendedProps.booking_mode != 'online'){
      if (eventInfo.event.classNames.indexOf("event-status-confirm") > -1 || eventInfo.event.classNames.indexOf("event-status-arrive") > -1 || eventInfo.event.classNames.indexOf("event-status-done") > -1 || eventInfo.event.classNames.indexOf("event-status-cancel") > -1 || eventInfo.event.classNames.indexOf("event-status-new") > -1 || eventInfo.event.classNames.indexOf("event-status-no-show") > -1) {
        eventInfo.el.innerHTML = '<div class="fc-content">' +
          '<div class="eventCard-Subcategory"> ' + eventInfo.event.extendedProps.sub_category_name + '</div>' +
          '<div class="eventCard-PartnerName">' + payment_status + eventInfo.event.extendedProps.partner_name + '</div>' +
          '<div class="eventCard-RoomName">' + eventInfo.event.extendedProps.room_name + '</div>' +
          '</div><div class="fc-resizer fc-end-resizer"></div>'
      }
    }

      $('.colorbox-booked').text($('.event-status-new').length)
      $('.colorbox-confirmed').text($('.event-status-confirm').length)
      $('.colorbox-arrived').text($('.event-status-arrive').length)
      $('.colorbox-no-show').text($('.event-status-no-show').length)
      $('.colorbox-completed').text($('.event-status-done').length)
      $('.colorbox-cancel').text($('.event-status-cancel').length)

      if (eventInfo.view.type == "timeGridWeek") {
        return eventInfo.event.extendedProps.extendedPropsRId == $(".instructor-single-filter-drop-down").val() && ['all', eventInfo.event.extendedProps.sub_category_id].indexOf($('.service-filter-drop-down').val()) >= 0 && ['all', eventInfo.event.extendedProps.company_id].indexOf($('.location-filter-drop-down').val()) >= 0
      } else {
        if (eventInfo.event.extendedProps.state != 'availability') {
          return ['all', eventInfo.event.extendedProps.sub_category_id].indexOf($('.service-filter-drop-down').val()) >= 0 && ['all', eventInfo.event.extendedProps.company_id].indexOf($('.location-filter-drop-down').val()) >= 0
        }
      }
    },
    eventClick: (info) => {
      $(info.el).tooltip('disable');
      $('.bs-tooltip-right').removeClass('show');
      $('.bs-tooltip-right').addClass('hide');
      $('.bs-tooltip-left').removeClass('show');
      $('.bs-tooltip-left').addClass('hide');
      $('.selected-popover-content').popover('hide');
      $('#cc_cancellation_charge').val(info.event.extendedProps.cc_cancellation_charge);
      $('#cc_cancellation_appointment_id').val(info.event.extendedProps.appointment_id);

      switch (info.event.extendedProps.event_type) {
        case 'appointment':
          if (!isEventPopOverOpen) {
            isEventPopOverOpen = true;
            previousEl = info.el;
            $(info.el).popover('show');
          }
          else {
            $(previousEl).tooltip('enable');
            $(previousEl).popover('hide');
            setTimeout(() => {
              $(info.el).popover('show');
              previousEl = info.el;
            }, 300);
          }
          break;
        case 'event':
          window.open(info.event.extendedProps.event_url);
          break;
      }

      setTimeout(() => {
        const elements = document.getElementsByClassName("popover-container-close-btn");
        for (let i = 0; i < elements.length; i++) {
          elements[i].addEventListener('click', () => {
            $('.bs-tooltip-right , .bs-tooltip-left').removeClass('disabled');
            $(info.el).tooltip('enable');
            if (isEventPopOverOpen) {
              $(previousEl).popover('hide');
              $("#calendar-mainwrap").css("pointer-events","all");
              $(".edit_appointment_custom").css("pointer-events","all");
            } else {
              $("#calendar-mainwrap").css("pointer-events","all");
              $(".edit_appointment_custom").css("pointer-events","all");
              $(info.el).popover('hide');
            }
            isEventPopOverOpen = false;
            $("#calendar-mainwrap").css("pointer-events","all");
            $(".edit_appointment_custom").css("pointer-events","all");
          }, false);
        }
      }, 500);
    },
    select: (selectedInfo) => {
      console.log('ooooooooooooooooo');
      if ($(selectedInfo.jsEvent.target)) {
        $('.popoverlist').popover('hide');
        // $(selectedInfo.jsEvent.target).popover('hide');
      }
      const availabilityStart = new Date(resourceAvailableMap[selectedInfo.resource.id].availability.start)
      const availabilityEnd = new Date(resourceAvailableMap[selectedInfo.resource.id].availability.end)
      if (resourceAvailableMap[selectedInfo.resource.id] &&
        resourceAvailableMap[selectedInfo.resource.id].availability &&
        (availabilityStart <= selectedInfo.start && availabilityStart < selectedInfo.end) &&
        (availabilityEnd > selectedInfo.start && availabilityEnd >= selectedInfo.end)) {

        if (checkTherapistServiceDuration(selectedInfo.start, selectedInfo.end, selectedInfo.resource.id) === 'False') {
          $("#therapist_service_duration_not_available").modal();
          return false;
        }

        if (AddBookingPopOver === false) {
          $(selectedInfo.jsEvent.target).popover({
            title: "title",
            placement: 'right',
            container: 'body',
            trigger: 'click',
            template: `
            <ul id="context-menu" class="popoverlist selected-popover-content context-menu context-right ctx-right POP-select-option while-event-available">
            <li><a class="popover-container-selected-Value"><i class="fas fa-times"></i></a></li>
            
            <li>
              <a id="CreateNewAppointmentCalc" class="checkout" title=""> 
              <span id="popover-edit-today-schedule"> <i class="fas fa-clipboard-list"></i> Add Appointment</span>
              </a>
            </li>
            
            
            </ul>
            `,
            // <li style="display:none !important;">
            //   <a href="/booking/url/redirect/add_availability_view" class="checkout" id="markAsUnavailable"> 
            //     <span class="popover-add-availability"> <i class="fas fa-highlighter"></i> Mark as Unavailable </span>
            //   </a>
            // </li>
          }).on('show.bs.popover', function () {
            // $("#overlay-calendar").remove();
            // $('.fc-highlight').closest('.fc-highlight-container').append("<div id='overlay-calendar'></div>");
            // $('#leftsidenav').css('z-index', '100');
            // $('.fc-highlight').css('z-index', '100');
            // $('.fc-head-container.fc-widget-header').css('z-index', '0');
            // $('.fc-event-container').css('z-index', '1');
            // $('.fc-highlight').parent('.fc-highlight-container').css('z-index', '4');
          }).on('hide.bs.popover', function () {
            // $("#overlay-calendar").remove();
            // $('.fc-highlight').css('z-index', '1');
            // $('#leftsidenav').css('z-index', '0');
            // $('.fc-head-container.fc-widget-header').css('z-index', '2');
            // $('.fc-highlight-container').css('z-index', '4');
          });

        }
      } else {
        return false;
      }

      var St_str = selectedInfo.startStr.split('T');
      St_str = St_str[1].split(':');
      St_str = St_str[0] + ':' + St_str[1];

      var En_str = selectedInfo.endStr.split('T');
      En_str = En_str[1].split(':');
      En_str = En_str[0] + ':' + En_str[1];

      $('#AddBookingForm #time_id').val(getServiceDuration(selectedInfo.start, selectedInfo.end));
      $('#AddBookingForm #time_slot_id').val(getTimeSlotId(St_str, En_str));


      $('#addAavailabilityForm').addClass('display-none');
      setTimeout(() => {
        $(selectedInfo.jsEvent.target).popover('show');

        const elements = document.getElementsByClassName("popover-container-selected-Value");
        for (let i = 0; i < elements.length; i++) {
          elements[i].addEventListener('click', () => {
            $(selectedInfo.jsEvent.target).popover('hide');
            $('#selectContactForm').addClass('display-none');
            $('#addUnavailabilityForm').addClass('display-none');
            $('#bottomContainer').removeClass('display-none');
            close_selected_apt()
            AddBookingPopOver = false;
          }, false);
        }

        // $("#markAsUnavailable").click(function () {
        //   $('#selectContactForm').addClass('display-none');
        //   // $('#addUnavailabilityForm').removeClass('display-none');
        //   $("#av_therapist_id").val(selectedInfo.resource.id);
        //   $("#av_available_date").val(selectedInfo.startStr.split("T")[0]);
        //   $("#av_start_date").val(selectedInfo.startStr.split("T")[0]);
        //   $("#av_end_date").val(selectedInfo.endStr.split("T")[0]);
        //   $("#av_start_time").val(selectedInfo.startStr.split("T")[1].split(':00+')[0]);
        //   $("#av_end_time").val(selectedInfo.endStr.split("T")[1].split(':00+')[0]);
        // });

        $("#createNewAvailability").click(function () {
          $('#selectContactForm').addClass('display-none');
          $('#addAavailabilityForm').removeClass('display-none');
          $('#av_therapist_name').val(selectedInfo.resource.title)
          $('#av_therapist_id').val(selectedInfo.resource.id)
          $('#av_available_date').val(selectedInfo.startStr.split("T")[0])
          $("#av_start_time").val(selectedInfo.startStr.split("T")[1].split(':00+')[0]);
          $("#av_end_time").val(selectedInfo.endStr.split("T")[1].split(':00+')[0]);
        });
      })
      selectedStart = selectedInfo.start;
      selectedEnd = selectedInfo.end;
      isAddEventFlowOpen = true;
      // $('#selectContactForm').removeClass('display-none');
      // $('#appointmentClientBTM').removeClass('display-none');
      // $('#bottomContainer').addClass('display-none');
      // openNav()
      CustomerAptBooking(selectedInfo.resource._resource.id,selectedInfo.startStr.split("T")[0],selectedInfo.startStr.split("T")[1].split(':00+')[0],selectedInfo.endStr.split("T")[1].split(':00+')[0],getTimeSlotId(St_str, En_str))
      $('#therapist_id').val(selectedInfo.resource._resource.id)
      $('#therapist_id_hidden').val(selectedInfo.resource._resource.id)
      $('#booking_date').val(selectedInfo.startStr.split("T")[0])

      return true

    },
    eventAllow: (dropInfo, draggedEvent) => {
      const d = new Date();
      if (selectedViewType === 'week' || dropInfo.start < d || dropInfo.event.extendedProps.state === 'unavailability') {
        return false;
      }
      let returnStatus = true
      if (resourceAvailableMap[dropInfo.resource.id] && resourceAvailableMap[dropInfo.resource.id].availability) {
        const availableStart = new Date(resourceAvailableMap[dropInfo.resource.id].availability.start)
        const availableEnd = new Date(resourceAvailableMap[dropInfo.resource.id].availability.end)
        if (dropInfo.start < availableStart || dropInfo.end < availableStart ||
          dropInfo.start > availableEnd || dropInfo.end > availableEnd) {
          returnStatus = false;
        }
      } else {
        returnStatus = false;
      }
      for (let event of events) {
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
    selectAllow: function (selectedInfo) {
      const d = new Date();
      if (selectedViewType === 'week' || selectedInfo.start < d) {
        return false;
      }
      let returnStatus = true;
      const availabilityStart = new Date(resourceAvailableMap[selectedInfo.resource.id].availability.start)
      const availabilityEnd = new Date(resourceAvailableMap[selectedInfo.resource.id].availability.end)

      if (resourceAvailableMap[selectedInfo.resource.id] &&
        resourceAvailableMap[selectedInfo.resource.id].availability &&
        (availabilityStart <= selectedInfo.start && availabilityStart < selectedInfo.end) &&
        (availabilityEnd > selectedInfo.start && availabilityEnd >= selectedInfo.end)) {
        events.forEach(event => {
          const eventStart = new Date(event.start);
          const eventEnd = new Date(event.end);
          if (selectedInfo.resource.id == event.resourceId && event.rendering !== 'background') {
            if ((eventStart <= selectedInfo.start && eventEnd > selectedInfo.start) ||
              (eventStart < selectedInfo.end && eventEnd >= selectedInfo.end)) {
              returnStatus = false;
            }
          }
        });
      }
      else {
        return false // while selecting outside the availability
      }

      if (resourceAvailableMap[selectedInfo.resource.id] &&
        resourceAvailableMap[selectedInfo.resource.id].availability &&
        (availabilityStart > selectedInfo.start && selectedInfo.end < availabilityStart) ||
        (availabilityEnd < selectedInfo.end && selectedInfo.start < availabilityEnd)) {
        returnStatus = false;
      }
      return returnStatus;
    },
    eventDrop: (dropInfo) => {
      if (selectedViewType === 'week') {
        dropInfo.revert();
      }
      if (checkTherapistServiceDuration(dropInfo.event.start, dropInfo.event.end, dropInfo.event.extendedProps.extendedPropsRId) === 'False') {
        $("#therapist_service_duration_not_available").modal();
        return false;
      }
      modelReschedule(dropInfo)
    },
    eventResize: (dropInfo) => {
      if (selectedViewType === 'week') {
        dropInfo.revert();
      }

      if (checkTherapistServiceDuration(dropInfo.event.start, dropInfo.event.end, dropInfo.event.extendedProps.extendedPropsRId) === 'False') {
        $("#therapist_service_duration_not_available").modal();
        return false;
      }
      modelReschedule(dropInfo)
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
    events: events
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

  ReloadScreen = () => {
    $('#BookingActivityLoaderCalendar').show();
    $('#afterLoad').addClass('d-none');
    location.reload()
  }

  $('#aptReschedule-model').on('hidden.bs.modal', function () {
    ReloadScreen();
  });

  $('#therapist_service_duration_not_available').on('hidden.bs.modal', () => {
    calendar.unselect();
    $('#AddBookingForm #sub_categ_id').find('option').remove()
    
  });

  $('#therapist_service_duration_not_available_reschedule').on('hidden.bs.modal', () => {
    calendar.unselect();
    location.reload()
  });

  $(document).on('show.bs.modal', '#aptCancellation-model', (e) => {
    $.ajax({
      url: "/booking_activities/get/cancellation/details",
      type: "POST",
      async: false,
      data: { 'cc_cancellation_appointment_id': $('#cc_cancellation_appointment_id').val() },
      success: function (result) {
        json = jQuery.parseJSON(result);
        $('#cancellation_type').val(json[0].cancellation_type);
        $('#cc_cancellation_charge').val(json[0].cc_cancellation_charge);
      },
    });
  });

  editAppointment = (info) => {
    console.log(info, 'infoooooooooooooooooooo');
    $('.datepickercontainer').removeClass('opendatepicker');
    $('#EditBookingForm').removeClass('display-none');
    $('#editCancelbtm').removeClass('display-none');
    $('#bottomContainer').addClass('display-none');

    $('#client-details-apt-se input[name=client_name]').val(info.event.extendedProps.partner_name);
    $('#client-details-apt-se input[name=client_id]').val(info.event.extendedProps.partner_id);
    $('#client-details-apt-se #booking_date').val(info.event.extendedProps.appointment_date);
    $('#client-details-apt-se #therapist_id_hidden').val(info.event.extendedProps.extendedPropsRId);
    $('#EditBookingForm #therapist_id').val(info.event.extendedProps.extendedPropsRId);
    $('#client-details-apt-se #appointment_id_hidden').val(info.event.extendedProps.appointment_id);
    $('#therapist_id').val(info.event.extendedProps.therapist_id)
    $('#client-details-apt-se input[name=client_mobile]').val(info.event.extendedProps.partner_phone);
    $('#client-details-apt-se input[name=client_email]').val(info.event.extendedProps.partner_email);
    AppendServiceCateg(info.event.extendedProps.therapist_id,info.event.extendedProps.appointment_date);
    $('#client-details-apt-se2 #service_categ_id').val(info.event.extendedProps.service_category_id);
    service_categ_func();
    $('#client-details-apt-se2 #sub_categ_id').val(info.event.extendedProps.sub_category_id);
    $('#client-details-apt-se2 #appointment_platform').val(info.event.extendedProps.appointment_type);
    $('#client-details-apt-se2 #time_id').val(info.event.extendedProps.time_id);
    sessionStorage.removeItem('time_slot_id_custom'); /*time_id removed from session for filter based on time-id in edit appointment */
    $('#client-details-apt-se2 #time_slot_id').val(info.event.extendedProps.time_slot_id);
    $('#client-details-apt-se2 #room_id').val(info.event.extendedProps.room_id);
    $('#client-details-apt-se2 #note').val(info.event.extendedProps.note);
    
    $("#calendar-mainwrap").css("pointer-events","none");    /* for calendar editable --false when clicked on popover */ 
    $(".edit_appointment_custom").css("pointer-events","none"); 


   
   
    if (info.event.extendedProps.isfavourite)
    {
      $('#client-details-apt-se2 #is_favourite_check').val("yes");
      $('#client-details-apt-se2 .gold_star').css("display","block");
      $('#client-details-apt-se2 .empty_star').css("display","none");
      console.log("GOld star JS")

    }
    else{
      $('#client-details-apt-se2 #is_favourite_check').val("no");
      $('#client-details-apt-se2 .gold_star').css("display","none");
      $('#client-details-apt-se2 .empty_star').css("display","block");
     
      console.log("Empty star JS")
    }
    editAppointmentBorder(info);
    getDuration();
    computeTimeSlot(info);
  }

  getDuration = () => {
    $.get('/edit/duration/details', {
      appointment: $('#EditBookingForm #appointment_id_hidden').val(),
      therapist: $('#EditBookingForm #therapist_id_hidden').val(),
      service_categ_id: $('#EditBookingForm #service_categ_id').val(),
      sub_categ_id: $('#EditBookingForm #sub_categ_id').val()
    }).done(function (result) {
      result = jQuery.parseJSON(result);
      $('#EditBookingForm #time_id').find('option').remove()

      $.each(result, function (key, value) {
        $('#EditBookingForm #time_id').append($('<option></option>').attr("value", key).text(value));        
      });

    });
  }

  computeTimeSlot = (info) => {

    $.get('/get/direct/time_slot', {
      appointment: info.event.extendedProps.appointment_id,
      therapist: info.event.extendedProps.extendedPropsRId,
      appointment_date: info.event.extendedProps.appointment_date,
      duration: $('#EditBookingForm #time_id').val(),
      time_slot_id: info.event.extendedProps.time_slot_id,
    }).done(function (result) {
      result = jQuery.parseJSON(result);
      console.log('result-->', result)
      $('#EditBookingForm #time_slot_id').find('option').remove()
      $.each(result, function (key, value) {
      	if (info.event.extendedProps.time_slot_id == key) {
      		let option = $('<option></option>')
      		option.attr("value", key).text(value)
      		option.attr("selected", 'selected')
      		$('#EditBookingForm #time_slot_id').append(option);
      	} else {
      		$('#EditBookingForm #time_slot_id').append($('<option></option>').attr("value", key).text(value));
      	}  
        
      });
    });

  }

  onchange_get_timeslot = () => {
    $.get('/get/direct/time_slot', {
      appointment: $('#EditBookingForm #appointment_id_hidden').val(),
      therapist: $('#EditBookingForm #therapist_id_hidden').val(),
      appointment_date: $('#EditBookingForm #booking_date').val(),
      duration: $('#EditBookingForm #time_id').val()
    }).done(function (result) {
      result = jQuery.parseJSON(result);
      console.log('result-->', result)
      $('#EditBookingForm #time_slot_id').find('option').remove()
      $.each(result, function (key, value) {
        $('#EditBookingForm #time_slot_id').append($('<option></option>').attr("value", key).text(value));       
      });
    });
  }

  makeFieldsReadonly = () => {
    $('#EditBookingForm #client-details-apt-se2 #service_categ_id').addClass('field-disabled');
    $('#EditBookingForm #client-details-apt-se2 #sub_categ_id').addClass('field-disabled');
    $('#EditBookingForm #client-details-apt-se2 #time_id').addClass('field-disabled');
    $('#EditBookingForm #client-details-apt-se2 #time_slot_id').addClass('field-disabled');
    $('#EditBookingForm #client-details-apt-se2 #appointment_platform').addClass('field-disabled');
    $('#EditBookingForm #client-details-apt-se2 #room_id').addClass('field-disabled');
  }

  makeFieldsReadable = () => {
    $('#EditBookingForm #client-details-apt-se2 #service_categ_id').removeClass('field-disabled');
    $('#EditBookingForm #client-details-apt-se2 #sub_categ_id').removeClass('field-disabled');
    $('#EditBookingForm #client-details-apt-se2 #time_id').removeClass('field-disabled');
    $('#EditBookingForm #client-details-apt-se2 #time_slot_id').removeClass('field-disabled');
    $('#EditBookingForm #client-details-apt-se2 #appointment_platform').removeClass('field-disabled');
    $('#EditBookingForm #client-details-apt-se2 #room_id').removeClass('field-disabled');
  }

  editAppointmentBorder = (info) => {
    switch (info.event.extendedProps.state) {
      case 'new':
        $('#EditBookingForm #client-details-apt-se2').css('border-top', '7px solid #476d47');
        makeFieldsReadable();
        break;
      case 'confirm':
        $('#EditBookingForm #client-details-apt-se2').css('border-top', '7px solid #543654');
        makeFieldsReadonly();
        break;
      case 'arrive':
        $('#EditBookingForm #client-details-apt-se2').css('border-top', '7px solid #31071f');
        makeFieldsReadonly();
        break;
      case 'no_show':
        $('#EditBookingForm #client-details-apt-se2').css('border-top', '7px solid #ce5757');
        makeFieldsReadonly();
        break;
      case 'done':
        $('#EditBookingForm #client-details-apt-se2').css('border-top', '7px solid #6f8e98');
        makeFieldsReadonly();
        break;
      case 'cancel':
        $('#EditBookingForm #client-details-apt-se2').css('border-top', '7px solid #861d1e');
        makeFieldsReadonly();
        break;
    }
  }

  AppendServiceCateg = (therapist_id,date_appointment) => {
    $.ajax({
      url: "/booking_activities/get/service_categ",
      type: "POST",
      async: false,
      data: { 'therapist_id': therapist_id,
              'date_value' : date_appointment,
         },
      success: function (result) {
        $('#service_categ_id').find('option').remove();
        $('#service_categ_id').append(result);
        $('#EditBookingForm #service_categ_id').find('option').remove();
        $('#EditBookingForm #service_categ_id').append(result);
      },
    });
  }

  modelReschedule = (dropInfo) => {
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
    let date_re = dropInfo.event.start.toLocaleDateString()
    $('#re-apt_name').text(dropInfo.event._def.title);
    $('input[name="re_apt_id"]').val(dropInfo.event.extendedProps.appointment_id);
    $('input[name="re_date"]').val(date_re);
    $('input[name="re_start_time"]').val(dropInfo_start_time);
    $('input[name="re_end_time"]').val(dropInfo_end_time);
    $('input[name="re_duration"]').val(minutes);


    console.log(dropInfo, 'dropInfodropInfodropInfodropInfodropInfo')
    console.log(dropInfo.event.extendedProps.service_category_id, 'dropInfodropInfodropInfodropInfodropInfo')
    // if (checkTherapistServiceDuration(dropInfo.event.start, dropInfo.event.end, dropInfo.event.extendedProps.therapist_id) === 'False') {
    if (ReschedulecheckTherapistServiceDuration(minutes, dropInfo.event.extendedProps.therapist_id, dropInfo.event.extendedProps.service_category_id, dropInfo.event.extendedProps.sub_category_id) == 'False') {
      $("#therapist_service_duration_not_available_reschedule").modal();
      return false;
    }
    else {
      $('#aptReschedule-model').modal();
    }

  }

  resources_go_to_week_view = (res_id) => {
    $('.instructor-single-filter-drop-down').val(res_id);
    $('#upComingEventDateViewTypeWeek').click();
  }

  $(document).on('click', "#CreateNewAppointmentCalc", () => {
    $('#AddBookingForm #sub_categ_id').find('option').remove()
    $('#selectContactForm').removeClass('display-none');
    $('#appointmentClientBTM').removeClass('display-none');
    $('#bottomContainer').addClass('display-none');
    $('.popoverlist').popover('hide');
    $('#client-advance-search-sidebar').val('');
    $('#client-advance-search-sidebar').focus();
    $(".editable_content").attr("style","pointer-events:auto;");
    AddBookingPopOver = true;
    openNav();
  });

  $(document).on('click', "#popover-apt-cancel-model", () => { $('#aptCancellation-model').modal(); });
  $(document).on('click', "#popover-apt-confirm-no_show-model", () => {
    // $.ajax({
    //   url: "/booking_activities/make/appointment/noshow",
    //   type: "POST",
    //   async: false,
    //   data: {
    //     'appointment_id': $('#appointment_id_hidden').val(),
    //   },
    //   success: function (result) {
    //     calendar.rerenderEvents();
    //   }
    // });'
    $.get('/booking/appointment/noshow/' + $('#EditBookingForm #appointment_id_hidden').val()).done(() => {
      $('#aptNoShow-model').modal();
    });

  });

  $(document).on('show.bs.modal', '#aptNoShow-model', (e) => {
    $.ajax({
      url: "/booking_activities/get/noshow/details",
      type: "POST",
      async: false,
      data: { 'appointment_id': $('#appointment_id_hidden').val() },
      success: function (result) {
        json = jQuery.parseJSON(result);
        $('#cc_noshow_appointment_id').val(json[0].appointments_id);
        $('#no_show_charges').val(json[0].no_show_charges);
        $('#aptNoShow-model #note').val(json[0].note);
        if (json[0].is_paid === 'no_paid') {
          $('#no-show-payment-ctnent').removeClass('display-none');
        }
      },
    });
  });

  $(document).on('hidden.bs.modal', '#aptNoShow-model', (e) => {
    location.reload();
  });

  // CreateNewAppointment = () => {
  //   $('#selectContactForm').removeClass('display-none');
  //   $('#appointmentClientBTM').removeClass('display-none');
  //   $('#bottomContainer').addClass('display-none');
  // }

  BookingeventRerender = () => {
    BookingFormCancel();
    calendar.rerenderEvents();    
  }

  changeClient = () => {
    BookingFormCancel();
  }

  BookingFormCancel = () => {
    $('.popoverlist').popover('hide');
    AddBookingPopOver = false;
    calendar.unselect();
    back_to_normal();   
  }

  close_selected_apt = () => {
    calendar.unselect();
  }
  custom_close_button = () => {
    $('.popover-container-close-btn i').click();
    $(".editable_content").attr("style","pointer-events:none;");
    console.log("doneeeeeeeeeppts")
    sessionStorage.removeItem('time_slot_id_custom');
    $(".content_show").attr("style","display:none !important;");
    $(".content_hide").attr("style","display:block !important;");
  }

  back_to_normal = () => {
    $('#selectContactForm').addClass('display-none');
    $('#appointmentClientBTM').addClass('display-none');
    $('#EditBookingForm').addClass('display-none');
    $('#AddBookingForm').addClass('display-none');
    $('#saveCancelbtm').addClass('display-none');
    $('.datepickercontainer').addClass('opendatepicker');
    $('#bottomContainer').removeClass('display-none');
    $(".editable_content").attr("style","pointer-events:none;");
    $(".content_hide").attr("style","display:block !important;");
    $(".content_show").attr("style","display:none !important;");
    custom_close_button();
  }
  

  // function fetchResourcePy({ start, end, timeZone }, successCallback) {
  //   resources = [{ 'id': 441, 'title': 'Sankar' }, { 'id': 442, 'title': 'Sankar1' }];
  //   successCallback(resources);
  //   // $.ajax({
  //   //   url: "/booking_activities/resources",
  //   //   type: "POST",
  //   //   async: false,
  //   //   data: {
  //   //     date: start,
  //   //   },
  //   //   success: function (result) {
  //   //     resources = jQuery.parseJSON(result);
  //   //     // if (viewChangeupdate == "resourceTimeGridDay") {
  //   //     // if (!resources?.length) {
  //   //     //   $('.eventresourcegridcalendar').addClass('d-none');
  //   //     //   $('#no-staff-container').removeClass('d-none');
  //   //     //   const monthStringArr = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"];
  //   //     //   const content = 'None of your staff members are available on ' +
  //   //     //     (start.getDate() > 9 ? start.getDate() : '0' + start.getDate()) +
  //   //     //     ' ' + monthStringArr[start.getMonth()] + ' ' + start.getFullYear() + '. Schedule availability or change the date range.'
  //   //     //   $('#no-staff-container-p').text(content);
  //   //     // } else {
  //   $('.eventresourcegridcalendar').removeClass('d-none');
  //   $('#no-staff-container').addClass('d-none');
  //   //     // }
  //   //     // }
  //   //     successCallback(resources);
  //   //   },
  //   // });
  // }

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
    // $('#AddBookingForm').addClass('display-none');
    // $('#editAvailabilityForm').addClass('display-none');
    // $('#createContactForm').addClass('display-none');
    // $('#selectContactForm').addClass('display-none');
    // $('#saveCancelbtm').addClass('display-none');
    // $('#addClientbtm').addClass('display-none');
    // $('#bottomContainer').addClass('display-none');
  }, 100);

  service_categ_func = (edit = false) => {
    if (edit === true) {
      edit_sevice_id = $('#EditBookingForm #service_categ_id').val()
      $('#AddBookingForm #service_categ_id').val(edit_sevice_id)
    }
    else {
      $('#service_categ_id').val()
    }

    $.ajax({
      url: "/booking_activities/get/sub_categ",
      type: "POST",
      async: false,
      data: {
        'therapist_id': $('#therapist_id').val(),
        'service_categ_id': $('#service_categ_id').val(),
        'date_value' : $('#booking_date').val(),
        'custom_time_min' :sessionStorage.getItem("time_slot_id_custom"),
      },
      success: function (result) {
        $('#AddBookingForm #sub_categ_id').find('option').remove()
        $('#AddBookingForm #sub_categ_id').append(result)

        $('#EditBookingForm #sub_categ_id').find('option').remove()
        $('#EditBookingForm #sub_categ_id').append(result)        
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
        // $('#time_id').find('option').remove()
        // $('#time_id').append(result)
        // $("#time_id").each(function () {
        //   $(this).siblings('[value="' + this.value + '"]').remove();
        // });
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
    $('#createContactForm').removeClass('display-none');
    $('#addClientbtm').removeClass('display-none');
    $('#bottomContainer').addClass('display-none');
  }

  addNewClientFlowCancel = () => {
    $('#selectContactForm').removeClass('display-none');
    $('#createContactForm').addClass('display-none');
    $('#addClientbtm').addClass('display-none');
    $('#bottomContainer').addClass('display-none');
  }

  addNewEventFlow = () => {
    $('#selectContactForm').addClass('display-none');
    $('#AddBookingForm').removeClass('display-none');
    $('#saveCancelbtm').removeClass('display-none');
    $('#bottomContainer').addClass('display-none');
    $('#note').val('');
    // $('#appointment_platform').val('type_online');
    $('#room_id').val('');
    room_id_func();
  }

  checkTherapistServiceDuration = (startTime, endTime, therapist) => {

    console.log('startTime---->', startTime, 'endTime----->', endTime, 'therapist----->', therapist)

    let therapistDuration = moment(endTime).diff(moment(startTime), 'minutes')

    console.log('therapistDuration--->', therapistDuration)
    sessionStorage.setItem("time_slot_id_custom",therapistDuration);
    console.log("hii sg",therapistDuration)
    


    let jResult
    $.ajax({
      url: "/therapist/get/service/duration",
      type: "POST",
      async: false,
      data: {
        'duration': therapistDuration,
        'therapist': therapist,
        
      },
      success: function (result) {
        jResult = result
        // var custom_id = therapistDuration
        // $('#custom_input_id').val(custom_id);
        console.log("completeddd")
      }
    });
    return jResult
  }

  ReschedulecheckTherapistServiceDuration = (duration, therapist, service_categ_id, sub_categ_id) => {

    console.log('service_categ_id')
    console.log(service_categ_id)
    console.log('sub_categ_idsss')
    console.log(sub_categ_id)
    var getresultvaluere
    // getDuration()
    $.ajax({
      url: "/therapist/get/service/sub_ids",
      type: "POST",
      async: false,
      data: {
        'duration': duration,
        'therapist': therapist,
        'services_categ_id': service_categ_id,
        'sub_categ_id': sub_categ_id,
      },
      success: function (result) {
        console.log(result, '--------')
        // if (result === 'False') {
        //   console.log(result, '--------')
        //   $('#AddBookingForm #sub_categ_id').val('')
        //   $("#therapist_service_duration_not_available").modal();
        //   return false
        // }
        getresultvaluere = result
      }
    });

    return getresultvaluere
  }

  $("#AddBookingForm #sub_categ_id").change(function () {

    if (ReschedulecheckTherapistServiceDuration($('#AddBookingForm #time_id').val(), $('#AddBookingForm #therapist_id').val(), $('#AddBookingForm #service_categ_id').val(), $('#AddBookingForm #sub_categ_id').val()) == 'False') {
      $("#therapist_service_duration_not_available").modal();
      return false;
    }

  });

  $("#EditBookingForm #sub_categ_id").change(function () {
    var resultsub_categ_idajax
    $.ajax({
      url: "/therapist/get/service/sub_ids",
      type: "POST",
      async: false,
      data: {
        'duration': $('#EditBookingForm #time_id').val(),
        'therapist': $('#EditBookingForm #therapist_id').val(),
        'services_categ_id': $('#EditBookingForm #service_categ_id').val(),
        'sub_categ_id': $('#EditBookingForm #sub_categ_id').val(),
      },
      success: function (result) {
        resultsub_categ_idajax = result
        if (result == 'False') {
          $('#EditBookingForm #sub_categ_id').val('')
          $('#EditBookingForm #time_id').val('')
          $("#therapist_service_duration_not_available").modal();
        }
      }
    });

    if (resultsub_categ_idajax != 'False') {
      getDuration()
    }

  });

  getServiceDuration = (startTime, endTime) => {
    let get_du = moment(endTime).diff(moment(startTime), 'minutes')
    let time_id
    $.ajax({
      url: "/get/service/duration",
      type: "POST",
      async: false,
      data: {
        'duration': get_du,
      },
      success: function (result) {
        time_id = result
      }
    });
    return time_id
  }

  getTimeSlotId = (startTime, endTime) => {
    let time_slot_id
    $.ajax({
      url: "/get/service/time_slot",
      type: "POST",
      async: false,
      data: {
        'startTime': startTime,
        'endTime': endTime,
      },
      success: function (result) {
        time_slot_id = result
      }
    });
    return time_slot_id
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

  // $(document).on('click', (e) => {
  //   if (typeof $(e.target).data('original-title') == 'undefined' &&
  //     !$(e.target).parents().is('.popoverlist')) {
  //     $('.popoverlist').popover('hide');
  //     $('.selected-popover-content').popover('hide');
  //   };
  //   $(this).css('z-index', 8);
  //   $('.tooltipevent').remove();
  // });

});

var serverTime = new Date();

updateTime = () => {
  serverTime = new Date(serverTime.getTime() + 1000);
  $('.fc-now-indicator-arrow').html(serverTime.getHours() + ":" + (serverTime.getMinutes() < 10 ? '0' : '') + serverTime.getMinutes());
}

$(() => {
  updateTime();
  setInterval(updateTime, 1000);
});

$(() => {

  var doc = new jsPDF();
  var specialElementHandlers = {
    '#editor': function (element, renderer) {
      return true;
    }
  };

  $('#print-apt-pdf').click(() => {
    doc.fromHTML($('#upComingEventCalendar').html(), 15, 15, {
      'width': 170,
      'elementHandlers': specialElementHandlers
    });
    doc.save('sample-file.pdf');
  });

});

// $('#fauxBlockContent').tooltip({
//   title: "This Is Working ",
// trigger: 'hover',
// placement: 'right',
// container: 'body',
// template: '<div class="tooltip-template"> Test </div>'

// $('#fauxBlockContent').tooltip({
//   title: " ",
//   trigger: 'hover',
//   placement: 'right',
//   container: 'body',
//   template: '<div class="tooltip-template"> Test </div>'
// });

$('#fauxBlockContent').tooltip({
  // title: "title",
  placement: 'left',
  trigger: 'hover',
  // container: 'body',
  animation: false,
  html: true,
  // template: eventInfo.event.extendedProps.POP_OVER,
  content: `
    <div class="tooltip-template" style="display:block;">
      <div class="tooltip-header-event">
        <p style="font-weight:bold;"> P-Content 1 </p> <span> S-Content 1 </span>
      </div>
      <div class="tooltip-body">
        <div class="tooltip-font-color">
            <span style="font-weight:bolder;color:#7F7F7F;font-size:12px;"> S-Content 2 </span>
            <div class="timeforflex" style="color:#7F7F7F;"> <small> Small Content </small>
                <div>

                </div>
            </div>
        </div>
      </div>
    </div>
  `,
});

toggleRebookSelect = (e) => {
  $('.fauxBlockContent').removeClass('selected');
  $(e).addClass('selected');
  $("#AddBookingForm #service_categ_id").val($(e).attr("data-service-category"));
  service_categ_func()
  $("#AddBookingForm #sub_categ_id").val($(e).attr("data-sub-category"));
  $("#AddBookingForm #appointment_platform").val($(e).attr("data-appointment-platform"));
}

rebookPastVisitData = (partner_id) => {
  $.ajax({
    url: "/get/rebook/appointment/client",
    type: "POST",
    async: false,
    data: {
      'partner_id': partner_id,
    },
    success: function (result) {
      var resultJSON = jQuery.parseJSON(result);
      $('fieldset.rebookpast #Rebook-fauxBlockContent').empty();
      setTimeout(function () {
        $.each(resultJSON, function (key, value) {
          var content = ''
          $.each(value, function (jkey, jvalue) {
            c_data = jvalue.split('%')
            content += `<li id="fauxBlockContent" class="appt fauxBlockContent" onclick="toggleRebookSelect(this)" 
            data-service-category="`+ c_data[3] + `" data-sub-category="` + c_data[4] + `" data-appointment-platform="` + c_data[5] + `"
            >
            <span class="appt-service">
                <i class="icon-addon"></i>
            `+ c_data[0] + `
            </span>
            <span class="appt-staff">`+ c_data[1] + `</span>
            <span class="appt-price">`+ c_data[2] + ` AED</span>
          </li>`})

          $('fieldset.rebookpast #Rebook-fauxBlockContent').append(`
            <h3 class="appt-date">
              <span>`+ key + `</span>
            </h3>`+ content);
        });
      }, 500);

    }
  });
}

editable_appointment_form = () => {
  $(".editable_content").css("pointer-events","auto");
  $(".content_show").attr("style","display:block !important;");
  $(".content_hide").attr("style","display:none !important;");
 
  // $(".edit_appointment_custom").css("pointer-events","all"); 
  // $('#service_categ_id option:selected').remove();

  console.log("helloooooo")
  checkTherapistServiceDuration()
  


  
    $.ajax({
      url: "/therapist/edit/custom",
      type: "POST",
      async: false,
      data: {
        'durationcustom': $("#time_id").val(),
        // 'therapist': therapist,
        
      },
      success: function (result) {
    
        console.log("hiiii boss done",$("#time_id").val())
        
        sessionStorage.setItem("time_slot_id_custom",result);
        service_categ_func();
        
        console.log("completeddd",sessionStorage.getItem("time_slot_id_custom"))
      }
    });
    
 }
