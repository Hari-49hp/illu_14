document.addEventListener('DOMContentLoaded', function () {
  var $calPopOver;

  if (localStorage.getItem("calendar_view_type") == null) {
    localStorage.setItem("calendar_view_type", "Day")
  }

  if (localStorage.getItem("calendar_view_type") == "Day") {
    $("#calendar-event-mindbody").css("display", "block");
    $(".day-view-filters-div").css("display", "block");
    $("#calendar-event-mindbody-week-view").css("display", "none");
  }


  var events_url_response

  if (window.location.pathname === '/appointment/calendar'){
    var events_url_response = '/event/calendar/resources/events/apt'
  }
  else{
    var events_url_response = '/event/calendar/resources/events/evnt'
  }
  

  var calendarEl = document.getElementById('calendar-event-mindbody');
  var zone = new Date().toLocaleTimeString('en-us', {
    timeZoneName: 'short'
  }).split(' ')[2]

  if (localStorage.getItem("fullcalendar-date") === null) {
    var date = new Date();
    var initialdateGet = date.yyyymmdd()
  } else {
    var date = new Date(localStorage.getItem("fullcalendar-date"));
    var initialdateGet = date.yyyymmdd();
  }
  if (localStorage.getItem("fullcalendar-date") === 'today') {
    var date = new Date();
    var initialdateGet = date.yyyymmdd()
  }

  var filter
  var calendar = new FullCalendar.Calendar(calendarEl, {
    plugins: ['interaction', 'resourceTimeGrid'],
    selectable: true,
        timeZone: 'local', //timezonedict[zone.toString()]
        nowIndicator: true,

        customButtons: {
          homeButton: {
            text: 'Home',
            click: function () {
              window.location.href = "/web#action=672&model=appointment.appointment&view_type=list&cids=&menu_id=479"
            }
          },
        },

        header: {
          left: 'homeButton today title prev,next resourceTimeGridDay,timeGridWeek',
          center: '',
          right: ''
        },
        timeFormat: 'H:mm',
        aspectRatio: 1.605,
        titleFormat: {
          weekday: 'short',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        },
        initialView: 'resourceTimeGridDay',
        contentHeight: "auto",
        handleWindowResize: true,
        themeSystem: 'bootstrap',
        defaultDate: initialdateGet,
        refetchResourcesOnNavigate: true,
        defaultView: 'resourceTimeGridDay',
        slotLabelFormat: {
          hour: 'numeric',
          minute: '2-digit',
          hour12: false
        },
        eventTimeFormat: { // like '14:30:00'
        hour: '2-digit',
        minute: '2-digit',
          // meridiem: 'short'
          hour12: false
        },
        select: function (info) {
          var today_datel = new Date();
          if (info.start >= today_datel) {
            $("#editAvail-client-add").css("display","none");
            $(".openButton").click();
            $(".legend-custom").css("display", "none");
            $("#addAvail").css("display", "block");
            $(".fasilitator-name-sidebar").text('Add Availability for ' + info.resource.title);
            $("#facilitator_selection").val(info.resource.title);
            $(".page-footer").css("display", "block");
            $(".multiday-add-avail").css("display", "block");

            var start_time_split = info.startStr.split("T");
            var end_time_split = info.endStr.split("T");
            start_timel = start_time_split[1].slice(0, -3)
            end_timel = end_time_split[1].slice(0, -3)
            start_time = start_timel.slice(0, -6)
            end_time = end_timel.slice(0, -6)

            var datel = new Date($('#calendar-event-mindbody > div.fc-toolbar.fc-header-toolbar > div.fc-left > h2').text());
            var day = ("0" + datel.getDate()).slice(-2);
            var month = ("0" + (datel.getMonth() + 1)).slice(-2);
            var today = datel.getFullYear() + "-" + (month) + "-" + (day);

            $("#avail-start_time").val(start_time)
            $("#avail-end_time").val(end_time)
            $("#avail-start_time-cus").val(start_time)
            $("#avail-end_time-cus").val(end_time)

            $("#date-add-avail").val(today)
          }
        },
        eventRender: function (info) {
          if (info.event.extendedProps.invoice_status === "paid") {
            pay_st = '<i class="fa fa-circle color-green" style="color:green !important;"></i>'
          } else {
            pay_st = '<i class="fa fa-circle color-red" style="color:red !important;"></i>'
          }

          var startaDate = new Date(Date.parse(info.event.start));
          var endaDate = new Date(Date.parse(info.event.end));
          var dateString = '';
          var h_st = startaDate.getHours();
          var m_st = startaDate.getMinutes();
          if (h_st < 10) h_st = '0' + h_st;
          if (m_st < 10) m_st = '0' + m_st;
          start_dateString = h_st + ':' + m_st;

          var dateString = '';
          var h_en = endaDate.getHours();
          var m_en = endaDate.getMinutes();
          if (h_en < 10) h_en = '0' + h_en;
          if (m_en < 10) m_en = '0' + m_en;
          end_dateString = h_en + ':' + m_en;
          if (info.event.classNames[0] === 'fc-bg-facilitator-event-default-color') {
            $(info.el).tooltip({
              title: " ",
              trigger: 'hover',
              template: '<div class="tooltip-template">' +
              '<div style="background-color:#666;" class="tooltip-header-event">' +
              '<span>' + info.event.title + '</span>' +
              '</div><div class="tooltip-body"><div class="tooltip-font-color">' +
              '<span>' + start_dateString + ' - ' + end_dateString + '</span></div></div></div>'
            });
          }
          if (info.event.classNames[0] === 'fc-bg-facilitator-available-grey-color') {
            $(info.el).tooltip({
              title: " ",
              trigger: 'hover',
              placement: 'left',
              template: '<div class="tooltip-template">' +
              '<div style="background-color:#666;" class="tooltip-header-event">' +
              '<span> Book ' + info.event.title + '</span>' +
              '</div><div class="tooltip-body"><div class="tooltip-font-color">' +
              '<span>' + info.event.extendedProps.services + '</span></div></div></div>'
            });
          }
          if (info.event.extendedProps.event_type_appoinment === 'True') {
            $(info.el).tooltip({
              title: " ",
              template: '<div class="tooltip-template">' +
              '<div class="' + info.event.extendedProps.tooltip_name + '">' +
              '<span>' + info.event.extendedProps.client + '</span>' +
              '<span class="float-right">' + info.event.extendedProps.phone + '</span>' +
              '</div><div class="tooltip-body"><div class="tooltip-font-color">' +
              '<span>' + start_dateString + ' - ' + end_dateString + '</span>' +
              '<span class="float-right">' +
              '<img class="calendar-icon" src="https://static.mindbodyonline.com/a/asp/adm/images/icon-bm-schedule-overlay-calendar.png"/>'+ pay_st +'</span></div>' +
              '<div class="tooltip-font-color" style="margin-top: 3px;">' + info.event.title + '</div></div></div>'
            });
          }
          if (localStorage.getItem("calendar_view_type") == "Day") {
            setTimeout(function () {
              $('#bookedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-new').length)
              $('#confirmedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-confirm').length)
              $('#arrivedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-arrive').length)
              $('#completedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-done').length)
              $('#noshowNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-cancel').length)

            }, 1000);
          }

          //   $('#bookedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-new').length)
          // $('#confirmedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-confirm').length)
          // $('#arrivedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-arrive').length)
          // $('#completedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-done').length)
          // $('#noshowNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-cancel').length)
        },

        eventClick: function (info) {

          // var today_datel = new Date();
          // if (0 === 0) {
            $("#fac_id").val(info.event.id)
            if (info.el.classList[4] === 'fc-bg-facilitator-available-grey-color') {
              $('.bs-popover-right').removeClass('show');
              $('.bs-popover-right').addClass('hide');
              if ($(".fc-time-grid-event").hasClass("border-popover-highlight")) {
                $(".fc-time-grid-event").removeClass("border-popover-highlight");
              }

              $('.context-menu').removeClass('show');
              $('.context-menu').addClass('hide');

              $(info.el).popover({
                title: "title",
                placement: 'right',
                trigger: 'click',
                template: '<ul id="context-menu" class="context-menu context-right ctx-right"><li><img id="popper-close-btn" onclick="close_btn_app()" src="https://clients.mindbodyonline.com/asp/images/close.png"></li><li><a href="/web#id=17&action=765&model=availability.availability&view_type=form&cids=1&menu_id=540" class="checkout" title=""><i class="fa fa-calendar"></i><span id="popover-edit-today-schedule">Edit today schedule</span></a></li><li><a href="#" class="checkout"><i class="fa fa-calendar"></i><span class="popover-add-availability">Add Appointment</span></a></li></ul>'
              });
              $(".context-menu").remove();
              $(info.el).popover('show');

              $("#popper-close-btn").click(function () {
                $('.bs-popover-right , .bs-popover-left').removeClass('show');
                // $('.bs-popover-right , .bs-popover-left').addClass('hide');
                if ($(".fc-time-grid-event").hasClass("border-popover-highlight")) {
                  $(".fc-time-grid-event").removeClass("border-popover-highlight");
                }
              });

              $(".popover-add-availability").click(function () {

                $(".openButton").click();
                $(".legend-custom").css("display", "none");
                $("#editAvail").css("display", "block");

                $('.context-menu').removeClass('show');
                $('.context-menu').addClass('hide');
                $("#popper-close-btn").click(function () {
                  $('.bs-popover-right , .bs-popover-left').removeClass('show');
                  $('.bs-popover-right , .bs-popover-left').addClass('hide');
                  if ($(".fc-time-grid-event").hasClass("border-popover-highlight")) {
                    $(".fc-time-grid-event").removeClass("border-popover-highlight");
                  }
                  $('.context-menu').removeClass('show');
                  $('.context-menu').addClass('hide');
                });


              });

            }
    // }

    var today_datel = new Date();
    // if (info.event.start >= today_datel) {

        // $.ajax({
        //     url: "/event/calendar/resources/services/resajax",
        //     type: 'POST',
        //     async: false,
        //     data: {'ap_id':info.event.extendedProps.ap_id},
        //     success: function(result) {
        //         if(result === 'paid'){
        //             $(".tab-payment-status-show").html("Paid");
        //             $("#tab-payment-status").html("<img class='tab-view-pane' style='width: 12px;' src='https://static.mindbodyonline.com/a/asp/adm/images/icon_green_circle.png'/>");
        //         } else {
        //             $(".tab-payment-status-show").html("Unpaid");
        //             $("#tab-payment-status").html("<img class='tab-view-pane' style='width: 12px;' src='https://static.mindbodyonline.com/a/asp/adm/images/icon_red_circle.png'/>");
        //         }
        //     },
        // });
        if (info.event.extendedProps.invoice_status === "paid") {
          $(".tab-payment-status-show").html("Paid");
          $("#DIV_paid_status").html("Paid");
          $("#services-searchbar").attr('disabled','disabled');

          $("#tab-payment-status").html("<img class='tab-view-pane' style='width: 12px;' src='https://static.mindbodyonline.com/a/asp/adm/images/icon_green_circle.png'/>");
        } else {
          $(".tab-payment-status-show").html("Unpaid");
          $("#tab-payment-status").html("<img class='tab-view-pane' style='width: 12px;' src='https://static.mindbodyonline.com/a/asp/adm/images/icon_red_circle.png'/>");
        }
        $("#editAvail-client-add > div:nth-child(5) > div.hover-tab.tab-payment-balance-show").html("Balance amount: " + info.event.extendedProps.balance + info.event.extendedProps.currency_id)

        if (info.el.classList[4] === 'fc-bg-facilitator-appoinment-new' || info.el.classList[4] === 'fc-bg-facilitator-appoinment-confirm' || info.el.classList[4] === 'fc-bg-facilitator-appoinment-arrive' || info.el.classList[4] === 'fc-bg-facilitator-appoinment-done' || info.el.classList[4] === 'fc-bg-facilitator-appoinment-cancel') {
          $(".openButton").click();
          $("#editAvail-client-add").css('display', 'block');
          $(".page-footer").css('display', 'block');
          $(".legend-custom").css('display', 'none');

          $('.bs-popover-right , .bs-popover-left').removeClass('show');
          $('.bs-popover-right , .bs-popover-left').addClass('hide');
          if ($(".fc-time-grid-event").hasClass("border-popover-highlight")) {
            $(".fc-time-grid-event").removeClass("border-popover-highlight");
          }

          $(".editAvail-client-name").text(info.event.extendedProps.client);
          $("#editAvail-client-name-fi").val(info.event.extendedProps.client);
          $("#editAvail-client-name-id").val(info.event.extendedProps.client_id);
          $("#editAvail-client-phone-fi").val(info.event.extendedProps.mobile);
          $("#editAvail-client-email-fi").val(info.event.extendedProps.client_email);
          $("#editAvail-client-date-fi").val(info.event.extendedProps.ap_date);
          $("#services_offer").val(info.event.extendedProps.appointments_type_id);
          $("#start_time_app").val(info.event.extendedProps.ap_start_time);
          $("#end_time_app").val(info.event.extendedProps.ap_end_time);
          $("#length_app").val(info.event.extendedProps.ap_length);
          $("#app_id").val(info.event.extendedProps.app_id);
          $("#app_line_id").val(info.event.extendedProps.ap_line_id);
          $("#fac_id").val(info.event.extendedProps.fac_id);
          $("#resource_app").val(info.event.extendedProps.apt_room_id);
          $("#note_app").val(info.event.extendedProps.notes);

          action_lst = ''
          modify_url = '/web#id=' + info.event.extendedProps.app_id + '&model=appointment.appointment&view_type=form'
          if (info.event.extendedProps.status == 'new') {
            // action_lst += '<li><a href="javascript:void(0)" class="checkout popover-checkout" title=""><i class="fa fa-shopping-basket"></i><span id="popover-checkout-span">Checkout</span></a></li>'
            action_lst += '<li><a href="/popover/action/cancel_early/' + info.event.extendedProps.app_id + '" class="popover-earlyCancel"><i class="fa fa-times"></i><span>Early Cancel</span></a></li>'
            action_lst += '<li title=""><a href="/popover/action/confirm/' + info.event.extendedProps.app_id + '" class="popover-confirmed"><i class="fa fa-square-o"></i><span>Mark Confirmed</span></a></li>'
            action_lst += '<li title=""><a href="/popover/action/arrive/' + info.event.extendedProps.app_id + '" class="popover-arrived"><i class="fa fa-square-o"></i><span>Mark Arrived</span></a></li>'
            action_lst += '<li><a href="' + modify_url + '" class="move"><i class="fa fa-pencil-square-o"></i><span> Modify</span></a></li>'
          }
          if (info.event.extendedProps.status == 'confirm') {
            action_lst += '<li><a href="javascript:void(0)" class="checkout popover-checkout" title=""><i class="fa fa-shopping-basket"></i><span id="popover-checkout-span">Checkout</span></a></li>'
            action_lst += '<li><a href="javascript:void(0)" class="retail popover-retails" title=""><i class="fa fa-book"></i><span id="popover-retails-span">Retail</span></a></li>'
            action_lst += '<li><a href="/popover/action/cancel_early/' + info.event.extendedProps.app_id + '" class="popover-earlyCancel"><i class="fa fa-times"></i><span>Early Cancel</span></a></li>'
            action_lst += '<li title=""><a href="#" class="confirmed"><i class="fa fa-check-square-o"></i><span>Confirmed</span></a></li>'
            action_lst += '<li title=""><a href="/popover/action/arrive/' + info.event.extendedProps.app_id + '" class="popover-arrived"><i class="fa fa-square-o"></i><span>Mark Arrived</span></a></li>'
            action_lst += '<li><a href="' + modify_url + '" class="move"><i class="fa fa-pencil-square-o"></i><span> Modify</span></a></li>'
          }
          if (info.event.extendedProps.status == 'partially_cancelled') {
            action_lst += '<li><a href="javascript:void(0)" class="checkout popover-checkout" title=""><i class="fa fa-shopping-basket"></i><span id="popover-checkout-span">Checkout</span></a></li>'
            action_lst += '<li><a href="javascript:void(0)" class="retail popover-retails" title=""><i class="fa fa-book"></i><span id="popover-retails-span">Retail</span></a></li>'
            action_lst += '<li><a href="/popover/action/cancel_early/' + info.event.extendedProps.app_id + '" class="popover-earlyCancel"><i class="fa fa-times"></i><span>Early Cancel</span></a></li>'
            action_lst += '<li title=""><a href="#" class="confirmed"><i class="fa fa-check-square-o"></i><span>Confirmed</span></a></li>'
            action_lst += '<li title=""><a href="/popover/action/arrive/' + info.event.extendedProps.app_id + '" class="popover-arrived"><i class="fa fa-square-o"></i><span>Mark Arrived</span></a></li>'
            action_lst += '<li><a href="' + modify_url + '" class="move"><i class="fa fa-pencil-square-o"></i><span> Modify</span></a></li>'
          }
          if (info.event.extendedProps.status == 'ongoing') {
            action_lst += '<li><a href="javascript:void(0)" class="checkout popover-checkout" title=""><i class="fa fa-shopping-basket"></i><span id="popover-checkout-span">Checkout</span></a></li>'
            action_lst += '<li><a href="javascript:void(0)" class="retail popover-retails" title=""><i class="fa fa-book"></i><span id="popover-retails-span">Retail</span></a></li>'
            action_lst += '<li><a href="/popover/action/cancel_early/' + info.event.extendedProps.app_id + '" class="popover-earlyCancel"><i class="fa fa-times"></i><span>Early Cancel</span></a></li>'
            action_lst += '<li title=""><a href="#" class="confirmed"><i class="fa fa-check-square-o"></i><span>Confirmed</span></a></li>'
            action_lst += '<li title=""><a href="/popover/action/arrive/' + info.event.extendedProps.app_id + '" class="popover-arrived"><i class="fa fa-square-o"></i><span>Mark Arrived</span></a></li>'
            action_lst += '<li><a href="' + modify_url + '" class="move"><i class="fa fa-pencil-square-o"></i><span> Modify</span></a></li>'
          }
          if (info.event.extendedProps.status == 'arrive') {
            action_lst += '<li><a href="javascript:void(0)" class="checkout popover-checkout" title=""><i class="fa fa-shopping-basket"></i><span id="popover-checkout-span">Checkout</span></a></li>'
            action_lst += '<li><a href="javascript:void(0)" class="retail popover-retails" title=""><i class="fa fa-book"></i><span id="popover-retails-span">Retail</span></a></li>'
            action_lst += '<li><a href="/popover/action/cancel_early/' + info.event.extendedProps.app_id + '" class="popover-earlyCancel"><i class="fa fa-times"></i><span>Early Cancel</span></a></li>'
            action_lst += '<li title=""><a href="#" class="confirmed"><i class="fa fa-check-square-o"></i><span>Confirmed</span></a></li>'
            action_lst += '<li title=""><a href="#" class="popover-arrived"><i class="fa fa-check-square-o"></i><span>Arrived</span></a></li>'
            action_lst += '<li><a href="' + modify_url + '" class="move"><i class="fa fa-pencil-square-o"></i><span> Modify</span></a></li>'
          }
          if (info.event.extendedProps.status == 'done') {
            action_lst += '<li><a href="/popover/action/cancel_early/' + info.event.extendedProps.app_id + '" class="popover-earlyCancel"><i class="fa fa-times"></i><span>Early Cancel</span></a></li>'
            action_lst += '<li><a href="/popover/action/cancel_early/' + info.event.extendedProps.app_id + '" class="popover-earlyCancel"><i class="fa fa-times"></i><span>Late Cancel</span></a></li>'
            action_lst += '<li title=""><a href="#" class="confirmed"><i class="fa fa-check-square-o"></i><span>Confirmed</span></a></li>'
            action_lst += '<li title=""><a href="#" class="popover-arrived"><i class="fa fa-check-square-o"></i><span>Arrived</span></a></li>'
            action_lst += '<li><a href="' + modify_url + '" class="move"><i class="fa fa-pencil-square-o"></i><span> Modify</span></a></li>'
          }
          // if (info.event.extendedProps.status == 'cancel') {
            // action_lst += '<li><a href="javascript:void(0)" class="checkout popover-checkout" title=""><i class="fa fa-shopping-basket"></i><span id="popover-checkout-span">Checkout</span></a></li>'
            // action_lst += '<li><a href="/popover/action/cancel_early/' + info.event.extendedProps.app_id + '" class="popover-earlyCancel"><i class="fa fa-times"></i><span>Early Cancel</span></a></li>'
            // action_lst += '<li title=""><a href="/popover/action/confirm/' + info.event.extendedProps.app_id + '" class="popover-confirmed"><i class="fa fa-square-o"></i><span>Mark Confirmed</span></a></li>'
            // action_lst += '<li title=""><a href="/popover/action/arrive/' + info.event.extendedProps.app_id + '" class="popover-arrived"><i class="fa fa-square-o"></i><span>Mark Arrived</span></a></li>'
            // action_lst += '<li><a href="' + modify_url + '" class="move"><i class="fa fa-pencil-square-o"></i><span> Modify</span></a></li>'
          // }

          if (info.event.extendedProps.status != 'cancel') {
            $(info.el).addClass("border-popover-highlight");
            $(info.el).popover({
              title: "title",
              placement: 'right',
              trigger: 'click',
              template: '<ul id="context-menu" class="context-menu context-right ctx-right"><li><img id="pop-app-close" onclick="close_btn_app()" src="https://clients.mindbodyonline.com/asp/images/close.png"></li>' + action_lst + '</ul>'

            });
            $(".context-menu").remove();
            $(info.el).popover('show');

            $("#pop-app-close").click(function () {
             $('.bs-popover-right , .bs-popover-left').removeClass('show');
                // $('.bs-popover-right , .bs-popover-left').addClass('hide');
                if ($(".fc-time-grid-event").hasClass("border-popover-highlight")) {
                  $(".fc-time-grid-event").removeClass("border-popover-highlight");
                }
              });
          }

          $("#popover-retails-span").click(function(){
            $("#retails-wizard").show();
            $('.bs-popover-right,.bs-popover-left').removeClass('show');
            $('.bs-popover-right,.bs-popover-left').addClass('hide');
            if ($(".fc-time-grid-event").hasClass("border-popover-highlight")) {
              $(".fc-time-grid-event").removeClass("border-popover-highlight");
            }

            $.ajax({
              url: "/pos/session/list/wiz",
              type: 'POST',
              async:false,
              data: {
              },
              success: function(result) {
                var resultJSON = jQuery.parseJSON(result);
                $('.pos-session-list').replaceWith("<ul class='pos-session-list'></ul>")
                $.each(resultJSON,function(key,value){
                  $('.pos-session-list').append(
                    "<a href='/pos/session/list/redirect/"+key+"/"+info.event.extendedProps.client_id+"/"+info.event.extendedProps.app_id+"'>"+ value +"</a><br/>"  ); 
                });
              },
            });


          });

          $(".close-btn-wiz").click(function(){
            $("#retails-wizard").hide();
          });

          $("#popover-checkout-span").click(function () {
            $("#popper-wizard").show();
            $('.bs-popover-right,.bs-popover-left').removeClass('show');
            $('.bs-popover-right,.bs-popover-left').addClass('hide');
            if ($(".fc-time-grid-event").hasClass("border-popover-highlight")) {
              $(".fc-time-grid-event").removeClass("border-popover-highlight");
            }
    // $(".context-menu").removeClass('show');
    // $(".context-menu").addClass('hide');

    setTimeout(function () {
      if ($("div").hasClass("DIV_CONTENT_1") === false) {
        $(".add-cart-lst-itemms").append("<span class='no-item-crt'>No item in cart</span>");
      }
      $("#demo-content").hide();
      $(".popper-content").removeClass("d-none");
      var header_name = info.event.extendedProps.client_name;
      $("#DIV_13").text(header_name.charAt(0));
      $("#DIV_14").text(header_name);
      var partner_id
      var order_id
      $.ajax({
        url: "/get/sale/order/details",
        type: 'POST',
        async: false,
        data: {
          "sale_id": info.event.extendedProps.sale_id,
        },
        success: function (result) {
          var resultJSON = jQuery.parseJSON(result);
          var list
          $.each(resultJSON, function (key, value) {
            list += "<div class='koh-tab-content-body'><div class='koh-faq'><div class='koh-faq-question' onclick='order_line_expend()'><div class='line-item-pt-icon'><i class='fa fa-chevron-right'></i></div>" +
            "<div class='line-item-pt-name' sale-order-line='" + value.line_id + "'>" + value.product_name + "</div>" +
            "<div class='line-item-pt-price'>" + value.product_price + value.product_currency + "</div></div>" +
            "<div class='koh-faq-answer lt-lane-add'><div class='lt-lane-details'>" +
            "<div class='line-item-pt-desc'> Paying for 1 service </div></div>" +
            "<div class='lt-lane-rmv'><a class='line-item-pt-desc-ed ul-line' href='/web#id=" + value.line_id + "&action=811&model=sale.order.line&view_type=form&cids=1&menu_id=216'>Edit</a>" +
            "<div class='ul-line'><a class='ul-line ul-line-rmv' href='/sale/order/line/rmv/" + value.line_id + "'>Remove</a></div></div></div></div></div>"

            $("#DIV_651").text(value.date);
            $("#DIV_661").text(value.sales_person);
            $("#DIV_656").text(value.address);
            partner_id = value.partner_id
            order_id = value.order_id
            $("#promo-order-id").val(order_id)
            $("input[name=partner_promo_id]").val(partner_id)
            
            $("#DIV_690").text(value.subtotal + value.product_currency);
            $("#DIV_696").text(value.taxes + value.product_currency);
            $("#DIV_699").text(value.total + value.product_currency);
          });


          if (!$("div").hasClass("DIV_CONTENT_1")) {
            $(".add-cart-lst-itemms").append("<span class='no-item-crt'>No item in cart</span>");
          }

          var tt = list.substr(9);
          $(".koh-tab-content-body").replaceWith(tt)
          $.ajax({
            url: "/pos/cart/line",
            type: 'POST',
            async: false,
            data: {
              'partner_id': partner_id
            },
            success: function (result) {
              var resultJSON = jQuery.parseJSON(result);
              var list = ''
              $.each(resultJSON, function (key, value) {
                list += "<div id='DIV_CONTENT_1' pos-line-id='" + value.pos_id + "' class='ado-rplace DIV_CONTENT_1'><div id='DIV_CONTENT_2'><div id='DIV_CONTENT_3'><div id='DIV_CONTENT_4'><div id='DIV_CONTENT_5'><div id='DIV_CONTENT_6'><div id='DIV_CONTENT_7'><div id='DIV_CONTENT_8'><div id='DIV_CONTENT_9'><div id='DIV_CONTENT_10'>" +
                "<span id='SPAN_11'>" + value.product_name + "</span>" +
                "</div><div id='DIV_CONTENT_28'>" +
                value.product_name +
                "</div></div><div id='DIV_CONTENT_29'><i class='fa fa-trash rmv-line-items' style='font-size: 25px;'></i></div></div></div></div></div></div></div></div></div>"
              });
              $(".ado-rplace").replaceWith(list);
              $(".no-item-crt").remove();
            },
          });

          var products = []
          $.ajax({
            url: "/products/list",
            type: 'POST',
            async: false,
            data: {},
            success: function (result) {
              var resultJSON = jQuery.parseJSON(result);
              $.each(resultJSON, function (key, value) {
                products.push(value.product_name)
              });
            },
          });

          var products = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.whitespace,
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            local: products
          });

          var services_searchbar = $('#services-searchbar').typeahead({
            hint: true,
            highlight: true,
            /* Enable substring highlighting */
            minLength: 1 /* Specify minimum characters required for showing result */
          }, {
            name: 'Client',
            source: products,
          });

          $('#services-searchbar').on('typeahead:selected', function (e, datum) {
            $.ajax({
              url: "/pos/line/add",
              type: 'POST',
              async: false,
              data: {
                'product': datum,
                'partner': partner_id
              },
              success: function (result) {
                $(".no-item-crt").remove();
                $(".add-cart-lst-itemms").append("<div id='DIV_CONTENT_1' class='ado-rplace DIV_CONTENT_1'><div id='DIV_CONTENT_2'><div id='DIV_CONTENT_3'><div id='DIV_CONTENT_4'><div id='DIV_CONTENT_5'><div id='DIV_CONTENT_6'><div id='DIV_CONTENT_7'><div id='DIV_CONTENT_8'><div id='DIV_CONTENT_9'><div id='DIV_CONTENT_10'>" +
                  "<span id='SPAN_11'>" + datum + "</span>" +
                  "</div><div id='DIV_CONTENT_28'>" +
                  datum +
                  "</div></div><div id='DIV_CONTENT_29'><i class='fa fa-trash rmv-line-items' style='font-size: 25px;'></i></div></div></div></div></div></div></div></div></div>");

                // setTimeout(function(){ 
                //     $("div#DIV_650").click();
                // }, 4000);

                // setTimeout(function(){ 
                //     $('#services-searchbar').val(null); 
                // }, 4000);

                $(".rmv-line-items").click(function () {
                  $.ajax({
                    url: "/pos/line/rmv",
                    type: 'POST',
                    async: false,
                    data: {
                      'line_id': $(this).closest("#DIV_CONTENT_1").attr('pos-line-id')
                    },
                    success: function (result) {},
                  });

                  $(this).closest("#DIV_CONTENT_1").remove();
                  $(".no-item-crt").remove();
                  if ($("div").hasClass("DIV_CONTENT_1") === false) {
                    $(".add-cart-lst-itemms").append("<span class='no-item-crt'>No item in cart</span>");
                  }

                });
              },
            });
          }).on('typeahead:autocompleted', function (e, datum) {
          });

        },
      });


$(".context-menu").css('display', 'none');
$(".rmv-line-items").click(function () {
  $.ajax({
    url: "/pos/line/rmv",
    type: 'POST',
    async: false,
    data: {
      'line_id': $(this).closest("#DIV_CONTENT_1").attr('pos-line-id')
    },
    success: function (result) {},
  });

  $(this).closest("#DIV_CONTENT_1").remove();
  $(".no-item-crt").remove();
  if ($("div").hasClass("DIV_CONTENT_1") === false) {
    $(".add-cart-lst-itemms").append("<span class='no-item-crt'>No item in cart</span>");
  }

});
$(".koh-faq-question").click(function () {
  $(this).parent().find(".koh-faq-answer").toggle();
  $(this).find(".fa").toggleClass('active');

});

$("#DIV_bottom_btn23").click(function () {
  $(".DIV_CONTENT_1").remove();
  if ($("div").hasClass("DIV_CONTENT_1") === false) {
    $(".add-cart-lst-itemms").append("<span class='no-item-crt'>No item in cart</span>");
  }
  $.ajax({
    url: "/pos/line/add_cart",
    type: 'POST',
    async: false,
    data: {
      'partner_id': partner_id,
      'order_id': order_id,
    },
    success: function (result) {
      var resultJSON = jQuery.parseJSON(result);
      $.each(resultJSON, function (key, value) {
        $(".line-item-cart").append("<div class='koh-tab-content-body'><div class='koh-faq'><div class='koh-faq-question' onclick='order_line_expend()'><div class='line-item-pt-icon'><i class='fa fa-chevron-right'></i></div>" +
          "<div class='line-item-pt-name' sale-order-line='" + value.sale_line_id + "'>" + value.product_name + "</div>" +
          "<div class='line-item-pt-price'>" + value.product_price + value.product_currency + "</div></div>" +
          "<div class='koh-faq-answer lt-lane-add'><div class='lt-lane-details'>" +
          "<div class='line-item-pt-desc'> Paying for 1 service </div></div>" +
          "<div class='lt-lane-rmv'><div class='line-item-pt-desc-ed ul-line'>Edit</div>" +
          "<div class='ul-line'>Remove</div></div></div></div></div>");
      });

    },
  });

});




$("#DIV_703,#DIV_704,#SPAN_717").unbind().click(function () {
  $.ajax({
    url: "/pos/process/checkout",
    type: 'POST',
    async: false,
    data: {
      'order_id': order_id,
    },
    success: function (result) {
      var resultJSON = jQuery.parseJSON(result);
      window.location.href = resultJSON.url;
    },
  });
});

$(".ul-line-rmv").click(function () {
  $(this).closest(".koh-tab-content-body").remove();
});


}, 2000);

});

}

},

