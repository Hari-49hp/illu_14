from datetime import date, datetime, timedelta, time
from email.policy import default
from itertools import product

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
import datetime
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime
import pytz
from odoo.tools.misc import formatLang


TIME = [('08:15','08:15'),('08:30','08:30'),('08:45','08:45'),('09:00','09:00'),('09:15','09:15'),('09:30','09:30'),('09:45','09:45'),('10:00','10:00'),('10:15','10:15'),('10:30','10:30'),('10:45','10:45'),('11:00','11:00'),('11:15','11:15'),('11:30','11:30'),('11:45','11:45'),('12:00','12:00'),('12:15','12:15'),('12:30','12:30'),('12:45','12:45'),('13:00','13:00'),('13:15','13:15'),('13:30','13:30'),('13:45','13:45'),('14:00','14:00'),('14:15','14:15'),('14:30','14:30'),('14:45','14:45'),('15:00','15:00'),('15:15','15:15'),('15:30','15:30'),('15:45','15:45'),('16:00','16:00'),('16:15','16:15'),('16:30','16:30'),('16:45','16:45'),('17:00','17:00'),('17:15','17:15'),('17:30','17:30'),('17:45','17:45'),('18:00','18:00'),('18:15','18:15'),('18:30','18:30'),('18:45','18:45'),('19:00','19:00'),('19:15','19:15'),('19:30','19:30'),('19:45','19:45'),('20:00','20:00'),('20:15','20:15'),('20:30','20:30'),('20:45','20:45'),('21:00','21:00'),('21:15','21:15'),('21:30','21:30'),('21:45','21:45'),('22:00','22:00'),('22:15','22:15'),('22:30','22:30'),('22:45','22:45'),('23:00','23:00'),('23:15','23:15'),('23:30','23:30'),('23:45','23:45'),('23:55','23:55')]

class AdvancePayment(models.Model):
    _name = "adv.payment"
    _description = 'Advance Payment'

    company_id = fields.Many2one('res.company', string='Branch')
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    partner_id = fields.Many2one('res.partner', string="Customer")
    journal_id = fields.Many2one('account.journal', store=True, readonly=False, string="Payment Type")
    destination_account_id = fields.Many2one('account.payment', string="Recipient Bank Account")
    amount = fields.Monetary(currency_field='currency_id', string="Amount", required=True)
    payment_date = fields.Date(string="Payment Date", required=True, default=datetime.today())
    appointment_id = fields.Many2one('appointment.appointment', string="Appointment")

    sale_order = fields.Many2one(comodel_name="sale.order")
    outstanding_balance = fields.Monetary(currency_field='currency_id',string="Outstanding Balance")
    take_outstanding_balance = fields.Boolean(string="Take from Outstanding Balance")
    amount_taken_from_outstanding = fields.Monetary(currency_field='currency_id',string="Taken Amount from Outstanding")
    total_amount = fields.Monetary(currency_field='currency_id',string="Total Amount")
    amount_due = fields.Monetary(currency_field='currency_id',string="Due Amount")
    ref = fields.Char('Notes')
    is_adjust_balance = fields.Boolean(string="Is Adjust Balance")
    payment_options = fields.Selection([('full', 'Full'),('partial', 'Partial')], string='Adjustment Policy', default='full')
    amount_topay = fields.Monetary(currency_field='currency_id',string="Amount to Pay for Appointment",compute='_compute_payment_topay',store=True)

    @api.onchange("take_outstanding_balance")
    def _onchange_take_outstanding_balance(self):
        if self.take_outstanding_balance:
            if self.outstanding_balance < self.appointment_id.amount_due:
                self.amount_taken_from_outstanding = self.outstanding_balance
                self.amount = self.appointment_id.amount_due - self.amount_taken_from_outstanding

            if self.outstanding_balance >= self.appointment_id.amount_due:
                self.amount_taken_from_outstanding = self.appointment_id.amount_due
                self.amount = 0
        else:
            self.amount_taken_from_outstanding = 0
            self.amount = self.appointment_id.amount_due

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        self.outstanding_balance=self.partner_id.total_due*(-1)

    @api.onchange("payment_options")
    def _onchange_payment_options(self):
        if self.payment_options=='full':
            self.amount_taken_from_outstanding=self.amount
        else:
            self.amount_taken_from_outstanding = 0.0

    @api.depends('payment_options',"amount_taken_from_outstanding")
    def _compute_payment_topay(self):
        for rec in self:
            if rec.amount:
                rec.amount_topay = rec.amount-rec.amount_taken_from_outstanding

    def create_adv_payment(self):
        self.total_amount = self.amount + self.amount_taken_from_outstanding
        self.amount_due = self.sale_order.due_advance_amount
        cmp_id = self.env['account.journal'].search(
            [('type', 'in', ('cash','bank')), ('company_id', '=', self.appointment_id.company_id.id)], limit=1)
        if self.amount:
            payment= self.env['account.payment'].sudo().create({
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': self.partner_id.id,
                'amount': self.amount,
                'date': self.payment_date,
                'journal_id': self.journal_id.id,
                'appointments_id': self.appointment_id.id,
                'company_id': self.appointment_id.company_id.id
                })

    def confirm_adjust_payment(self):
        account_types = []
        receivable_type = self.env.ref('account.data_account_type_receivable').id
        payable_type = self.env.ref('account.data_account_type_payable').id
        account_types.extend([receivable_type, payable_type])
        domain = [('partner_id', '=', self.partner_id.id), ('amount_residual', '!=', 0),
                  ('account_id.user_type_id', 'in', account_types),('move_id.state', '=', 'posted'),
                  ('move_id.move_type', '=', 'out_refund')]

        customer_balance_line = self.env['account.move.line'].search(domain)

        adjusted_amount=self.amount_taken_from_outstanding

        for inv in customer_balance_line:
            residual_amount=inv.amount_residual
            if not adjusted_amount==0:
                if residual_amount>=adjusted_amount:
                    adj_amt = residual_amount-adjusted_amount
                    inv.write({'amount_residual': -adj_amt, 'amount_residual_currency': -adj_amt,
                               'appointment_ids': [(4, self.appointment_id.id)]})

                    inv.move_id.write({'appointment_ids': [(4, self.appointment_id.id)]})

                    adjusted_amount=adjusted_amount-adj_amt
                else:
                    adj_amt = adjusted_amount
                    inv.write({'amount_residual': -adj_amt, 'amount_residual_currency': -adj_amt,
                               'appointment_ids': [(4, self.appointment_id.id)]})
                    inv.move_id.write({'appointment_ids': [(4, self.appointment_id.id)]})
                    adjusted_amount = adjusted_amount-adj_amt
            else:
                continue
        self.appointment_id.due_adjustment=self.amount_taken_from_outstanding

class TwoStepVoid(models.TransientModel):
    _name = "apt.two.step.void"
    _description = 'Two Step Void'

    appointments_id = fields.Many2one('appointment.appointment', string='Appointment')
    note = fields.Text("Remarks", required=True)

    def action_void(self):
        self.appointments_id.void_notes = self.note
        self.appointments_id.action_void()

