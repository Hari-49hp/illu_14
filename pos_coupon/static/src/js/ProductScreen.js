odoo.define('pos_coupon.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { Gui } = require('point_of_sale.Gui');

    const PosCouponProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
                useBarcodeReader({
                    coupon: this._onCouponScan,
                });
            }
            _onCouponScan(code) {
                this.currentOrder.activateCode(code.base_code);
            }
            /**
             * 1/ Perform the usual set value operation (super._setValue) if the line being modified
             * is not a reward line or if it is a reward line, the `val` being set is '' or 'remove' only.
             *
             * 2/ Update activated programs and coupons when removing a reward line.
             *
             * 3/ Trigger 'update-rewards' if the line being modified is a regular line or
             * if removing a reward line.
             *
             * @override
             */
            _setValue(val) {
                const selectedLine = this.currentOrder.get_selected_orderline();
                if (
                    !selectedLine ||
                    !selectedLine.is_program_reward ||
                    (selectedLine.is_program_reward && ['', 'remove'].includes(val))
                ) {
                    super._setValue(val);
                }
                if (!selectedLine) return;
                if (selectedLine.is_program_reward && val === 'remove') {
                    if (selectedLine.coupon_id) {
                        const coupon_code = Object.values(selectedLine.order.bookedCouponCodes).find(
                            (couponCode) => couponCode.coupon_id === selectedLine.coupon_id
                        ).code;
                        delete selectedLine.order.bookedCouponCodes[coupon_code];
                        selectedLine.order.trigger('reset-coupons', [selectedLine.coupon_id]);
                        Gui.showPopup('ErrorPopup', {
								'title': self.env._t('Expired'),
								'body': self.env._t(`Coupon (${coupon_code}) has been deactivated.`),
							});

//                        this.do_warn.showNotification(`Coupon (${coupon_code}) has been deactivated.`);
                    } else if (selectedLine.program_id) {
                        // remove program from active programs
                        const index = selectedLine.order.activePromoProgramIds.indexOf(selectedLine.program_id);
                        selectedLine.order.activePromoProgramIds.splice(index, 1);
                        Gui.showPopup('ErrorPopup', {
								'title': self.env._t('Expired'),
								'body': self.env._t(`'${
                                this.env.pos.coupon_programs_by_id[selectedLine.program_id].name
                            }' program has been deactivated.`),
							});

//                        this.do_warn.showNotification(
//                            `'${
//                                this.env.pos.coupon_programs_by_id[selectedLine.program_id].name
//                            }' program has been deactivated.`
//                        );
                    }
                }
                if (!selectedLine.is_program_reward || (selectedLine.is_program_reward && val === 'remove')) {
                    selectedLine.order.trigger('update-rewards');
                }
            }
        };

    Registries.Component.extend(ProductScreen, PosCouponProductScreen);

    return ProductScreen;
});
