$(document).ready(function () {

var start_time = localStorage.getItem("room_booking_startTime")
var end_time = localStorage.getItem("room_booking_endTime")
var date1 = start_time.split("T");
var date2 = end_time.split("T");

var time_start = date1[1].split("+");
var time_end = date2[1].split("+");

$("#SELECT_225").val(time_start[0].slice(0, -3));
$("#SELECT_301").val(time_end[0].slice(0, -3));
$("#room_appDate").val(date1[0]);
$("#SELECT_87").val(localStorage.getItem("room_booking_room_id"));

});