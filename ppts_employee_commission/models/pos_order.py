# -*- coding: utf-8 -*-
from odoo import models, fields
    
class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    hr_employee_id = fields.Many2one('hr.employee', string='Employee')
    commission_percentage = fields.Float("Commission %")
    commission_amt = fields.Float("Commission amount")
    
    def get_employee_pos(self):
        emp_list = []
        for emp in self.env['hr.employee'].search([('enable_commission','=',True)]):
            emp_list.append({'id':emp.id,'name':emp.name})
        return emp_list
    
    def create(self, vals):
        if 'hr_employee_id' in vals and vals.get('hr_employee_id'):
            employee_id = self.env['hr.employee'].search([('id','=',vals.get('hr_employee_id'))])
            product_id = self.env['product.product'].search([('id','=',vals.get('product_id'))])
            if product_id.type == 'service':
                vals['commission_percentage'] = employee_id.services_commission if employee_id.services_commission else 0
                vals['commission_amt'] = (vals.get('price_subtotal')*employee_id.services_commission)/100
            if product_id.type in ('product','consu'):
                vals['commission_percentage'] = employee_id.retail_commission if employee_id.retail_commission else 0
                vals['commission_amt'] = (vals.get('price_subtotal')*employee_id.retail_commission)/100
        return super(PosOrderLine, self).create(vals)
