# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Documents(models.Model):
    _inherit = 'documents.document'

    status=fields.Selection([('draft','Draft'),('submitted','Submitted')],default='submitted',string='Status')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    show_address_tab = fields.Boolean('Show Address Bar',default=False)

    def button_show_address(self):
        if self.show_address_tab == False:
            self.show_address_tab =True
        else:
            self.show_address_tab =False

    def button_membership(self):
        return True       

    def credit_transfer(self):
        return {
                'type': 'ir.actions.act_window',
                'name': _('Credit Transfer'),
                'res_model': 'partner.credit.transfer',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_from_partner_id': self.id,},
            }

    def action_client_consent_documents(self):
        self.ensure_one()
        folder_id = self.env['documents.folder'].search([('name', '=', "Customer Document")])
        return {
            'name': _('Client Consent Form'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'views': [(False, 'tree')],
            'view_mode': 'tree',
            'context': {
                "searchpanel_default_folder_id": folder_id.id,
                "default_partner_id":self.id,
            },
            'domain':[('partner_id','=',self.id)],
        }

        
