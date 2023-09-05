from odoo import api, fields, models, _
from datetime import datetime
from datetime import date
from odoo.exceptions import UserError


class CustomCalendarApt(models.Model):
    _inherit = 'calendar.event'
    
    appointment_id = fields.Many2one('appointment.appointment', string='appointment', copy=False, tracking=True)
    appointment_type_id = fields.Many2one('calendar.appointment.type', string='appointment Type ', copy=False, tracking=True)
    appointment_line_id = fields.Many2one('appointment.line.id', string='appointment Line', copy=False, tracking=True)

class SaleOrderAppts(models.Model):
    _inherit = 'sale.order'

    appt_sale_id = fields.Many2one('appointment.appointment',string="appointment")
    type_appt_sale_id = fields.Many2one('calendar.appointment.type',string="appointment type")
    appt_line_id = fields.Many2one('appointment.line.id',string="appointment lines id")
    descriptions = fields.Char(string="Descriptions")
    amount_paid = fields.Float(string="Amount Paid",compute="_sale_paid_amount")
    payment_type = fields.Selection([('credit_card','Credit Card'),('debit_card','Debit Card')],string="Payment Method")
    sale_type_for = fields.Selection([('appointment','Appointment'),('event','Event'),('other','Other')], default='other')

    apt_booking_date = fields.Date(string='Appointment Date',tracking=True)
    apt_booked_by = fields.Many2one('res.users',string='Sales Rep', tracking=True)
    web_apt_id = fields.Many2one('appointment.appointment',string="Appointment")
    web_event_id = fields.Many2one('event.event',string="Event")
    partner_id = fields.Many2one(
        'res.partner', string='Customer',
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",compute="compute_get_partner",store=True)
    # invoice_payment_status_set = fields.Selection([('not_paid','=','Not Paid'),('partially_paid','Partially Paid'),('paid','Paid')],compute='_invoice_payment_balance',string='Payment Status')
    customer_id = fields.Many2one('res.partner',string="Customer")
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one(related='pricelist_id.currency_id', depends=["pricelist_id"], store=True)
    invoice_payment_status_set = fields.Float('Invoice Balance', compute='_compute_invoice_payment_balance')
    
    invoice_fully_paid = fields.Boolean('invoice_fully_paid')
    invoice_partially_paid = fields.Boolean('invoice_partially_paid')
    invoice_not_paid = fields.Boolean('invoice_not_paid')

    adv_payment_ids = fields.One2many("adv.payment","sale_order", string="Advance Payments")

    total_advance_amount_paid = fields.Monetary(currency_field='currency_id', string="Total Advance Amount Paid", compute="_compute_total_advance_amount_paid")

    due_advance_amount = fields.Monetary(currency_field='currency_id', string="Due Advance Amount", compute="_compute_total_advance_amount_paid")


    payment_button_show = fields.Boolean(compute="_compute_total_advance_amount_paid")
    partner_inv_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        readonly=True, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)

    partner_ship_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    discount = fields.Float(string="Discount")
    type = fields.Selection([('apt','Appointment'),('event','Event')],string="Type")

    def _sale_paid_amount(self):
        for rec in self:
            rec.amount_paid = 0.0
            account = self.env['account.move'].search([('sale_id','=',rec.id)],limit=1)
            if account and account.payment_state in ['paid','in_payment']:
                rec.amount_paid = rec.amount_total


    @api.depends('customer_id')
    def compute_get_partner(self):
        for rec in self:
            if rec.customer_id:
                rec.partner_id = rec.customer_id.id
            else:
                rec.partner_id = False




    def _compute_total_advance_amount_paid(self):
        advance_amount = 0
        for payment in self.adv_payment_ids:
            advance_amount=advance_amount+payment.total_amount
        self.total_advance_amount_paid = advance_amount

        if self.state in ["draft","sent","sale","done"]:
            if self.total_advance_amount_paid >=self.amount_total:
                self.payment_button_show = False
            else:
                self.payment_button_show = True
        else:
            self.payment_button_show = False

        if self.total_advance_amount_paid < self.amount_total:
            self.due_advance_amount = self.amount_total - self.total_advance_amount_paid
        
        if self.total_advance_amount_paid >= self.amount_total:
            self.due_advance_amount = 0
                

    @api.depends('invoice_payment_status_set')
    def _compute_invoice_payment_balance(self):
        for rec in self:
            rec.invoice_payment_status_set = 0.0
            if rec.invoice_ids:
                for i in rec.invoice_ids:
                    rec.invoice_payment_status_set += i.amount_residual

                if rec.invoice_payment_status_set == rec.amount_total:
                    rec.invoice_fully_paid = False
                    rec.invoice_partially_paid = False 
                    rec.invoice_not_paid = True

                elif rec.invoice_payment_status_set > 0.0 and rec.invoice_payment_status_set < rec.amount_total:
                    rec.invoice_fully_paid = False
                    rec.invoice_partially_paid = True 
                    rec.invoice_not_paid = False

                elif rec.invoice_payment_status_set == 0.0:
                    rec.invoice_fully_paid = True
                    rec.invoice_partially_paid = False 
                    rec.invoice_not_paid = False

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')


    session_type = fields.Selection([
        ('type_single', 'Single Session'),
        ('type_package', 'Package Session')], string='Type Of Session?', default='type_single', required=True,
        tracking=True)

    booking_type = fields.Selection([
        ('facilitator', 'Facilitator'),
        ('appointment', 'Appointment'),
        ('room', 'Room'), ('event', 'Event')
    ], string='Booking Type', copy=False, tracking=True)

    def action_sale_register_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_model': 'adv.payment',
            'view_id': 'ppts_custom_apt_mgmt.adv_payment_wizard_form',
            'target': 'new',
            'context': {
                        'default_partner_id': self.partner_id.id,
                        'default_appointment_id':self.appt_sale_id.id,
                        'default_amount':self.due_advance_amount,
                        'default_sale_order':self.id,
                        'default_company_id':self.company_id.id,
                        }
        }
    # download the invoice report
    def action_invoice_report(self):
        invoice_id = self.env['account.move'].search([('sale_id','=',self.id)],limit=1)
        if invoice_id:
            return self.env.ref("account.account_invoices").report_action(invoice_id)
        else:
            raise UserError(_("No link to an invoice for %s." % (self.name)))

    # open the invoice mail wizard
    def action_open_invoice_wizard(self):
        account_move = self.env['account.move'].search([('sale_id','=',self.id)])
        if account_move:
            '''
            This function opens a window to compose an email, with the edi MOM template message loaded by default
            '''
            self.ensure_one()
            ir_model_data = self.env['ir.model.data']
            template_id = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
            try:
                compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False
            ctx = {
                'default_model': 'account.move',
                'default_res_id': account_move.id,
                'default_use_template': bool(template_id),
                'default_template_id': template_id.id or False,
                'default_composition_mode': 'comment',
                'force_email': True
            }
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id, 'form')],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }

        else:
            raise UserError(_("No link to an invoice for %s." % (self.name)))

    # open the invoice form
    def redirect_to_web_invoice(self):
        for rec in self:
            account_id = self.env['account.move'].search([('sale_id','=',rec.id)],limit=1)
            if account_id:
                return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'name': _('Invoice'),
                'res_model': 'account.move',
                'res_id': account_id.id,
                'target': 'new',
                }
            else:
                raise UserError(_("No link to an invoice for %s." % (self.name)))