class TwoStepCancel(models.TransientModel):
    _name = "apt.two.step.cancel"
    _description = 'Two Step Cancellation'

    appointments_id = fields.Many2one('appointment.appointment', string='Appointment')
    session_type = fields.Selection(string='Type Of Session?', related='appointments_id.session_type', required=True)
    cancel_reason_template = fields.Many2one('appointment.cancel.reason', string='Reason')
    create_invoice = fields.Boolean(string='Do you Want to Apply Cancellation Charges?', default=False)
    cc_cancellation_charge = fields.Float('Cancellation Charges',related='appointments_id.cc_cancellation_charge')

    note = fields.Text("Note")

    cancel_options = fields.Selection([('now', 'Apply Now'), ('later', 'Apply Later'), ('ignore', 'Ignore Charges')], string='Cancellation Policy')

    cc_confirmation = fields.Boolean('cc_confirmation')

    is_no_show = fields.Boolean('Is No show')
    is_paid = fields.Char('Is Paid')
    no_show_charges = fields.Float('No Show Charges', readonly=True, store=True)
    noshow_options = fields.Selection([('later', 'Apply Later'),
                                       ('ignore', 'Ignore Charges')], string='No Show Policy', default='later')

    #Apt Line cancel added
    is_line_cancel = fields.Many2one('appointment.line.id',string='Is Line Cancel')
    line_cancel_charges = fields.Float('Line Cancel Charges', readonly=True, store=True)
    cancellation_type = fields.Selection([('early', 'Early Cancel'), ('late', 'Late Cancel')], string='Method')

    #to calculate cancellation due
    @api.onchange('cancel_options')
    def _onchange_cancel_options(self):
        if self.cancel_options=='now':
            self.create_invoice = True
        elif self.cancel_options=='later' and not self.appointments_id.is_package_claim:
            self.create_invoice = True
        else:
            self.create_invoice = False

    #to calculate cancellation due
    @api.onchange('cancellation_type')
    def _onchange_cancel_charges_update(self):
        if self.cancellation_type=='early':
            self.cc_cancellation_charge = 0.0
        else:
            self.cc_cancellation_charge = self.appointments_id.cc_cancellation_charge

    #Cancel wizard and invoice/ cr note generation upon conditions
    def cancel_apt(self):
        self.appointments_id.cancel_reason_id = self.cancel_reason_template.id
        self.appointments_id.cancel_note = self.note
        self.appointments_id.cancel_options = self.cancel_options
        self.appointments_id.cancellation_type = self.cancellation_type

        if self.cancel_options=='now':
            self.appointments_id.due_cancellation_charge = 0.0
        elif self.cancel_options=='later':
            self.appointments_id.due_cancellation_charge = self.cc_cancellation_charge
        else:
            self.appointments_id.due_cancellation_charge = 0.0

        self.appointments_id.cancellation_datetime = datetime.now()

        if self.appointments_id.session_type == 'type_package':

            if not self.is_line_cancel:
                for i in self.appointments_id.appointment_line_id:
                    if i.state_line not in ('confirm','void','no_show'):
                        i.write({
                                'state_line': 'cancel', 
                                'cancelled_date': datetime.now(),
                                'cancellation_type': self.cancellation_type,
                                })

                        apt_id = self.env['appointment.appointment'].search([
                            ('package_line_id', '=', i.id),('state', '=', 'new')], limit=1)
                        apt_id.write({'state': 'cancel', 'color': 1})
                        self.appointments_id.write({'state': 'cancel', 'color': 1})

                if self.create_invoice == True:
                    self.appointments_id.write({'state': 'cancel', 'color': 1})
                    if self.appointments_id.payment_status_apt in ('payment_received', 'paid'):
                        self.create_new_crnote_single()
                    else:
                        self.create_new_invoice_single()

                    self.appointments_id.write({'state': 'cancel', 'color': 1})
            else:
                self.is_line_cancel.write({'state_line': 'cancel','cancellation_type': self.cancellation_type,})
                if self.create_invoice == True:
                    if self.appointments_id.payment_status_apt in ('payment_received', 'paid'):

                        self.create_new_crnote_single()
                    else:
                        self.create_new_invoice_single()
                
        #single
        else:
            if self.appointments_id.package_line_id:
                self.appointments_id.package_line_id.write({'state_line': 'draft'})

            if self.create_invoice and not self.appointments_id.package_line_id:
                self.appointments_id.write({'state': 'cancel', 'color': 1})
                if self.appointments_id.payment_status_apt in ('payment_received','paid'):
                    self.create_new_crnote_single()
                else: #not paid
                    if self.cancellation_type == 'late' and self.cancel_options == 'now':
                        self.create_new_invoice_single()

            elif self.create_invoice and self.appointments_id.package_line_id:
                self.create_new_invoice_single()
                self.appointments_id.write({'state': 'cancel', 'color': 1})

            else:
                self.appointments_id.write({'state': 'cancel', 'color': 1})
                
                if self.appointments_id.payment_status_apt in ('payment_received','paid'):
                    if self.cancel_options == 'ignore':
                        self.create_new_crnote_single(ignore=True)

        notes = "\nNotes: "+ str(self.note) if self.note else ""
        cancel_options = dict(self._fields['cancel_options'].selection).get(self.cancel_options) if self.cancel_options else ' '
        self.appointments_id.cancel_notes = \
            "Type: "+ dict(self._fields['cancellation_type'].selection).get(self.cancellation_type) +','+\
                "\nCancelled Charges: "+ str(self.cc_cancellation_charge) +"AED ,"+ \
                    "\nReason: "+ self.cancel_reason_template.name +","+ \
                        "\nCancellation Policy: " + cancel_options + ',' +\
                        notes
                        
        self.appointments_id.action_cancel()
        return True

    def create_new_invoice_single(self):
        pack_amt=self.cc_cancellation_charge
        pos_session_id = self.env['pos.session'].search([('state', '=', 'opened')], limit=1)
        if not pos_session_id:
            raise UserError(_("Please create a POS session to create POS order"))

        seq = self.env['ir.sequence'].search([('name','=','POS APT'),('code','=','POS APT')])
        if seq:
            pos_seq = seq.next_by_id()
        else:
            seq =  self.env['ir.sequence'].create({'name': 'POS APT','code':'POS APT','active':True,'implementation':'no_gap','prefix':'POS/APT','padding':5,'number_increment':1,'number_next_actual':1})
            pos_seq = seq.next_by_id()

        or_id = self.env['pos.order'].sudo().create({
            'partner_id': self.appointments_id.partner_id.id,
            'pricelist_id': 1,
            'appt_sale_id': self.appointments_id.id,
            'session_id': pos_session_id.id,
            'amount_tax': 0.0,
            'amount_paid': 0.0,
            'amount_return': 0.0,
            'amount_total': 0.0,
            'session_type': self.appointments_id.session_type,
            'state': 'draft',
            'booking_type': 'appointment',
            'sale_type_for': 'appointment',
            'apt_booking_date': self.appointments_id.booking_date,
            'apt_booked_by': self.appointments_id.booked_by.id,
            'company_id': self.appointments_id.company_id.id,
            'name': self.appointments_id.sequence,
            'pos_reference': pos_seq,
        })

        self.env['pos.order.line'].sudo().create({
            'apt_service_category': self.appointments_id.service_categ_id.id,
            'full_product_name': 'Cancellation Charges',
            'product_id': self.appointments_id.appointments_type_id.product_id.id,
            'qty': 1,
            'price_subtotal': pack_amt,
            'price_subtotal_incl': pack_amt,
            'order_id': or_id.id,
            'tax_ids_after_fiscal_position': self.appointments_id.single_tax_ids,
            'price_unit': pack_amt,
            'name': self.appointments_id.name,
        })

        return True

        # self.refund_enable = True

    def create_new_crnote_single(self, ignore=False):
        apt_total_value = 0.0
        apt_tax_amt = 0.0
        apt_withtax_amt =0.0
        apt_total =0.0
        count = 0
        if ignore == False:
            if self.appointments_id.session_type == 'type_package':
                if self.is_line_cancel:
                    pack_amt = self.cc_cancellation_charge
                    name = 'Cancellation Charges-Line of Package Session'
                    inv_amt = self.line_cancel_charges
                else:
                    pack_amt=self.cc_cancellation_charge
                    pos_order_price = self.appointments_id.pos_order_id.amount_paid

                    name = 'Cancellation Charges-Package Session'
                    rec = self.env['appointment.line.id'].search(
                        [('state_line', '=', 'confirm'), ('appointment_id', '=', self.appointments_id.id)])
                    for i in self.appointments_id.appointment_line_id:
                        if i.state_line == 'confirm':
                            count += 1
                    for apt_line in rec:
                        if count <=3 :
                            apt_total_value += apt_line.price_after_dis + apt_line.amount_discount
                            apt_tax_amt = apt_total_value *0.05
                            apt_withtax_amt =apt_total_value + apt_tax_amt
                        if count > 3 and count <= 5:
                            apt_total += apt_line.price_after_dis + apt_line.amount_discount
                            apt_total_value = (apt_total-(apt_total *0.05))
                            apt_tax_amt = apt_total_value *0.05
                            apt_withtax_amt =apt_total_value + apt_tax_amt
                        if count > 5 and count <= 10:
                            apt_total += apt_line.price_after_dis + apt_line.amount_discount
                            apt_total_value = (apt_total-(apt_total *0.10))
                            apt_tax_amt = apt_total_value *0.05
                            apt_withtax_amt =apt_total_value + apt_tax_amt
                        if count > 10 and count <= 15:
                            apt_total += apt_line.price_after_dis + apt_line.amount_discount
                            apt_total_value = (apt_total-(apt_total *0.15))
                            apt_tax_amt = apt_total_value *0.05
                            apt_withtax_amt =apt_total_value + apt_tax_amt
                            
                    # rec = self.env['appointment.line.id'].search(
                    #     [('state_line', '=', 'cancel'), ('appointment_id', '=', self.appointments_id.id)])
                    out_sum = pos_order_price - apt_withtax_amt
                    inv_amt=out_sum

            else:
                pack_amt = self.cc_cancellation_charge
                pos_line_price = self.appointments_id.pos_order_id.amount_paid
                inv_amt = pos_line_price - pack_amt
                name = 'Cancellation Charges-Single Session'
            
            self.appointments_id.partner_id.CreateCreditPartner(self.appointments_id.partner_id.id, inv_amt)

        else:
            if self.appointments_id.session_type != 'type_package' and not self.appointments_id.package_line_id:
                pos_line_price = self.env['pos.order.line'].search([('order_id','=',self.appointments_id.pos_order_id.id),\
                                        ('product_id','=',self.appointments_id.appointments_type_id.product_id.id)]).price_subtotal_incl

                self.appointments_id.partner_id.CreateCreditPartner(self.appointments_id.partner_id.id, pos_line_price)

        return True

    #no show calculations
    def process_no_show(self):

        if self.appointments_id.pos_order_id:
            pos_line_price = self.env['pos.order.line'].search([('order_id', '=', self.appointments_id.pos_order_id.id),\
                                ('product_id', '=', self.appointments_id.appointments_type_id.product_id.id)],limit=1).price_subtotal
        else:
            pos_line_price =self.appointments_id.amount_unit_price_tot

        self.appointments_id.is_no_show_done=True
        if self.noshow_options == 'later' and not self.appointments_id.is_package_claim:
            self.appointments_id.no_show_charges = pos_line_price
        else:
            self.appointments_id.no_show_charges = 0.0

    #Invoice, CRNote creation for no show
    def create_new_invoice_noshow(self):
        pack_amt = self.appointments_id.amount_total

        pos_session_id = self.env['pos.session'].search([('state', '=', 'opened')], limit=1)
        if not pos_session_id:
            raise UserError(_("Please create a POS session to create POS order"))

        seq = self.env['ir.sequence'].search([('name','=','POS APT'),('code','=','POS APT')])
        if seq:
            pos_seq = seq.next_by_id()
        else:
            seq =  self.env['ir.sequence'].create({'name': 'POS APT','code':'POS APT','active':True,'implementation':'no_gap','prefix':'POS/APT','padding':5,'number_increment':1,'number_next_actual':1})
            pos_seq = seq.next_by_id()

        or_id = self.env['pos.order'].sudo().create({
            'partner_id': self.appointments_id.partner_id.id,
            'pricelist_id': 1,
            'appt_sale_id': self.appointments_id.id,
            'session_id': pos_session_id.id,
            'amount_tax': 0.0,
            'amount_paid': 0.0,
            'amount_return': 0.0,
            'amount_total': 0.0,
            'session_type': self.appointments_id.session_type,
            'state': 'draft',
            'booking_type': 'appointment',
            'sale_type_for': 'appointment',
            'apt_booking_date': self.appointments_id.booking_date,
            'apt_booked_by': self.appointments_id.booked_by.id,
            'company_id': self.appointments_id.company_id.id,
            'name': self.appointments_id.sequence,
            'pos_reference': pos_seq,
        })

        self.env['pos.order.line'].sudo().create({
            'apt_service_category': self.appointments_id.service_categ_id.id,
            'full_product_name': 'Cancellation Charges',
            'product_id': self.appointments_id.appointments_type_id.product_id.id,
            'qty': 1,
            'price_subtotal': pack_amt,
            'price_subtotal_incl': pack_amt,
            'order_id': or_id.id,
            'tax_ids_after_fiscal_position': self.appointments_id.single_tax_ids,
            'price_unit': pack_amt,
            'name': self.appointments_id.name,
        })
        
        return True

    def create_new_crnote_noshow(self):
        pack_amt = self.appointments_id.pos_order_id.amount_paid
        self.appointments_id.partner_id.CreateCreditPartner(self.appointments_id.partner_id.id, pack_amt)
        return True

    #cancellation functions
    def cancel_apt_older(self):
        self.appointments_id.cancel_reason_id = self.cancel_reason_template.id
        self.appointments_id.cancel_note = self.note
        if self.appointments_id.session_type == 'type_package':
            for i in self.appointments_id.appointment_line_id:
                if i.state_line not in ('confirm','void'):
                    i.write({'state_line': 'cancel', 'cancelled_date': datetime.now()})

                    apt_id = self.env['appointment.appointment'].search([
                        ('package_line_id', '=', i.id),('state', '=', 'new')], limit=1)
                    apt_id.write({'state': 'cancel', 'color': 1})

            if self.create_invoice == True:
                self.appointments_id.action_cancel()
            else:
                self.appointments_id.write({'state': 'cancel', 'color': 1})
                room_av_idst = self.env['event.meeting.room'].sudo().search([("appointment_id", "=", self.appointments_id.id)])

                for rec in room_av_idst:
                    rec.sudo().unlink()

        else:
            if self.create_invoice:
                self.appointments_id.action_cancel()
            else:
                self.appointments_id.write({'state': 'cancel', 'color': 1})

                room_av_idst = self.env['event.meeting.room'].sudo().search([("appointment_id", "=", self.appointments_id.id)])

                for rec in room_av_idst:
                    rec.sudo().unlink()

    def cancel_and_create(self):
        self.cancel_apt()
        apt_line = []
        # apt_line.append((0, 0, {
        #     'appointment_id': self.appointments_id.id,
        #     'expiry_date': self.appointments_id.expiry_date,
        #     'service_categ_id': self.appointments_id.service_categ_id.id,
        #     'appointments_type_id': self.appointments_id.appointments_type_id.id,
        #     'therapist_id': self.appointments_id.therapist_id.id,
        #     'appointment_type': self.appointments_id.appointment_type,
        # }))
        self.env['appointment.appointment'].create({
            'partner_id': self.appointments_id.partner_id.id,
            'reffer_type_id': self.appointments_id.reffer_type_id.id,
            'session_type': 'type_single',
            'therapist_id': self.appointments_id.therapist_id.id,
            'du_service_categ_id': self.appointments_id.du_service_categ_id.id,
            'service_categ_id': self.appointments_id.service_categ_id.id,
            'appointments_type_id': self.appointments_id.appointments_type_id.id,
            'appointment_type': self.appointments_id.appointment_type,
            # 'appointment_line_id': apt_line,
        })
        


