odoo.define('allure_backend_theme_ent.FavoriteMenu', function (require) {
    "use strict";

    var Widget = require('web.Widget');

    const core = require('web.core');
    const config = require('web.config');
    const QWeb = core.qweb;

    var FavoriteMenuWidget = Widget.extend({
        template: 'menu.FavoriteMenu',
        resModel: 'ir.favorite.menu',
        events: {
            'click .oe_apps_menu .o_app.oe_favorite': '_onOpenMenu',
        },

        init: function () {
            this._super.apply(this, arguments);
            this.menus = [];
            this.debug = config.isDebug() ? '?debug' : '';
            this.isTouchDevice = config.device.touch;
            this.favoriteMenuNameById = {};
        },

        start: function () {
            return Promise.all([this._render(), this._super()]);
        },

        _doInitMenu: function() {
            var self = this;
            return self._rpc({
                model: self.resModel,
                method: 'get_favorite_menus'
            }).then(function (menu_data) {
                self.menus = menu_data;
                _.each(menu_data, function(menu) {
                    self.favoriteMenuNameById[menu.favorite_menu_id[0]] = menu.favorite_menu_id[1];
                });
            });
        },

        _render: function() {
            var self = this;
            return this._doInitMenu().then(function() {
                var $targetToAppend = self.$('.oe_apps_menu');
                $targetToAppend.empty();
                $(QWeb.render('menu.FavoriteMenuItem', {
                    widget: self
                })).appendTo($targetToAppend);
                if (!self.isTouchDevice) {
                    self._linkingEvents();
                };
            })
        },

        _onSortableElement: function() {
            var self = this;
            this.$('#oe_shorting').sortable({
                axis: 'y',
                connectWith: '.oe_favorite_menu',
                stop: (event, ui) => {
                    var favicons = self.$el.parents('body').find('.oe_favorite_menu .oe_apps_menu');
                    favicons.children().each(function (index) {
                        var vals = {};
                        var menu_id = $(this).data('id');
                        vals['sequence'] = index;
                        vals['favorite_menu_id'] = $(this).data('menu-id');
                        self._rpc({
                            model: self.resModel,
                            method: 'write',
                            args: [[menu_id], vals],
                        });
                    });
                },
            });
        },

        _linkingEvents: function() {
            this._onSortableElement();
        },

        _onOpenMenu: function (event) {
            var self = this;
            var $el = $(event.currentTarget);
            //in case need in future
        },

    });
    return FavoriteMenuWidget;
});
