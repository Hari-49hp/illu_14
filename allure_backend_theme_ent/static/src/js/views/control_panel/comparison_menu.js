odoo.define("allure_backend_theme.ComparisonMenu", function (require) {
'use strict';

    const ComparisonMenu = require('web.ComparisonMenu');
    const { patch } = require('web.utils');

    patch(ComparisonMenu, 'allure_backend_theme.ComparisonMenu', {

        async willStart() {
            var prom = this._super(...arguments);
            this.displayComparison = true;
            return prom;
        },
    });
});
