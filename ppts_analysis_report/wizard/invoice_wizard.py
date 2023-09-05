from odoo import fields, models, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta

class InvoiceWiz(models.TransientModel):
    _name = 'invoice.wizard'
    _description="InvoiceWiz"

    date_from = fields.Date("Date from", default=datetime.today())
    date_to = fields.Date("Date to", default=datetime.today())
    company_id = fields.Many2one('res.company', string="Location")
    status = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Payment Due'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy')],
        string="Status", store=True, copy=False)
    date_range = fields.Selection([
        ('year', 'Year'),
        ('quarter', 'Quarter'),('month', 'Month'),
        ('day', 'Day')], string='Quick Dates')


    def action_apply(self):
        ref = self.env['invoice.report'].search([])
        if ref:
            if self.company_id:
                action = self.env.ref('ppts_analysis_report.invoice_report_action_view').read()[0]
                action['domain'] = [('sale_date', '>=', self.date_from),('sale_date', '<=', self.date_to),
                        ('location_id', '=', self.company_id.id)]
                return action

            elif self.status:
                action = self.env.ref('ppts_analysis_report.invoice_report_action_view').read()[0]
                action['domain'] = [('sale_date', '>=', self.date_from),('sale_date', '<=', self.date_to),
                        ('status', '=', self.status)]
                return action

        else:
            action = self.env.ref('ppts_analysis_report.invoice_report_action_view').read()[0]
            action['domain'] = [('sale_date', '>=', self.date_from),('sale_date', '<=', self.date_to)]
            return action

    @api.onchange('date_range')
    def date_one(self):
        dt = self.date_to
        if self.date_range == 'year':
            y = relativedelta(years=1)
            tot = dt - y
            self.date_from = tot
        if self.date_range == 'quarter':
            q = relativedelta(months=3)
            tot = dt - q
            self.date_from = tot
        if self.date_range == 'month':
            m = relativedelta(days=30)
            tot = dt - m
            self.date_from = tot
        if self.date_range == 'day':
            self.date_from = dt

