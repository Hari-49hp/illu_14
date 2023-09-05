from odoo import fields, models, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta

class SalesWizard(models.TransientModel):
    _name = 'sales.wizard'
    _description="SalesWizard"

    date_from = fields.Date("Date from", default=datetime.today())
    date_to = fields.Date("Date to", default=datetime.today())
    company_id = fields.Many2one('res.company', string="Location")
    payment_method = fields.Selection([('cash', 'Cash'),('net', 'Net Banking'),
        ('bank', 'Bank')], string="Payment Method")
    entered_by = fields.Many2one('res.users', string="Entered by")
    sales_rep_id = fields.Many2one('res.users', string="Sales Rep")
    date_range = fields.Selection([
        ('year', 'Year'),
        ('quarter', 'Quarter'),('month', 'Month'),
        ('day', 'Day')], string='Quick Dates')
    product_service = fields.Selection([
        ('consu', 'Consumable'),('product', 'Product'),
        ('service', 'Service')], string='Product Type')
    view = fields.Selection([
        ('summary', 'Summary'),('detail', 'Detail')], string='View', default='summary')


    def action_apply(self):
        if self.view == 'summary':
            if self.sales_rep_id:
                action = self.env.ref('ppts_analysis_report.sales_report_summary_action_view').read()[0]
                action['domain'] = [('sale_date', '>=', self.date_from),('sale_date', '<=', self.date_to),
                        ('sales_rep_id', '=', self.sales_rep_id.id)]
                return action

            elif self.company_id:
                action = self.env.ref('ppts_analysis_report.sales_report_summary_action_view').read()[0]
                action['domain'] = [('sale_date', '>=', self.date_from),('sale_date', '<=', self.date_to),
                        ('location', '=', self.company_id.id)]
                return action

            elif self.entered_by:
                action = self.env.ref('ppts_analysis_report.sales_report_summary_action_view').read()[0]
                action['domain'] = [('sale_date', '>=', self.date_from),('sale_date', '<=', self.date_to),
                        ('entered_by', '=', self.entered_by.id)]
                return action


            elif self.product_service:
                action = self.env.ref('ppts_analysis_report.sales_report_summary_action_view').read()[0]
                action['domain'] = [('sale_date', '>=', self.date_from),('sale_date', '<=', self.date_to),
                        ('product_service', '=', self.product_service)]
                return action

            else:
                action = self.env.ref('ppts_analysis_report.sales_report_summary_action_view').read()[0]
                action['domain'] = [('sale_date', '>=', self.date_from),('sale_date', '<=', self.date_to)]
                return action
        elif self.view == 'detail':
            if self.sales_rep_id:
                action = self.env.ref('ppts_analysis_report.sales_report_detail_action_view').read()[0]
                action['domain'] = [('detail_sale_date', '>=', self.date_from),
                                    ('detail_sale_date', '<=', self.date_to),
                                    ('sales_rep_id', '=', self.sales_rep_id.id)]
                return action

            if self.company_id:
                action = self.env.ref('ppts_analysis_report.sales_report_detail_action_view').read()[0]
                action['domain'] = [('detail_sale_date', '>=', self.date_from),
                                    ('detail_sale_date', '<=', self.date_to),
                                    ('company_id', '=', self.company_id.id)]
                return action

            if self.entered_by:
                action = self.env.ref('ppts_analysis_report.sales_report_detail_action_view').read()[0]
                action['domain'] = [('detail_sale_date', '>=', self.date_from),
                                    ('detail_sale_date', '<=', self.date_to),
                                    ('entered_by', '=', self.entered_by.id)]
                return action

            elif self.product_service:
                action = self.env.ref('ppts_analysis_report.sales_report_detail_action_view').read()[0]
                action['domain'] = [('detail_sale_date', '>=', self.date_from),
                                    ('detail_sale_date', '<=', self.date_to),
                                    ('product_service', '=', self.product_service)]
                return action

            else:
                action = self.env.ref('ppts_analysis_report.sales_report_detail_action_view').read()[0]
                action['domain'] = [('detail_sale_date', '>=', self.date_from),
                                    ('detail_sale_date', '<=', self.date_to)]
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
