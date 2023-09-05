odoo.define("allure_backend_theme_ent.HomeMenuWrapper", function (require) {
'use strict';

    const HomeMenuWrapper = require('web_enterprise.HomeMenuWrapper');
    const utils = require('web.utils');

    const { patch } = require('web.utils');

    patch(HomeMenuWrapper, 'allure_backend_theme_ent.HomeMenuWrapper', {

        _processMenuData(menuData) {
            const apps = [];
            const menuItems = [];
            utils.traversePath(menuData, (menuItem, parents) => {
                if (!menuItem.id || !menuItem.action) {
                    return;
                }
                const isApp = !menuItem.parent_id;
                const item = {
                    parents: parents.slice(1).map(p => p.name).join(' / '),
                    label: menuItem.name,
                    id: menuItem.id,
                    xmlid: menuItem.xmlid,
                    action: menuItem.action ? menuItem.action.split(',')[1] : '',
                    webIcon: menuItem.web_icon,
                };
                if (!menuItem.parent_id) {
                    const [iconClass, color, backgroundColor] = (item.webIcon || '').split(',');
                    if (menuItem.theme_icon_data) {
                        item.webIconData = `data:image/png;base64,${menuItem.theme_icon_data}`.replace(/\s/g, "");
                    } else if (!menuItem.theme_icon_data) {
                        if (menuData.base_menu_icon == 'base_icon') {
                            item.webIconData = '/allure_backend_theme_ent/static/src/img/no_modul_ioc.png';
                        } else if (menuData.base_menu_icon == '3d_icon') {
                            item.webIconData = '/allure_backend_theme_ent/static/src/img/menu/custom.png';
                        } else if (menuData.base_menu_icon == '2d_icon') {
                            item.webIconData = '/allure_backend_theme_ent/static/src/img/menu_2d/custom.png';
                        }
                    } else if (backgroundColor !== undefined) { // Could split in three parts?
                        item.webIcon = { iconClass, color, backgroundColor };
                    } else {
                        item.webIconData = '/web_enterprise/static/src/img/default_icon_app.png';
                    }
                } else {
                    item.menu_id = parents[1].id;
                }
                if (isApp) {
                    apps.push(item);
                } else {
                    menuItems.push(item);
                }
            });
            return { apps, menuItems };
        }
    });
});