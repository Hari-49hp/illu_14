odoo.define('ppts_custom_apt_mgmt/static/src/js/message.js', function (require) {
    'use strict';

    const MessageList = require('mail/static/src/components/message_list/message_list.js'); // Message's parent component
    const Message = require('mail/static/src/components/message/message.js'); // Component what we want inherit
    
    class MessageExtended extends Message {
        constructor() {
            super(...arguments);
        }

        _computeDateFromNow() {
            if (!this.date) {
                return clear();
            }
            super._update(...arguments);
            return this.date;
        }

    };
    MessageList.components.Message = MessageExtended;
});

