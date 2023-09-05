# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from datetime import timedelta
from random import randint

from odoo import api, fields, models, tools, _
from odoo.osv import expression
from odoo.exceptions import AccessError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    partner_mobile = fields.Char(string='Customer Mobile', compute='_compute_partner_info', store=True, readonly=False)

    @api.depends('partner_id')
    def _compute_partner_info(self):
        for ticket in self:
            if ticket.partner_id:
                ticket.partner_name = ticket.partner_id.name
                ticket.partner_email = ticket.partner_id.email
                ticket.partner_mobile = ticket.partner_id.mobile

    @api.model_create_multi
    def create(self, list_value):
        print(list_value)
        res = super(HelpdeskTicket, self).create(list_value)
        for vals in list_value:
            partner_id = vals.get('partner_id', False)
            partner_name = vals.get('partner_name', False)
            partner_mobile = vals.get('partner_mobile', False)
            if partner_name and partner_mobile and not partner_id:
                exist_partner_id = self.env['res.partner'].search([('mobile', '=', partner_mobile)], limit=1)
                print(exist_partner_id)
                if len(exist_partner_id) != 0:
                    res.partner_id = exist_partner_id.id
                else:
                    res.partner_id = self.env['res.partner'].create({
                        'name': partner_name,
                        'mobile': partner_mobile,
                    }).id
        return res

