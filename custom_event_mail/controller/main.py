# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db, Home
from datetime import datetime
from odoo.addons.website_event.controllers.main import WebsiteEventController
import logging

_logger = logging.getLogger(__name__)

class CustomWebsiteSale(WebsiteEventController):
    def event_register(self, event, **post):
        res = super(CustomWebsiteSale, self).event_register(event)
        order = request.website.sale_get_order();order_name = '';ctx = {}
        template_id = request.env.ref('custom_event_mail.event_registration_mail_for_partner_custom_event')
        if order:
            for i in order.order_line:
                order_name += i.name+','
            ctx['subject'] = order_name
            if template_id:
                template_id.sudo().with_context(ctx).send_mail(order.id, force_send=True)
        return res