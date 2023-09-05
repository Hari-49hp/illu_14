odoo.define('allure_backend_theme_ent.MainView', function (require) {
    "use strict";

    require('web.dom_ready');
    var config = require('web.config');

    (function() {
        const $body = jQuery("body");
        //Mobile view detect
        if (config.device.isMobile) {
            $body.addClass('ad_mobile ad_full_view');
        };

        if (config.device.size_class < config.device.SIZES.LG) {
            $body.addClass('ad_full_view');
        };
    })();
});