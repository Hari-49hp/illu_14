from odoo import api, fields, models, _
from datetime import date, timedelta, datetime


class InvoiceReport(models.Model):
    _name = 'invoice.report'
    _description ="InvoiceReport"

    def _get_company_allowed_domain(self):
        if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

    name = fields.Char()
    tax_id = fields.Many2one('account.move', string='Tax Invoice ID')
    sale_date = fields.Date(string='Sale Date', copy=False)
    client = fields.Many2one('res.partner', string="Client")
    client_id = fields.Char(string='Client ID', related='client.sequence')  # , related='client.sequence'
    location_id = fields.Many2one('res.company', string='Location')
    status = fields.Selection(selection=[
        ('not_paid', 'Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Payment Due'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy')],
        string="Status", store=True, copy=False)
    inv_total = fields.Monetary(currency_field='currency_id',string='Invoiced Total', copy=False)
    company_id = fields.Many2one('res.company', string='Venue', change_default=True,
                                 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
                                 required=False)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")