resources: '/event/calendar/resources/',
events: events_url_response,

resourceRender: function (renderInfo, successCallback) {
  var datel = new Date($('#calendar-event-mindbody > div.fc-toolbar.fc-header-toolbar > div.fc-left > h2').text());
  var day = ("0" + datel.getDate()).slice(-2);
  var month = ("0" + (datel.getMonth() + 1)).slice(-2);
  var today = datel.getFullYear() + "-" + (month) + "-" + (day);
  $.ajax({
    url: "/event/calendar/resources/resajax",
    type: 'POST',
    async: false,
    data: {
      "date": today,
    },
    success: function (result) {
      var resultJSON = jQuery.parseJSON(result);
      list = ''
      $.each(resultJSON, function (key, value) {
        list += "<li><a class='dropdown-item' href='/web#id=&action=665&model=availability.availability&view_type=form&cids=1&menu_id=488'>" + value + "</a></li>"
      });
              // $("#calendar-event-mindbody > div.fc-view-container > div > table > thead > tr > td > div > table > thead > tr > th.fc-axis.fc-widget-header").replaceWith("<th class='fc-axis fc-widget-header' style='width: 42px;background: #424242;'><div class='dropdown'><button class='btn btn-default dropdown-toggle dropdown-toggle-none' type='button' data-toggle='dropdown' style='padding: 0px;color: #fff;'><i class='fa fa-plus'></i> Add</button><ul class='dropdown-menu add-res-dropdown'></ul></div></div>");
            },
          });

          // $("#calendar-event-mindbody > div.fc-toolbar.fc-header-toolbar > div.fc-left > h2").each(function() {
          //   $(this).html($(this).html().replace(/,/g, ''));
          // });

          // if (!$('.header_location').length) {
          // var location_option
          // var services_option
          // $.ajax({
          //   url: "/event/calendar/resources/location/resajax",
          //   type: 'POST',
          //   async: false,
          //   data: {},
          //   success: function(result) {
          //     var resultJSON = jQuery.parseJSON(result);
          //     $.each(resultJSON, function(key, value) {
          //       location_option += "<option value='" + key + "'>" + value + "</option>"
          //     });
          //   },
          // });
          // $.ajax({
          //   url: "/event/calendar/resources/services/resajax",
          //   type: 'POST',
          //   async: false,
          //   data: {},
          //   success: function(result) {
          //     var resultJSON = jQuery.parseJSON(result);
          //     $.each(resultJSON, function(key, value) {
          //       services_option += "<option value='" + key + "'>" + value + "</option>"
          //     });
          //   },
          // });

          // $("#calendar-event-mindbody > div.fc-toolbar.fc-header-toolbar > div.fc-left > div:nth-child(4)").replaceWith("<div class='fc-button-group'><button type='button' class='fc-resourceTimeGridDay-button fc-button fc-button-primary fc-button-active'>day</button><button type='button' class='fc-timeGridWeek-button fc-button fc-button-primary'>week</button></div><div class='fc-button-group'><select name='header_location' class='header_location header-selection' id='header_location'><option value='all'>All</option>" + location_option + "</select><select name='header_services' class='header_services header-selection right-margin-header' id='header_services'><option value='all'>All Service Category</option>" + services_option + "</select> <button id='instructor-wizard-btn'>All Instructors</button>  <select name='header_gender' class='header_gender header-selection' id='header_gender'><option value='all'>All</option><option value='male'>Male</option><option value='female'>Female</option></select></div>")

          // }


        },
      });

