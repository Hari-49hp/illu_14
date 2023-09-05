$(document).ready(function () {
    var calendarEl = document.getElementById('room-calendar-dashbord');

    var calendar = new FullCalendar.Calendar(calendarEl, {
      plugins: [ 'interaction', 'resourceTimeGrid' ],
      timeZone: 'local',
      selectable: true,
      slotLabelFormat: {
        hour: 'numeric',
        minute: '2-digit',
        hour12: false
      },
      header: {
        left: 'title today prev,next',
        center: '',
        right: ''
      },
      select: function(info) {
        localStorage.setItem("room_booking_startTime", info.startStr);
        localStorage.setItem("room_booking_endTime", info.endStr);
        localStorage.setItem("room_booking_date", info.start);
        localStorage.setItem("room_booking_room_id", info.resource.id);
        window.location.href = "/room/dashbord/booking";
      },
      eventRender: function(info) {
        console.log(info,'lll')
        console.log(info.event.extendedProps.services,'lll')
        var env_type1
        var env_type2
        var location1
        var location2
        var service_if1
        var service_if2

        if ($('#header_gender').val() != 'all' && $('#header_gender').val() != undefined){
          env_type1 = $('#header_gender').val()
          env_type2 = info.event.extendedProps.av_type
        }
        else{
          env_type1 = 1
          env_type2 = 1
        }

        if ($('#header_location').val() != 'all' && $('#header_location').val() != undefined){
          location1 = $('#header_location').val()
          location2 = info.event.extendedProps.location_id
        }
        else{
          location1 = 1
          location2 = 1
        }

        if ($('#header_services').val() != 'all' && $('#header_services').val() != undefined){
          service_if1 = parseInt($('#header_services').val())
          service_if2 = info.event.extendedProps.services
        }
        else{
          service_if1 = 1
          service_if2 = [1]
        }
        console.log(parseInt($('#header_services').val()))
        console.log(info.event.extendedProps.services)
        console.log($.inArray(service_if1, service_if2) !== -1)
        return env_type1 === env_type2 && $.inArray(service_if1, service_if2) !== -1 && parseInt(location1) === location2 

      },
      defaultView: 'resourceTimeGridDay',
      resources: '/room/calendar/resources',
      events: '/room/calendar/events',
    });

    calendar.render();

    $('#header_gender , #header_location').on('change',function(){
      calendar.rerenderEvents();
    });

});