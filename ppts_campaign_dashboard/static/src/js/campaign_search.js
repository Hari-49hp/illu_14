odoo.define('ppts_campaign_dashboard.campaign_dashboard_search', function (require) {
"use strict";
const ActionModel = require("web/static/src/js/views/action_model.js");
const {Component } = owl;

var BasicView = require('web.AbstractView');
BasicView.include({
      _createSearchModel: function (params, extraExtensions) {
        // Search model + common config
        const { fields, favoriteFilters, controlPanelInfo, searchPanelInfo } = params;
        const extensions = Object.assign({}, extraExtensions);
        const importedState = params.controllerState || {};

        // Control panel params
        if (this.withControlPanel) {
            // Control panel (Model)
            const ControlPanelComponent = this.config.ControlPanel;
            extensions[ControlPanelComponent.modelExtension] = {
                actionId: params.action.id,
                // control initialization
                activateDefaultFavorite: params.activateDefaultFavorite,
                archNodes: controlPanelInfo.children,
                dynamicFilters: params.dynamicFilters,
                favoriteFilters,
                withSearchBar: params.withSearchBar,
            };
            this.controllerParams.withControlPanel = true;
            // Control panel (Component)
            // used to define the variable for
            console.log(params)
            // set default search as false if view type form or campaign using override 08-08-22
            var searchbox = true;
            if (this.viewType == 'campaign' || this.viewType == 'form') {
                searchbox = false;
            }
            const controlPanelProps = {
                action: params.action,
                breadcrumbs: params.breadcrumbs,
                fields,
                searchMenuTypes: params.searchMenuTypes,
                view: this.fieldsView,
                views: params.action.views && params.action.views.filter(
                    v => v.multiRecord === this.multi_record
                ),
                withBreadcrumbs: params.withBreadcrumbs,
                withSearchBar: params.withSearchBar,
                withSearchBar: searchbox,
            };
            this.controllerParams.controlPanel = {
                Component: ControlPanelComponent,
                props: controlPanelProps,
            };
        }

        // Search panel params
        if (this.withSearchPanel) {
            // Search panel (Model)
            const SearchPanelComponent = this.config.SearchPanel;
            extensions[SearchPanelComponent.modelExtension] = {
                archNodes: searchPanelInfo.children,
            };
            this.controllerParams.withSearchPanel = true;
            this.rendererParams.withSearchPanel = true;
            // Search panel (Component)
            const searchPanelProps = {
                importedState: importedState.searchPanel,
            };
            if (searchPanelInfo.attrs.class) {
                searchPanelProps.className = searchPanelInfo.attrs.class;
            }
            this.controllerParams.searchPanel = {
                Component: SearchPanelComponent,
                props: searchPanelProps,
            };
        }

        const searchModel = new ActionModel(extensions, {
            env: Component.env,
            modelName: params.modelName,
            context: Object.assign({}, this.loadParams.context),
            domain: this.loadParams.domain || [],
            importedState: importedState.searchModel,
            searchMenuTypes: params.searchMenuTypes,
            searchQuery: params.searchQuery,
            fields,
        });

        return searchModel;
    },
});
});