calendar.render();


function default_reset_data() {
  localStorage.setItem("header_instructor", "all");
  $('#header_instructor-filter').multiselect('selectAll', false);

  $.ajax({
    url: "/event/calendar/resources/pass/session",
    type: 'POST',
    async: false,
    data: {
      "header_filter_reset": "True",
    },
    success: function (result) {
      localStorage.setItem("header_location", "all");
      localStorage.setItem("header_services", "all");
      localStorage.setItem("header_instructor", "all");
      localStorage.setItem("header_gender", "all");
      localStorage.setItem("header_filter_reset", "ff");
      localStorage.setItem("header_instructor_refresh", "yes");

    },
  });
}
$('.fc-today-button').click(function () {

  var date = new Date();
  var initialdateGet = date.yyyymmdd()

  localStorage.setItem("current-date-calendar", initialdateGet);

  if (document.getElementById('calendar_view_type').innerHTML == "Day") {

    default_reset_data();
          // location.reload();

          var datel = new Date();
          var day = ("0" + datel.getDate()).slice(-2);
          var month = ("0" + (datel.getMonth() + 1)).slice(-2);
          var today = datel.getFullYear() + "-" + (month) + "-" + (day);

          localStorage.setItem("fullcalendar-date", today);

        }
      });

$('.fc-prev-button').click(function () {

        // setTimeout(function(){ 
        //     $("th.fc-axis").html("<a class='fc-axis-a' href='/web#id=&action=678&model=availability.availability&view_type=form&cids=1&menu_id=488' style='color:#fff'><i class='fa fa-plus'></i> Add</a>");
        // }, 1000);

        if (localStorage.getItem("calendar_view_type") == "Day") {


          var date1 = localStorage.getItem("current-date-calendar");
          var date = new Date(Date.parse(date1));
          date.setDate(date.getDate() - 1);

          var newDate = date.yyyymmdd();

          localStorage.setItem("current-date-calendar", newDate);


          var datel = new Date($('#calendar-event-mindbody > div.fc-toolbar.fc-header-toolbar > div.fc-left > h2').text());
          var day = ("0" + datel.getDate()).slice(-2);
          var month = ("0" + (datel.getMonth() + 1)).slice(-2);
          var today = datel.getFullYear() + "-" + (month) + "-" + (day);

          localStorage.setItem("fullcalendar-date", today);


          default_reset_data();
          location.reload();
        }


        if (localStorage.getItem("calendar_view_type") == "Week") {

          // var date1 = localStorage.getItem("current-date-calendar");
          // var date = new Date( Date.parse( date1 ) ); 
          // date.setDate( date.getDate() - 1 );

          // var newDate = date.yyyymmdd(); 

          // localStorage.setItem("current-date-calendar",newDate);

          // default_reset_data();
          // location.reload();
        }

      });

