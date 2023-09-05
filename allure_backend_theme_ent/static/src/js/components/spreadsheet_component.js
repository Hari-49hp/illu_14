odoo.define("allure_backend_theme_ent.SpreadsheetComponent", function (require) {
'use strict';

    if (!_.contains(odoo._modules, 'documents_spreadsheet') && 
        !_.has(odoo.__DEBUG__.services, 'documents_spreadsheet.SpreadsheetComponent')) { return; };

    const SpreadsheetComponent = require('documents_spreadsheet.SpreadsheetComponent');
    const { patch } = require('web.utils');
    const { device } = require("web.config");

    patch(SpreadsheetComponent, 'allure_backend_theme_ent.SpreadsheetComponent', {

        toggleSpreadsheetClass(display) {
            const $oContent = this.el && this.el.closest('.o_content');
            if (_.isElement($oContent) && $oContent.classList) {
                $oContent.classList[display ? 'add' : 'remove']('ad_spreadsheet');
            };
        },

        mounted() {
            this._super(...arguments);
            this.toggleSpreadsheetClass(true);
        },

        willUnmount() {
            this._super(...arguments);
            this.toggleSpreadsheetClass(false);
        },
    });
});
