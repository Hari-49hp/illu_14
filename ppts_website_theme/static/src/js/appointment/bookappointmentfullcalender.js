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

  var monthStringArrmS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "June",
    "July",
    "Aug",
    "Sept",
    "Oct",
    "Nov",
    "Dec",
  ];
  var weekFullStringArr = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  var weekStringArrmS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  var weekStringTwoStringArr = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
  var isShowTime = false;


  // Getting Slots

  var handleDateClick = (date) => {
    $('#selected_appointment_date').val(date);
    isShowTime = true;
    $(".time-picker").removeClass("display-none");
    // timePicker

    $('#appointment-timepickerrows').empty();
    $.ajax({
      url: "/appointment/service/slot/filter",
      type: 'POST',
      async: false,
      data: {
        'therapist_id': $('#selected_service_therapist_id').val(),
        'booking_date': date,
        'time_id': $('#appointment_time_id').val(),
        'service_id': $('#selected_service_id').val(),
        'service_categ_id': $('#selected_service_categ_id').val(),
      },
      success: function (result) {
        var resultJSON = jQuery.parseJSON(result);

        $.each(resultJSON, function (key, value) {

          $('#appointment-timepickerrows').append(`
                                
                            <a class="timepickerbuttons" id="appointment-timepickerbuttons" data-slot-id="`+ value['id'] + `" >` + value['name'] + `</a>
                            
                         `);

        });

      },
    });



    // accessing the elements with same classname
    const timepickerbuttons = document.querySelectorAll('#appointment-timepickerbuttons');

    // adding the event listener by looping
    timepickerbuttons.forEach(element => {

      element.addEventListener("click", (e) => {
        $(".timepickerbuttons").removeClass("timeshooseactive");
        //$(this).addClass("selectedDate");
        e.currentTarget.classList.add('timeshooseactive');
        const slot_id = e.currentTarget.getAttribute("data-slot-id");
        $("#selected_appointment_slot_id").val(slot_id);
      });
    });





  };



  // Clear Slots

  var clearslotsClick = () => {


    $('#selected_appointment_date').val('');
    $(".time-picker").addClass("display-none");
    $('#appointment-timepickerrows').empty();
    $("#selected_appointment_slot_id").val('');
    $(".timepickerbuttons").removeClass("timeshooseactive");
  };




  // Start add slots method
  var add_calender_slot_method = () => {

    const add_calender_slot_method_for = document.querySelectorAll('#box-date-calender');
    $("#selected_appointment_slot_id").val('');
    $(".timepickerbuttons").removeClass("timeshooseactive");
    const date_elements = [];
    add_calender_slot_method_for.forEach(element => {
      var data_date = element.getAttribute("data-date");
      // data_date = data_date.split('-')
      date_elements.push(data_date);

      element.addEventListener("click", (e) => {

        window.scrollTo({ top: 600, behavior: 'smooth' });

        $(".box-date-calender").removeClass("selectedDate");
        $(".div_slot").removeClass("selectedDate");
        $(".month-fc-day-number").removeClass("selectedDate");
        e.currentTarget.classList.add('selectedDate');
        const selected_date = e.currentTarget.getAttribute("data-date");
        handleDateClick(selected_date)
        var div_slot = e.currentTarget.querySelectorAll('.div_slot')
        div_slot.forEach(div_slot => {
          div_slot.classList.add('selectedDate');
        });
        var month_day_number = e.currentTarget.querySelectorAll('.month-fc-day-number')
        month_day_number.forEach(month_day_number => {
          month_day_number.classList.add('selectedDate');
        });
      });

    });

    $.ajax({
      url: "/appointment/service/slot/count/filter",
      type: 'POST',
      async: false,
      data: {
        'therapist_id': $('#selected_service_therapist_id').val(),
        'booking_date': JSON.stringify(date_elements),
        'time_id': $('#appointment_time_id').val(),
        'service_id': $('#selected_service_id').val(),
        'service_categ_id': $('#selected_service_categ_id').val(),
      },
      success: function (result) {
        var resultJSON = jQuery.parseJSON(result);

        $.each(resultJSON, function (key, value) {
          if (value['count'] == 'N/A'){
            $(`div[data-date=${value['date']}] > .div_slot`).text(value['count']);
          }else{
            $(`div[data-date=${value['date']}] > .div_slot`).text(value['count'] + " Slots Available");
          }
        });

        // if (resultJSON.length === 0) {
        //   div_slot.forEach(div_slot => {
        //     div_slot.innerHTML = "";
        //   });
        // }
      },
    });

  };
  //end






  var calendarEl = document.getElementById("bookappointmentCalendar");

  var calendar = new FullCalendar.Calendar(calendarEl, {
    plugins: ["dayGrid", "dayGridMonth", "dayGridWeek"],
    defaultView: "dayGridMonth",
    columnHeaderFormat: {
      day: "numeric",
      month: "long",
      weekday: "short",
      omitCommas: true,
    },
    columnHeaderText: function (date) {
      return weekFullStringArr[date.getDay()];
    },
    dayRender: (info) => {
      console.log(info)
      console.log(info.date.getMonth())
      const item = info.date.getDate() + " " + monthStringArrmS[info.date.getMonth()];
      const outputDate = info.date.getFullYear() + "-" + (("" + (info.date.getMonth()+1)).length < 2 ? "0" : "") +
        (info.date.getMonth()+1) + "-" + (("" + info.date.getDate()).length < 2 ? "0" : "") + info.date.getDate();
      const parent_div = document.createElement("div");
      parent_div.classList.add("box-date-calender");
      parent_div.setAttribute("id", "box-date-calender");
      parent_div.setAttribute('data-date', outputDate);

      const div = document.createElement("div");
      div.classList.add("month-fc-day-number");
      div.setAttribute("id", "month-fc-day-number");
      if (info.el.classList.value.search("fc-other-month") >= 0) {
        div.classList.add("other-month-date");
      }
      div.setAttribute('data-date', outputDate);
      div.innerHTML = item;

      const div_slot = document.createElement("div");
      div_slot.setAttribute('data-date', outputDate);
      div_slot.classList.add("div_slot");
      div_slot.setAttribute("id", "month-fc-day-number");
      parent_div.appendChild(div)
      parent_div.appendChild(div_slot)

      info.el.appendChild(parent_div);
      //info.el.appendChild(div_slot);
      return '';
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
    }
  });


  let currentDate = calendar.getDate();
  let month = currentDate.getMonth()
  let mon_text = monthStringArrmS[month]
  let year = currentDate.getFullYear()
  year = year.toString();

  $("#currentCalendarWeekRange").text(mon_text + ' ' + year);

  add_calender_slot_method();

  calendar.render();


  setTimeout(function () {
    $(".time-picker").addClass("display-none");
  }, 500);


  /*
  // accessing the elements with same classname
  const date_select_month = document.querySelectorAll('#month-fc-day-number');
  
  // adding the event listener by looping
  date_select_month.forEach(element => {	
	
     element.addEventListener("click", (e) => {
          $(".month-fc-day-number").removeClass("selectedDate");
          //$(this).addClass("selectedDate");
          e.currentTarget.classList.add('selectedDate');
          const selected_date = e.currentTarget.getAttribute("data-date");
          handleDateClick(selected_date)
      });
  });
  */



  const appointment_time_id = document.querySelector('#appointment_time_id');

  appointment_time_id.addEventListener('change', (event) => {
    $('#selected_appointment_date').val();
    const selected_date = $('#selected_appointment_date').val();
    handleDateClick(selected_date);

    var div_slot = document.querySelectorAll('.div_slot')
    div_slot.forEach(element => {
      element.innerHTML = "";
    });

    add_calender_slot_method();

  });


  /*
  	
    document
      .getElementById("appointment_time_id")
      .addEventListener("click", () => {
      
        $('#selected_appointment_date').val();
       
        const selected_date = $('#selected_appointment_date').val();
      handleDateClick(selected_date);
      
      add_calender_slot_method();
      
      
      
        
      });
      
  */



  document.getElementById("open_appointment_calendar_menu").addEventListener("click", (e) => {

      $('#open_appointment_calendar_menu').html(`
        <i class="fa fa-spinner fa-spin"></i>Loading
      `)
      $('#open_appointment_calendar_menu').attr('disabled', 'disabled');

      setTimeout(() => {
        $('#open-therapist-menu').removeClass("active")
        $('#open-content-therapist-menu').removeClass("show active");
        $('#open-appointment-calendar-menu').last().addClass("active");
        $('#open-content-appointment-calendar-menu').last().addClass("show active");

        add_calender_slot_method();
      }, 100);

    });
    
    $("#open_appointment_calendar_menu_skip_sel_therapist").click(function(e){
    // document.getElementById("open_appointment_calendar_menu_skip_sel_therapist").addEventListener("click", (e) => {

      $('#open_appointment_calendar_menu').html(`
        <i class="fa fa-spinner fa-spin"></i>Loading
      `)
      $('#open_appointment_calendar_menu').attr('disabled', 'disabled');

      setTimeout(() => {
        $('#open-location-menu').removeClass("active")
        $('#open-content-location-menu').removeClass("show active");
        $('#open-appointment-calendar-menu').last().addClass("active");
        $('#open-content-appointment-calendar-menu').last().addClass("show active");

        add_calender_slot_method();
      }, 100);

    });



  document.getElementById("currentCalendarmonthRightArrow").addEventListener("click", () => {
      calendar.next(); // call method

      add_calender_slot_method();

      let currentDate = calendar.getDate();
      let month = currentDate.getMonth()
      let mon_text = monthStringArrmS[month]
      let year = currentDate.getFullYear()
      year = year.toString();

      $("#currentCalendarWeekRange").text(mon_text + ' ' + year);

      clearslotsClick();

    });

  document.getElementById("currentCalendarmonthLeftArrow").addEventListener("click", () => {

      calendar.prev(); // call method

      add_calender_slot_method();

      let currentDate = calendar.getDate();
      let month = currentDate.getMonth()
      let mon_text = monthStringArrmS[month]
      let year = currentDate.getFullYear()
      year = year.toString();

      $("#currentCalendarWeekRange").text(mon_text + ' ' + year);

      clearslotsClick();

    });

});

/*

function selectedDate_on_calender(date) {

    $(".month-fc-day-number").removeClass("selectedDate");
      $(this).addClass("selectedDate");
      const selected_date = date
      //handleDateClick(selected_date)
      // 2021-07-19
      // eventRenderAppend(selected_date);
    	
      alert(selected_date);
    	
  }
*/