$('.fc-next-button').click(function () {

  if (localStorage.getItem("calendar_view_type") == "Day") {
          // setTimeout(function(){ 
          //     $("th.fc-axis").html("<a class='fc-axis-a' href='/web#id=&action=678&model=availability.availability&view_type=form&cids=1&menu_id=488' style='color:#fff'><i class='fa fa-plus'></i> Add</a>");
          // }, 1000);
          var date1 = localStorage.getItem("current-date-calendar");
          var date = new Date(Date.parse(date1));
          date.setDate(date.getDate() + 1);

          var newDate = date.yyyymmdd();

          localStorage.setItem("current-date-calendar", newDate);

          default_reset_data();
          var datel = new Date($('#calendar-event-mindbody > div.fc-toolbar.fc-header-toolbar > div.fc-left > h2').text());
          var day = ("0" + datel.getDate()).slice(-2);
          var month = ("0" + (datel.getMonth() + 1)).slice(-2);
          var today = datel.getFullYear() + "-" + (month) + "-" + (day);

          localStorage.setItem("fullcalendar-date", today);
          location.reload();
        }

        if (localStorage.getItem("calendar_view_type") == "Week") {
          // var date1 = localStorage.getItem("current-date-calendar");
          // var date = new Date( Date.parse( date1 ) ); 
          // date.setDate( date.getDate() + 1 );

          // var newDate = date.yyyymmdd(); 

          // localStorage.setItem("current-date-calendar",newDate);

          // default_reset_data();
          // location.reload();
        }

      });


