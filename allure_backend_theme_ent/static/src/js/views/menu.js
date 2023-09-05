// odoo Menu inherit Open time has Children submenu add.
odoo.define('allure_backend_theme_ent.Menu', function (require) {
    "use strict";

    var __themesDB = require('allure_backend_theme_ent.AllureWebThemes');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var Menu = require('web_enterprise.Menu');
    // var AppsMenu = require('web.AppsMenu');
    var UserMenu = require('web.UserMenu');
    var QuickMenu = require('allure_backend_theme_ent.QuickMenu');
    var favoriteMenu = require('allure_backend_theme_ent.FavoriteMenu');
    var config = require('web.config');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var dom = require('web.dom');
    var SwitchCompanyMenu = require('web.SwitchCompanyMenu');

    var QWeb = core.qweb;

    var LogoutMessage = Widget.extend({
        template: 'LogoutMessage',
        events: {
            'click  a.oe_cu_logout_yes': '_onClickLogout',
            'click  .mb-control-close': '_onClickClose',
        },
        init: function (parent) {
            this._super(parent);
        },
        _onClickLogout: function (e) {
            var self = this;
            self.getParent()._onMenuLogout();
        },
        _onClickClose: function (e) {
            this.$el.remove();
        }
    });

    if (config.device.isMobile) {
        SystrayMenu.Items.push(SwitchCompanyMenu);
    };

    UserMenu.include({
        init: function () {
            this._super.apply(this, arguments);
            if (config.device.isMobile) {
                this.className = 'o_user_menu';
                this.tagName = 'li';
                this.template = 'UserMenu';
            }
        },
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                var $avatar = self.$('.oe_topbar_avatar');
                var avatar_src = session.url('/web/image', {
                    model: 'res.users',
                    field: 'image_256',
                    id: session.uid,
                });
                $avatar.attr('src', avatar_src);
                self.$el.on('click', 'a.o_menu_logout', function (ev) {
                    ev.preventDefault();
                    return new LogoutMessage(self).appendTo(self.$el.closest('body'));
                });
            });
        },
    });

    Menu.include({
        menusTemplate: 'Menu.sections',
        events: _.extend({}, Menu.prototype.events, {
            'click #children_toggle': '_onSubmenuToggleClicked',
            'click #av_full_view': '_onFullViewClicked',
            'click .oe_back_btn': '_onMenuClose',
            'click a[data-menu]': '_onMenuClose',
            'click .oe_full_button': '_onFullScreen',
            'click .o_mobile_menu_toggle': '_onMobileMenu',
            'click .o_mail_preview': '_onMenuClose',
            'click #menu_toggle': '_menuClick',
            'click .ad_systray_skeleton': '_onClickAdSystraySkeleton',
            'click .oe_apps_menu': '_onClickAppsMenu',
            'click .user_menu': '_onSystrayOpen',
        }),
        init: function (parent, menu_data) {
            this._super.apply(this, arguments);
            this.company_id = session.company_id;
            this.user_id = session.uid;
            this.menu_id = true;
            this.themeData = __themesDB.get_theme_config_by_uid(session.uid);
            core.bus.on('reload_favorite_menu', this, this._reloadFavoriteMenu);
        },
        start: function () {
            var self = this;
            if (this.themeData && this.themeData.base_menu === 'base_menu') {
                $('body').addClass('oe_base_menu');
                this.$('.o_main_navbar').replaceWith($(QWeb.render('MenuTitle')));
            }
            this.$av_full_view = this.$('#av_full_view');
            this.$menu_toggle = this.$('#menu_toggle');
            this.$menu_brand_placeholder = this.$('.o_menu_brand');
            this.$section_placeholder = this.$('.o_menu_sections');
            this.$children_toggle = this.$('#children_toggle');
            this.$menu_apps = this.$('.o_menu_apps');

            var on_secondary_menu_click = function (ev) {
                ev.preventDefault();
                var menu_id = $(ev.currentTarget).data('menu');
                var action_id = $(ev.currentTarget).data('action-id');
                self._on_secondary_menu_click(menu_id, action_id);
            };
            var menu_ids = _.keys(this.$menu_sections);
            var primary_menu_id, $section;
            for (var i = 0; i < menu_ids.length; i++) {
                primary_menu_id = menu_ids[i];
                $section = this.$menu_sections[primary_menu_id];
                $section.on('click', 'a[data-menu]', self, on_secondary_menu_click.bind(this));
            }

            // // Apps Menu
            // this._appsMenu = new AppsMenu(self, this.menu_data);
            // var appsMenuProm = this._appsMenu.appendTo(this.$menu_apps);

            // Systray Menu
            this.systray_menu = new SystrayMenu(this);
            var systrayMenuProm = this.systray_menu.attachTo(this.$('.o_menu_systray')).then(function() {
                if (self.themeData && self.themeData.base_menu === 'base_menu' && !config.device.touch) {
                    dom.initAutoMoreMenu(self.$section_placeholder, {
                        maxWidth: function () {
                            return self.$el.width() - (self.$av_full_view.outerWidth(true) + self.$menu_toggle.outerWidth(true) + self.$menu_brand_placeholder.outerWidth(true) + self.systray_menu.$el.outerWidth(true));
                        },
                    });
                }
            });
            var QuickMenu = this._loadQuickMenu();
            // return Promise.all([appsMenuProm, systrayMenuProm, QuickMenu]);
            return Promise.all([systrayMenuProm, QuickMenu]);
        },
        _updateMenuBrand: function (brandName) {
            if (brandName) {
                this.$menu_brand_placeholder.text(brandName).show();
                this.$section_placeholder.show();
                this.$children_toggle.show()
            } else {
                this.$menu_brand_placeholder.hide()
                this.$section_placeholder.hide();
                this.$children_toggle.hide()
            }
        },
        _onToggleHomeMenu: function (ev) {
            if (!this.homeMenuDisplayed) { core.bus.trigger('reload_home_menu'); };
            $('.o_menu_systray').hasClass('show') && $('.o_menu_systray').removeClass('show');
            return this._super.apply(this, arguments);
        },
        _onSubmenuToggleClicked: function (e) {
            $('body').removeClass('nav-sm').toggleClass('ad_open_childmenu');
            $(this).toggleClass('active');
            $('.o_menu_systray').hasClass('show') && $('.o_menu_systray').removeClass('show');
        },
        change_menu_section: function (primary_menu_id) {
            if (!this.$menu_sections[primary_menu_id]) {
                this._updateMenuBrand();
                return; // unknown menu_id
            }

            if (this.current_primary_menu === primary_menu_id) {
                return; // already in that menu
            }

            if (this.current_primary_menu) {
                this.$menu_sections[this.current_primary_menu].detach();
            }

            // Get back the application name
            for (var i = 0; i < this.menu_data.children.length; i++) {
                if (this.menu_data.children[i].id === primary_menu_id) {
                    this._updateMenuBrand(this.menu_data.children[i].name);
                    break;
                }
            }
            if (this.themeData && this.themeData.base_menu === 'base_menu') {
                this.$menu_sections[primary_menu_id].appendTo(this.$section_placeholder);
                this.current_primary_menu = primary_menu_id;
            } else {
                // Selcted Menu
                var submenu_data = _.findWhere(this.menu_data.children, {id: primary_menu_id});
                this.menu_id = submenu_data;
                var $submenu_title = $(QWeb.render('SubmenuTitle', {
                    selected_menu: submenu_data,
                }));
                this.$section_placeholder.html($submenu_title);
                $('<div>', {
                    class: 'o_submenu_list',
                }).append(this.$menu_sections[primary_menu_id]).appendTo(this.$section_placeholder);
                this.current_primary_menu = primary_menu_id;
                $('body').toggleClass('ad_nochild', !submenu_data.children.length);

                if ($('body').hasClass('ad_open_childmenu') && !submenu_data.children.length) {
                    $('body').removeClass('ad_open_childmenu')
                }
            }

            core.bus.trigger('resize');
        },
        _onMobileMenu: function (e) {
            $('body').toggleClass('open_mobile_menu');
        },
        _onMenuClose: function (e) {
            $('body').removeClass('open_mobile_menu');
            $('.o_menu_systray').removeClass('show');
            if (config.device.touch || config.device.size_class <= config.device.SIZES.MD) {
                $('body').removeClass('ad_open_childmenu').removeClass('nav-sm');
            }
        },
        _onSystrayOpen: function (e) {
            $('body').removeClass('ad_open_childmenu open_mobile_menu');
        },
        _onClickAdSystraySkeleton: function (e) {
            $('.o_menu_systray').removeClass('show');
        },
        _onClickAppsMenu: function(e) {
            $('.o_menu_systray').hasClass('show') && $('.o_menu_systray').removeClass('show');
        },
        _onFullScreen: function (e) {
            document.fullScreenElement && null !== document.fullScreenElement || !document.mozFullScreen &&
            !document.webkitIsFullScreen ? document.documentElement.requestFullScreen ? document.documentElement.requestFullScreen() :
                document.documentElement.mozRequestFullScreen ? document.documentElement.mozRequestFullScreen() :
                    document.documentElement.webkitRequestFullScreen && document.documentElement.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT) :
                document.cancelFullScreen ? document.cancelFullScreen() :
                    document.mozCancelFullScreen ? document.mozCancelFullScreen() :
                        document.webkitCancelFullScreen && document.webkitCancelFullScreen()
        },
        _onFullViewClicked: function (e) {
            $('body').removeClass('nav-sm').toggleClass('ad_full_view');
        },
        // Check this method
        _on_secondary_menu_click: function (menu_id, action_id) {
            var self = this;

            // It is still possible that we don't have an action_id (for example, menu toggler)
            if (action_id) {
                self._trigger_menu_clicked(menu_id, action_id);
                this.current_secondary_menu = menu_id;
            }
        },
        _loadQuickMenu: function () {
            var self = this;
            this.FavoriteMenu = new favoriteMenu(self);
            this.FavoriteMenu.appendTo(this.$el.find('.oe_menu_layout.oe_theme_menu_layout'));
            this.$el.parents('.o_web_client').find('.o_menu_systray li.o_global_search').remove();
        },
        switchMode: function (mode) {
            var self = this;
            this._super.apply(this, arguments);
            if (!mode) {
                this.$detached_systray.appendTo('.o_main_navbar');
                if (this.studio_menu) {
                    this.studio_menu.destroy();
                    this.studio_menu = undefined;
                }
            }
        },
        _reloadFavoriteMenu: function () {
            if (this.FavoriteMenu) {
                this.FavoriteMenu._render();
            };
        },
        _menuClick: function(ev) {
            if (config.device.isMobile && config.device.size_class <= config.device.SIZES.XS) {
                $('body').removeClass('ad_open_childmenu');
            };
        },
    });

});
