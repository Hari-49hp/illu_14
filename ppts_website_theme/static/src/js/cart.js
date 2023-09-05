$(document).ready(function () {
    $('#nb_register_cart').val(1);
    $('.promo-code-custom').val('');
    $('.cartcounter').val(1);
    $( "#BookNowEvent" ).click(function() {
        $('#cart-popup').modal({
        keyboard: false,
        show: true,
        focus: true
      })
      var event_id = $(this).data("event-id");
      var event = $(this).data("event");
      var cart_ticket_id = $(this).data("cart_ticket_id");

    });
    $('.addcartbtn').on('click', function() {
        var value = parseFloat($('.cartcounter').val(), 10);
        if (value + 1 > 10){
            alert('Maximum 10 quantity allowed!');
            $('.cartcounter').val(10);
        }else{
        $('.cartcounter').val(value + 1);
        var this_qty = $('.cartcounter').val();
        $('#nb_register_cart').val(this_qty);
        var hidden_amount_cart = $('#hidden_amount_cart').val();
        var value_amount = this_qty * hidden_amount_cart
        $(".amount-total-cart-custom").html(value_amount.toFixed(2));
        }
    });
    $('.subcartbtn').on('click', function() {
        var value = parseFloat($('.cartcounter').val(), 10);
        if (value > 1) {
           $('.cartcounter').val(value - 1);
        }
        var this_qty = $('.cartcounter').val();
        $('#nb_register_cart').val(this_qty);
        var hidden_amount_cart = $('#hidden_amount_cart').val();
        var value_amount = this_qty * hidden_amount_cart
        $(".amount-total-cart-custom").html(value_amount.toFixed(2));

    });
    $('.cartcounter').on('change', function() {
        current = $(this).val();
        var value = parseFloat(current, 10);
        console.log(value);
        if (value > 10){
            alert('Maximum 10 quantity allowed!');
            $(this).val(10);
            $('#nb_register_cart').val(10);
        }else{
            if (value >= 1) {
                var hidden_amount_cart = $('#hidden_amount_cart').val();
                var value_amount = value * hidden_amount_cart
                $('#nb_register_cart').val(value);
                $(".amount-total-cart-custom").html(value_amount.toFixed(2));
            }else{
                var hidden_amount_cart = $('#hidden_amount_cart').val();
                var value_amount = 1 * hidden_amount_cart
                $(".amount-total-cart-custom").html(value_amount.toFixed(2));
                $(this).val(1);
                $('#nb_register_cart').val(1);
            }

        }
    });
});

function ChangeCountryCart(id) {
    var current = document.getElementById(id+"-country_id").value;
    $('select#'+String(id)+'-city_id>option').each(function () {
        var text = $(this).val();
        if (text === current) {
            $(this).show();
        }
        else {
            $(this).hide();
        }
    });
 }
