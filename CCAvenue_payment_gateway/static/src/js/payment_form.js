odoo.define('CCAvenue_payment_gateway.payment_form', function (require) {
"use strict";

var core = require('web.core');
var Session = require('web.session');
var Dialog = require('web.Dialog');
var payment_form = require('payment.payment_form');

var _t = core._t;


payment_form.include({
    init: function(parent, context) {
        return this._super.apply(this, arguments);
    },
    
    
	/**
     * @private
     * @param {Event} ev
     */
    payEvent: function (ev) {
        ev.preventDefault();
        
        var CCAvenue_bank_id = document.getElementById("CCAvenue_bank_id").value;
        var cc_number = document.getElementById("cc_avenue_number").value;
        var cc_cvc = document.getElementById("cc_avenue_cvc").value;
        var cc_expiry = document.getElementById("cc_avenue_expiry").value;
        var cc_holder_name = document.getElementById("cc_avenue_name").value;
        var ccavenue_save_token = document.getElementById("o_payment_ccavenue_save_token").value;
        //var cc_brand = document.getElementById("cc_brand").value;
        var form = this.el;
        var checked_radio = this.$('input[type="radio"]:checked');
        var self = this;
        if (ev.type === 'submit') {
            var button = $(ev.target).find('*[type="submit"]')[0]
        } else {
            var button = ev.target;
        }

        // first we check that the user has selected a payment method
        if (checked_radio.length === 1) {
            checked_radio = checked_radio[0];

            // we retrieve all the input inside the acquirer form and 'serialize' them to an indexed array
            var acquirer_id = this.getAcquirerIdFromRadio(checked_radio);
            var acquirer_form = false;
            if (this.isNewPaymentRadio(checked_radio)) {
                acquirer_form = this.$('#o_payment_add_token_acq_' + acquirer_id);
            } else {
                acquirer_form = this.$('#o_payment_form_acq_' + acquirer_id);
            }
            var inputs_form = $('input', acquirer_form);
            var ds = $('input[name="data_set"]', acquirer_form)[0];
            // if the user is adding a new payment
            if (this.isNewPaymentRadio(checked_radio)) {
                if (this.options.partnerId === undefined) {
                    console.warn('payment_form: unset partner_id when adding new token; things could go wrong');
                }
                var form_data = this.getFormData(inputs_form);
                var wrong_input = false;

                inputs_form.toArray().forEach(function (element) {
                    //skip the check of non visible inputs
                    if ($(element).attr('type') == 'hidden') {
                        return true;
                    }
                    $(element).closest('div.form-group').removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
                    $(element).siblings( ".o_invalid_field" ).remove();
                    //force check of forms validity (useful for Firefox that refill forms automatically on f5)
                    $(element).trigger("focusout");
                    if (element.dataset.isRequired && element.value.length === 0) {
                            $(element).closest('div.form-group').addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
                            $(element).closest('div.form-group').append('<div style="color: red" class="o_invalid_field" aria-invalid="true">' + _.str.escapeHTML("The value is invalid.") + '</div>');
                            wrong_input = true;
                    }
                    else if ($(element).closest('div.form-group').hasClass('o_has_error')) {
                        wrong_input = true;
                        $(element).closest('div.form-group').append('<div style="color: red" class="o_invalid_field" aria-invalid="true">' + _.str.escapeHTML("The value is invalid.") + '</div>');
                    }
                });

                if (wrong_input) {
                    return;
                }

                this.disableButton(button);
                // do the call to the route stored in the 'data_set' input of the acquirer form, the data must be called 'create-route'
                return this._rpc({
                    route: ds.dataset.createRoute,
                    params: form_data,
                }).then(function (data) {
                    // if the server has returned true
                    if (data.result) {
                        // and it need a 3DS authentication
                        if (data['3d_secure'] !== false) {
                            // then we display the 3DS page to the user
                            $("body").html(data['3d_secure']);
                        }
                        else {
                            checked_radio.value = data.id; // set the radio value to the new card id
                            form.submit();
                            return new Promise(function () {});
                        }
                    }
                    // if the server has returned false, we display an error
                    else {
                        if (data.error) {
                            self.displayError(
                                '',
                                data.error);
                        } else { // if the server doesn't provide an error message
                            self.displayError(
                                _t('Server Error'),
                                _t('e.g. Your credit card details are wrong. Please verify.'));
                        }
                    }
                    // here we remove the 'processing' icon from the 'add a new payment' button
                    self.enableButton(button);
                }).guardedCatch(function (error) {
                    error.event.preventDefault();
                    // if the rpc fails, pretty obvious
                    self.enableButton(button);

                    self.displayError(
                        _t('Server Error'),
                        _t("We are not able to add your payment method at the moment.") +
                            self._parseError(error)
                    );
                });
            }
            // if the user is going to pay with a form payment, then
            else if (this.isFormPaymentRadio(checked_radio)) {
                this.disableButton(button);
                var $tx_url = this.$el.find('input[name="prepare_tx_url"]');
                var self = this
                // if there's a prepare tx url set
                if ($tx_url.length === 1) {
                    // if the user wants to save his credit card info
                    var form_save_token = acquirer_form.find('input[name="o_payment_form_save_token"]').prop('checked');
                    //var ccavenue_save_token = acquirer_form.find('input[name="o_payment_ccavenue_save_token"]').prop('checked');
                    // then we call the route to prepare the transaction
                    return this._rpc({
                        route: $tx_url[0].value,
                        params: {
                            'acquirer_id': parseInt(acquirer_id),
                            'save_token': form_save_token,
                            'access_token': self.options.accessToken,
                            'success_url': self.options.successUrl,
                            'error_url': self.options.errorUrl,
                            'callback_method': self.options.callbackMethod,
                            'order_id': self.options.orderId,
                            'CCAvenue_bank_id':CCAvenue_bank_id,
                            'cc_number':cc_number,
                            'cc_cvc':cc_cvc,
                            'cc_holder_name':cc_holder_name,
                            'cc_expiry':cc_expiry,
                            'ccavenue_save_token': ccavenue_save_token,
                        },
                    }).then(function (result) {
                        if (result) {
                            // if the server sent us the html form, we create a form element
                            var newForm = document.createElement('form');
                            newForm.setAttribute("method", "post"); // set it to post
                            newForm.hidden = true; // hide it
                            newForm.innerHTML = result; // put the html sent by the server inside the form
                            var action_url = $(newForm).find('input[name="data_set"]').data('actionUrl');
                            
                            if((action_url==="https://secure.ccavenue.ae/transaction/transaction.do?command=initiateTransaction")) {
                                newForm.setAttribute("name", "redirect");
                            }
                            
                            newForm.setAttribute("action", action_url); // set the action url
                            $(document.getElementsByTagName('body')[0]).append(newForm); // append the form to the body
                            
                            if((action_url==="https://secure.ccavenue.ae/transaction/transaction.do?command=initiateTransaction")) {
                                newForm.setAttribute("name", "redirect");
                            	
                            	//ev.preventDefault();
                            	
                                newForm.submit(); // and finally submit the form
                                return new Promise(function () {});
                            }
                            else if(action_url) {
                            	newForm.submit(); // and finally submit the form
                                return new Promise(function () {});
                            }
                            
                        }
                        else {
                            self.displayError(
                                _t('Server Error'),
                                _t("We are not able to redirect you to the payment form.")
                            );
                            self.enableButton(button);
                        }
                    }).guardedCatch(function (error) {
                        error.event.preventDefault();
                        self.displayError(
                            _t('Server Error'),
                            _t("We are not able to redirect you to the payment form.") + " " +
                                self._parseError(error)
                        );
                    });
                }
                else {
                    // we append the form to the body and send it.
                    this.displayError(
                        _t("Cannot setup the payment"),
                        _t("We're unable to process your payment.")
                    );
                    self.enableButton(button);
                }
            }
            else {  // if the user is using an old payment then we just submit the form
                this.disableButton(button);
                form.submit();
                return new Promise(function () {});
            }
        }
        else {
            this.displayError(
                _t('No payment method selected'),
                _t('Please select a payment method.')
            );
            this.enableButton(button);
        }
    },
});
});
