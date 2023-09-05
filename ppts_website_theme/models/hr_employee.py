'''
Created on Nov 6, 2018

@author: Zuhair Hammadi
'''
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _inherit = "hr.employee"

    partner_id = fields.Many2one('res.partner',string="Related Partner",help="Employee will be created as partner",readonly=True)
    @api.model
    def create(self, vals):
        res = super(Employee, self).create(vals)       
        value = {
        'name': res.name or "",
        'mobile':res.work_phone,
        'email':res.work_email,
        'customer_rank':0,
        'company_type':'company',
        'alternate_mobile':False,
        'alternate_email':False,
        'type':'contact',
        'is_employee':True,
        'hr_id':res.id,
        }
        partner_id = self.env['res.partner'].create(value)
        res.partner_id = partner_id.id
        return res
