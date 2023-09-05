odoo.define('allure_backend_theme_ent.AppsMenu', function (require) {
    "use strict";

    var AppsMenu = require('web.AppsMenu');
    var session = require('web.session');

    AppsMenu.include({
        init: function (parent, menuData) {
            this._super.apply(this, arguments);
            this._activeApp = undefined;
            this.company_id = session.company_id;
            this._apps = _.map(menuData.children, function (appMenuData) {
                var menuIconData = '';
                if(appMenuData.theme_icon_data) {
                    menuIconData = ('data:image/png;base64,' + appMenuData.theme_icon_data).replace(/\s/g, "");
                }
                else {
                    menuIconData = '/allure_backend_theme/static/src/img/no_modul_ioc.png';
                }
                return {
                    actionID: parseInt(appMenuData.action.split(',')[1]),
                    menuID: appMenuData.id,
                    name: appMenuData.name,
                    xmlID: appMenuData.xmlid,
                    menuIcon: menuIconData,
                };
            });
        },
    });
});