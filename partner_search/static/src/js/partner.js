odoo.define('partner_search.string', function (require) {
    var core = require('web.core');
    var BasicController = require('web.BasicController');
    var _t = core._t;
 BasicController.include({
     
    _notifyInvalidFields: function (invalidFields) {
        var record = this.model.get(this.handle, {raw: true});
        var fields = record.fields;
        var warnings = invalidFields.map(function (fieldName) {
            var fieldStr = fields[fieldName].string;
            return _.str.sprintf('<li>%s</li>', _.escape(fieldStr));
        });
        warnings.unshift('<ul>');
        warnings.push('</ul>');
        this.do_warn(_t("Incomplete Information!"), warnings.join(''));
    },
    })
});