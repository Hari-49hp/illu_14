odoo.define("allure_backend_theme_ent.DropdownMenu", function (require) {
'use strict';

    const DropdownMenu = require('web.DropdownMenu');
    const { patch } = require('web.utils');

    patch(DropdownMenu, 'allure_backend_theme_ent.DropdownMenu', {

        async willStart() {
            this.displayComparison = false;
            return this._super(...arguments);
        },

        /**
        * Click event of dropdown button click for toggle ad_active class.
        **/

        _onDropdownBtnClick(ev) {
            if (this.displayCaret || (this.displayChevron && this.el.closest('.o_search_options'))) {
                return this.state.open = !this.state.open;
            };
            var searchOptions = document.querySelector('.o_search_options');
            searchOptions && searchOptions.childNodes.forEach(childNode => {
                childNode.classList && childNode.classList.remove('ad_active');
            });
            var actionMenus = document.querySelector('.o_cp_action_menus');
            actionMenus && actionMenus.childNodes.forEach(childNode => {
                childNode.classList && childNode.classList.remove('ad_active');
            });
            this.el.classList.add('ad_active');
            this.state.open = true;
        },
    });
});
