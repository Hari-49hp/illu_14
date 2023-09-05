// odoo.define("ppts_campaign_dashboard.CampaignView", function (require) {
//     "use strict";

//     const AbstractView = require("web.AbstractView");
//     const core = require("web.core");
//     const RendererWrapper = require("web.RendererWrapper");
//     const view_registry = require("web.view_registry");

//     const AbstractController = require('web.AbstractController');
//     const AbstractModel = require('web.AbstractModel');
//     const CampaignController = require('web.AbstractController');
//     const CampaignRenderer = require('ppts_campaign_dashboard.CampaignRenderer');
//     const CampaignModel = AbstractModel.extend({});

//     const _lt = core._lt;

//     const CampaignView = AbstractView.extend({
//         accesskey: "m",
//         display_name: _lt("Campaign View"),
//         icon: "fa-tasks",
//         config: _.extend({}, AbstractView.prototype.config, {
//             Controller: CampaignController,
//             Model: CampaignModel,
//             Renderer: CampaignRenderer,
//         }),
//         viewType: "campaign",
//         searchMenuTypes: ["filter", "favorite"],

//         /**
//          * @override
//          */

//         init: function () {
//             this._super.apply(this, arguments);
//         },
//         getRenderer(parent, state) {
//             state = Object.assign(state || {}, this.rendererParams);
//             return new RendererWrapper(parent, this.config.Renderer, state);
//         },

//     });

//     view_registry.add("campaign", CampaignView);
//     return CampaignView;
// });


odoo.define('ppts_campaign_dashboard.CampaignView', function (require) {
    "use strict";

    var AbstractView = require('web.AbstractView');
    var view_registry = require('web.view_registry');

    var CampaignController = require('ppts_campaign_dashboard.CampaignController');
    var CampaignModel = require('ppts_campaign_dashboard.CampaignModel');
    var CampaignRenderer = require('ppts_campaign_dashboard.CampaignRenderer');


    var CampaignView = AbstractView.extend({
        display_name: 'Campaign View',
        icon: 'fa-pagelines',
        cssLibs: [],
        config: _.extend({}, AbstractView.prototype.config, {
            Model: CampaignModel,
            Controller: CampaignController,
            Renderer: CampaignRenderer,
        }),
        viewType: 'campaign',
        groupable: false,
        init: function () {
            this._super.apply(this, arguments);
        },
    });
    view_registry.add('campaign', CampaignView);
    return CampaignView;
});