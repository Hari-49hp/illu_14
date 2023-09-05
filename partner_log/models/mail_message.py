# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, tools, _

class MailMessage(models.Model):
    _inherit = 'mail.message'

    partner_id = fields.Many2one('res.partner', string='Customer')
    model_id = fields.Many2one('ir.model', 'Model')

    # @api.model
    # def create(self,vals):
    #     log_id = self.env['log.config'].search([])
    #     model_id = self.env['ir.model'].search([('model','=',vals['model'])],limit=1)
    #     if model_id: vals['model_id'] = model_id.id
        
    #     if 'tracking_value_ids' in vals:
    #         for i in vals['tracking_value_ids']:
    #             old = 'False'; new = 'False'
    #             if 'old_value_char' in i[2]:
    #                 old = i[2]['old_value_char'] or 'N/A'
    #             if 'new_value_char' in i[2]: 
    #                 new = i[2]['new_value_char'] or 'N/A'
    #             vals['body'] += old + ' \u2794 ' + new + '<br/>'

    #     for rec in log_id:
    #         if vals['model'] == rec.model and rec.active:
    #             record_id = self.env[vals['model']].browse(int(vals['res_id']))
    #             if 'partner_id' in self.env[vals['model']]._fields:
    #                 vals['partner_id'] = record_id.partner_id.id
    #     return super(MailMessage, self).create(vals)