$(".date-picker").datepicker().on('changeDate', function (e) {
  var d = new Date(e.dates[0]);
  localStorage.setItem("fullcalendar-date", d.yyyymmdd())
  calendar.gotoDate(d);
  setTimeout(function () {
    if (localStorage.getItem("calendar_view_type") == "Day") {
      setTimeout(function () {
        $('#bookedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-new').length)
        $('#confirmedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-confirm').length)
        $('#arrivedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-arrive').length)
        $('#completedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-done').length)
        $('#noshowNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-cancel').length)

      }, 1000);
    }
    if (localStorage.getItem("calendar_view_type") == "Week") {
      setTimeout(function () {
        $('#bookedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-new').length)
        $('#confirmedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-confirm').length)
        $('#arrivedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-arrive').length)
        $('#completedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-done').length)
        $('#noshowNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-cancel').length)

      }, 1000);
    }



  }, 500);

});



$(".openButton").click(function () {
  $('.bs-popover-right').removeClass('show');
  $('.bs-popover-right').addClass('hide');
  if ($(".fc-time-grid-event").hasClass("border-popover-highlight")) {
    $(".fc-time-grid-event").removeClass("border-popover-highlight");
  }

  document.getElementById("main").style.marginLeft = "20%";
  document.getElementById("sidebar").style.width = "20%";
  document.getElementById("sidebar").style.display = "block";
  $(".openButton").css("display", "none");
  $(".closeButton").css("display", "block");
  $(".fc-header-toolbar").css("margin-left", "51px");
  $(".ui-datepicker-inline").css("border-color", "#c9f0f5 !important");
  $(".date-picker").css("display", "block");
  $(".toggler-unshow").css("display", "none");
  $(".toggler-show").css("display", "block");
  $(".legend-custom").css("display", "block");

});

