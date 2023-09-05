odoo.define("allure_backend_theme_ent.ControlPanel", function (require) {

    const ControlPanel = require('web.ControlPanel');
    const { device } = require("web.config");
    const { hooks } = owl;
    const { useExternalListener } = hooks;

    var core = require('web.core');

    ControlPanel.patch('web.ControlPanel', T => class extends T {

        constructor() {
            super(...arguments);
            this.isMobileView = device.isMobile;

            useExternalListener(window, 'click', this._onWindowClick);
        }

        _onClickSearchButton(e) {
            var parentNode = this.el.parentNode;
            var searchOptions = e.target.closest('.o_control_panel').querySelector('.o_search_options');

            parentNode.classList.toggle('ad_open_search');
            searchOptions.classList.toggle('o_hidden');
            searchOptions && searchOptions.childNodes.forEach(childNode => {
                childNode.classList && childNode.classList.remove('ad_active');
            });
            if (searchOptions.childNodes.length > 0) {
                searchOptions.childNodes[0].classList.add('ad_active');
            };
        }

        _onShowMobileSearchFilter(e) {
            var $oSearchOptions = e.target.closest('.o_action') || e.target.closest('.o_widget_Discuss');
            $oSearchOptions && $oSearchOptions.classList.remove('ad_open_search');
        }

        _onShowMobileSearchClear(e) {
            this.model.dispatch('clearQuery');
        }

        _onClickCpButtons(e) {
            var $oCpBottom = e.target.closest('.o_cp_bottom');
            $oCpBottom.classList.add('cp_open');
        }

        _onWindowClick(ev) {
            if (this.isMobileView && this.el &&
                !this.el.contains(document.activeElement) &&
                !this.el.contains(ev.target)) {
                var $oCpBottom = this.el.querySelector('.o_cp_bottom');
                $oCpBottom && $oCpBottom.classList.remove('cp_open');
            };
        }
    });

    return ControlPanel;
});