class SaleOrderLineAppts(models.Model):
    _inherit = 'sale.order.line'


    # useless
    appt_sale_id = fields.Many2one('appointment.appointment',string="appointment")
    type_appt_sale_id = fields.Many2one('calendar.appointment.type',string="appointment type")
    appt_line_id = fields.Many2one('appointment.line.id',string="appointment lines id")
    package_id = fields.Many2one('appointment.package',string="appointment lines id")

    session_type = fields.Selection(string='Type Of Session?', related='appt_sale_id.session_type')
    booking_type = fields.Selection([
        ('facilitator', 'Facilitator'),
        ('appointment', 'Appointment'),
        ('room', 'Room'), ('event', 'Event')
    ], string='Booking Type', copy=False)
    reference_no = fields.Char(related="order_id.name",string="Payment Ref #")
    date_order = fields.Datetime(string="SALE DATE",related="order_id.date_order")
    company_id = fields.Many2one('res.company',related="order_id.company_id")
    apt_id = fields.Many2one('appointment.appointment',related="order_id.web_apt_id",string="Sale Id")
    event_id = fields.Many2one('event.event',string="Event Ref")
    web_event = fields.Char(string="Event Ref")
    amount_paid = fields.Float(string="Amount Paid",related="order_id.amount_paid")
    payment_type = fields.Selection([('credit_card','Credit Card'),('debit_card','Debit Card')],string="Payment Method",related="order_id.payment_type")
    # useless

    apt_service_category = fields.Many2one('appointment.category', string='Service Category')
    apt_sub_category = fields.Many2one('calendar.appointment.type', string='Sub Category')
    card_type = fields.Selection([('credit_card','Credit Card'),('debit_card','Debit Card')],string="Payment Method")
    type = fields.Selection([('apt','Appointment'),('event','Event')],string="Type",related="order_id.type")

    def redirect_to_appointment_event(self):
        for rec in self:
            if rec.order_id.web_apt_id:
                appointment = self.env['appointment.appointment'].search([('id','=',rec.order_id.web_apt_id.id)],limit=1)
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'name': _('Appointment'),
                    'res_model': 'appointment.appointment',
                     'res_id': appointment.id,
                     'target': 'new',
                }
            if rec.order_id.web_event_id:
                event = self.env['event.event'].search([('id','=',rec.order_id.web_event_id.id)],limit=1)
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'name': _('Event'),
                    'res_model': 'event.event',
                     'res_id': event.id,
                     'target': 'new',
                }

class AccountInvAppts(models.Model):
    _inherit = 'account.move'

    # active = fields.Boolean('Active', default=True)
    appointment_id = fields.Many2one('appointment.appointment',string="appointment")
    type_appointment_id = fields.Many2one('calendar.appointment.type',string="appointment type")
    appt_line_id = fields.Many2one('appointment.line.id',string="appointment lines id")

    session_type = fields.Selection([
        ('type_single', 'Single Session'),
        ('type_package', 'Package Session')], string='Type Of Session?', default='type_single', required=True,
        tracking=True)

    booking_type = fields.Selection([
        ('facilitator', 'Facilitator'),
        ('appointment', 'Appointment'),
        ('room', 'Room'), ('event', 'Event')
    ], string='Booking Type', copy=False, tracking=True)

# class AccountInvAppts(models.Model):
#     _inherit = 'account.move.line'

#     active = fields.Boolean('Active', default=True)

