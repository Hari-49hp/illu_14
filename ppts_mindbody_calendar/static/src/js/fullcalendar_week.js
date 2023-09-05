document.addEventListener('DOMContentLoaded', function() {
  if(localStorage.getItem("calendar_view_type")=="Week")
  {
    $("#calendar-event-mindbody").css("display", "none");
    $(".day-view-filters-div").css("display", "none");

    $("#calendar-event-mindbody-week-view").css("display", "block");
    $(".fc-button-group-week").css("display", "block");

    $.ajax({
      url: "/event/calendar/resources/instructor/resajax",
      type: 'POST',
      async: false,
      data: {
        'date': 'True',
      },
      success: function(result) {
        var resultJSON = jQuery.parseJSON(result);
        $.each(resultJSON, function(key, value) {
          // employee_option += "<option value='" + key + "'>" + value + "</option>"
          $('#header_instructor-filter-week').append($('<option></option>').attr("value", key).text(value));
        });

        $('#header_instructor-filter-week').multiselect({
          allSelectedText: 'All Instructor',
          enableFiltering: true,
          includeSelectAllOption: true,
          enableCaseInsensitiveFiltering: true,
          maxHeight: 400,
          dropUp: true
        });
        $('#header_instructor-filter-week').multiselect('selectAll', false);

      },
    });
  }
  var $calPopOver;
  var calendarEl = document.getElementById('calendar-event-mindbody-week-view');
  var timezonedict = {'UTC+1':'A','UTC+10:30':'ACDT','UTC+9:30':'ACST','UTC-5':'ACT','UTC+9:30/+10:30':'ACT','UTC+8:45':'ACWST','UTC+4':'ADT','UTC-3':'ADT','UTC+11':'AEDT','UTC+10':'AEST','UTC+10:00/+11:00':'AET','UTC+4:30':'AFT','UTC-8':'AKDT','UTC-9':'AKST','UTC+6':'ALMT','UTC-3':'AMST','UTC+5':'AMST','UTC-4':'AMT','UTC+4':'AMT','UTC+12':'ANAST','UTC+12':'ANAT','UTC+5':'AQTT','UTC-3':'ART','UTC+3':'AST','UTC-4':'AST','UTC-4:00/-3:00':'AT','UTC+9':'AWDT','UTC+8':'AWST','UTC+0':'AZOST','UTC-1':'AZOT','UTC+5':'AZST','UTC+4':'AZT','UTC-12':'AoE','UTC+2':'B','UTC+8':'BNT','UTC-4':'BOT','UTC-2':'BRST','UTC-3':'BRT','UTC+6':'BST','UTC+11':'BST','UTC+1':'BST','UTC+6':'BTT','UTC+3':'C','UTC+8':'CAST','UTC+2':'CAT','UTC+6:30':'CCT','UTC-5':'CDT','UTC-4':'CDT','UTC+2':'CEST','UTC+1':'CET','UTC+13:45':'CHADT','UTC+12:45':'CHAST','UTC+9':'CHOST','UTC+8':'CHOT','UTC+10':'CHUT','UTC-4':'CIDST','UTC-5':'CIST','UTC-10':'CKT','UTC-3':'CLST','UTC-4':'CLT','UTC-5':'COT','UTC-6':'CST','UTC+8':'CST','UTC-5':'CST','UTC-6:00/-5:00':'CT','UTC-1':'CVT','UTC+7':'CXT','UTC+10':'ChST','UTC+4':'D','UTC+7':'DAVT','UTC+10':'DDUT','UTC+5':'E','UTC-5':'EASST','UTC-6':'EAST','UTC+3':'EAT','UTC-5':'ECT','UTC-4':'EDT','UTC+3':'EEST','UTC+2':'EET','UTC+0':'EGST','UTC-1':'EGT','UTC-5':'EST','UTC-5:00/-4:00':'ET','UTC+6':'F','UTC+3':'FET','UTC+13':'FJST','UTC+12':'FJT','UTC-3':'FKST','UTC-4':'FKT','UTC-2':'FNT','UTC+7':'G','UTC-6':'GALT','UTC-9':'GAMT','UTC+4':'GET','UTC-3':'GFT','UTC+12':'GILT','UTC+0':'GMT','UTC+4':'GST','UTC-2':'GST','UTC-4':'GYT','UTC+8':'H','UTC-9':'HDT','UTC+8':'HKT','UTC+8':'HOVST','UTC+7':'','UTC-10':'HST','UTC+9':'I','UTC+7':'ICT','UTC+3':'IDT','UTC+6':'IOT','UTC+4:30':'IRDT','UTC+9':'IRKST','UTC+8':'IRKT','UTC+3:30':'IRST','UTC+5:30':'IST','UTC+1':'IST','UTC+2':'IST','UTC+9':'JST','UTC+10':'K','UTC+6':'KGT','UTC+11':'KOST','UTC+8':'KRAST','UTC+7':'KRAT','UTC+9':'KST','UTC+4':'KUYT','UTC+11':'L','UTC+11':'LHDT','UTC+10:30':'LHST','UTC+14':'LINT','UTC+12':'M','UTC+12':'MAGST','UTC+11':'MAGT','UTC-9:30':'MART','UTC+5':'MAWT','UTC-6':'MDT','UTC+12':'MHT','UTC+6:30':'MMT','UTC+4':'MSD','UTC+3':'MSK','UTC-7':'MST','UTC-7:00/-6:00':'MT','UTC+4':'MUT','UTC+5':'MVT','UTC+8':'MYT','UTC-1':'N','UTC+11':'NCT','UTC-2:30':'NDT','UTC+12':'NFDT','UTC+11':'NFT','UTC+7':'NOVST','UTC+7':'NOVT','UTC+5:45':'NPT','UTC+12':'NRT','UTC-3:30':'NST','UTC-11':'NUT','UTC+13':'NZDT','UTC+12':'NZST','UTC-2':'O','UTC+7':'OMSST','UTC+6':'OMST','UTC+5':'ORAT','UTC-3':'P','UTC-7':'PDT','UTC-5':'PET','UTC+12':'PETST','UTC+12':'PETT','UTC+10':'PGT','UTC+13':'PHOT','UTC+8':'PHT','UTC+5':'PKT','UTC-2':'PMDT','UTC-3':'PMST','UTC+11':'PONT','UTC-8':'PST','UTC-8':'PST','UTC-8:00/-7:00':'PT','UTC+9':'PWT','UTC-3':'PYST','UTC-4':'PYT','UTC+8:30':'PYT','UTC-4':'Q','UTC+6':'QYZT','UTC-5':'R','UTC+4':'RET','UTC-3':'ROTT','UTC-6':'S','UTC+11':'SAKT','UTC+4':'SAMT','UTC+2':'SAST','UTC+11':'SBT','UTC+4':'SCT','UTC+8':'SGT','UTC+11':'SRET','UTC-3':'SRT','UTC-11':'SST','UTC+3':'SYOT','UTC-7':'T','UTC-10':'TAHT','UTC+5':'TFT','UTC+5':'TJT','UTC+13':'TKT','UTC+9':'TLT','UTC+5':'TMT','UTC+14':'TOST','UTC+13':'TOT','UTC+3':'TRT','UTC+12':'TVT','UTC-8':'U','UTC+9':'ULAST','UTC+8':'ULAT','UTC':'UTC','UTC-2':'UYST','UTC-3':'UYT','UTC+5':'UZT','UTC-9':'V','UTC-4':'VET','UTC+11':'VLAST','UTC+10':'VLAT','UTC+6':'VOST','UTC+11':'VUT','UTC-10':'W','UTC+12':'WAKT','UTC-3':'WARST','UTC+2':'WAST','UTC+1':'WAT','UTC+1':'WEST','UTC+0':'WET','UTC+12':'WFT','UTC-2':'WGST','UTC-3':'WGT','UTC+7':'WIB','UTC+9':'WIT','UTC+8':'WITA','UTC+14':'WST','UTC+1':'WST','UTC+0':'WT','UTC-11':'X','UTC-12':'Y','UTC+10':'YAKST','UTC+9':'YAKT','UTC+10':'YAPT','UTC+6':'YEKST','UTC+5':'YEKT','UTC+0':'Z'}
  var zone = new Date().toLocaleTimeString('en-us',{timeZoneName:'short'}).split(' ')[2]
  Date.prototype.yyyymmdd = function() {
    var yyyy = this.getFullYear().toString();
      var mm = (this.getMonth()+1).toString(); // getMonth() is zero-based
      var dd  = this.getDate().toString();
      return yyyy + "-" + (mm[1]?mm:"0"+mm[0]) + "-" + (dd[1]?dd:"0"+dd[0]); // padding
    };

    if (localStorage.getItem("fullcalendar-date") === null) {
      var date = new Date();
      var initialdateGet = date.yyyymmdd()
    } else {
      var date = new Date(localStorage.getItem("fullcalendar-date"));
      var initialdateGet = date.yyyymmdd();
    }
    if(localStorage.getItem("fullcalendar-date") === 'today'){
      var date = new Date();
      var initialdateGet = date.yyyymmdd()
    }

    var filter
    var set_count = "Fail"
    var calendar = new FullCalendar.Calendar(document.getElementById('calendar-event-mindbody-week-view'), {
      plugins: ['resourceTimeGrid'],
      timeZone: 'local', //timezonedict[zone.toString()]
      nowIndicator: true,

      customButtons: {
        dayViewButton: {
          text: 'Day',
          click: function() {
            $("#calendar-event-mindbody").css('display','block');
            $("#calendar-event-mindbody-week-view").css('display','none');
            document.getElementById('calendar_view_type').innerHTML="Day";
            localStorage.setItem("calendar_view_type","Day");
            location.reload();
          }
        },
        weekViewButton: {
          text: 'Week',
          click: function() {
            $("#calendar-event-mindbody").css('display','none');
            $("#calendar-event-mindbody-week-view").css('display','block');
            document.getElementById('calendar_view_type').innerHTML="Week";
            localStorage.setItem("calendar_view_type","Week");
            location.reload();
          }
        },
        homeButton: {
          text: 'Home',
          click: function() {
            window.location.href = "/web#action=672&model=appointment.appointment&view_type=list&cids=&menu_id=479"
          }
        },
        // filterViewButton: {
        //   text: 'filter',
        // }
      },

      header: {
        left: 'homeButton today title prev,next dayViewButton,weekViewButton',
        center: '',
        right: ''
      },
      timeFormat: 'H:mm',
      aspectRatio: 1.605,
      titleFormat: { weekday: 'short',
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' },
      initialView: 'timeGridWeek',
      contentHeight:"auto",
      handleWindowResize:true,
      themeSystem: 'bootstrap',
      defaultDate: initialdateGet,
      // refetchResourcesOnNavigate: true,
      defaultView: 'timeGridWeek',
      slotLabelFormat: {hour: 'numeric', minute: '2-digit', hour12: false},
      eventTimeFormat: { // like '14:30:00'
      hour: '2-digit',
      minute: '2-digit',
        // meridiem: 'short'
        hour12: false
      },
      select: function(info) {
        $(".openButton").click();
        $(".legend-custom").css("display", "none");
        $("#addAvail").css("display", "block");
        $(".fasilitator-name-sidebar").text('Add Availability for '+info.resource.title);
        $("#facilitator_selection").val(info.resource.title);
        $(".page-footer").css("display", "block");
        $(".multiday-add-avail").css("display", "block");

        var start_time_split = info.startStr.split("T");
        var end_time_split = info.endStr.split("T");
        start_timel = start_time_split[1].slice(0, -3) 
        end_timel = end_time_split[1].slice(0, -3)
        start_time = start_timel.slice(0, -6) 
        end_time = end_timel.slice(0, -6)

        var datel = new Date($('#calendar-event-mindbody-week-view > div.fc-toolbar.fc-header-toolbar > div.fc-left > h2').text());
        var day = ("0" + datel.getDate()).slice(-2);
        var month = ("0" + (datel.getMonth() + 1)).slice(-2);
        var today = datel.getFullYear()+"-"+(month)+"-"+(day);

        $("#avail-start_time").val(start_time)
        $("#avail-end_time").val(end_time)
        $("#date-add-avail").val(today)
      },
      eventRender: function(info) {
        set_count = "Pass"
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
        if (info.event.classNames[0] === 'fc-bg-facilitator-event-default-color'){
          $(info.el).tooltip({
            title : " ",
            trigger: 'hover',
            template : '<div class="tooltip-template">'+
            '<div style="background-color:#666;" class="tooltip-header-event">'
            +'<span>'+ info.event.title +'</span>'
            +'</div><div class="tooltip-body"><div class="tooltip-font-color">'
            +'<span>'+ start_dateString+' - '+ end_dateString +'</span></div></div></div>'
          });
        }
        if (info.event.classNames[0] === 'fc-bg-facilitator-available-grey-color'){
          $(info.el).tooltip({
            title : " ",
            trigger: 'hover',
            placement: 'left',
            template : '<div class="tooltip-template">'+
            '<div style="background-color:#666;" class="tooltip-header-event">'
            +'<span> Book '+ info.event.title +'</span>'
            +'</div><div class="tooltip-body"><div class="tooltip-font-color">'
            +'<span>'+ info.event.extendedProps.services +'</span></div></div></div>'
          });
        }
        if (info.event.extendedProps.event_type_appoinment === 'True'){
          $(info.el).tooltip({
            title : " ",
            template : '<div class="tooltip-template">'+
            '<div class="'+ info.event.extendedProps.tooltip_name +'">'
            +'<span>'+info.event.extendedProps.client+'</span>'
            +'<span class="float-right">'+info.event.extendedProps.phone+'</span>'
            +'</div><div class="tooltip-body"><div class="tooltip-font-color">'
            +'<span>'+ start_dateString +' - '+ end_dateString +'</span>'
            +'<span class="float-right">' 
            +'<img class="calendar-icon" src="https://static.mindbodyonline.com/a/asp/adm/images/icon-bm-schedule-overlay-calendar.png"/><i class="fa fa-circle color-green" style="color:green !important;"></i></span></div>'
            +'<div class="tooltip-font-color" style="margin-top: 3px;">'+ info.event.title +'</div></div></div>'
          });
        }
        var location_if1
        var location_if2
        var service_if1
        var service_if2
        var gender_if1
        var gender_if2
        if(localStorage.getItem("calendar_view_type")=="Week")
        {
          if ($('#header_location_week').val() != 'all' && $('#header_location_week').val() != undefined){
            location_if1 = parseInt($('#header_location_week').val())
            location_if2 = info.event.extendedProps.location
            // return parseInt($('#header_location_week').val()) === info.event.extendedProps.location
          }
          else{
            location_if1 = 1
            location_if2 = 1
          }

          if ($('#header_services_week').val() != 'all' && $('#header_services_week').val() != undefined){
            service_if1 = parseInt($('#header_services_week').val())
            service_if2 = info.event.extendedProps.services
          }
          else{
            service_if1 = 1
            service_if2 = [1]
          }

          if ($('#header_gender_week').val() != 'all' && $('#header_gender_week').val() != undefined){
            gender_if1 = $('#header_gender_week').val()
            gender_if2 = info.event.extendedProps.gender
          }
          else{
            gender_if1 = 1
            gender_if2 = 1
          }

          if(localStorage.getItem("calendar_view_type") === "Week"){
            setTimeout(function(){ 
              $('#bookedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-new').length)
              $('#confirmedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-confirm').length)
              $('#arrivedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-arrive').length)
              $('#completedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-done').length)
              $('#noshowNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-cancel').length)

            }, 1000);
          }

          return location_if1 === location_if2 && $.inArray(service_if1, service_if2) !== -1 && $.inArray(info.event.id, $("#header_instructor-filter-week").val()) !== -1 && gender_if1 === gender_if2
        }
      },


      events: '/event/calendar/resources/week/',
    // events: [
    //     {
    //     id: 'a',
    //     title: 'my event',
    //     start: '2021-02-01'
    //     }
    //     ],

  });

