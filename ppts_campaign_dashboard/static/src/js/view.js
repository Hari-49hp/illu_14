odoo.define(
    "ppts_campaign_dashboard/static/src/js/view.js",
    function (require) {
        "use strict";
        const { Component } = owl;
        const patchMixin = require("web.patchMixin");
        const { useState } = owl.hooks;

        var rpc = require('web.rpc');

        var ActionManager = require('web.ActionManager');

        var core = require('web.core');
        var _t = core._t;
        var _lt = core._lt;

        class TreeItem extends Component {
            constructor(...args) {
                super(...args);
                this.state = useState({
                    isDraggedOn: false,
                });
            }

            toggleChildren(event) {
                var self = this;
                // event.stopPropagation();
                // event.preventDefault();

                // self.do_action({
                //     name: _t("My Profile"),
                //     type: 'ir.actions.act_window',
                //     res_model: 'hr.employee',
                //     view_mode: 'tree',
                //     view_type: 'tree',
                //     views: [[false, 'tree']],
                //     context: { 'edit': true },
                //     domain: [],
                //     target: 'current'
                // }, { on_reverse_breadcrumb: function () { return self.reload(); } })

                rpc.query({
                    model: "res.partner",
                    method: "move_to_the_page",
                    args: [],
                }).then(function () {
                    //Set a delay or the update is not visible
                    // window.location.reload();

                    this.do_action({
                        name: _t("My Profile"),
                        type: 'ir.actions.act_window',
                        res_model: 'hr.employee',
                        view_mode: 'tree',
                        view_type: 'tree',
                        views: [[false, 'tree']],
                        context: { 'edit': true },
                        domain: [],
                        target: 'current'
                    }, { on_reverse_breadcrumb: function () { return this.reload(); } })
                });

            }


        }

        Object.assign(TreeItem, {
            components: { TreeItem },
            props: {
                item: {},
                countField: "",
            },
            template: "ppts_campaign_dashboard.TreeItem",
        });




        return patchMixin(TreeItem);
    }
);
