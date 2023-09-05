from odoo import api, fields, models, _
from odoo.exceptions import UserError

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    retail_commission = fields.Float("Retail product commission", default=0, help='Enter the retail product commission %')
    services_commission = fields.Float("Services product commission", default=0, help='Enter the services product commission %')
    enable_commission = fields.Boolean(string='Employee Commission', help='Enable the Employee Commission')
