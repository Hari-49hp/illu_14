$(document).ready(function () {
  var partners = []
  $.ajax({
    url: "/partner/list",
    type: 'POST',
    async:false,
    data: {
      // "unavail_name": $(".side-bar-name").text()
    },
    success: function(result) {
      var resultJSON = jQuery.parseJSON(result);
      $.each(resultJSON,function(key,value){
        partners.push(value)
      });
    },
  });

  var services = []
  $.ajax({
    url: "/appointment/services",
    type: 'POST',
    async:false,
    data: {
      // "unavail_name": $(".side-bar-name").text()
    },
    success: function(result) {
      var resultJSON = jQuery.parseJSON(result);
      $.each(resultJSON,function(key,value){
        $('#services_offer').append($('<option></option>').attr("value", key).text(value)); 
      });
    },
  });

  $.ajax({
    url: "/appointment/rooms",
    type: 'POST',
    async:false,
    data: {
      // "unavail_name": $(".side-bar-name").text()
    },
    success: function(result) {
      var resultJSON = jQuery.parseJSON(result);
      $.each(resultJSON,function(key,value){
        $('#resource_app').append($('<option></option>').attr("value", key).text(value)); 
      });
    },
  });

    // Constructing the suggestion engine
    var partners = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.whitespace,
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      local: partners
    });
    
    // Initializing the typeahead
    $('#searchbar').typeahead({
      hint: true,
      highlight: true, /* Enable substring highlighting */
      minLength: 1 /* Specify minimum characters required for showing result */
    },
    {
      name: 'Client',
      source: partners
    });

    var services = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.whitespace,
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      local: services
    });

    $('#services_offer').typeahead({
      hint: true,
      highlight: true, /* Enable substring highlighting */
      minLength: 1 /* Specify minimum characters required for showing result */
    },
    {
      name: 'Services',
      source: services,
    });

    $('#services_offer').on('change',function(){
      $.ajax({
        url: "/appointment/services/get/details",
        type: 'POST',
        async:false,
        data: {
          "service_app": $("#services_offer").val()
        },
        success: function(result) {
          console.log(result);
          $("#length_app").val(convertNumToTime(parseFloat(result)));
          // $("#length_app").val(result);
        },
      });

    });

    $('#start_time_app').on('change',function(){
      console.log($('#start_time_app').val(),1);
      console.log($('#length_app').val(),2);

      var oldDate = new Date("1/1/1900 " + $('#start_time_app').val());
      var hour = oldDate.getHours();
      var newDate = oldDate.setHours(hour + $("#length_app").val());
      console.log(newDate);

      console.log(getDifference($('#start_time_app').val(), $("#length_app").val()));
      $('#end_time_app').val(getDifference($('#start_time_app').val(), $("#length_app").val()));
    });


    function convertNumToTime(number) {
      var sign = (number >= 0) ? 1 : -1;
      number = number * sign;
      var hour = Math.floor(number);
      var decpart = number - hour;
      var min = 1 / 60;
      decpart = min * Math.round(decpart / min);
      var minute = Math.floor(decpart * 60) + '';
      if (minute.length < 2) {
        minute = '0' + minute; 
      }
      sign = sign == 1 ? '' : '-';
      time = sign + hour + ':' + minute;
      return time;
    }


    let getDifference = (time1, time2) => {
      var prodhrd = time1 + ":00";
      var conprod = time2 + ":00";
      prodhrdArr = prodhrd.split(":");
      conprodArr = conprod.split(":");
      var hh1 = parseInt(prodhrdArr[0]) + parseInt(conprodArr[0]);
      var mm1 = parseInt(prodhrdArr[1]) + parseInt(conprodArr[1]);
      var ss1 = parseInt(prodhrdArr[2]) + parseInt(conprodArr[2]);

      if (ss1 > 59) {
        var ss2 = ss1 % 60;
        var ssx = ss1 / 60;
        var ss3 = parseInt(ssx);//add into min
        var mm1 = parseInt(mm1) + parseInt(ss3);
        var ss1 = ss2;
      }
      if (mm1 > 59) {
        var mm2 = mm1 % 60;
        var mmx = mm1 / 60;
        var mm3 = parseInt(mmx);//add into hour
        var hh1 = parseInt(hh1) + parseInt(mm3);
        var mm1 = mm2;
      }
      if (mm1 === 0){
        mm1 = '00'
      }
      var finaladd = hh1 + ':' + mm1;
      return finaladd
    }

  });
