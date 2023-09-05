from odoo import fields, models, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta

class ProductWizard(models.TransientModel):
    _name = 'product.wizard'
    _description = "ProductWizard"

    date_from = fields.Date("Date from", default=datetime.today())
    date_to = fields.Date("Date to", default=datetime.today())
    company_id = fields.Many2one('res.company', string="Location")
    product_id = fields.Many2one('product.product', string="Product")
    category_id = fields.Many2one('pos.category', string='Category')
    payment_method = fields.Selection([('cash', 'Cash'),('net', 'Net Banking'),
        ('bank', 'Bank')], string="Payment Method")
    date_range = fields.Selection([
        ('year', 'Year'),
        ('quarter', 'Quarter'),('month', 'Month'),
        ('day', 'Day')], string='Quick Dates')
    view = fields.Selection([
        ('summary', 'Summary'), ('detail', 'Detail')], string='View', default='summary')


    def action_apply(self):
        if self.view == 'summary':
            ref = self.env['sales.product.summary'].search([('payment_method', '=', self.payment_method)])
            if ref:
                if self.product_id:
                    action = self.env.ref('ppts_analysis_report.sales_by_product_sumy_action_view').read()[0]
                    action['domain'] = [('date', '>=', self.date_from),('date', '<=', self.date_to),
                            ('product_id', '=', self.product_id.id)]
                    return action

                elif self.company_id:
                    action = self.env.ref('ppts_analysis_report.sales_by_product_sumy_action_view').read()[0]
                    action['domain'] = [('date', '>=', self.date_from),('date', '<=', self.date_to),
                            ('location_id', '=', self.company_id.id)]
                    return action

                elif self.payment_method:
                    action = self.env.ref('ppts_analysis_report.sales_by_product_sumy_action_view').read()[0]
                    action['domain'] = [('date', '>=', self.date_from),('date', '<=', self.date_to),
                            ('payment_method', '=', self.payment_method)]
                    return action

            else:
                action = self.env.ref('ppts_analysis_report.sales_by_product_sumy_action_view').read()[0]
                action['domain'] = [('date', '>=', self.date_from),('date', '<=', self.date_to)]
                return action
        elif self.view == 'detail':
            if self.product_id:
                action = self.env.ref('ppts_analysis_report.sales_by_product_detail_action_view').read()[0]
                action['domain'] = [('sale_date', '>=', self.date_from), ('sale_date', '<=', self.date_to),
                                    ('product_id', '=', self.product_id.id)]
                return action

            elif self.company_id:
                action = self.env.ref('ppts_analysis_report.sales_by_product_detail_action_view').read()[0]
                action['domain'] = [('sale_date', '>=', self.date_from), ('sale_date', '<=', self.date_to),
                                    ('location_id', '=', self.company_id.id)]
                return action

            elif self.payment_method:
                action = self.env.ref('ppts_analysis_report.sales_by_product_detail_action_view').read()[0]
                action['domain'] = [('sale_date', '>=', self.date_from), ('sale_date', '<=', self.date_to),
                                    ('payment_method', '=', self.payment_method)]
                return action

            else:
                action = self.env.ref('ppts_analysis_report.sales_by_product_detail_action_view').read()[0]
                action['domain'] = [('sale_date', '>=', self.date_from), ('sale_date', '<=', self.date_to)]
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

