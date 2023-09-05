var acc = document.getElementsByClassName("accordions");
var l;

for (l = 0; l < acc.length; l++) {
acc[l].addEventListener("click", function() {
    this.classList.toggle("active");
    var panel = this.nextElementSibling;
    if (panel.style.display === "block") {
    panel.style.display = "none";
    console.log("if check working")
    } 
    else {
    panel.style.display = "block";
    console.log("else check working")
    }
});
}

console.log("hii1223")


$(document).ready(function(){
    $(".count_button").click(function(){
        
        $(".custom_panel").css("display", "none");
        console.log("done")
        });
     
    });

$(document).ready(function(){

    $(".o_delete").attr("style", "display:block !important");

    sessionStorage.removeItem('time_slot_id_custom');
});




    
  