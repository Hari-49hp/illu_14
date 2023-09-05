odoo.define('ppts_employee_commission.modelsorderline', function (require) {
"use strict";

    var models = require('point_of_sale.models');

    var _super_orderline = models.Orderline.prototype;

    models.Orderline = models.Orderline.extend({
        initialize: function(attr, options) {
            _super_orderline.initialize.call(this,attr,options);
            this.employee = this.employee || "";
            this.hr_employee_id = this.hr_employee_id || 0.0;
        },
        set_employee: function(employee){
            this.employee = employee.value;
            this.hr_employee_id = employee.id;
            this.trigger('change',this);
        },
        get_employee: function(employee){
            return this.employee;
        },
        can_be_merged_with: function(orderline) {
            if (orderline.get_employee() !== this.get_employee()) {
                return false;
            } else {
                return _super_orderline.can_be_merged_with.apply(this,arguments);
            }
        },
        clone: function(){
            var orderline = _super_orderline.clone.call(this);
            orderline.employee = this.employee;
            orderline.hr_employee_id = this.hr_employee_id;
            return orderline;
        },
        export_as_JSON: function(){
            var json = _super_orderline.export_as_JSON.call(this);
            json.employee = this.employee;
            json.hr_employee_id = this.hr_employee_id;
            return json;
        },
        init_from_JSON: function(json){
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.employee = json.employee;
            this.hr_employee_id = json.hr_employee_id;
        },
    });

});
