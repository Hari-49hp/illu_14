odoo.define("allure_backend_theme_ent.HomeMenu", function (require) {
'use strict';

    const HomeMenu = require('web_enterprise.HomeMenu');
    var session = require('web.session');
    var core = require('web.core');

    var _t = core._t;

    const { patch } = require('web.utils');
    const { useState } = owl.hooks;

    patch(HomeMenu, 'allure_backend_theme_ent.HomeMenu', {

        async willStart() {
            const prom = this._super(...arguments);
            this.menus = [];
            this.favoriteMenuById = {};
            this.favoriteMenuNameById = {};
            this.editable = useState({ open: false });
            core.bus.on('reload_home_menu', this, this._reloadHomeMenu);
            return Promise.race([this._getFavMenuData(), prom]);
        },

        async _getFavMenuData() {
            var self = this;
            const favoriteMenus = await this.rpc({
                model: "ir.favorite.menu",
                method: "get_favorite_menus",
            });
            this.menus = favoriteMenus;
            _.each(favoriteMenus, function(menu) {
                self.favoriteMenuById[menu.favorite_menu_id[0]] = menu.id;
                self.favoriteMenuNameById[menu.favorite_menu_id[0]] = menu.favorite_menu_id[1];
            });
        },

        _openMenu({ menu, isApp }) {
            if (this.editable.open) { return; };
            this._super(...arguments);
        },

        _onKeydown(ev) {
            if (this.editable.open) { return; };
            this._super(...arguments);
        },

        _reloadHomeMenu(ev) {
            if (!this.editable.open) { return; };
            return this.editable.open = false;
        },

        _onClickFavorite: async function(ev) {
            var $favorited = ev.target;
            var isFavorited = $favorited.getAttribute('data-favorited');
            var parentElement = $favorited.parentNode;

            parentElement.classList.add('favorited_click_disabled');

            var def = Promise.resolve();
            if (isFavorited === 'true') {
                def = this._bindToRemoveOnUnFavorited(ev);
            } else {
                def = this._makeFavourited({
                    favorite_menu_id: parentElement.getAttribute('data-menu-id'),
                    favorite_menu_xml_id: parentElement.getAttribute('data-menu-xmlid'),
                    favorite_menu_action_id: parentElement.getAttribute('action-id'),
                    user_id: session.uid
                }, ev);
            };

            await def;
            parentElement.classList.remove('favorited_click_disabled');

        },

        async _makeFavourited(values, ev) {
            var currentTarget = ev.target;
            var parentElement = currentTarget.parentNode;

            const favoriteMenuId = await this.rpc({
                model: "ir.favorite.menu",
                method: "create",
                args: [values],
            });
            if (favoriteMenuId) {
                await this._getFavMenuData();
                core.bus.trigger('reload_favorite_menu');
                currentTarget.setAttribute('data-favorited', 'true');
                parentElement.setAttribute('data-favorite-menu-id', favoriteMenuId);
                currentTarget && currentTarget.classList.remove('fa-star-o');
                currentTarget && currentTarget.classList.add('fa-star');
                this.env.services.notification.notify({
                    message: _.str.sprintf(_t('%s added to favorite.'), this.favoriteMenuNameById[values.favorite_menu_id]),
                    type: 'info',
                });
            };
        },

        async _bindToRemoveOnUnFavorited(ev) {
            var currentTarget = ev.target;
            var parentElement = currentTarget.parentNode;
            var MenuId = parentElement.getAttribute('data-favorite-menu-id');
            var FavoriteMenuId = parentElement.getAttribute('data-menu-id');

            const favoriteMenuIdUnlink = await this.rpc({
                model: "ir.favorite.menu",
                method: "unlink",
                args: [MenuId],
            });
            if (favoriteMenuIdUnlink) {
                await this._getFavMenuData();
                core.bus.trigger('reload_favorite_menu');
                currentTarget.setAttribute('data-favorited', 'false');
                currentTarget && currentTarget.classList.remove('fa-star');
                currentTarget && currentTarget.classList.add('fa-star-o');
                this.env.services.notification.notify({
                    message: _.str.sprintf(_t('%s removed from favorite.'), this.favoriteMenuNameById[FavoriteMenuId]),
                    type: 'info',
                });
                this.favoriteMenuNameById = _.omit(this.favoriteMenuNameById, FavoriteMenuId);
            };
        },

        _onClickAppEdit(ev) {
            var inputval = this.el.querySelector('.o_menu_search_input').value;
            if (inputval) {
                this._updateQuery("");
            };
            this.editable.open = !this.editable.open;
            this.state.isSearching = false;
        },
    });
});