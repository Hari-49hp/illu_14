from odoo import api, fields, models, _
from datetime import datetime
from datetime import date

class CustomAppointments(models.Model):
    _inherit = 'appointment.appointment'

    invoice_balance = fields.Float('Invoice Balance',help="To view the Appointment Balance", compute='_compute_partner_apt_balance')

    invoice_fully_paid = fields.Boolean('invoice_fully_paid')
    invoice_partially_paid = fields.Boolean('invoice_partially_paid')
    invoice_not_paid = fields.Boolean('invoice_not_paid')

    adv_payment_ids = fields.One2many("adv.payment","sale_order", string="Advance Payments")

    # payment_ids = fields.One2many("account.payment","sale_order", string="Advance Payments")

    total_advance_amount_paid = fields.Monetary(currency_field='currency_id', string="Total Advance Amount Paid") #compute="_compute_total_advance_amount_paid"

    due_advance_amount = fields.Monetary(currency_field='currency_id', string="Due Advance Amount") #compute="_compute_total_advance_amount_paid"


    payment_button_show = fields.Boolean()#compute="_compute_total_advance_amount_paid"
    change_time = fields.Boolean()

    cancel_charge_applied = fields.Boolean(string='Cancellation Charges Applied?')
    cancel_options = fields.Selection([('now', 'Applied'),
                                       ('later', 'Applied Later'),
                                       ('ignore', 'Charges Ignored')], string='Cancellation Policy')
    
    due_cancellation_charge = fields.Float('Cancellation Charges Due')
    topay_cancellation_charge = fields.Float('Cancellation Charges')
    note_cancellation_charge = fields.Char('Cancellation Charges On')

    #no show

    is_no_show = fields.Boolean('Is No show')
    is_no_show_done = fields.Boolean('Is No show Done')
    is_no_show_date = fields.Date('No Show Date')
    no_show_charges = fields.Float('No Show Charges')
    topay_no_show_charges = fields.Float('No Show Charges to Pay')
    pay_no_show = fields.Boolean('Add No show amount to this Billing')
    noshow_options = fields.Selection([('now', 'Apply Now'),('later', 'Apply Later'), ('ignore', 'Ignore Charges')], string='No Show Policy', default='now')

    note_no_show = fields.Char('No Show Charges On')

    partner_due = fields.Float('Customer Balance Due', readonly=True)
    
    customer_balance = fields.Float("Customer Balance",compute="_compute_partner_balance")


    account_balance = fields.Monetary('Customer Balance old', related='partner_id.account_balance')

    no_show_invoice_id = fields.Many2one('account.move', string='NoShow Invoice')
    # note_no_show_charge = fields.Char('Cancellation Charges On')
    # reset_cc_amounts = fields.Boolean('Reset Previous Charges On Confirmation')
    booking_date_time = fields.Datetime(string='Appointment Datetime ')


    def _compute_partner_balance(self):
        self.customer_balance= 0.0
        for each in self:
            if each.partner_id:
                each.customer_balance = each.partner_id.customer_balance


    def _compute_partner_apt_balance(self):
        for each_apt in self:
            if each_apt.pos_order_id:
                each_apt.invoice_balance = (each_apt.pos_order_id.amount_total - each_apt.pos_order_id.amount_paid) * -1
            elif each_apt.state in('void','cancel'):
                each_apt.invoice_balance = 0.0
            elif not each_apt.pos_order_id and each_apt.payment_status_apt in ("paid","payment_received"):
                each_apt.invoice_balance = 0.0    
            else:
                each_apt.invoice_balance = each_apt.amount_due * -1

    #not used now
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
                        'default_appointment_id':self.id,
                        'default_amount':self.amount_due,
                        'default_company_id':self.company_id.id,
                        }
        }

    #Action move to POS from list view
    def action_move_to_pos_bulk(self):

        active_id = self.env['appointment.appointment'].browse(self.env['appointment.appointment']._context.get('active_ids'))
        for pos in active_id:
            if not pos.pos_order_id and not pos.is_package_claim:
                pos.action_move_to_pos()

    #btn click of No show
    def action_no_show(self):
        dates=datetime.today()
        for rec in self:
            if rec.payment_status_apt in ('no_paid') and not rec.parent_id:
                if self.pos_order_id:
                    pos_line_price = self.env['pos.order.line'].search(
                        [('order_id', '=', self.pos_order_id.id),
                         ('product_id', '=',
                          self.appointments_type_id.product_id.id)]).price_subtotal
                else:
                    pos_line_price = self.amount_unit_price_tot

                no_show=pos_line_price
            else:
                no_show=0.0

            rec.write({'color': 6,
                       'is_no_show':True,
                       'is_no_show_date':dates,
                       'no_show_charges':no_show,
                       'state':'no_show',
                       })

            if rec.parent_id:
                self.package_line_id.write({'state_line': 'no_show'})

    #no show process action..
    def action_no_show_process(self):
        cc_partner_ids = self.env['appointment.appointment'].search(
            [('partner_id', '=', self.partner_id.id), ('no_show_charges', '>', 0)])
        
        self.state = 'no_show'
        
        cc_due = 0.0
        # note_cancellation_charge
        note = 'Info : '
        apt_state = 'Info : '

        for due_ns in cc_partner_ids:
            cc_due += due_ns.no_show_charges
            note += ("Booking Date : " + str(due_ns.creation_date) + " Appointment Date : " + str(
                due_ns.booking_date) + " Session : " + due_ns.session_type)

            apt_state = due_ns.payment_status_apt

        if self.payment_status_apt == 'paid':
            noshow_options = 'ignore'
        else:
            noshow_options = 'later'

        return {
            'type': 'ir.actions.act_window',
            'name': 'No Show Processing',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'apt.two.step.cancel',
            'context': {
                'default_appointments_id': self.id,
                'default_is_no_show': True,
                'default_no_show_charges': cc_due,
                'default_noshow_options': noshow_options,
                'default_note': note,
                'default_is_paid': apt_state,
            },
        }

    #to set pay now options for cancel and no show..

    @api.onchange('cancel_options','topay_cancellation_charge')
    def _onchange_reset_cc_amount(self):
        if self.cancel_options == 'now' and self.topay_cancellation_charge>0:
            self.cancel_charge_applied=True
        else:
            self.cancel_charge_applied = False

    def create_new_account_cancel(self):
        account_sale = self.env['account.account'].create({
            'code': 'CAN-9585',
            'name': 'Cancellation Charges',
            'reconcile': True,
            'company_id':self.company_id.id,
            'user_type_id': self.env.ref('account.data_account_type_revenue').id,
        })

    def create_new_product_cancel(self):
        product_id = self.env['product.product'].create({
            'name': 'Cancellation Charges',
            'categ_id': 1,
            'type': 'service',
            'invoice_policy': 'order',
            'supplier_taxes_id': False,
            'sale_ok': True,
            'purchase_ok': False,
            'list_price': 0.0,
            'product_used': 'appointments',
            'company_id': False,
            'available_in_pos': True
        })

    def create_new_account_noshow(self):
        account_sale = self.env['account.account'].create({
            'code': 'NS-9585',
            'name': 'No Show Charges',
            'reconcile': True,
            'company_id': self.company_id.id,
            'user_type_id': self.env.ref('account.data_account_type_revenue').id,
        })

    def create_new_product_noshow(self):
        product_id = self.env['product.product'].create({
            'name': 'No Show Charges',
            'categ_id': 1,
            'type': 'service',
            'invoice_policy': 'order',
            'supplier_taxes_id': False,
            'sale_ok': True,
            'purchase_ok': False,
            'list_price': 0.0,
            'product_used': 'appointments',
            'company_id': False,
            'available_in_pos': True
        })

    def create_new_account_adjust(self):
        account_sale = self.env['account.account'].create({
            'code': 'ADJ-9585',
            'name': 'Adjustment on Existing Balance',
            'reconcile': True,
            'company_id': self.company_id.id,
            'user_type_id': self.env.ref('account.data_account_type_revenue').id,
        })

    def create_new_product_adjust(self):
        product_id = self.env['product.product'].create({
            'name': 'Adjustment on Existing Balance',
            'categ_id': 1,
            'type': 'service',
            'invoice_policy': 'order',
            'supplier_taxes_id': False,
            'sale_ok': True,
            'purchase_ok': False,
            'list_price': 0.0,
            'product_used': 'appointments',
            'company_id': False,
            'available_in_pos': True
        })

class CustomAppointmentsLine(models.Model):
    _inherit  = 'appointment.line.id'

    def action_partial_cancel(self):
        self.appointment_id.write({'state': 'ongoing'})
        self.cancelled_date = datetime.now()
        self.appointment_id.action_cancel()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cancellation Options',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'apt.two.step.cancel',
            'context': {
                'default_appointments_id': self.appointment_id.id,
                'default_is_line_cancel': self.id,
                'default_line_cancel_charges': self.price_subtotal,
            },
        }
