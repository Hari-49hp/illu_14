$(document).ready(function() {
    var list_menus = ''
    $.ajax({
        url: "/web/custom/details",
        type: 'POST',
        async:true,
        data: {
            "x": 'x'
        },
        success: function(result) {
            var obj = jQuery.parseJSON(result);
            $.each(obj.name, function(key,value) {
              var res = value.split("$$$$");
              list_menus += "<a class='nav-link-menu_side' role='menuitem' href='"+res[1]+"'>"+
                    "<img class='mk_apps_sidebar_icon' src='"+res[2]+"' style='width: 23px;'/>"
                    +"<span class='mk_apps_sidebar_name' style='vertical-align: middle;font-size: 13px;margin-left: 6px;'>"+
                        res[0]
                    "</span></a>"
            });
            $( ".web_applist_class_replace" ).replaceWith(list_menus); 
        },
    });

});