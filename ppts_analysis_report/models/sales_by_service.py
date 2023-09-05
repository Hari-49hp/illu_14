from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
from datetime import datetime as dt


class SalesServiceSummary(models.Model):
    _name = 'sales.service.summary'
    _description="SalesServiceSummary"

    name = fields.Char()
    apt_id = fields.Many2one('appointment.appointment')
    service_catg_id = fields.Many2many('calendar.appointment.type') #, compute='get_service_catg_id'
    sub_category_id = fields.Many2one('calendar.appointment.type', string="Category")
    pricing_option = fields.Many2one('appointment.category', string="Service")
    total_amount = fields.Float(string="Total Amount") #, compute='compute_total_amount'
    per_revenue_category = fields.Char(string="% of Revenue Category" ,compute='compute_revenue')
    cash_equal = fields.Float(string="Cash Equivalent")
    non_cash_equal = fields.Float(string="Non-Cash Equivalent")
    quantity = fields.Float(string="Quantity")
    pos_id = fields.Many2one('pos.order')
    date = fields.Date("Date")
    entered_by = fields.Many2one('res.users', string="Entered by",default=lambda self: self.env.uid)
    location_id = fields.Many2one('res.company', string="Location",default=lambda self: self.env.company)
    service_id = fields.Many2one('appointment.category', string="service")

    
    def compute_revenue(self):
        for rec in self:
            totals = 0.00
            revenue = 0.00
            apt = self.env['appointment.appointment'].search(
                        [('state', 'in', ['new', 'confirm', 'arrive', 'no_show', 'ongoing', 'done', 'cancel']),
                         ('service_categ_id', '=', rec.pricing_option.id)])
            pos = self.env['pos.order'].search([('appt_sale_id', 'in', apt.ids)])
            for total in pos.lines:
                totals += total.price_subtotal_incl
            amount = rec.total_amount * 100
            if amount and totals:
                revenue = amount / totals
            rec.per_revenue_category = "{0}%".format(round(revenue, 2))

    @api.onchange('sub_category_id')
    def onchange_category(self):
        for rec in self:
            category = self.env['calendar.appointment.type'].search([('id', '=', rec.sub_category_id.id)])
            rec.pricing_option = category.service_categ_id.id



class SalesServiceDetail(models.Model):
    _name = 'sales.service.detail'
    _description="SalesServiceDetail"

    name = fields.Char()
    apt_id = fields.Many2one('appointment.appointment')
    service_id = fields.Many2one('appointment.category')
    location_id = fields.Many2one('res.company', string='Location',default=lambda self: self.env.company)
    sub_category_id = fields.Many2one('calendar.appointment.type', string="Category")
    pos_id = fields.Many2one('pos.order', compute='get_pos_id')
    client = fields.Many2one('res.partner', string="Client")
    mobile = fields.Char(string='Mobile') #,related='partner_id.mobile'
    detail_sale_date = fields.Date(string='Sale Date', copy=False)
    activation_date = fields.Date(string='Activation Date', copy=False)
    activation_off = fields.Char(string="Activation Off-Set Days") # , compute='compute_offset'
    exp_date = fields.Date(string='Expiration Date', copy=False)
    total_amount = fields.Float(string="Total Amount")
    cash_equal = fields.Float(string="Cash Equivalent")
    non_cash_equal = fields.Float(string="Non-Cash Equivalent")
    quantity = fields.Float(string="Quantity")
    entered_by = fields.Many2one('res.users', string="Entered by",default=lambda self: self.env.uid)

    def get_pos_id(self):
        for rec in self:
            qty = 0.00
            apt = self.env['appointment.appointment'].search(
                [('state', 'in', ['new', 'confirm', 'arrive', 'no_show', 'ongoing', 'done', 'cancel'])])
            pos = self.env['pos.order'].search([('appt_sale_id', '=', rec.apt_id.id)])
            rec.pos_id = pos.ids