$(".cancelBtn").click(function () {
  $('.bs-popover-right').removeClass('show');
  $('.bs-popover-right').addClass('hide');
  if ($(".fc-time-grid-event").hasClass("border-popover-highlight")) {
    $(".fc-time-grid-event").removeClass("border-popover-highlight");
  }

  document.getElementById("main").style.marginLeft = "2%";
  document.getElementById("sidebar").style.width = "2%";
  $(".openButton").css("display", "block");
  $(".closeButton").css("display", "none");
  $(".date-picker").css("display", "none");
  $(".toggler-unshow").css("display", "none");
  $(".toggler-show").css("display", "none");
  $(".fc-header-toolbar").css("margin-left", "3px");
  $("#addAvail").css("display", "none");
  $(".page-footer").css("display", "none");
  $(".multiday-add-avail").css("display", "none");
  $(".legend-custom").css("display", "none");
  $("#editAvail-client-add").css("display", "none");

});

$(".closeButton").click(function () {
  $('.bs-popover-right').removeClass('show');
  $('.bs-popover-right').addClass('hide');
  if ($(".fc-time-grid-event").hasClass("border-popover-highlight")) {
    $(".fc-time-grid-event").removeClass("border-popover-highlight");
  }

  document.getElementById("main").style.marginLeft = "2%";
  document.getElementById("sidebar").style.width = "2%";
  $(".openButton").css("display", "block");
  $(".closeButton").css("display", "none");
  $(".date-picker").css("display", "none");
  $(".toggler-unshow").css("display", "none");
  $(".toggler-show").css("display", "none");
  $(".fc-header-toolbar").css("margin-left", "3px");
  $("#addAvail").css("display", "none");
  $(".page-footer").css("display", "none");
  $(".multiday-add-avail").css("display", "none");
  $(".legend-custom").css("display", "none");
  $("#editAvail-client-add").css("display", "none");
  $("#editAvail").css("display", "none");

});

