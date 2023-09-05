from odoo import fields, models, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta

class TaxesWizard(models.TransientModel):
    _name = 'taxes.wizard'
    _description ="TaxesWizard"

    date_from = fields.Date("Date from", default=datetime.today())
    date_to = fields.Date("Date to", default=datetime.today())
    company_id = fields.Many2one('res.company', string="Location")
    entered_by = fields.Many2one('res.users', string="Entered By")
    date_range = fields.Selection([
        ('year', 'Year'),
        ('quarter', 'Quarter'),('month', 'Month'),
        ('day', 'Day')], string='Quick Dates')
    view = fields.Selection([
        ('summary', 'Summary'), ('detail', 'Detail')], string='View', default='summary')

    def action_apply(self):
        if self.view == 'summary':
            if self.company_id:
                action = self.env.ref('ppts_analysis_report.sales_tax_sumy_action_view').read()[0]
                action['domain'] = [('date', '>=', self.date_from),('date', '<=', self.date_to),
                        ('company_id', '=', self.company_id.id)]
                return action

            if self.entered_by:
                action = self.env.ref('ppts_analysis_report.sales_tax_sumy_action_view').read()[0]
                action['domain'] = [('date', '>=', self.date_from),('date', '<=', self.date_to),
                        ('entered_by', '=', self.entered_by.id)]
                return action

            else:
                action = self.env.ref('ppts_analysis_report.sales_tax_sumy_action_view').read()[0]
                action['domain'] = [('date', '>=', self.date_from),('date', '<=', self.date_to)]
                return action
        elif self.view == 'detail':
            if self.company_id:
                action = self.env.ref('ppts_analysis_report.sales_tax_detail_action_view').read()[0]
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('location_id', '=', self.company_id.id)]
                return action

            elif self.entered_by:
                action = self.env.ref('ppts_analysis_report.sales_tax_detail_action_view').read()[0]
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('entered_by', '=', self.entered_by.id)]
                return action

            else:
                action = self.env.ref('ppts_analysis_report.sales_tax_detail_action_view').read()[0]
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to)]
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
