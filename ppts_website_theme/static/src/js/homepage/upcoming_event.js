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
  
    var handleDateClick = (date) => {
      console.log(date);
      $(".fc-day-header").removeClass("dateactivebtn");
      $("[data-date='" + date + "'").addClass("dateactivebtn");
    };
  
    var eventRenderAppend = (date) => {
      $.ajax({
        url: "/theme/upcoming_event/render",
        type: "POST",
        async: false,
        data: {
          date: date,
        },
        success: function (result) {
          var resultJSON = jQuery.parseJSON(result);
  
          $("#calendarEventsContainer").empty();
          $.each(resultJSON, function (key, value) {
            listItem =
              `<div class="calenday-eventlist-item">
                          <div class="cal-event-img">
                          <label class="filtercatlabel">` +
              value.type +
              `</label>
                          <img src="/ppts_website_theme/static/src/img/post1.png" />
                          </div>
                          <div class="eventfullinfos">
                          <div class="event-typoingo">
                          <div class="eventtitleinfos">
                          <h5>` +
              value.name +
              `</h5> <label class="training chipsone">Training</label> <label class="chipsone">Event</label>
                          <label class="meditation chipsone">Meditation</label>
                          </div>
                          <div class="eventinfos">
                          <label><i class="fas fa-map-marker-alt"></i>` +
              value.location +
              `</label>
                          <label><i class="far fa-calendar-minus"></i>` +
              value.date +
              `</label>
                          <label><i class="far fa-clock"></i>` +
              value.time +
              `</label>
                          <label><i class="far fa-user"></i>` +
              value.facilitator +
              `</label>
                          </div>
                          </div>
                          <div class="event-listbtn">
                          <button class="borderedbtn">Enquire Now</button>
                          <button class="fullbutton">Book Now <b> 120 <i>AED </i> </b></button>
                          </div>
                          </div>
                          </div>`;
            $("#calendarEventsContainer").append(listItem);
          });
        },
      });
    };
  
    var monthStringArrmL = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];
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
    var weekStringArrmS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    let thListIds = [
      "fullcalenderTableTh1",
      "fullcalenderTableTh2",
      "fullcalenderTableTh3",
      "fullcalenderTableTh4",
      "fullcalenderTableTh5",
      "fullcalenderTableTh6",
      "fullcalenderTableTh7",
    ];
  
    var calendarEl = document.getElementById("calendar-hmt");
    const date = new Date();
    var selectedDate =
      (date.getMonth() + 1 > 9
        ? date.getMonth() + 1
        : "0" + (date.getMonth() + 1)) +
      "-" +
      (date.getDate() > 9 ? date.getDate() : "0" + date.getDate()) +
      "-" +
      date.getFullYear();
    var displayDate = "";
    var countDate = 1;
    var thList;
  
    var calendar = new FullCalendar.Calendar(calendarEl, {
      plugins: ["dayGrid"],
      defaultView: "dayGridWeek",
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
    });
  
    calendar.render();
  
    $("#datepicker")
      .datepicker({
        autoclose: true,
        todayHighlight: true
      })
      .on("changeDate", function (e) {
        // `e` here contains the extra attributes
        if (e?.date) {
          console.log("date", e);
          var d = new Date(e.date);
          calendar.gotoDate(d);
          var active_date = new Date(e.date);
          var month = active_date.getMonth() + 1;
          var day = active_date.getDate();
          var output =
            active_date.getFullYear() +
            "-" +
            (("" + month).length < 2 ? "0" : "") +
            month +
            "-" +
            (("" + day).length < 2 ? "0" : "") +
            day;
          $("#datepicker > input").val(output);
          handleDateClick(output);
          eventRenderAppend(output);
        }
      });
  
    setTimeout(function () {
      $("#calendar-hmt > div.fc-header-toolbar").children().not(":first").remove();
      $("#calendar-hmt > div.fc-view-container").children().not(":first").remove();
  
      var active_date = new Date();
      var month = active_date.getMonth() + 1;
      var day = active_date.getDate();
      var output =
        active_date.getFullYear() +
        "-" +
        (("" + month).length < 2 ? "0" : "") +
        month +
        "-" +
        (("" + day).length < 2 ? "0" : "") +
        day;
      handleDateClick(output);
      $("#datepicker > input").val(output);
      $("#calendarEventsContainer").empty();
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
    }, 500);
  
    document
      .getElementById("currentCalendarWeekLeftArrow")
      .addEventListener("click", () => {
        calendar.prev(); // call method
      });
  
    document
      .getElementById("currentCalendarWeekRightArrow")
      .addEventListener("click", () => {
        calendar.next(); // call method
      });
  });
  