odoo.define('ppts_employee_commission.orderline', function(require) {
    'use strict';

    const Orderline = require('point_of_sale.Orderline');
    const Registries = require('point_of_sale.Registries');

    const PosResOrderline = Orderline =>
        class extends Orderline {
            async usericonclick(){
		const empDetails = await this.rpc({
		        model: 'pos.order.line',
			method: 'get_employee_pos',
		        args: [[]],
		    });
                this.showPopup('EmpLoyeePopup',{
                    title: this.env._t('Select Employee'),
                    users: empDetails,
                    pos: this.env.pos,
                    orderline: this.props.line,
                });
           }

           removeemployee(){
                this.props.line.employee = '';
                this.props.line.hr_employee_id = 0.0;
                this.props.line.trigger('change',this.props.line);
           }
        };

    Registries.Component.extend(Orderline, PosResOrderline);

    return Orderline;
});
