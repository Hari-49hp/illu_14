odoo.define('ppts_employee_commission.EmpLoyeePopup', function (require) {
"use strict";

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { useAutoFocusToLast } = require('point_of_sale.custom_hooks');

    class EmpLoyeePopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);            
            useAutoFocusToLast();
        }
        employeepopup(event){
            var order = this.props.pos.get_order();
            if (!this.props.orderline) {
                order.get_orderlines().forEach(function (orderline) {
                    orderline.set_employee(event.currentTarget.dataset);
                });
            }
            else{
                this.props.orderline.set_employee(event.currentTarget.dataset);
                this.props.orderline.trigger('change',this.props.orderline);
            }
            this.trigger('close-popup');
        }

    }
    EmpLoyeePopup.template = 'EmpLoyeePopup';
    EmpLoyeePopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
    };

    Registries.Component.add(EmpLoyeePopup);
    return EmpLoyeePopup;

});