class AptCoupon(models.TransientModel):
    _name = "apt.coupon"
    _description = 'Coupon'

    code = fields.Char("Code",required=True)
    sale_id = fields.Many2one("sale.order",string="Sale")
    def apply(self):
        order = self.sale_id
        promo = self.code
        self.env['sale.coupon.apply.code'].sudo().apply_coupon(order, promo)

class AptPromo(models.TransientModel):
    _name = "apt.promo"
    _description = 'Promo'

    code = fields.Char("Code",required=True)
    sale_id = fields.Many2one("sale.order",string="Sale")

    def apply(self):
        self.sale_id.recompute_coupon_lines()

class SingleSessionWizard(models.Model):
    _name = "single.session.wizard"
    _description = 'Single Session Wizard'

    appointments_id = fields.Many2one('appointment.appointment', string='Appointment')
    service_categ_id = fields.Many2one('appointment.category', string='Service Category' )

    appointments_type_id = fields.Many2one('calendar.appointment.type', string='Appointment Type' )
    # appointments_domain_id = fields.Many2one('calendar.appointment.type', string='Appointment Type' )

    therapist_id = fields.Many2one('hr.employee', string='Therapist' )
    therapist_assistant_id = fields.Many2one('hr.employee', string='Instructor' )
    apt_room_id = fields.Many2one('roomtype.master', string='Room' )
    start_time_str = fields.Selection(TIME,string='Start Time' )
    start_time = fields.Float(string='Start Time' )

    end_time_str = fields.Selection(TIME, string='End Time strrr' )
    end_time = fields.Float(string='End Time',compute='_compute_endtime',store=True )

    time_id = fields.Many2one('time.time',string="Duration")
    duration = fields.Float(string='Duration', copy=False)
    booking_date = fields.Date(string='Appointment Date')
    company_id = fields.Many2one('res.company',related='appointments_id.company_id')
    customer_id = fields.Many2one('res.partner',string='Customer')
    
    pos_order_id = fields.Many2one('pos.order',string='Order')
    pos_order_line_id = fields.Many2one('pos.order.line',string='Order Line')

    product_ids = fields.Many2many('product.product',string='Product')
    apt_atv = fields.Boolean('Apt')

    @api.onchange('pos_order_line_id')
    def _onchange_pos_order_line_id(self):
        apt_id = self.env['calendar.appointment.type'].search([('product_id','=',self.pos_order_line_id.product_id.id)])
        self.appointments_type_id = apt_id.id

    @api.onchange('pos_order_id')
    def _onchange_pos_order_id(self):
        self.product_ids = False
        if self.pos_order_id: self.apt_atv = True
        else: self.apt_atv = False
        for rec in self.pos_order_id.lines:
            self.product_ids = [(4, rec.product_id.id)]

    @api.onchange('therapist_id','appointments_type_id','service_categ_id')
    def _onchange_therapist_id_val(self):
        if self.therapist_id and self.appointments_type_id and self.service_categ_id:
            ap_type_id = self.env['staff.list.line'].search([('appointment_id','=',self.appointments_type_id.id),('employee_id','=',self.therapist_id.id)],limit=1)
            self.write({'time_id':ap_type_id.time_id.id})

    @api.onchange('booking_date')
    def _onchange_booking_date(self): 
        if self.booking_date:
            cur_dt = datetime.strftime(self.booking_date, "%d/%m/%Y %H:%M:%S")
            cur_dt_now = datetime.strftime(datetime.now(), "%d/%m/%Y %H:%M:%S")
            pcur_dt = datetime.strptime(cur_dt, "%d/%m/%Y %H:%M:%S")
            pcur_dt_now = datetime.strptime(cur_dt_now, "%d/%m/%Y %H:%M:%S")

            if pcur_dt < pcur_dt_now:
                raise UserError('Appointments should be booked for Future Date..!')

    @api.onchange('appointments_id')
    def _onchange_appointments_id(self):
        if self.appointments_id:
            self.service_categ_id=self.appointments_id.service_categ_id.id
            self.appointments_type_id=self.appointments_id.appointments_type_id.id
            self.therapist_id=self.appointments_id.therapist_id.id
            self.therapist_assistant_id=self.appointments_id.therapist_assistant_id.id
            self.apt_room_id=self.appointments_id.apt_room_id.id
            self.start_time_str=self.appointments_id.start_time_str
            self.start_time=self.appointments_id.start_time
            self.end_time_str=self.appointments_id.end_time_str
            self.end_time=self.appointments_id.end_time
            self.duration=self.appointments_id.duration
            self.booking_date=self.appointments_id.booking_date

    def _onchange_therapist_id(self):
        if self.therapist_id and self.end_time:
            av_idst = self.env['availability.availability'].search(
                [("available_date", "=", self.booking_date)])
            if av_idst:
                print("proceed")
            else:
                raise UserError(_("Time solt is not available."))

    @api.onchange('time_id')
    def _onchange_time_id(self):
        if self.time_id:
            time_val = str(timedelta(minutes=int(self.time_id.duration)))[:-3]
            time_val = time_val.replace(':','.')
            self.write({'duration':float(time_val)})
        else:
            self.write({'duration':0})

    @api.onchange('appointments_type_id')
    def _onchange_duration(self):
        if self.appointments_type_id:
            self.write({
                'duration':self.appointments_type_id.appointment_duration,
                'time_id':self.appointments_type_id.time_id.id
                })

            product_id = self.env['pos.order.line'].search([('order_id','=',self.pos_order_id.id),('product_id','=',self.appointments_type_id.product_id.id)])
            self.pos_order_line_id = product_id.id

            res = {'domain': {'therapist_id': "[('id', 'not in', False)]"}}
            line_ids = []
            for line in self.appointments_type_id.apt_staff_list_ids:
                line_ids.append(line.employee_id.id)
            res['domain']['therapist_id'] = "[('id', 'in', %s)]" % line_ids
            return res



    def add_appointment_wiz(self):
        for rec in self:
            for m_date in rec.appointments_id.appointment_line_id:
                m_date.unlink()
            vals = {
            'service_categ_id':rec.service_categ_id.id,
            'appointments_type_id':rec.appointments_type_id.id,
            'therapist_id':rec.therapist_id.id,
            'therapist_assistant_id':rec.therapist_assistant_id.id,
            'apt_room_id':rec.apt_room_id.id,
            'start_time_str':rec.start_time_str,
            'start_time':rec.start_time,
            'end_time_str':rec.end_time_str,
            'end_time':rec.end_time,
            'booking_start_date':rec.booking_date,
            'appointment_id':self.appointments_id.id,
            'duration':rec.duration}

            head_vals = {
                'service_categ_id': rec.service_categ_id.id,
                'appointments_type_id': rec.appointments_type_id.id,
                'therapist_id': rec.therapist_id.id,
                'therapist_assistant_id': rec.therapist_assistant_id.id,
                'apt_room_id': rec.apt_room_id.id,
                'booking_date': rec.booking_date,
                'start_time_str': rec.start_time_str,
                'start_time': rec.start_time,
                'end_time_str': rec.end_time_str,
                'end_time': rec.end_time,
                'duration': rec.duration,
                'time_id': rec.time_id.id,
                'pos_order_id':rec.pos_order_id.id,
                'pos_order_line_id':rec.pos_order_line_id.id,
                'pos_atv': True if rec.pos_order_id else False
                }

        self.appointments_id.appointment_line_id.create(vals)
        self.appointments_id.write(head_vals)

    @api.depends('start_time', 'duration', 'start_time_str', "apt_room_id")
    def _compute_endtime(self):
        for rec in self:
            if rec.start_time_str:
                start_time = datetime.strptime(str(rec.start_time_str), "%H:%M")
                start_time = start_time.strftime("%H.%M")
                rec.start_time = float(start_time)
                rec.end_time = abs(rec.start_time + rec.duration)
                dsfsdee = '%.2f' % abs(rec.duration)
                stri = str(dsfsdee).split(".")
                d_end_start_time = datetime.strptime(str('%.2f' % abs((rec.start_time))), "%H.%M")
                new_time_end = d_end_start_time + timedelta(hours=int(stri[0]), minutes=int(stri[1]),seconds=0)
                str_new_time_end = new_time_end.strftime("%H:%M")
                rec.end_time_str = str(str_new_time_end)

    @api.onchange("apt_room_id", 'booking_date','end_time_str')
    def onchange_apt_room_id(self):

        if self.apt_room_id and self.booking_date and self.start_time_str  and self.end_time_str:

            a_start = str(self.booking_date) + ' 00:00:00'
            a_end = str(self.booking_date) + ' 23:59:59'

            start_date = datetime.strptime(str(a_start), '%Y-%m-%d %H:%M:%S')
            end_date = datetime.strptime(str(a_end), '%Y-%m-%d %H:%M:%S')

            booked_room_ids = self.env['event.meeting.room'].search([('room_id', '=', self.apt_room_id.id),
                                                                     ('apt_start_dt', '>=', start_date),
                                                                     ('apt_end_dt', '<=', end_date)
                                                                     ])
            status_list = []

            for room in booked_room_ids:

                now_year = room.apt_start_dt.year
                now_month = room.apt_start_dt.month
                now_date = room.apt_start_dt.day

                now_hr = room.apt_start_dt.hour
                now_min = room.apt_start_dt.minute
                now_sec = 00

                end_now_hr = room.apt_end_dt.hour
                end_now_min = room.apt_end_dt.minute

                date_begin = datetime(now_year, now_month, now_date, now_hr, now_min, now_sec)
                date_begin = date_begin + timedelta(hours=5, minutes=30)
                date_end = datetime(now_year, now_month, now_date, end_now_hr, end_now_min, now_sec)
                date_end = date_end + timedelta(hours=5, minutes=30)


                avail_start = datetime.strptime(str(date_begin), "%Y-%m-%d %H:%M:%S").time()
                avail_end = datetime.strptime(str(date_end), "%Y-%m-%d %H:%M:%S").time()

                apt_start = datetime.strptime(self.start_time_str, '%H:%M').time()
                apt_end = datetime.strptime(self.end_time_str, '%H:%M').time()

                res = {}
                if avail_start == apt_start and avail_end == apt_end:
                    self.start_time = False
                    self.start_time_str = False
                    self.end_time = False
                    self.end_time_str = False
                    res['warning'] = {'title': _('Warning'), 'message': _('Room Slot not available at this Time.')}
                    return res

                if avail_start < apt_start < avail_end or avail_start < apt_end < avail_end:
                    self.start_time = False
                    self.start_time_str = False
                    self.end_time = False
                    self.end_time_str = False
                    res['warning'] = {'title': _('Warning'), 'message': _('Room Slot not available at this Time.')}
                    return res

