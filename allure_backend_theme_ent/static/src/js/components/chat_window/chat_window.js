odoo.define("allure_backend_theme_ent/static/src/js/components/chat_window/chat_window.js", function (require) {
'use strict';

    const ChatWindow = require('mail/static/src/components/chat_window/chat_window.js');
    const { patch } = require('web.utils');

    patch(ChatWindow, 'allure_backend_theme_ent/static/src/js/components/chat_window/chat_window.js', {

        mounted() {
            this._super(...arguments);
            if (!this.env.messaging.device.isMobile) {
                document.body.classList.add('ad-chat-window');
            }
        },

        willUnmount() {
            if (this.env.messaging.device.isMobile) { this._super(...arguments); };

            var $odial = document.querySelector('.o_dial');
            var isVoip = _.contains(odoo._modules, 'voip') && _.has(odoo.__DEBUG__.services, 'voip.DialingPanel');
            if ((!isVoip || (isVoip && $odial && $odial.style.display === "none"))
                && (document.querySelectorAll('.o_ChatWindow').length - 1) === 0) {
                document.body.classList.remove('ad-chat-window');
            };
            this._super(...arguments);
        },
    });
});