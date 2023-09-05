odoo.define('ppts_employee_commission.OrderlineEmployeeButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class OrderlineEmployeeButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }

        async onClick() {
		const empDetails = await this.rpc({
		        model: 'pos.order.line',
			method: 'get_employee_pos',
		        args: [[]],
		    });
            this.showPopup('EmpLoyeePopup', {
                title: this.env._t('Select Employee'),
                users: empDetails,
                pos: this.env.pos,
            });
        }
    }
    /*OrderlineEmployeeButton.template = 'OrderlineEmployeeButton';

    ProductScreen.addControlButton({
        component: OrderlineEmployeeButton,
        condition: function() {
            return true;
        },
        position: ['before', 'SetPricelistButton'],
    });

    Registries.Component.add(OrderlineEmployeeButton);

    return OrderlineEmployeeButton;*/
});
