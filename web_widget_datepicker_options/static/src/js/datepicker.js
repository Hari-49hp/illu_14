/*
License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
*/

odoo.define('web_widget_datepicker_options.datepicker', function(require) {
    "use strict";
    var FieldDate = require('web.basic_fields').FieldDate;
    FieldDate.include({
        init: function () {
            this._super.apply(this, arguments);
            if (this.nodeOptions.disable_past_date) {
                var d = new Date();
                d.setHours(0,0,0,0);
                this.datepickerOptions['minDate'] = moment(d);
            }
        }
    });

});
