from odoo import api, fields, models, _

class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    employee_desc = fields.Text(string='Description about Employee')
    employee_type = fields.Many2many('hr.employee.category',string='Employee Type')

