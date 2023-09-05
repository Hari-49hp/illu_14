from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class Contract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Contract'

    pay_rate_ids = fields.One2many('hr.contract.payrate', 'contract_id', string='Pay Rate')



class ContractPayrate(models.Model):
    _name = 'hr.contract.payrate'
    _rec_name = 'contract_id'
    _description ="ContractPayrate"

    contract_id = fields.Many2one('hr.contract', string='Contract')
    module_name = fields.Selection([('appointment','Appointment'),
                                   ('event','Event')],
                                  string='Module Name',required=True)
    staff_rate = fields.Selection([('none','None'),
                                   ('flat_rate','Flat Rate'),
                                   ('percentage_rate','Percentage Rate')],
                                  string='Pay Rate Type',
                                  default='percentage_rate',required=True)

    staff_rate_percentage = fields.Float('Pay Rate')

    unit_price_type = fields.Char(string=' ', compute='_compute_unit_price_type', store='True', copy=False)

    unit_price = fields.Float('Price')

    @api.depends('staff_rate')
    def _compute_unit_price_type(self):
        for rec in self:
            if rec.staff_rate == 'flat_rate':
                cur = self.env.company.currency_id.name

                rec.unit_price_type = cur

            elif rec.staff_rate == 'percentage_rate':
                rec.unit_price_type = '%'

            else:
                rec.unit_price_type = ''
