odoo.define('pos_credit_payment.PaymentScreenWidget', function (require) {
	'use strict';

	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const { Component } = owl;
	var rpc = require('web.rpc');

	const PaymentScreenWidget = (PaymentScreen) =>
		class extends PaymentScreen {
			constructor() {
				super(...arguments);
				// this.orderline_remove();
			}

			async validateOrder(isForceValidate) {
				// if (await this._isOrderValid(isForceValidate)) {
				// remove pending payments before finalizing the validation
				// for (let line of this.paymentLines) {
				//     if (!line.is_done()) this.currentOrder.remove_paymentline(line);
				// }
				// await this._finalizeValidation();

				var self = this;
				var currentOrder = this.env.pos.get_order();
				var plines = currentOrder.get_paymentlines();
				var dued = currentOrder.get_due();
				var changed = currentOrder.get_change();
				var clients = currentOrder.get_client();
				var total_amt = currentOrder.get_total_with_tax()
				
				if ($("#checkbox_cgv").prop('checked')) {
					this.env.pos['add_to_credit'] = true
				}
				else {
					this.env.pos['add_to_credit'] = false
				}

				if (document.getElementById("checkbox_cgv") == null){
					var click = false
				}
				if (document.getElementById("checkbox_cgv") != null){
					var click = document.getElementById("checkbox_cgv").checked
				}

				var a = [];
				var pos_cur = this.env.pos.config.currency_id[0];
				var company_id = this.env.pos.config.company_id;
				for (var i = 0; i < plines.length; i++) {
					if (plines[i].payment_method.credit_jr === true) {

						a.push(plines[i]);
					}
				}
				if (currentOrder.get_orderlines().length === 0) {
					self.showPopup('ErrorPopup', {
						'title': this.env._t('Empty Order'),
						'body': this.env._t('There must be at least one product in your order before it can be validated.'),
					});
					return;
				}

				// Make Condition: Popup Occurs When Customer is not selected on credit_jr payment method, While any other payment method, this error popup will not be showing
				if (clients) {  //if customer is selected
					if (a['length'] !== 0) { //we've given Miscellaneous Type
						for (var i = 0; i < plines.length; i++) {
							if (plines[i].payment_method.credit_jr === true) {
								if (!currentOrder.get_client()) {
									self.showPopup('ErrorPopup', {
										'title': this.env._t('Unknown customer1'),
										'body': this.env._t('You cannot use Credit payment. Select customer first.'),
									});
									return;
								}

								// if(currentOrder.get_change() > 0){ // Make Condition that amount is greater than selected customer's credit_jr amount
								//    self.rpc({
								// 	model: 'pos.order',
								// 	method: 'UpdateVals',
								// 	args: [changed]
								// });
								// 	return;
								// }
								// if (click == true) {
								// 	this.rpc({
								// 		model: 'res.partner',
								// 		method: 'CreateCreditPartner',
								// 		args: [1, clients, changed],
								// 	});
								// }
								var amount = plines[i].get_amount();
								self.rpc({
									model: 'res.partner',
									method: 'CheckCredit',
									args: [1, clients, company_id, pos_cur, amount]
								}).then(function (output) {
									if (output > clients.custom_credit) { // Make Condition that amount is greater than selected customer's credit_jr amount
										self.showPopup('ErrorPopup', {
											'title': self.env._t('Not Sufficient Credit'),
											'body': self.env._t('Customer has not Sufficient Credit To Pay'),
										});
										return;
									} else {
										if (self._isOrderValid(isForceValidate)) {
											self.rpc({
												model: 'res.partner',
												method: 'UpdateCredit',
												args: [1, clients, company_id, pos_cur, amount],
												// args: [[client.id], {'custom_credit': updated}],
											}).then(function (output) {
												if (output == false) {
													self.showPopup('ErrorPopup', {
														'title': this.env._t('Not Sufficient Credit'),
														'body': this.env._t('Customer has not Sufficient Credit To Pay'),
													});
													return;
												}
												else {
												    self.rpc({
                                                        model: 'pos.order',
                                                        method: 'UpdateCreditJournal',
                                                        args: [currentOrder,clients, company_id, pos_cur, amount],
                                                        // args: [[client.id], {'custom_credit': updated}],
                                                    }).then(function (output) {


                                                    });
													clients.custom_credit = clients.custom_credit - amount
													self._finalizeValidation();
												}
											});
										}
									}
								});
							}
						}
					} else {
						// if (this._isOrderValid(isForceValidate)) {
						// 		self._finalizeValidation();
						// 	}
						if (await this._isOrderValid(isForceValidate)) {
							// remove pending payments before finalizing the validation
							if (click == true) {
								await this.rpc({
									model: 'res.partner',
									method: 'CreateCreditPartner',
									args: [1, clients, changed],
								});
							}
							for (let line of this.paymentLines) {
								if (!line.is_done()) this.currentOrder.remove_paymentline(line);
							}
							await this._finalizeValidation();
						}
					}


				} else if (a['length'] == 0) {
					// if (this._isOrderValid(isForceValidate)) {
					// 		self._finalizeValidation();
					// }
					if (await this._isOrderValid(isForceValidate)) {

						for (let line of this.paymentLines) {
							if (!line.is_done()) this.currentOrder.remove_paymentline(line);
						}
						await this._finalizeValidation();
					}
				} else {
					self.showPopup('ErrorPopup', {
						'title': this.env._t('Unknown customer/use credit payment'),
						'body': this.env._t('You cannot use Credit payment. Select customer first.'),
					});
					return;
				}
				if (total_amt < 0){
				    try {
				        console.log($(return_reason)[0].value);
                        if ($(return_reason)[0].value != undefined){
                            currentOrder.note = $(return_reason)[0].value;
                            self.rpc({
									model: 'pos.order',
									method: 'updateReturnReason',
									args: [currentOrder.name,currentOrder.note]
								}).then(function (output) {

								});
                        }
				    }
				    catch(err) {
				        self.showPopup('ErrorPopup', {
						'title': this.env._t('Return Reason'),
						'body': this.env._t(err),
					    });
				    }

				}

			}
			// }	
		};

	Registries.Component.extend(PaymentScreen, PaymentScreenWidget);

	return PaymentScreen;

});