class AppointmentCompletion(models.TransientModel):
    _name = "apt.complete"
    _description = 'Appointment Completion Warning'

    name = fields.Char()
    appointments_id = fields.Many2one('appointment.appointment', string='Appointment')

    def pay(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dashboard',
            'view_mode': 'kanban,tree,form',
            'res_model': 'pos.config',
        }

class AptPaymentConfirmation(models.TransientModel):
    _name = "apt.payment.confirmation"
    _description = 'Appointment Payment Confirmation'

    appointments_id = fields.Many2one('appointment.appointment', string='Appointment')
    company_id = fields.Many2one('res.company', string='Venue', change_default=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")

    def pay_now(self):
        payrate = self.env['hr.employee.payrate'].search([('service_category_type_id','=',self.appointments_id.service_categ_id.id),\
                    ('appoinment_type_id','=',self.appointments_id.appointments_type_id.id),('duration_id','=',self.appointments_id.time_id.id),\
                    ('employee_id','=',self.appointments_id.therapist_id.id)])
        
        def product_tax(product_id, amount):
            if product_id:
                total_included = 0
                for tax in product_id.taxes_id:
                    taxes = tax.compute_all(amount, self.currency_id, 1, product=product_id.id, partner=False)
                    t2 = taxes['total_included'] - amount
                    total_included += t2
                return total_included

        if self.appointments_id.pos_order_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Dashboard',
                'view_mode': 'kanban,tree,form',
                'res_model': 'pos.config',
            } 
        else:
            lst = []
            if self.appointments_id.session_type == 'type_single':
                lst.append([0, 0, {
                            'full_product_name':self.appointments_id.appointments_type_id.product_id.name,
                            'product_id': self.appointments_id.appointments_type_id.product_id.id,
                            'qty': 1,
                            'price_subtotal': payrate.unit_price,
                            'price_subtotal_incl': payrate.unit_price + product_tax(self.appointments_id.appointments_type_id.product_id, payrate.unit_price),
                            'discount': 0,
                            'price_unit': payrate.unit_price,
                            'name': self.appointments_id.name,
                            'default_product': True,
                        }])
            elif self.appointments_id.session_type == 'type_package':
                for line in self.appointments_id.appointment_line_id:
                    lst.append([0, 0, {
                            'full_product_name':self.appointments_id.appointments_type_id.product_id.name,
                            'product_id': self.appointments_id.appointments_type_id.product_id.id,
                            'qty': 1,
                            'price_subtotal': payrate.unit_price,
                            'price_subtotal_incl': payrate.unit_price + product_tax(self.appointments_id.appointments_type_id.product_id, payrate.unit_price),
                            'discount': self.appointments_id.s_service_categ_id.discount,
                            'price_unit': payrate.unit_price,
                            'name': self.appointments_id.name,
                            'appt_line_id': line.id,
                            'default_product': True,
                        }])

            if self.appointments_id.topay_cancellation_charge > 0 and self.appointments_id.cancel_options == 'now':
                product_id = self.env['product.product'].search([('name','=','Cancellation Charges')],limit=1)
                lst.append([0, 0,{
                    'full_product_name': product_id.name,
                    'product_id': product_id.id,
                    'qty': 1,
                    'price_subtotal': self.appointments_id.topay_cancellation_charge,
                    'price_subtotal_incl': self.appointments_id.topay_cancellation_charge + product_tax(product_id, self.appointments_id.topay_cancellation_charge),
                    'discount': 0,
                    'price_unit': self.appointments_id.topay_cancellation_charge,
                    'name': self.appointments_id.note_cancellation_charge,
                    'default_product': True,
                }])

            if self.appointments_id.topay_no_show_charges > 0 and self.appointments_id.noshow_options == 'now':
                    product_id = self.env['product.product'].search([('name','=','No Show Charges')],limit=1)
                    lst.append([0, 0,{
                        'full_product_name': product_id.name,
                        'product_id': product_id.id,
                        'qty': 1,
                        'price_subtotal': self.appointments_id.topay_no_show_charges,
                        'price_subtotal_incl': self.appointments_id.topay_no_show_charges + product_tax(product_id, self.appointments_id.topay_no_show_charges),
                        'discount': self.appointments_id.single_discount,
                        'price_unit': self.appointments_id.topay_no_show_charges,
                        'name': self.appointments_id.note_no_show,
                        'default_product': True,
                    }])
            CONFIRM = self.env['apt.order.confirmation']
            CONFT = CONFIRM.search([('appointments_id','=',self.appointments_id.id)],limit=1)
            def con_return(ap_id):

                return {
                        'type': 'ir.actions.act_window',
                        'name': _('Pay Now'),
                        'res_model': 'apt.order.confirmation',
                        'res_id': ap_id,
                        'target': 'new',
                        'view_mode': 'form',
                        'view_type': 'form',
                        # 'context': {
                        #     'default_product_categ_id': 1,
                        # },
                }
            # base_url=self.env ['ir.config_parameter'].sudo ().get_param ('web.base.url')
            if CONFT:
                CONFT.product_categ_id = CONFT.qty = 1
                CONFT.product_id = False
                CONFT.price_unit = CONFT.discount = 0.0
                CONFT.discount_type = 'percentage'
                # CONFT.quick_invoice_sms = 'Please pay your %s invoice bill of %s %s/appointment/ccavenue/request/%s' % (self.appointments_id.name, str(payrate.unit_price + product_tax(self.appointments_id.appointments_type_id.product_id, payrate.unit_price)) ,base_url, str(self.appointments_id.id))
                return con_return(CONFT.id)

            else:
                conf_id = CONFIRM.create({
                    'appointments_id': self.appointments_id.id,
                    'partner_id': self.appointments_id.partner_id.id,
                    'product_categ_id': 1,
                    # 'quick_invoice_sms': 'Please pay your %s invoice bill of %s %sappointment/ccavenue/request/%s' % (self.appointments_id.name, str(payrate.unit_price + product_tax(self.appointments_id.appointments_type_id.product_id, payrate.unit_price)) ,base_url, str(self.appointments_id.id)),
                    'lines': lst,
                })
                return con_return(conf_id.id)

    # appointment pay later functionality 28-07-22
    def pay_later(self):
        get_partner_id = self.env['res.partner'].search([('id', '=', self.appointments_id.partner_id.id)])
        form_view_id = self.env.ref('custom_partner.res_partner_history_history_from_view').id
        if get_partner_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Client'),
                'res_model': 'res.partner',
                'res_id': get_partner_id.id,
                'view_mode': 'form',
                'views': [[form_view_id, 'form']],
                
                    }
           

