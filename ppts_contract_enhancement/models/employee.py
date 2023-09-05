from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    def _domain_incharge_id(self):
        # domain = self.env['hr.department'].search([('name','=','Sales Department')], limit=1)
        # company_id = self.env.company.id
        company_ids = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
        employee_id = self.env['hr.employee'].search([('user_id','!=',False),('department_id.name','=','Sales Department'),('location_ids','in',company_ids.ids)])
        lst = []
        for i in employee_id: 
            lst.append(i.user_id.id)
        return [('id','in',lst)]

    incharge_id = fields.Many2one('res.users', string='Sales Incharge', domain=_domain_incharge_id)



