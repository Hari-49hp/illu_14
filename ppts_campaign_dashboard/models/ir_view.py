# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError

class IR_UI_View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('campaign', "Campaign View")])


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def move_to_the_page(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Contact',
                'view_mode': 'tree',
                'res_model': 'res.partner',
                # 'view_id': False,
                # 'views': [(self.env.ref('custom_partner.res_partner_history_history_from_view').id, 'form')],
                # 'res_id': self.id,
                # 'clear_breadcrumb': True,
                'domain': [],
                'target': 'main',
            }