calendar.render();

$( ".toggler-show" ).click(function() {
  $(".date-picker").css("display", "none");
  $(".toggler-unshow").css("display", "block");
  $(".toggler-show").css("display", "none");
});
$( ".toggler-unshow" ).click(function() {
  $(".date-picker").css("display", "block");
  $(".toggler-unshow").css("display", "none");
  $(".toggler-show").css("display", "block");
});


setTimeout(function(){
  var modal = document.getElementById("instructor-wizard");
  var btn = document.getElementById("instructor-wizard-btn");
  var span = document.getElementsByClassName("close")[0];
  
  var modal_popper = document.getElementById("popper-wizard");
  var btn_popper = document.getElementsByClassName("popover-checkout");
  var span_popper = document.getElementsByClassName("close")[0];
  

  $(".fc-resourceTimeGridDay-button").click(function(){
    $("#calendar-event-mindbody").css("display", "block");
    $("#calendar-event-mindbody-week-view").css("display", "none");
    document.getElementById('calendar_view_type').innerHTML="Day";
    localStorage.setItem("calendar_view_type","Day");
    location.reload();

  });

  $(".fc-timeGridWeek-button").click(function(){
    $("#calendar-event-mindbody").css("display", "none");
    $("#calendar-event-mindbody-week-view").css("display", "block");
    document.getElementById('calendar_view_type').innerHTML="Week";
    localStorage.setItem("calendar_view_type","Week");
    location.reload();

  });
  // $("#calendar-event-mindbody-week-view > div.fc-toolbar.fc-header-toolbar > div.fc-left > div:nth-child(4) > button.fc-prev-button.fc-button.fc-button-primary").click(function(){
  //   setTimeout(function(){ 
  //     $('#bookedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-new').length)
  //     $('#confirmedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-confirm').length)
  //     $('#arrivedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-arrive').length)
  //     $('#completedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-done').length)
  //     $('#noshowNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-cancel').length)

  //   }, 500);
  // });
  // $("#calendar-event-mindbody-week-view > div.fc-toolbar.fc-header-toolbar > div.fc-left > div:nth-child(4) > button.fc-next-button.fc-button.fc-button-primary").click(function(){
  //   setTimeout(function(){ 
  //     $('#bookedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-new').length)
  //     $('#confirmedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-confirm').length)
  //     $('#arrivedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-arrive').length)
  //     $('#completedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-done').length)
  //     $('#noshowNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-cancel').length)

  //   }, 500);
  // });
  if(set_count === "Fail"){
    setTimeout(function(){ 
      $('#bookedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-new').length)
      $('#confirmedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-confirm').length)
      $('#arrivedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-arrive').length)
      $('#completedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-done').length)
      $('#noshowNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-cancel').length)

    }, 500);
  }

  if(localStorage.getItem("calendar_view_type")=="Week")
  {
    var location_option
    var services_option
    $.ajax({
      url: "/event/calendar/resources/location/resajax",
      type: 'POST',
      async:false,
      data: {},
      success: function(result) {
        var resultJSON = jQuery.parseJSON(result);
        $.each(resultJSON, function(key, value) {   
          $("#header_location_week").append("<option value='"+key+"'>"+value+"</option>");
        });
      },
    });
    $.ajax({
      url: "/event/calendar/resources/services/resajax",
      type: 'POST',
      async:false,
      data: {},
      success: function(result) {
        var resultJSON = jQuery.parseJSON(result);
        $.each(resultJSON, function(key, value) {   
          $("#header_services_week").append("<option value='"+key+"'>"+value+"</option>");
        });
      },
    });

    // $("#calendar-event-mindbody-week-view > div.fc-toolbar.fc-header-toolbar > div.fc-left > button.fc-filterViewButton-button.fc-button.fc-button-primary").replaceWith("<div class='fc-button-group-week'><select name='header_location_week' class='header_location_week header-selection' id='header_location_week'><option value='all'>All</option>"+location_option+"</select><select name='header_services_week' class='header_services_week header-selection right-margin-header' id='header_services_week'><option value='all'>All Service Category</option>"+services_option+"</select> <button id='instructor-wizard-btn-week'>All Instructors</button>  <select name='header_gender_week' class='header_gender_week header-selection' id='header_gender_week'><option value='all'>All</option><option value='male'>Male</option><option value='female'>Female</option></select></div>")
    $('#header_location_week').on('change',function(){
      calendar.rerenderEvents();
    });
    $('#header_services_week').on('change',function(){
      calendar.rerenderEvents();
    });
    $('#header_instructor-filter-week').on('change',function(){
      calendar.rerenderEvents();
    });
    $('#header_gender_week').on('change',function(){
      calendar.rerenderEvents();
    });

    if(localStorage.getItem("gotoweek_set")=="True"){
        // localStorage.setItem("gotoweek_set", "False");
        arr_v = []
        arr_v.push(localStorage.getItem("gotoweek_set_arr"))
        $('#header_instructor-filter-week').multiselect('select', arr_v);
      }
    }
  }, 500);


$(".date-picker").datepicker().on('changeDate', function(e) {

  var d = new Date(e.dates[0]);
  localStorage.setItem("fullcalendar-date", d.yyyymmdd())
  calendar.gotoDate(d);
  
  setTimeout(function() {
    if(localStorage.getItem("calendar_view_type")=="Day"){
      setTimeout(function(){ 
        $('#bookedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-new').length)
        $('#confirmedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-confirm').length)
        $('#arrivedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-arrive').length)
        $('#completedNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-done').length)
        $('#noshowNum').text($('#calendar-event-mindbody .fc-bg-facilitator-appoinment-cancel').length)

      }, 1000);
    }
    if(localStorage.getItem("calendar_view_type")=="Week"){
      setTimeout(function(){ 
        $('#bookedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-new').length)
        $('#confirmedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-confirm').length)
        $('#arrivedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-arrive').length)
        $('#completedNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-done').length)
        $('#noshowNum').text($('#calendar-event-mindbody-week-view .fc-bg-facilitator-appoinment-cancel').length)

      }, 1000);
    }
  }, 500);

});

});