$(".toggler-show").click(function () {
  $(".date-picker").css("display", "none");
  $(".toggler-unshow").css("display", "block");
  $(".toggler-show").css("display", "none");
});
$(".toggler-unshow").click(function () {
  $(".date-picker").css("display", "block");
  $(".toggler-unshow").css("display", "none");
  $(".toggler-show").css("display", "block");
});


setTimeout(function () {

  $("#popper-close-btn").click(function () {
    $('.bs-popover-right , .bs-popover-left').removeClass('show');
    $('.bs-popover-right , .bs-popover-left').addClass('hide');
    if ($(".fc-time-grid-event").hasClass("border-popover-highlight")) {
      $(".fc-time-grid-event").removeClass("border-popover-highlight");
    }
  }); 
  $("#pop-app-close").click(function () {
    $('.bs-popover-right , .bs-popover-left').removeClass('show');
    $('.bs-popover-right , .bs-popover-left').addClass('hide');
    if ($(".fc-time-grid-event").hasClass("border-popover-highlight")) {
      $(".fc-time-grid-event").removeClass("border-popover-highlight");
    }
  });

  if ($("button").hasClass("dropdown-toggle") === false) {
  }

  $('.filter-reset').click(function () {

    $.ajax({
      url: "/event/calendar/resources/pass/session",
      type: 'POST',
      async: false,
      data: {
        "header_filter_reset": "True",
      },
      success: function (result) {
        localStorage.setItem("header_location", "all");
        localStorage.setItem("header_services", "all");
        localStorage.setItem("header_instructor", "all");
        localStorage.setItem("header_gender", "all");
        localStorage.setItem("header_filter_reset", "ff");

        location.reload();
      },
    });
              // $('#header_instructor-filter').multiselect('select', localStorage.getItem("header_instructor")); 
              $('#header_instructor-filter').multiselect('select', localStorage.getItem("header_instructor"));
            });
}, 1000);

