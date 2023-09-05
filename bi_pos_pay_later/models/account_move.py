# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    reconcile_pos_id = fields.Many2one('pos.order', string='POS Order')
    
    
class AccountMove(models.Model):
    _inherit = 'account.move'

    pos_payment_ref = fields.Char(string='POS Payment Ref.')