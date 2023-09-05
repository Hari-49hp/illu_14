$(document).ready(function(){
    $('.oe_login_form').on('submit', function (e) {

        var $form = $(e.currentTarget)
        $.ajax({
            url:'/wiz/web/login',
            type: 'POST',
            data: {
                'login': $('#login').val(),
                'password': $('#password').val(),
            },
            async: false,
            success: function(data){
                var data_main = JSON.parse(data)

                if (data_main.status === 'worng'){
                    e.preventDefault()
                    $(".alert-danger").removeClass('d-none');
                }
                else {
                    $(".alert-danger").addClass('d-none');
                    window.location.replace("/");
                }

            },
            error: function(data) {
                console.log(data)
                console.log('An error occurred.')
            },
        });

    });
    

});
