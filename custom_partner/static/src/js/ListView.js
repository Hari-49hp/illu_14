// odoo.define('dynamic_notes_tooltip', function(require) {

//     var core = require('web.core');
//     var Model = require('web.DataModel'); // make asynchronous calls to the DB

//     /* Make a special widget to include dynamic tooltips for the product name char field,
//        see addons/web/static/src/js/views/list_view.js for reference.
//     */
//     var DynamicTooltip = core.list_widget_registry.get('field').extend({
//         _format: function(row_data, options) {
//             var value = row_data[this.id].value;
//             var product_tmpl_id = row_data[this.id].value[0],
//                 product_name = row_data[this.id].value[1];

//             // Create a Query() object to make a request to the DB
//             var productTemplate = new Model('appointment.appointment')

//             console.log(productTemplate)
//             console.log(productTemplate)
//             productTemplate.query(['description_sale'])
//                 .filter([
//                     ['id', '=', product_tmpl_id]
//                 ])
//                 .first()
//                 .then(function(res) {
//                     if (res) {
//                         // Attach the tooltip asynchronously after the corresponding element is rendered
//                         $('#' + product_tmpl_id).prop('title', res.notes);
//                     };
//                 })
//                 // Return a <p> tag with id of the product_temlate record
//             return '<p id="' + product_tmpl_id + '">' + product_name + '</p>';
//         }
//     });

//     // Make the created widget accessible by other models
//     core.list_widget_registry.add('field.dynamic_notes_tooltip', DynamicTooltip);
// })

odoo.define("dynamic_notes_tooltip", function(require) {
    "use strict";

    var field_registry = require("web.field_registry");
    var basic_fields = require("web.basic_fields");

    var YearWidget = basic_fields.FieldChar.extend({
        // _format: function(row_data, options) {
        //     var value = row_data[this.id].value;
        //     var product_tmpl_id = row_data[this.id].value[0],
        //         product_name = row_data[this.id].value[1];

        //     // Create a Query() object to make a request to the DB
        //     var productTemplate = new Model('appointment.appointment')

        //     console.log(productTemplate)
        //     console.log(productTemplate)
        //     productTemplate.query(['description_sale'])
        //         .filter([
        //             ['id', '=', product_tmpl_id]
        //         ])
        //         .first()
        //         .then(function(res) {
        //             if (res) {
        //                 // Attach the tooltip asynchronously after the corresponding element is rendered
        //                 $('#' + product_tmpl_id).prop('title', res.notes);
        //             };
        //         })
        //         // Return a <p> tag with id of the product_temlate record
        //     return '<p id="' + product_tmpl_id + '">' + product_name + '</p>';
        // }
        _render: function() {
            // var intValue = parseInt(this.value);
            // var parseIntValue = isNaN(intValue) ? 0 : intValue;

            // if (this.mode !== "readonly") {
            //     var $input = this.$el.find("input");
            //     $input.val(intValue);
            //     this.$input = $input;
            //     this.$(".oe_field_year").text(parseIntValue);
            // } else {
            //     this.$(".oe_field_year").text(parseIntValue);
            // }
            console.log('kkkkkkkkkkkllllllll');
        }
    });
    field_registry.add("field.dynamic_notes_tooltip", YearWidget);
});