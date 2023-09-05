from odoo import api, fields, models, _
from datetime import date, timedelta, datetime


class ReturnsReport(models.Model):
    _name = 'returns.report'
    _description= "ReturnsReport"

    def _get_company_allowed_domain(self):
        if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

    name = fields.Char()
    date = fields.Date(string='Return Date', copy=False)
    client = fields.Many2one('res.partner', string="Client")
    item_name = fields.Char(string="Item")
    color = fields.Char(string='Color')
    size = fields.Char(string='Size')
    qty = fields.Float(string='Quantity')
    return_amount = fields.Monetary(currency_field='currency_id', string='Return Amount')
    payment_method = fields.Many2many('pos.payment.method') #, compute='_get_pay_method'
    reason = fields.Char('Reason')
    defective = fields.Char('Defective')
    location_id = fields.Many2one('res.company', string='Location')
    company_id = fields.Many2one('res.company', string='Venue', change_default=True,
                                 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
                                 required=False)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    pos_id = fields.Many2one('pos.order')

