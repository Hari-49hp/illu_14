odoo.define('date_highlighter_widget.DateHighlighterWidget', function(require) {
    "use strict";
    var field_registry = require('web.field_registry');
    var fields = require('web.basic_fields');


    var FieldDateMultipleDate = fields.InputField.extend({
        template: 'FieldDateMultipleDate',

        events: _.extend({}, fields.InputField.prototype.events, {
            'click': '_onSelectDateField',
        }),

        _onSelectDateField: function(ev) {
            var date = new Date();
            var today = new Date(date.getFullYear(), date.getMonth(), date.getDate());
            this.$input.datepicker({
                // autoHide: true,
                beforeShowDay: function(date) {
                    var available_dates_list = $("[name='available_dates_list']").val();
                    var available_dates_list = available_dates_list.split(",");
                    var hilightedDays = available_dates_list;

                    var year = date.getFullYear()
                    var month = String(date.getMonth() + 1).padStart(2, '0')
                    var day = String(date.getDate()).padStart(2, '0')

                    var final_date = month + '/' + day + '/' + year

                    if (~hilightedDays.indexOf(final_date)) {
                        return { classes: 'highlight-availability', tooltip: 'Title' };
                    }
                },

            }).trigger('focus');
        },

    });

    field_registry.add('date_highlighter', FieldDateMultipleDate);
    return {
        FieldDateMultipleDate: FieldDateMultipleDate
    };

});