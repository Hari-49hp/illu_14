odoo.define('bi_pos_pay_later.PaymentScreen', function (require) {
	'use strict';

	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const Registries = require('point_of_sale.Registries');
	const session = require('web.session');
    var rpc = require('web.rpc');
    
    localStorage.setItem("error_credit",0)

	const BiPaymentScreen = PaymentScreen =>
		class extends PaymentScreen {
			constructor() {
				super(...arguments);
			}

			async selectClient() {
				let self = this;
				if (this.currentOrder.is_paying_partial) {
					return self.showPopup('ErrorPopup', {
						title: self.env._t('Not Allowed'),
						body: self.env._t('You cannot change customer of draft order.'),
					});
				} else {
					super.selectClient();
				}
			}

			async click_back() {
				let self = this;
				if (this.currentOrder.is_paying_partial) {
					const { confirmed } = await this.showPopup('ConfirmPopup', {
						title: self.env._t('Cancel Payment ?'),
						body: self.env._t('Are you sure,You want to Cancel this payment?'),
					});
					if (confirmed) {
						self.env.pos.delete_current_order();
						self.showScreen('ProductScreen');
					}
				}
				else {
					self.showScreen('ProductScreen');
				}
			}

			async debitFromCreditAmount() {
				localStorage.setItem("error_credit",0)
			    var self = this;
			    var currentOrder = this.env.pos.get_order();
				var plines = currentOrder.get_paymentlines();
				var dued = currentOrder.get_due();
				var changed = currentOrder.get_change();
				var clients = currentOrder.get_client();
				var company_id = this.env.pos.config.company_id;
				var pos_cur = this.env.pos.config.currency_id[0];
				localStorage.setItem("error_credit",0)
				if (clients) {
                    for (var i = 0; i < plines.length; i++) {
                        if (plines[i].payment_method.credit_jr === true) {
                            if (!currentOrder.get_client()) {
                                self.showPopup('ErrorPopup', {
                                    'title': this.env._t('Unknown customer1'),
                                    'body': this.env._t('You cannot use Credit payment. Select customer first.'),
                                });
                                localStorage.setItem("error_credit",1)
                                return 1;
                            }
                            var amount = plines[i].get_amount();
                            
                            if (amount > clients.custom_credit) { // Make Condition that amount is greater than selected customer's credit_jr amount
                                    self.showPopup('ErrorPopup', {
                                        'title': self.env._t('Not Sufficient Credit'),
                                        'body': self.env._t('Customer has not Sufficient Credit To Pay'),
                                    });
                                    localStorage.setItem("error_credit",1)
                                    return 1;
                                } else {
                                
                                	this.rpc({
                                        model: 'res.partner',
                                        method: 'UpdateCredit',
                                        args: [1, clients, company_id, pos_cur, amount],
                                    }).then(function (output) {
                                        if (output == false) {
                                            self.showPopup('ErrorPopup', {
                                                'title': this.env._t('Not Sufficient Credit'),
                                                'body': this.env._t('Customer has not Sufficient Credit To Pay'),
                                            });
                                            return 1;
                                        }
                                    });
                                
                                }
                              
                                
                            
                            
                            self.rpc({
                                model: 'res.partner',
                                method: 'CheckCredit',
                                args: [1, clients, company_id, pos_cur, amount]
                            }).then(function (output) {
                                console.log("CheckCredit  >>> ",output)
                                if (output > clients.custom_credit) { // Make Condition that amount is greater than selected customer's credit_jr amount
                                    self.showPopup('ErrorPopup', {
                                        'title': self.env._t('Not Sufficient Credit'),
                                        'body': self.env._t('Customer has not Sufficient Credit To Pay'),
                                    });
                                    return 1;
                                } else {
                                    self.rpc({
                                        model: 'res.partner',
                                        method: 'UpdateCredit',
                                        args: [1, clients, company_id, pos_cur, amount],
                                    }).then(function (output) {
                                        if (output == false) {
                                            self.showPopup('ErrorPopup', {
                                                'title': this.env._t('Not Sufficient Credit'),
                                                'body': this.env._t('Customer has not Sufficient Credit To Pay'),
                                            });
                                            return 1;
                                        }
                                    });
                                }
                            });
                        }
                    }
				}
			}

			clickPayLater() {
				localStorage.setItem("error_credit",0)
				let self = this;
				let order = self.env.pos.get_order();
				let orderlines = order.get_orderlines();
				let partner_id = order.get_client();
				if (!partner_id) {
					return self.showPopup('ErrorPopup', {
						title: self.env._t('Unknown customer'),
						body: self.env._t('You cannot perform partial payment.Select customer first.'),
					});
				}
				else if (orderlines.length === 0) {
					return self.showPopup('ErrorPopup', {
						title: self.env._t('Empty Order'),
						body: self.env._t('There must be at least one product in your order.'),
					});
				}
				else {
				    var plines = order.get_paymentlines();
						for (var i = 0; i < plines.length; i++) {
                            if (plines[i].payment_method.credit_jr === true){
                            	localStorage.setItem("error_credit",0)
                                self.debitFromCreditAmount();
                            }
                            
                    
					if (order.get_total_with_tax() !== order.get_total_paid() && order.paymentlines.length != 0 && localStorage.getItem("error_credit") == 0) {
						order.is_partial = true;
						order.amount_due = order.get_due();
						order.set_is_partial(true);
						//order.to_invoice = false;
						order.finalized = false;
						self.env.pos.push_single_order(order);
						self.showScreen('ReceiptScreen');
                        }
						console.log('order -->', order)
						console.log('amount_due -->', order.get_due())
					}
				}
			}
		}

	Registries.Component.extend(PaymentScreen, BiPaymentScreen);

	return PaymentScreen;

});
