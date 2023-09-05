# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_pos_order = fields.Boolean(related='company_id.is_pos_order', string='Create POS Order', readonly=False)

class ResCompany(models.Model):
    _inherit = "res.company"

    is_pos_order = fields.Boolean(string='Create POS Order', readonly=False)
