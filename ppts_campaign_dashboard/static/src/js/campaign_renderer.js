// odoo.define("ppts_campaign_dashboard.CampaignRenderer", function (require) {
//     "use strict";

//     const AbstractRendererOwl = require("web.AbstractRendererOwl");
//     const patchMixin = require("web.patchMixin");
//     const QWeb = require("web.QWeb");
//     const session = require("web.session");
//     const { useState } = owl.hooks;

//     class CampaignRenderer extends AbstractRendererOwl {
//         constructor(parent, props) {
//             super(...arguments);
//             this.qweb = new QWeb(this.env.isDebug(), { _s: session.origin });
//             this.state = useState({
//                 localItems: props.items || [],
//                 countField: "",
//             });

//             $.ajax({
//                 url: "/get/asterisk_dialer_campaign_content",
//                 type: "POST",
//                 data: { 'uid': session.uid, },
//                 dataType: "json",
//                 async: false,
//                 success: function (data) {
//                     console.log(data, '--------')
//                     props.items = data
//                 }
//             });

//         }


//         do_action_lister(event) {
//             console.log('controllll')
//         }

//         // events: {
//         //     "click .o_optional_columns_dropdown .dropdown-item": "_onToggleOptionalColumn",
//         // }


//     }

//     const components = {
//         TreeItem: require("ppts_campaign_dashboard/static/src/js/view.js"),
//     };

//     Object.assign(CampaignRenderer, {
//         components,
//         defaultProps: {
//             items: [],
//         },
//         props: {
//             arch: {
//                 type: Object,
//                 optional: true,
//             },
//             items: {
//                 type: Array,
//             },
//             isEmbedded: {
//                 type: Boolean,
//                 optional: true,
//             },
//             noContentHelp: {
//                 type: String,
//                 optional: true,
//             },
//         },
//         template: "ppts_campaign_dashboard.CampaignRenderer",
//     });

//     return patchMixin(CampaignRenderer);
// });



odoo.define('ppts_campaign_dashboard.CampaignRenderer', function (require) {
    "use strict";

    var AbstractRenderer = require('web.BasicRenderer');
    var core = require('web.core');
    var QWeb = core.qweb;
    var view_registry = require('web.view_registry');
    const session = require("web.session");

    var CampaignRenderer = AbstractRenderer.extend({
        events: _.extend({}, AbstractRenderer.prototype.events, {

            "click #btn_redirect_partner": "redirect_partner",

        }),

        _render: function () {

            
            var items = []
            $.ajax({
                url: "/get/asterisk_dialer_campaign_content",
                type: "POST",
                data: { 'uid': session.uid, 'allowed_company': this.state.context.allowed_company_ids},
                dataType: "json",
                async: false,
                success: function (data) {
                    items = data
                }
            });
            this.$el.html(QWeb.render('CampaignRenderer', {
                items: items
            }));
        },

        redirect_partner: function (e) {
            var partner = $(e.currentTarget).data('partners').split(',').map(v => parseInt(v, 10))
            var form_id = parseInt($(e.currentTarget).data('form'))
            var tree_id = parseInt($(e.currentTarget).data('tree'))
            var campaign_id = parseInt($(e.currentTarget).data('campaign'))

            this.do_action(
                {
                    name: ("Contact"),
                    type: 'ir.actions.act_window',
                    res_model: 'res.partner',
                    view_mode: 'tree',
                    view_type: 'tree',
                    views: [[tree_id, 'list'], [form_id, 'form'], [false, 'kanban']],
                    domain: [['id', 'in', partner]],
                    target: 'current',
                    context:{campaign_id},
                    flags: {
                        mode: 'edit'
                    },
                },
                {
                    on_reverse_breadcrumb: function () {
                        // return window.location.reload(); 
                    }
                }
            )

        }


    });

    // fieldRegistry.add('video_preview', FieldVideoPreview);

    core.action_registry.add('CampaignRenderer', CampaignRenderer);
    return CampaignRenderer;

});