odoo.define('allure_backend_theme_ent.AbstractAction', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');


AbstractAction.include({

    _toggleJsFilterClass(isFliter) {
        if (this.hasControlPanel) {
            var searchMenuTypes = (this.controlPanelProps && this.controlPanelProps.searchMenuTypes) || new Array;
            var $oSearchOptions = this.$('.o_search_options');
            if ($oSearchOptions.length && !searchMenuTypes.length) {
                $oSearchOptions.toggleClass('ad_js_filters', isFliter);
            };
        };
    },

    start: async function() {
        await this._super(...arguments);
        this._toggleJsFilterClass(true);
    },

    destroy: function() {
        this._super.apply(this, arguments);
        this._toggleJsFilterClass(false);
    },

});
});
