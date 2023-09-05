
//alert('test');

$(".ccavenue-credit-card").hide()
$(".CCAvenue_partner_card").hide()

$("#CCAvenue_bank_id").val('');

//$('.btn.btn-secondary.a-submit').attr("href", "/shop/payment")

/*
$("#CCAvenue_bank_id").change(function() {
	
	var partner_invoice_id = $("#partner_invoice_id").val();
	
	var CCAvenue_bank_id = $("#CCAvenue_bank_id").val();
	
	if (CCAvenue_bank_id == "OPTCRDC"){
	
			$(".ccavenue-credit-card").show()
			$(".CCAvenue_partner_card").show()
	
			$.ajax({
			            url: "/partner_card/filter",
			            type: 'POST',
			            async: false,
			            data: {
			                'partner_invoice_id':partner_invoice_id,
			            },
			            success: function (result) {
			                var resultJSON = jQuery.parseJSON(result);
			                
			                console.log(resultJSON);  
		                    $('#CCAvenue_partner_card_id').empty();
		                    $('#CCAvenue_partner_card_id').append(`
									<option value="" disabled="disabled" selected="selected">Choose..</option>
		                         `);
		
			                $.each(resultJSON, function (key, value) {
			                    $('#CCAvenue_partner_card_id').append(`
									
									<option value="`+ value['id']+`">`+ value['name'] +`</option>
		                                
		                         `);
		                                 
			                });
			                
		                         
			            },
			     });
		     
	} else {
	
		$('#CCAvenue_partner_card_id').empty();
		$('#CCAvenue_partner_card_id').append(`
									<option value="" disabled="disabled" selected="selected">Choose..</option>
		                         `);
	
	}
	
	

});

*/

$("#CCAvenue_partner_card_id").change(function() {
	
	var partner_invoice_id = $("#partner_invoice_id").val();
	var CCAvenue_partner_card_id = $("#CCAvenue_partner_card_id").val();
	
	
	$.ajax({
	            url: "/partner_card/filter",
	            type: 'POST',
	            async: false,
	            data: {
	                'partner_invoice_id':partner_invoice_id,
	                'CCAvenue_partner_card_id':CCAvenue_partner_card_id,
	            },
	            success: function (result) {
	                var resultJSON = jQuery.parseJSON(result);
	                
	                console.log(resultJSON);  
	                $.each(resultJSON, function (key, value) {
                                 
                       $("#cc_avenue_number").val(value['cc_avenue_number']);
                       $("#cc_avenue_name").val(value['cc_avenue_name']);
                       $("#cc_avenue_expiry").val(value['cc_avenue_expiry']);
                       $("#cc_avenue_cvc").val(value['cc_avenue_cvc']);
                                 
	                });
	                
                         
	            },
	     });

});






