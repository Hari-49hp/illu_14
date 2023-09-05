odoo.define('allure_backend_theme_ent.WebClient', function (require) {
"use strict";

const WebClient = require('web.WebClient');

WebClient.include({
    _onHideHomeMenu: function () {
        $('body').removeClass('ad_open_childmenu open_mobile_menu nav-sm');
        $('.o_menu_systray').hasClass('show') && $('.o_menu_systray').removeClass('show');
        return this._super.apply(this, arguments);
    },

    do_action: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function (action) {
            $('body').removeClass('ad_open_childmenu open_mobile_menu nav-sm');
            $('.o_menu_systray').hasClass('show') && $('.o_menu_systray').removeClass('show');
            return action
        });
    },
});
});