setTimeout(function () {
  var modal = document.getElementById("instructor-wizard");
  var btn = document.getElementById("instructor-wizard-btn");
  var span = document.getElementsByClassName("close")[0];

  var modal_popper = document.getElementById("popper-wizard");
  var btn_popper = document.getElementsByClassName("popover-checkout");
  var span_popper = document.getElementsByClassName("close")[0];

          // $(".popover-checkout").click(function(){
          //   $('.bs-popover-right').removeClass('show');
          //   $('.bs-popover-right').addClass('hide');
          //   if($(".fc-time-grid-event").hasClass("border-popover-highlight")){ 
          //     $(".fc-time-grid-event").removeClass("border-popover-highlight");
          //   }
          //   $("#popper-wizard").css("display", "block") 
          // });


          // btn_popper.onclick = function() {
          //   $('.bs-popover-right').removeClass('show');
          //   $('.bs-popover-right').addClass('hide');
          //   if($(".fc-time-grid-event").hasClass("border-popover-highlight")){ 
          //     $(".fc-time-grid-event").removeClass("border-popover-highlight");
          //   }
          //   modal_popper.style.display = "block";

          // }
          // span_popper.onclick = function() {
          //   modal_popper.style.display = "none";
          // }

          // window.onclick = function(event) {
          //   if (event.target == modal_popper) {
          //     modal_popper.style.display = "none";
          //   }
          // }

          btn.onclick = function () {
            modal.style.display = "block";
            var datel = new Date($('#calendar-event-mindbody > div.fc-toolbar.fc-header-toolbar > div.fc-left > h2').text());
            var day = ("0" + datel.getDate()).slice(-2);
            var month = ("0" + (datel.getMonth() + 1)).slice(-2);
            var today = datel.getFullYear() + "-" + (month) + "-" + (day);
            var employee_option
            $.ajax({
              url: "/event/calendar/resources/instructor/resajax",
              type: 'POST',
              async: false,
              data: {
                'date': today,
              },
              success: function (result) {
                var resultJSON = jQuery.parseJSON(result);
                $.each(resultJSON, function (key, value) {
                  employee_option += "<option value='" + key + "'>" + value + "</option>"
                  $('#header_instructor-filter').append($('<option></option>').attr("value", key).text(value));
                });

                $('#header_instructor-filter').multiselect({
                  allSelectedText: 'All Instructor',
                  enableFiltering: true,
                  includeSelectAllOption: true,
                  enableCaseInsensitiveFiltering: true,
                  maxHeight: 400,
                  dropUp: true
                });

                if (localStorage.getItem("header_instructor")) {
                  var ins_local = localStorage.getItem("header_instructor").split(",")
                  $('#header_instructor-filter').multiselect('select', ins_local);
                } else {
                  $('#header_instructor-filter').multiselect('selectAll', false);
                }

                if (localStorage.getItem("header_instructor_refresh") == "yes") {
                  localStorage.setItem("header_instructor_refresh", "no");
                  $('#header_instructor-filter').multiselect('selectAll', false);


                }
              },
            });
          }
          var datel = new Date($('#calendar-event-mindbody > div.fc-toolbar.fc-header-toolbar > div.fc-left > h2').text());
          var day = ("0" + datel.getDate()).slice(-2);
          var month = ("0" + (datel.getMonth() + 1)).slice(-2);
          var today = datel.getFullYear() + "-" + (month) + "-" + (day);
          var employee_option
          $.ajax({
            url: "/event/calendar/resources/instructor/resajax",
            type: 'POST',
            async: false,
            data: {
              'date': today,
            },
            success: function (result) {
              var resultJSON = jQuery.parseJSON(result);
              count = 0;
              $.each(resultJSON, function (key, value) {
                count = count + 1;
              });
              // $('#instructor-wizard-btn').text("All Instructors(" + count + ")");

            },
          });
          span.onclick = function () {
            modal.style.display = "none";
          }
          window.onclick = function (event) {
            if (event.target == modal) {
              modal.style.display = "none";
            }
          }

          $(".header_location").val(localStorage.getItem("header_location"));
          $(".header_services").val(localStorage.getItem("header_services"));
          $(".header_instructor").val(localStorage.getItem("header_instructor"));
          $(".header_gender").val(localStorage.getItem("header_gender"));

          $('.header_location').on('change', function () {
            $.ajax({
              url: "/event/calendar/resources/pass/session",
              type: 'POST',
              async: false,
              data: {
                "header_location": $(".header_location").val(),
              },
              success: function (result) {
                localStorage.setItem("header_location", $(".header_location").val());
                // location.reload();
                calendar.refetchResources();
              },
            });
            $(".header_location").val(localStorage.getItem("header_location"));
          });

          $('.header_services').on('change', function () {
            $.ajax({
              url: "/event/calendar/resources/pass/session",
              type: 'POST',
              async: false,
              data: {
                "header_services": $(".header_services").val(),
              },
              success: function (result) {
                localStorage.setItem("header_services", $(".header_services").val());
                calendar.refetchResources();
              },
            });
            $(".header_services").val(localStorage.getItem("header_services"));
          });

          $('.header_gender').on('change', function () {
            $.ajax({
              url: "/event/calendar/resources/pass/session",
              type: 'POST',
              async: false,
              data: {
                "header_gender": $(".header_gender").val(),
              },
              success: function (result) {
                localStorage.setItem("header_gender", $(".header_gender").val());
                calendar.refetchResources();
              },
            });
            $(".header_gender").val(localStorage.getItem("header_gender"));
          });

          $('.filter-apply').click(function () {
            if ($('#header_instructor-filter').val().length === 0) {
              $(".header_instructor-err").removeClass("d-none");
              setTimeout(function () {
                $(".header_instructor-err").addClass("d-none");
              }, 2000);
            } else {
              $.ajax({
                url: "/event/calendar/resources/pass/session",
                type: 'POST',
                async: false,
                data: {
                  "header_instructor": $('#header_instructor-filter').val().toString(),
                },
                success: function (result) {
                  localStorage.setItem("header_instructor", $('#header_instructor-filter').val());
                  location.reload();
                },
              });
              $('#header_instructor-filter').multiselect('select', localStorage.getItem("header_instructor"));
              $("#instructor-wizard").css("display", "none");
            }
          });


          $(".fc-resourceTimeGridDay-button").click(function () {
            $("#calendar-event-mindbody").css("display", "block");
            $("#calendar-event-mindbody-week-view").css("display", "none");
            $(".fc-button-group-week").css("display", "none");
            document.getElementById('calendar_view_type').innerHTML = "Day";
            localStorage.setItem("calendar_view_type", "Day");

            $('#bookedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-new').length)
            $('#confirmedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-confirm').length)
            $('#arrivedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-arrive').length)
            $('#completedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-done').length)
            $('#noshowNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-cancel').length)

            location.reload();
          });

          $(".fc-timeGridWeek-button").click(function () {
            $("#calendar-event-mindbody").css("display", "none");
            $("#calendar-event-mindbody-week-view").css("display", "block");
            $(".fc-button-group-week").css("display", "block");
            document.getElementById('calendar_view_type').innerHTML = "Week";
            localStorage.setItem("calendar_view_type", "Week");
            setTimeout(function () {
              $('#bookedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-new').length)
              $('#confirmedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-confirm').length)
              $('#arrivedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-arrive').length)
              $('#completedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-done').length)
              $('#noshowNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-cancel').length)

            }, 1000);

            location.reload();
          });

          $("#calendar-event-mindbody > div.fc-view-container > div > table > thead > tr > td > div > table > thead > tr > th > div > div > a:nth-child(1)").click(function () {
            var fill_close = $(this).closest(".fc-resource-cell").attr('data-resource-id')
            var arr_close = []
            arr_close.push(fill_close)
            $("#calendar-event-mindbody").css("display", "none");
            $("#calendar-event-mindbody-week-view").css("display", "block");
            $(".fc-button-group-week").css("display", "block");
            document.getElementById('calendar_view_type').innerHTML = "Week";
            localStorage.setItem("calendar_view_type", "Week");

            localStorage.setItem("gotoweek_set", "True");
            localStorage.setItem("gotoweek_set_arr", arr_close);

            location.reload();

          });

        }, 500);

$(".openButton").click();


$(".rmv-line-items").click(function () {
  $.ajax({
    url: "/pos/line/rmv",
    type: 'POST',
    async: false,
    data: {
      'line_id': $(this).closest("#DIV_CONTENT_1").attr('pos-line-id')
    },
    success: function (result) {},
  });

  $(this).closest("#DIV_CONTENT_1").remove();
  $(".no-item-crt").remove();
  if ($("div").hasClass("DIV_CONTENT_1") === false) {
    $(".add-cart-lst-itemms").append("<span class='no-item-crt'>No item in cart</span>");
  }

});


});