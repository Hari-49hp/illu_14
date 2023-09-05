odoo.define("allure_backend_theme_ent.SearchBar", function (require) {
'use strict';

    const SearchBar = require('web.SearchBar');
    const { patch } = require('web.utils');

    var config = require('web.config');

    patch(SearchBar, 'allure_backend_theme_ent.SearchBar', {

        mounted() {
            this._super(...arguments);
            this.isMobileView = config.device.isMobile;
            this.searchFacets = this.model.get('facets');
            this._manageFacets();
        },

        patched() {
            this.searchFacets = this.model.get('facets');
            this._manageFacets();
        },

        _manageFacets: function(detachToInput) {
            detachToInput = _.isUndefined(detachToInput) ? false : detachToInput;

            var searchArea = 0;
            var deviceWidth = window.innerWidth;
            var mobileClass = this.isMobileView ? '_mobile' : '';

            var $o_searchview = document.querySelector('.o_searchview');
            var $o_searchview_input = document.querySelector('.o_searchview_input');
            var $o_search_recs = document.querySelector('.o_search_recs' + mobileClass);
            var $o_search_rec_ul = document.querySelector('.o_search_rec_ul' + mobileClass);

            for (var i = 0; i < this.searchFacets.length; i++) {
                const $searchFacet = document.querySelectorAll('[facet-count="' + i + '"]');

                $searchFacet.forEach(facet => {
                    searchArea += facet.clientWidth;
                    if (!detachToInput && searchArea !== 0) {
                        if (this.isMobileView && (searchArea > (deviceWidth - 230))) {
                            $o_search_rec_ul && $o_search_rec_ul.appendChild(facet);
                        }
                        if (!this.isMobileView && searchArea > ((deviceWidth / 2) - 250)) {
                            $o_search_rec_ul && $o_search_rec_ul.appendChild(facet);
                        };
                    } else {
                        if ($o_searchview_input && $o_searchview_input.parentNode) {
                            $o_searchview_input.parentNode.insertBefore(facet, $o_searchview_input);
                        };
                    };
                });
            };

            setTimeout(function () {
                if($o_search_rec_ul){
                    var hasDropDownFacet = Boolean($o_search_rec_ul.childNodes.length);
                    $o_searchview.classList.toggle('show', hasDropDownFacet);
                    $o_search_recs && $o_search_recs.classList.toggle('o_hidden', !hasDropDownFacet);
                    $o_search_rec_ul.classList.toggle('show', hasDropDownFacet);
                    $o_search_rec_ul.classList.toggle('o_hidden', !hasDropDownFacet);
                }
            }, 10);
        },
    });
});