class Coupon(models.Model):
    _inherit = 'coupon.coupon'

    apt_order_id = fields.Many2one('apt.order.confirmation', 'Used in', readonly=True,
        help="The sales order on which the coupon is applied")

class AptOrderConfirmation(models.Model):
    _name = "apt.order.confirmation"
    _rec_name = "appointments_id"
    _description = 'Appointment Order Confirmation'

    @api.depends('lines')
    def _compute_price_total(self):
        for order in self:
            currency = order.currency_id
            order.amount_tax = currency.round(sum(self._amount_line_tax(line) for line in order.lines))
            amount_untaxed = currency.round(sum(line.price_subtotal_incl for line in order.lines))
            amount_sub_untaxed = currency.round(sum(line.price_unit*line.qty for line in order.lines))
            
            order.amount_discount = -1 * currency.round(sum(line.amount_discount for line in order.lines))
            order.amount_sub_total = amount_sub_untaxed
            order.amount_total = amount_untaxed
            order.amount_untaxed = currency.round(sum(line.price_unit * line.qty for line in order.lines))

    @api.depends('lines')
    def _compute_line_description(self):
        for rec in self:
            rec.write({
                'line_description': rec.lines.ids
            })


    appointments_id = fields.Many2one('appointment.appointment', string='Appointment')
    partner_id = fields.Many2one('res.partner', string='Name')

    cheque = fields.Char('Cheque #')
    payment_method_id = fields.Many2many('pos.payment.method', string='Payment Method')

    customer_code = fields.Char(string='Customer Code', related='partner_id.sequence')
    mobile = fields.Char(string='Mobile', related='partner_id.mobile')
    email = fields.Char(string='Email', related='partner_id.email')

    sequence = fields.Char(related='appointments_id.sequence')
    single_line_address = fields.Char(string="Address", related='partner_id.single_line_address')
    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    zip = fields.Char(related='partner_id.zip')
    city_id = fields.Many2one('city.master',string='City', related='partner_id.city_id')
    state_id = fields.Many2one("res.country.state", string='State', related='partner_id.state_id')
    country_id = fields.Many2one('res.country', string='Country', related='partner_id.country_id')
    company_id = fields.Many2one('res.company', string='Venue', change_default=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    gender = fields.Selection(string="Gender", related='partner_id.gender')
    location_ids = fields.Many2many('res.company',string='Locations', compute="get_location_ids")
    booking_ref = fields.Char('Booking Ref. #', related='appointments_id.sequence')
    sales_rep_id = fields.Many2one('res.users',string='Sales Rep.', related='appointments_id.sales_rep_id')
    pos_order_check = fields.Boolean(string="Pos Order")
    lines = fields.One2many('appointment.order.retail.product', 'apt_order_confirmation_id', string='Order Details')
    line_description = fields.Many2many('appointment.order.retail.product', 'line_description_new_order_table',\
        string="Order Summary", compute="_compute_line_description")
    amount_untaxed = fields.Float(string='Untaxed Amount', digits=0, compute='_compute_price_total')
    amount_tax = fields.Float(string='Taxes', digits=0, compute='_compute_price_total')
    amount_sub_total = fields.Float(string='Sub Total', digits=0, compute='_compute_price_total')
    amount_total = fields.Float(string='Total', digits=0, compute='_compute_price_total')
    amount_discount = fields.Float(string='Discount', digits=0, compute='_compute_price_total')

    apt_promotion = fields.Boolean('Promotion')
    apt_coupon_code = fields.Char('Coupon Code')
    no_code_promo_program_ids = fields.Many2many('coupon.program', string="Applied Immediate Promo Programs",
        domain="[('promo_code_usage', '=', 'no_code_needed'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", copy=False)
    code_promo_program_id = fields.Many2one('coupon.program', string="Applied Promo Program",
        domain="[('promo_code_usage', '=', 'code_needed'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", copy=False)
    promo_code = fields.Char(related='code_promo_program_id.promo_code', help="Applied program code", readonly=False)

    applied_coupon_ids = fields.One2many('coupon.coupon', 'apt_order_id', string="Applied Coupons", copy=False)

    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string='Fiscal Position',
        domain="[('company_id', '=', company_id)]", check_company=True,
        help="Fiscal positions are used to adapt taxes and accounts for particular customers or sales orders/invoices."
        "The default value comes from the customer.")
    
    product_categ_id = fields.Many2one('product.category', string='Show')
    product_id = fields.Many2one('product.product', string='Search By')
    price_unit = fields.Float(string='Unit Price', digits=0)
    qty = fields.Float('Quantity', digits='Product Unit of Measure', default=1)
    discount = fields.Float(string='Discount', digits=0, default=0.0)
    single_prod_subtotal = fields.Float(string="Subtotal",compute="_compute_cal_prod_subtotal")
    discount_type = fields.Selection([('flate_rate','Flate Rate'),('percentage','Percentage')], default='percentage', string='Discount Type', required=True)

    partner_credit = fields.Float('Credit Balance', related="partner_id.customer_balance")
    credit_reconcile = fields.Float('Enter the amount')
    mail_inv = fields.Boolean(string="Mail",help="Invisible the send mail and pos button in first click")

    @api.depends('partner_id')
    def get_location_ids(self):
        self.location_ids = self.appointments_id.company_id.ids

    @api.depends('shipping_handling_overall', 'lines')
    def _compute_subtotal_overall(self):
        for rec in self:
            rec.subtotal_overall = 0
            rec.taxes_overall = 0
            rec.total_overall = 0
            total_values = 0.0
            for i in rec.lines:
                rec.subtotal_overall += i.total_amt
                rec.taxes_overall += i.price_subtotal_incl - i.price_subtotal
            total_values = rec.subtotal_overall + rec.amount_discount
            rec.total_overall = total_values + rec.taxes_overall + rec.shipping_handling_overall
            base_url = self.env ['ir.config_parameter'].sudo ().get_param ('web.base.url')
            rec.quick_invoice_sms = 'Please pay your %s invoice bill of %s AED %s/appointment/ccavenue/request/%s/%s' % (rec.appointments_id.name, str(rec.total_overall) ,base_url, str(rec.appointments_id.id), str(rec.total_overall))
            rec.payment_link = '%s/appointment/ccavenue/request/%s/%s' % (base_url, str(rec.appointments_id.id), str(rec.total_overall))

    subtotal_overall = fields.Float(string="Subtotal", compute="_compute_subtotal_overall")
    shipping_handling_overall = fields.Float(string="Shipping Handling", compute="_compute_subtotal_overall", readonly=False, store=True)
    taxes_overall = fields.Float(string="Taxes", compute="_compute_subtotal_overall")
    total_overall = fields.Float(string="Total", compute="_compute_subtotal_overall")

    customer_phone_number = fields.Char(string="Customer Phone Number", related='partner_id.mobile', readonly=False)
    quick_invoice_sms = fields.Text(string="Quick Invoice SMS")
    select_payment_mode = fields.Selection([('none','None'),('credit','Available Credit'),('online_payment','Online Payment')], default='none', string='Select Payment Mode')
    payment_link = fields.Text(string="Payment Link")
    
    # pass the product price while select the product 01-07-22
    @api.onchange('product_id')
    def product_price(self):
        self.price_unit = self.product_id.list_price


    def product_tax(self, product_id, amount):
        if product_id:
            total_included = 0
            for tax in product_id.taxes_id:
                taxes = tax.compute_all(amount, self.env.company.currency_id, 1, product=product_id.id, partner=False)
                t2 = taxes['total_included'] - amount
                total_included += t2
            return total_included

    # calculate the subtotal for single product 21-09-22
    @api.depends('qty','price_unit','discount','discount_type')
    def _compute_cal_prod_subtotal(self):
        self.single_prod_subtotal = self.qty * self.price_unit
        if self.discount and self.discount_type == 'percentage':
            sub_total = (self.qty * self.price_unit)
            self.single_prod_subtotal =sub_total - (sub_total * self.discount/100)
        else:
            sub_total = self.qty * self.price_unit
            self.single_prod_subtotal =sub_total - self.discount


    def apply_credit(self):
        # Added validation for apply credit 02-07-22
        if self.partner_credit < 0:
            raise UserError(_("Cannot apply amount when credit Balance is Negative ! "))

        if self.partner_credit < self.credit_reconcile:
            raise UserError(_("An amount greater than the credit balance cannot be applied ! "))
        if self.total_overall < self.credit_reconcile:
            raise UserError(_("An amount greater than the order total cannot be applied ! "))


        pos_lines = payment_lines = []
        pos_session_id = self.env['pos.session'].search([('state', '=', 'opened')], limit=1)
        if not pos_session_id:
            raise UserError(_("Please create a POS session to create POS order and confirm the Appointment"))

        for rec in self.lines:
            l_id = self.env['appointment.order.retail.product'].browse(rec.id)
            
            pos_lines.append([0, 0, {
                'apt_service_category': rec.service_categ_id.id,
                'full_product_name': l_id.product_id.name,
                'product_id': l_id.product_id.id,
                'qty': rec.qty,
                'price_subtotal': l_id.price_subtotal,
                'price_subtotal_incl':l_id.price_subtotal_incl,
                'commission_recipient':l_id.commission_recipient,
                # 'order_id': rec.pos_order_id.id,
                'discount': l_id.discount if l_id.discount_type == 'percentage' else 0.0,
                'absolute_discount': l_id.discount if l_id.discount_type == 'flate_rate' else 0.0,
                'tax_ids': l_id.tax_ids.ids,
                'tax_ids_after_fiscal_position': l_id.tax_ids.ids,
                'price_unit': l_id.price_unit,
                'name': l_id.product_id.name,
                'appt_line_id': False,
            }])
        payment_method_id = self.env['pos.payment.method'].search([('credit_jr','=', True)], limit=1)
        # payment_lines.append([0, 0, {
        #     'payment_method_id': payment_method_id.id,
        #     'amount': self.credit_reconcile,
        # }])

        
        sale_id = self.env['pos.order'].create({
                    'partner_id': self.appointments_id.partner_id.id,
                    'pricelist_id': 1,
                    'appt_sale_id': self.appointments_id.id,
                    'session_id': pos_session_id.id,
                    'session_type': self.appointments_id.session_type,
                    'amount_tax': 0.0,
                    'amount_paid': 0.0,
                    'amount_return': 0.0,
                    'amount_total': 0.0,
                    'state': 'draft',
                    'booking_type': 'appointment',
                    'sale_type_for': 'appointment',
                    'apt_booking_date': self.appointments_id.booking_date,
                    'apt_booked_by': self.appointments_id.booked_by.id,
                    'company_id': self.appointments_id.company_id.id,
                    'name': self.appointments_id.sequence,
                    # 'pos_reference': pos_seq,
                    'payment_methods': payment_method_id.name,
                    'cheque': self.cheque,
                    # 'payment_method_id': payment_method_id.id,
                    'lines': pos_lines,
                    # 'payment_ids': payment_lines,
                })
        sale_id._onchange_amount_all()
        self.appointments_id.pos_order_id = sale_id.id

        #apply credit 25/07/2022

        statement_ids = [[0, 0, {'name': '2022-07-05 06:15:18', 'payment_method_id': payment_method_id.id, 'amount': self.credit_reconcile, 'payment_status': '', 'ticket': '', 'card_type': '', 'cardholder_name': '', 'transaction_id': ''}]]


        data = self.env['pos.order'].search_read([('id','=',sale_id.id)])[0]
        data['pos_session_id'] = pos_session_id.id
        data_lines = []
        for line in sale_id.lines:
            da = self.env['pos.order.line'].search_read([('id','=',line.id)])[0]
            da['company_id'] = self.appointments_id.company_id.id
            da['product_id'] = line.product_id.id
            da['tax_ids'] = [(6,0, tuple(da['tax_ids']))] if da['tax_ids'] else []
            data_lines.append([0, 0, da])
            if sale_id.creation_date.month < 10 :
                month = '0' + str(sale_id.creation_date.month)
            else:
                month = str(sale_id.creation_date.month)
            if sale_id.creation_date.day < 10 :
                day = '0' + str(sale_id.creation_date.day)
            else:
                day = str(sale_id.creation_date.day)
        data['creation_date'] = ('%s-%s-%s'+'T'+'00:00:00.000Z')% (str(sale_id.creation_date.year), str(month), str(day))
        # '2022-07-05T06:15:18.063Z'
        data['lines'] = data_lines
        data['to_invoice']= True
        data['statement_ids'] = statement_ids
        data['company_id'] = self.appointments_id.company_id.id

        order = {"data":data}
        partner_data = self.env['res.partner'].search_read([('id','=',sale_id.partner_id.id)])[0]
        partner_order = {"client":partner_data}

        sale_id._process_order(order,False,sale_id)
        sale_id.action_pos_order_invoice()
        sale_id.UpdateCreditJournal(order=partner_order, clients=partner_data, company_id=self.appointments_id.company_id.ids, pos_cur=sale_id.session_id.currency_id.id, amount=self.credit_reconcile)
        sale_id.partner_id.UpdateCredit(partner_id=partner_data,company_id=self.appointments_id.company_id.ids, pos_currency_id=sale_id.session_id.currency_id.id, custom_credit=self.credit_reconcile)


        # self.env['pos.payment'].create({
        #     'payment_method_id': payment_method_id.id,
        #     'amount': self.credit_reconcile,
        #     'pos_order_id': sale_id.id,
        # })

        # if self.credit_reconcile >= self.total_overall:
        #     sale_id.state = 'paid'


    def preview_invoice(self):
        print('090909090909090909')

    def send_by_sms(self):
        print('090909090909090909')

    def add_item(self):
        if not self.product_id:
            raise UserError(_("Please select product to continue !!"))
        
        if self.qty < 1:
            raise UserError(_("Quantity should not be less then 1 !!"))

        self.env['appointment.order.retail.product'].create({
                'full_product_name':self.product_id.name,
                'product_id': self.product_id.id,
                'qty': self.qty,
                'price_subtotal': self.price_unit,
                'price_subtotal_incl': self.price_unit + self.product_tax(self.product_id, self.price_unit),
                'discount': self.discount,
                'discount_type': self.discount_type,
                'price_unit': self.price_unit,
                'name': self.product_id.name,
                'default_product': True,
                'apt_order_confirmation_id': self.id,
        })

        self.product_categ_id = self.qty = 1
        self.product_id = False
        self.price_unit = self.discount = 0.0
        self.discount_type = 'percentage'

        return {
                'type': 'ir.actions.act_window',
                'name': _('Pay Now'),
                'res_model': 'apt.order.confirmation',
                'res_id': self.id,
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
            }

    def proforma_invoice(self):
        return self.env.ref('ppts_custom_apt_mgmt.action_report_proforma_invoice').report_action(self)

    def send_email(self):
        self.mail_inv = True
        template_id = self.env.ref('ppts_custom_apt_mgmt.proforma_email_template')
        template = self.env['mail.template'].search([('model', '=', 'mail.compose.message')], limit=1)
        ctx = dict(
            default_model='apt.order.confirmation',
            default_res_id=self.id,
            default_res_model='apt.order.confirmation',
            default_use_template=bool(template_id),
            default_template_id=template_id and template_id.id or False,
            default_composition_mode='comment',
            # custom_layout="mail.mail_notification_paynow",
            force_email=True
        )
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    def _get_reward_values_product(self, program):
        price_unit = self.order_line.filtered(lambda line: program.reward_product_id == line.product_id)[0].price_reduce

        order_lines = (self.lines - self._get_reward_lines()).filtered(lambda x: program._get_valid_products(x.product_id))
        # order_lines = (self.order_line - self._get_reward_lines()).filtered(lambda x: program._get_valid_products(x.product_id))
        max_product_qty = sum(lines.mapped('qty')) or 1
        # max_product_qty = sum(order_lines.mapped('product_uom_qty')) or 1
        total_qty = sum(self.lines.filtered(lambda x: x.product_id == program.reward_product_id).mapped('qty'))
        # total_qty = sum(self.order_line.filtered(lambda x: x.product_id == program.reward_product_id).mapped('product_uom_qty'))
        # Remove needed quantity from reward quantity if same reward and rule product
        if program._get_valid_products(program.reward_product_id):
            # number of times the program should be applied
            program_in_order = max_product_qty // (program.rule_min_quantity + program.reward_product_quantity)
            # multipled by the reward qty
            reward_product_qty = program.reward_product_quantity * program_in_order
            # do not give more free reward than products
            reward_product_qty = min(reward_product_qty, total_qty)
            if program.rule_minimum_amount:
                order_total = sum(lines.mapped('price_total')) - (program.reward_product_quantity * program.reward_product_id.lst_price)
                # order_total = sum(order_lines.mapped('price_total')) - (program.reward_product_quantity * program.reward_product_id.lst_price)
                reward_product_qty = min(reward_product_qty, order_total // program.rule_minimum_amount)
        else:
            program_in_order = max_product_qty // program.rule_min_quantity
            reward_product_qty = min(program.reward_product_quantity * program_in_order, total_qty)

        reward_qty = min(int(int(max_product_qty / program.rule_min_quantity) * program.reward_product_quantity), reward_product_qty)
        # Take the default taxes on the reward product, mapped with the fiscal position
        taxes = program.reward_product_id.taxes_id.filtered(lambda t: t.company_id.id == self.company_id.id)
        taxes = self.fiscal_position_id.map_tax(taxes)
        return {
            'product_id': program.discount_line_product_id.id,
            'price_unit': - price_unit,
            'qty': reward_qty,
            # 'product_uom_qty': reward_qty,
            'is_reward_line': True,
            'name': _("Free Product") + " - " + program.reward_product_id.name,
            'product_uom_id': program.reward_product_id.uom_id.id,
            # 'product_uom': program.reward_product_id.uom_id.id,
            'tax_ids': [(4, tax.id, False) for tax in taxes],
        }

    def _get_base_order_lines(self, program):
        """ Returns the sale order lines not linked to the given program.
        """
        return self.lines.filtered(lambda x: not (x.is_reward_line and x.product_id == program.discount_line_product_id))
        # return self.order_line.filtered(lambda x: not (x.is_reward_line and x.product_id == program.discount_line_product_id))

    def _get_paid_order_lines(self):
        """ Returns the sale order lines that are not reward lines.
            It will also return reward lines being free product lines. """
        free_reward_product = self.env['coupon.program'].search([('reward_type', '=', 'product')]).mapped('discount_line_product_id')
        return self.lines.filtered(lambda x: not x.is_reward_line or x.product_id in free_reward_product)
        # return self.order_line.filtered(lambda x: not x.is_reward_line or x.product_id in free_reward_product)

    def _get_reward_values_discount_fixed_amount(self, program):
        total_amount = sum(self._get_base_order_lines(program).mapped('price_total'))
        fixed_amount = program._compute_program_amount('discount_fixed_amount', self.currency_id)
        if total_amount < fixed_amount:
            return total_amount
        else:
            return fixed_amount

    def _get_cheapest_line(self):
        # Unit prices tax included
        return min(self.order_line.filtered(lambda x: not x.is_reward_line and x.price_reduce > 0), key=lambda x: x['price_reduce'])

    def _get_reward_values_discount_percentage_per_line(self, program, line):
        discount_amount = line.qty * line.price_unit * (program.discount_percentage / 100)
        # discount_amount = line.product_uom_qty * line.price_reduce * (program.discount_percentage / 100)
        return discount_amount

    def _get_reward_values_discount(self, program):
        if program.discount_type == 'fixed_amount':
            taxes = program.discount_line_product_id.taxes_id
            if self.fiscal_position_id:
                taxes = self.fiscal_position_id.map_tax(taxes)
            return [{
                'name': _("Discount: %s", program.name),
                'product_id': program.discount_line_product_id.id,
                'price_unit': - self._get_reward_values_discount_fixed_amount(program),
                'qty': 1.0,
                # 'product_uom_qty': 1.0,
                'product_uom_id': program.discount_line_product_id.uom_id.id,
                # 'product_uom': program.discount_line_product_id.uom_id.id,
                'is_reward_line': True,
                'tax_id': [(4, tax.id, False) for tax in taxes],
            }]
        reward_dict = {}
        lines = self._get_paid_order_lines()
        amount_total = sum(self._get_base_order_lines(program).mapped('price_subtotal'))
        if program.discount_apply_on == 'cheapest_product':
            line = self._get_cheapest_line()
            if line:
                discount_line_amount = min(line.price_reduce * (program.discount_percentage / 100), amount_total)
                if discount_line_amount:
                    taxes = self.fiscal_position_id.map_tax(line.tax_id)

                    reward_dict[line.tax_id] = {
                        'name': _("Discount: %s", program.name),
                        'product_id': program.discount_line_product_id.id,
                        'price_unit': - discount_line_amount if discount_line_amount > 0 else 0,
                        'qty': 1.0,
                        # 'product_uom_qty': 1.0,
                        'product_uom_id': program.discount_line_product_id.uom_id.id,
                        # 'product_uom': program.discount_line_product_id.uom_id.id,
                        'is_reward_line': True,
                        'tax_id': [(4, tax.id, False) for tax in taxes],
                    }
        elif program.discount_apply_on in ['specific_products', 'on_order']:
            if program.discount_apply_on == 'specific_products':
                # We should not exclude reward line that offer this product since we need to offer only the discount on the real paid product (regular product - free product)
                free_product_lines = self.env['coupon.program'].search([('reward_type', '=', 'product'), ('reward_product_id', 'in', program.discount_specific_product_ids.ids)]).mapped('discount_line_product_id')
                lines = lines.filtered(lambda x: x.product_id in (program.discount_specific_product_ids | free_product_lines))

            # when processing lines we should not discount more than the order remaining total
            currently_discounted_amount = 0
            for line in lines:
                discount_line_amount = min(self._get_reward_values_discount_percentage_per_line(program, line), amount_total - currently_discounted_amount)

                if discount_line_amount:

                    if line.tax_ids in reward_dict:
                        reward_dict[line.tax_ids]['price_unit'] -= discount_line_amount
                    else:
                        taxes = self.fiscal_position_id.map_tax(line.tax_ids)

                        reward_dict[line.tax_ids] = {
                            'name': _(
                                "Discount: %(program)s - On product with following taxes: %(taxes)s",
                                program=program.name,
                                taxes=", ".join(taxes.mapped('name')),
                            ),
                            'product_id': program.discount_line_product_id.id,
                            'price_unit': - discount_line_amount if discount_line_amount > 0 else 0,
                            'qty': 1.0,
                            # 'product_uom_qty': 1.0,
                            'product_uom_id': program.discount_line_product_id.uom_id.id,
                            # 'product_uom': program.discount_line_product_id.uom_id.id,
                            'is_reward_line': True,
                            'tax_ids': [(4, tax.id, False) for tax in taxes],
                        }
                        currently_discounted_amount += discount_line_amount

        # If there is a max amount for discount, we might have to limit some discount lines or completely remove some lines
        max_amount = program._compute_program_amount('discount_max_amount', self.currency_id)
        if max_amount > 0:
            amount_already_given = 0
            for val in list(reward_dict):
                amount_to_discount = amount_already_given + reward_dict[val]["price_unit"]
                if abs(amount_to_discount) > max_amount:
                    reward_dict[val]["price_unit"] = - (max_amount - abs(amount_already_given))
                    add_name = formatLang(self.env, max_amount, currency_obj=self.currency_id)
                    reward_dict[val]["name"] += "( " + _("limited to ") + add_name + ")"
                amount_already_given += reward_dict[val]["price_unit"]
                if reward_dict[val]["price_unit"] == 0:
                    del reward_dict[val]
        return reward_dict.values()

    def _get_reward_line_values(self, program):
        self.ensure_one()
        self = self.with_context(lang=self.partner_id.lang)
        program = program.with_context(lang=self.partner_id.lang)
        if program.reward_type == 'discount':
            return self._get_reward_values_discount(program)
        elif program.reward_type == 'product':
            return [self._get_reward_values_product(program)]

    def _is_global_discount_already_applied(self):
        applied_programs = self.no_code_promo_program_ids + \
                           self.code_promo_program_id + \
                           self.applied_coupon_ids.mapped('program_id')
        return applied_programs.filtered(lambda program: program._is_global_discount_program())
    
    def _get_reward_lines(self):
        self.ensure_one()
        return self.lines.filtered(lambda line: line.is_reward_line)

    def _get_no_effect_on_threshold_lines(self):
        self.ensure_one()
        lines = self.env['appointment.order.retail.product']
        return lines

    def _create_new_no_code_promo_reward_lines(self):
        '''Apply new programs that are applicable'''
        self.ensure_one()
        order = self
        programs = order._get_applicable_no_code_promo_program()
        
        # programs = programs._keep_only_most_interesting_auto_applied_global_discount_program()
        for program in programs:
            # VFE REF in master _get_applicable_no_code_programs already filters programs
            # why do we need to reapply this bunch of checks in _check_promo_code ????
            # We should only apply a little part of the checks in _check_promo_code...
            error_status = program._check_promo_code(order, False)
            if not error_status.get('error'):
                if program.promo_applicability == 'on_next_order':
                    order.state != 'cancel' and order._create_reward_coupon(program)
                elif program.discount_line_product_id.id not in self.lines.mapped('product_id').ids:
                    promotion_rec = self._get_reward_line_values(program)
                    return promotion_rec
                # elif program.discount_line_product_id.id not in self.order_line.mapped('product_id').ids:
                    # self.write({'lines': [(0, False, value) for value in self._get_reward_line_values(program)]})
                order.no_code_promo_program_ids |= program
        

    def _get_applicable_no_code_promo_program(self):
        self.ensure_one()
        programs = self.env['coupon.program'].with_context(
            no_outdated_coupons=True,
            applicable_coupon=True,
        ).search([
            ('promo_code_usage', '=', 'no_code_needed'),
            '|', ('rule_date_from', '=', False), ('rule_date_from', '<=', self.appointments_id.booking_date),
            '|', ('rule_date_to', '=', False), ('rule_date_to', '>=', self.appointments_id.booking_date),
            '|', ('company_id', '=', self.company_id.id), ('company_id', '=', False),
        ])._filter_programs_from_common_rules(self)
        return programs

    def move_to_pos(self):
        self.appointments_id.action_move_to_pos(self.lines.ids, self.cheque, self.payment_method_id.ids,self.shipping_handling_overall)
        if self.appointments_id.session_type == 'type_package':
            service_product = []
            for apt_pack_line in self.appointments_id.appointment_line_id:
                # sub = ['calendar.appointment.type'].search([('id','=',apt_pack_line.appointments_type_id.product_id.id)])
                service_product.append(apt_pack_line.appointments_type_id.product_id.id)
            for line in self.lines:
                
                if line.product_id.product_used == 'appointments' and line.product_id.id not in (service_product):
                    self.appointments_id.with_context(new_product_id=line.id).copy()
            
        elif self.appointments_id.session_type == 'type_single': 
            if len(self.lines.mapped('product_id')) > 1:
                for line in self.lines:
                    if self.lines[0].product_id.id != line.product_id.id and line.product_id.product_used == 'appointments':
                        self.appointments_id.with_context(new_product_id=line.id).copy()
        else:
            pass

        self.pos_order_check = True

# Open the pos dashboard 23-06-22
    def open_pos_dashboard(self):
        
        return {
                'type': 'ir.actions.act_window',
                'name': 'Dashboard',
                'view_mode': 'kanban,tree,form',
                'res_model': 'pos.config',
            } 


    def _create_reward_line(self, program):
        coupon_rec = self._get_reward_line_values(program)
        return coupon_rec
        
    def _get_applicable_programs(self):
        """
        This method is used to return the valid applicable programs on given order.
        """
        self.ensure_one()
        programs = self.env['coupon.program'].with_context(
            no_outdated_coupons=True,
        ).search([
            ('company_id', 'in', [self.company_id.id, False]),
            '|', ('rule_date_from', '=', False), ('rule_date_from', '<=', self.appointments_id.booking_date),
            '|', ('rule_date_to', '=', False), ('rule_date_to', '>=', self.appointments_id.booking_date),
        ], order="id")._filter_programs_from_common_rules(self)
        return programs

    def apply_coupon(self, order, coupon_code):
        error_status = {}
        program = self.env['coupon.program'].search([('promo_code', '=', coupon_code)])
        if program:
            error_status = program._check_promo_code(order, coupon_code)
            if not error_status:
                if program.promo_applicability == 'on_next_order':
                    # Avoid creating the coupon if it already exist
                    if program.discount_line_product_id.id not in order.generated_coupon_ids.filtered(lambda coupon: coupon.state in ['new', 'reserved']).mapped('discount_line_product_id').ids:
                        coupon = order._create_reward_coupon(program)
                        return {
                            'generated_coupon': {
                                'reward': coupon.program_id.discount_line_product_id.name,
                                'code': coupon.code,
                            }
                        }
                else:  # The program is applied on this order
                    order._create_reward_line(program)
                    order.code_promo_program_id = program
        else:
            coupon = self.env['coupon.coupon'].search([('code', '=', coupon_code)], limit=1)
            if coupon:
                error_status = coupon._check_coupon_code(order)
                if not error_status:
                    order._create_reward_line(coupon.program_id)
                    order.applied_coupon_ids += coupon
                    coupon.write({'state': 'used'})
                    return order._create_reward_line(coupon.program_id)
            else:
                error_status = {'not_found': _('This coupon is invalid (%s).') % (coupon_code)}
        return error_status

    def _amount_line_tax(self, line):
        if line.product_id:
            total_included = price = 0
            if line.discount_type == 'percentage':
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            else:
                price = line.price_unit - line.discount

            for tax in line.tax_ids:
                taxes = tax.compute_all(price, self.currency_id, line.qty, product=line.product_id, partner=False)
                t2 = taxes['taxes'][0]['amount']
                total_included += t2
            return total_included

    @api.onchange('lines')
    def _onchange_amount_all(self):
        for order in self:
            currency = order.currency_id
            order.amount_tax = currency.round(sum(self._amount_line_tax(line) for line in order.lines))
            amount_untaxed = currency.round(sum(line.price_subtotal_incl for line in order.lines))
            amount_sub_untaxed = currency.round(sum(line.price_unit*line.qty for line in order.lines))
            order.amount_discount = -1 * currency.round(sum(line.amount_discount for line in order.lines))
            order.amount_sub_total = amount_sub_untaxed
            order.amount_total = amount_untaxed
            
class AppointmentOrderRetailProduct(models.Model):
    _name = 'appointment.order.retail.product'
    _description = 'Appointment Order Retail Product'




    name = fields.Char()
    service_categ_id = fields.Many2many('appointment.category', string="Services Category")
    sub_categ_id = fields.Many2many('calendar.appointment.type', string="Sub Category")
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True),('product_used','in',('appointments','event','none')),('type','in',('product','service'))])
    price_unit = fields.Float(string='Unit Price', digits=0)
    qty = fields.Float('Quantity', digits='Product Unit of Measure', default=1)
    price_subtotal = fields.Float(string='Subtotal w/o Tax', digits=0, compute='_compute_price_subtotal')
    price_subtotal_incl = fields.Float(string='Subtotal', digits=0, compute='_compute_price_subtotal')
    discount = fields.Float(string='Discount', digits=0, default=0.0)
    order_id = fields.Many2one('pos.order', string='Order Ref', ondelete='cascade')
    tax_ids = fields.Many2many('account.tax', string='Taxes', related="product_id.taxes_id", readonly=False,company_dependent=True)
    
    product_uom_id = fields.Many2one('uom.uom', string='Product UoM', related='product_id.uom_id')
    company_id = fields.Many2one('res.company', string='Venue', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    full_product_name = fields.Char('Full Product Name')
    apt_order_confirmation_id = fields.Many2one('apt.order.confirmation', string='Order Confirmation')
    default_product = fields.Boolean()
    amount_discount = fields.Float(string='Discount', digits=0, compute="_compute_discount")
    
    commission_recipient = fields.Selection([('none', 'None'),('sale_person', 'Sale Person'),('therapist', 'Therapist')], string='Commission Recipient', default='none')
    commission_type = fields.Selection(string='Commission Price Type', default='percentage', related='product_id.commission_type', store=True, readonly=False)
    therapist_commission_type = fields.Float('Percentage or Price', compute='_compute_therapist_commission_type', readonly=False)
    therapist_commission = fields.Float(string='Discount', readonly=False, compute='_compute_therapist_commission')

    appt_line_id = fields.Many2one('appointment.line.id',string="appointment lines id")
    is_reward_line = fields.Boolean('Is a program reward line')
    total_amt = fields.Float(string="Amount Total",compute="_compute_total_amt")

    # use to calculate amount with qty 24-06-22
    @api.depends('qty','price_unit')
    def _compute_total_amt(self):
        for rec in self:
            rec.total_amt = rec.qty * rec.price_unit

    @api.depends('qty', 'discount', 'price_unit', 'tax_ids', 'discount_type')
    def _compute_price_subtotal(self):
        for rec in self:

            if rec.product_id:
                if rec.discount_type == 'percentage':
                    price = rec.price_unit * (1 - (rec.discount or 0.0) / 100.0)
                else:
                    if rec.discount > rec.price_unit: 
                        raise UserError(_("Discount price should not be greater than unit price!!"))
                    price = rec.price_unit - rec.discount

                price_no_discount = 0
                
                rec.price_subtotal = rec.price_subtotal_incl = price * rec.qty
                price_no_discount = rec.price_unit * rec.qty
                rec.amount_discount = price_no_discount - rec.price_subtotal

                total_excluded = 0
                total_included = 0
                for tax in rec.product_id.taxes_id:
                    taxes = tax.compute_all(price, rec.currency_id, rec.qty, product=rec.product_id, partner=False)
                    t1 = taxes['total_excluded'] - rec.price_subtotal
                    t2 = taxes['taxes'][0]['amount']
                    total_excluded += t1
                    total_included += t2
                rec.price_subtotal += total_excluded
                rec.price_subtotal_incl += total_included
            else:
                rec.price_subtotal = 0
                rec.price_subtotal_incl = 0

    @api.depends('product_id','commission_type')
    def _compute_therapist_commission_type(self):
        for rec in self:
            if rec.product_id.commission_type == 'percentage':
                rec.therapist_commission_type = rec.product_id.commission_percentage
            else:
                rec.therapist_commission_type = rec.product_id.commission_fixed_price

    @api.depends('product_id','commission_type','therapist_commission_type','price_unit')
    def _compute_therapist_commission(self):
        for rec in self:
            rec.therapist_commission = 0.0
            if rec.commission_type == 'percentage':
                if rec.therapist_commission_type < rec.price_subtotal:
                    rec.therapist_commission = rec.price_subtotal * rec.therapist_commission_type / 100
            else:
                if rec.therapist_commission_type < rec.price_subtotal:
                    rec.therapist_commission = rec.therapist_commission_type

    discount_type = fields.Selection([('flate_rate','Flate Rate'),('percentage','Percentage')], default='percentage', string='Discount Type', required=True)

    @api.depends('discount_type','qty','discount','price_unit','tax_ids')
    def _compute_discount(self):
        for rec in self:
            rec.amount_discount = 0
            if rec.discount_type == 'percentage':
                price = rec.price_unit * (1 - (rec.discount or 0.0) / 100.0)
            else:
                if rec.discount > rec.price_unit: 
                    raise UserError(_("Discount price should not be greater than unit price!!"))
                price = rec.price_unit - rec.discount

            price_no_discount = 0
            with_discount = price * rec.qty
            price_no_discount = rec.price_unit * rec.qty
            rec.amount_discount = price_no_discount - with_discount
        
    @api.onchange('qty', 'discount', 'price_unit', 'tax_ids', 'discount_type')
    def _onchange_qty(self):
        if self.product_id:
            if self.discount_type == 'percentage':
                price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            else:
                if self.discount > self.price_unit: 
                    raise UserError(_("Discount price should not be greater than unit price!!"))
                price = self.price_unit - self.discount

            price_no_discount = 0
            
            self.price_subtotal = self.price_subtotal_incl = price * self.qty
            price_no_discount = self.price_unit * self.qty
            self.amount_discount = price_no_discount - self.price_subtotal

            total_excluded = 0
            total_included = 0
            for tax in self.product_id.taxes_id:
                taxes = tax.compute_all(price, self.currency_id, self.qty, product=self.product_id, partner=False)
                t1 = taxes['total_excluded'] - self.price_subtotal
                t2 = taxes['taxes'][0]['amount']
                total_excluded += t1
                total_included += t2
            self.price_subtotal += total_excluded
            self.price_subtotal_incl += total_included


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    download_report = fields.Boolean(string="Preview & Download ")

    # used to send the mail and open the invoice preview and also create the pos 29-06-22
    def apt_create_pos_mail_send(self):

        active_id = self._context.get('active_id')
        rec_id = self.env["apt.order.confirmation"].browse(active_id)
        if self.model == "apt.order.confirmation":
            # pos order creation 29-06-22
            rec_id.move_to_pos()
            for rec in self:
                # use to send mail as default flow 29-06-22
                rec.action_send_mail()
                if rec.download_report:
                    # download the pdf report
                    return rec_id.proforma_invoice()







