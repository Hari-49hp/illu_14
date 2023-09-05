import base64
import requests

from odoo import api, fields, models, _
from dateutil import rrule
import re
import pytz
import babel.dates
from odoo import tools
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from odoo.tools.misc import get_lang

from datetime import date, timedelta, datetime
from dateutil.relativedelta import * 
import time
from odoo.http import request, Response
import json, werkzeug
import requests
import urllib.request
import urllib
import logging

_logger = logging.getLogger(__name__)

TIME = [('08:00','08:00'),('08:15','08:15'),('08:30','08:30'),('08:45','08:45'),('09:00','09:00'),('09:15','09:15'),('09:30','09:30'),('09:45','09:45'),('10:00','10:00'),('10:15','10:15'),('10:30','10:30'),('10:45','10:45'),('11:00','11:00'),('11:15','11:15'),('11:30','11:30'),('11:45','11:45'),('12:00','12:00'),('12:15','12:15'),('12:30','12:30'),('12:45','12:45'),('13:00','13:00'),('13:15','13:15'),('13:30','13:30'),('13:45','13:45'),('14:00','14:00'),('14:15','14:15'),('14:30','14:30'),('14:45','14:45'),('15:00','15:00'),('15:15','15:15'),('15:30','15:30'),('15:45','15:45'),('16:00','16:00'),('16:15','16:15'),('16:30','16:30'),('16:45','16:45'),('17:00','17:00'),('17:15','17:15'),('17:30','17:30'),('17:45','17:45'),('18:00','18:00'),('18:15','18:15'),('18:30','18:30'),('18:45','18:45'),('19:00','19:00'),('19:15','19:15'),('19:30','19:30'),('19:45','19:45'),('20:00','20:00'),('20:15','20:15'),('20:30','20:30'),('20:45','20:45'),('21:00','21:00'),('21:15','21:15'),('21:30','21:30'),('21:45','21:45'),('22:00','22:00'),('22:15','22:15'),('22:30','22:30'),('22:45','22:45'),('23:00','23:00'),('23:15','23:15'),('23:30','23:30'),('23:45','23:45'),('23:55','23:55')]

# Appointments & Booking
class CustomAppointments(models.Model):
    _name = 'appointment.appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Appointments Module'
    _rec_name = 'sequence'

    @api.model
    def set_current_company_default(self):
        return self.env['res.company'].search([('id', '=', self.env.company.id)]).ids

    def _get_company_allowed_domain(self):
        if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

    name = fields.Char(tracking=True)
    ther_id = fields.Many2one('hr.employee')
    sequence = fields.Char('Sequence',readonly=True, copy=False, default=' ',tracking=True)
    use_rescheule = fields.Boolean(string='Show reschedule',tracking=True,)
    state = fields.Selection([('new', 'Booked'),('confirm', 'Confirmed'),('arrive', 'Arrived'),('no_show','No Show'),('ongoing','Ongoing'),
                              ('done', 'Completed'),('void', 'Void'),('cancel', 'Cancelled')], string='State', default='new', required=True, tracking=True)
    color = fields.Integer(string='Color', default=10)
    type_partner = fields.Selection([('type_existing', 'Existing'),('type_new', 'New')], string='Type of Customer?',default='type_existing',required=True)
    partner_id = fields.Many2one('res.partner',string='Customer Name ', copy=False, tracking=True, \
        domain=['&','&','|',('is_a_customer','=',True),('is_a_vendor','=',True),('user_ids','=',False),('is_company','=',False)])
    email = fields.Char(string='E-Mail ID',related='partner_id.email', tracking=True)
    mobile = fields.Char(string='Mobile',related='partner_id.mobile', tracking=True)
    creation_date = fields.Date(string='Creation Date ',default=fields.Date.context_today, tracking=True)
    creation_datetime = fields.Datetime(string='Creation Date', tracking=True)
    booking_date = fields.Date(string=' Appoinment Date ',default=fields.Date.context_today,tracking=True)
    expiry_date = fields.Date(string='Package Expiry Date', tracking=True)
    sales_rep_id = fields.Many2one('res.users',string='Sales Rep', default=lambda self: self.env.uid, tracking=True)
    booked_by = fields.Many2one('res.users',string='Created By ', default=lambda self: self.env.uid, tracking=True)
    altered_booked_by = fields.Many2one('res.users',string='Modified By', tracking=True)
    sale_person_id = fields.Many2one('res.users', string='Sales Person', copy=False, tracking=True)
    source_id = fields.Many2one('appointment.source', string='Source', copy=False, tracking=True)
    reffer_ids = fields.Many2one("master.refferal", string="Lead", store=True)
    reffer_type_id = fields.Many2one("master.refferal", string="Lead Source", tracking=True)
    company_id = fields.Many2one('res.company', string='Venue', change_default=True, default=lambda self: self.env.company, domain=_get_company_allowed_domain, required=False)
    location_id = fields.Many2one('res.partner', string='Location', copy=False,tracking=True,help='Location of Appointment')
    #platform
    appointment_type = fields.Selection([('type_online', 'Online'),('type_onsite', 'On-site')],
                                        string='Appointment Platform', default='type_onsite', tracking=True)
    
    is_prebook = fields.Boolean(string="Is Prebook",help="To show is the pre booking record.")
    apt_date = fields.Boolean(string="Apt date",help="To invisible appointment date.")
    #mode of appt
    booking_mode = fields.Selection([('online', 'Website'),('direct', 'Backend')],
                                    string='Mode Of Appointment?' , default='direct', tracking=True)
    online_web_link = fields.Char(string='Zoom Link', tracking=True)
    pre_booking = fields.Boolean(string='Pre-Booking', tracking=True)
    session_type = fields.Selection([('type_single', 'Single'),('type_package', 'Package')], string='Type Of Session',  default='type_single', required=True, tracking=True)
    unit_price = fields.Float(string='Actual Unit Price')
    amount_unit_price_tot = fields.Float(string='Actual Amount',compute='_amount_all_apt',store=True)
    amount_discount = fields.Float(string='Discounts',compute='_amount_all_apt',store=True)
    amount_promo = fields.Float(string='Promo Discounts',compute='_amount_all_apt',store=True)
    amount_recharge_coupon = fields.Float(string='Recharge Coupon Discounts',compute='_amount_all_apt',store=True)
    amount_untaxed = fields.Float(string='Sub Total',compute='_amount_all_apt',store=True)
    amount_tax = fields.Float(string='Taxes',compute='_amount_all_apt',store=True)
    amount_total = fields.Float(string='Total',compute='_amount_all_apt',store=True)
    amount_due = fields.Monetary(currency_field='currency_id',string='Total Due')
    customer_feedback = fields.Text(string='Feedback')
    customer_prescription = fields.Text(string='Prescription/ Notes about Patient')
    payment_status = fields.Char(string='Payment status')
    use_promo_code = fields.Boolean(string='Use Promo Code',default=False)
    promo_code = fields.Char(string='Promo Code')
    s_service_categ_id=fields.Many2one('appointment.package', string='Package ')
    discount_on_other = fields.Float(string='Total Disc on others', copy=False)
    reschedule_flag = fields.Boolean(string='Reschedule Flag', default=False)
    appointment_line_id=fields.One2many('appointment.line.id','appointment_id',string='Service Lines')
    appointment_resch_line=fields.One2many('appointment.resch.line','appointments_id',string='Reschedule History')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    pos_order_id = fields.Many2one('pos.order', string='POS Order')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    refund_id = fields.Many2one('account.move', string='Credit Note ')
    therapist_assistant_id = fields.Many2one('hr.employee', string='Instructor')
    start_time = fields.Float(string='Start Time ', copy=False)
    end_time = fields.Float(string='End Time ',store=True, copy=False)
    duration = fields.Float(string='Duration', copy=False)
    available_ids = fields.Many2many('availability.availability', string='Availability ')
    package_category = fields.Many2one('appointment.category',string="Service Category ")
    package_appointment_type = fields.Many2one('calendar.appointment.type',string="Appointment Type")
    cancel_count = fields.Integer('Cancel Count',compute='_compute_appointment_line_id_count')
    tag_by_healing_id = fields.Many2one('tag.by.healing', string='Tag By Healing')
    tag_by_sub_healing_id = fields.Many2one('tag.by.sub.healing', string='Tag By Sub Healing')
    tag_by_therapy_id = fields.Many2one('tag.by.therapy', string='Tag By Therapy')
    credit_note_id = fields.Many2one('account.move',string='Credit Note')
    cc_cancel_atv = fields.Boolean('CC_ACTIVE')
    cc_total_invoiced = fields.Float('Total Invoiced Amount')
    cc_confirmed = fields.Float('Confirmed Services ')
    cc_confirmed_items = fields.Float('Confirmed Services')
    cc_cancelled = fields.Float('Cancelled Services ')
    cc_cancelled_items = fields.Float('Cancelled Services')
    cc_cancellation_charge = fields.Float('Cancellation Charges ')
    cc_subtotal = fields.Float('Subtotal ')
    cc_refund = fields.Float('Refund')
    pos_order_id = fields.Many2one('pos.order',string='Order')
    pos_order_line_id = fields.Many2one('pos.order.line',string='Order Line')
    pos_atv = fields.Boolean('Pos Avt')
    pac_pos_order_id = fields.Many2one('pos.order',string='Pos Order ')
    pac_pos_order_line_id = fields.Many2one('pos.order.line',string='Package')
    pac_pos_atv = fields.Boolean(string='Pos Order')
    time_selection = fields.Char('Time Selection')
    therapist_id = fields.Many2one('hr.employee', string='Therapist', copy=False, tracking=True)##
    service_categ_id = fields.Many2one('appointment.category',string='Service Category',copy=False,tracking=True)##
    du_service_categ_id = fields.Many2one('appointment.category',string=' Service Category ',copy=False,tracking=True)##
    appointments_type_id = fields.Many2one('calendar.appointment.type',string='Sub Category',copy=False,tracking=True)##
    apt_room_id = fields.Many2one('roomtype.master', string='Room', copy=False, tracking=True)##
    time_id = fields.Many2one('time.time',string="Duration ", tracking=True)##
    start_time_str = fields.Selection(TIME,string='Start Time', copy=False)
    end_time_str = fields.Selection(TIME, string='End Time', copy=False)
    notes = fields.Text(string='Internal Notes',tracking=True)##
    quick_remarks = fields.Text(string='Quick Remarks Text')
    quick_remarks_id = fields.Many2one('appointment.quick.remark',string='Quick Remarks',tracking=True)
    cancel_notes = fields.Text(string='Cancellation Reason',tracking=True)##
    void_notes = fields.Text(string='Void Reason',tracking=True)##
    time_slot_id = fields.Many2one('time.slot', string='Time Slots',tracking=True)
    account_id = fields.Many2one('account.account', string='Account ID', copy=False)  ##
    package_discount = fields.Float('Discount ')
    refund_enable = fields.Boolean()
    single_discount = fields.Float(string='Discount')
    single_tax_ids = fields.Many2many('account.tax', 'apt_line_account_tax_single_tax_ids',string='Tax', copy=False)
    single_subtotal = fields.Float('Subtotal')
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    next_activity = fields.Char(default="Next Activity")
    show_history = fields.Boolean('Show History', default=True)
    apt_partner_history = fields.Many2many('appointment.appointment', 'appointment_appointment_apt_partner_history', 'apt_history_change', string='History ')
    apt_alter_dt = fields.Char(string='Modified on :', copy=False, tracking=True)
    pack_differ = fields.Char(compute="get_package", string="Unused Packages")
    amount_differ = fields.Char(compute="get_amt_differ", string="Availed Amount")
    booked_count = fields.Integer('Confirm Count', compute='get_confirm_count')
    package_count = fields.Integer('Packages Count', compute='get_count')
    amount_confirm = fields.Integer('Amount Confirm', compute='get_confirm_amount')
    date_day = fields.Char('Day',compute='_Compute_booking_date_date',store=True)
    cancellation_datetime = fields.Datetime()
    descriptions = fields.Char('Description',compute='get_description')
    created_by = fields.Char('Created By',compute='get_created_by_details')
    creation_date_time = fields.Char('Date Time', store=True, tracking=True)
    cancellation_type = fields.Selection([('early','Early'),('late','Late')],string='Method ')
    pre_cancellation_type = fields.Selection([('early', 'Early'), ('late', 'Late')], string='Method')
    check_package = fields.Boolean('Check Package')
    available_dates = fields.Many2one('date.date', string='Appointment Date')
    available_dates_list = fields.Char('Date List')
    available_booking_date = fields.Char('Appointment Date ')
    session_remaining = fields.Char('Session Remaining', compute='_compute_session_remaining_sence')
    apt_sale_amount = fields.Float('')
    extras_partner_id = fields.Many2one('res.partner',string='Customer')
    website_payment_statuss = fields.Boolean('Website Payment Status')
    website_payment_status_char = fields.Char('Payment received via CCAvenue', default="Payment received via CCAvenue")
    website_payment_status = fields.Selection([('no_paid','Not Paid'),('partially_paid','Partially Paid'),('payment_received','Paid'),('paid','Paid')],default='no_paid')

    # value has been empty

    @api.onchange('appointments_type_id')
    def value_changes_toempty(self):
        if self.partner_inv == False:
            self.time_id = False
            self.time_slot_id = False
            self.apt_room_id = False

    # set sub category value empty based on category selection 29-06-22
    @api.onchange('du_service_categ_id')
    def set_subcateg_empty(self):
        if self.partner_inv == False:
            self.appointments_type_id = False
    
    # change the time id fild empty while change the change time 23-06-22
    @api.onchange('change_time')
    def set_value_empty(self):
        if self.partner_inv == False:
            self.time_id = False
            self.apt_room_id = False
            self.time_slot_id = False

    # if change booking date and pre booking reset all the values 01-07-22

    @api.onchange('booking_date','pre_booking')
    def all_value_reset(self):
        if self.partner_inv == False:
            # self.therapist_id = False
            # self.du_service_categ_id = False
            # self.appointments_type_id = False
            # self.time_id = False
            self.time_slot_id = False
            self.apt_room_id = False
            self.appointment_type = False
        # used for visible the prebooking appointment 26-07-22
        if self.pre_booking:
            self.is_prebook = True


    # Invisible the appointment date based on below field 26-07-22
    @api.onchange('pre_booking')
    def apt_inv_appointment(self):
        if self.pre_booking == False and self.is_prebook and self.change_time == True:
            self.apt_date = True

    @api.depends('state')
    def _compute_session_remaining_sence(self):
        for rec in self:
            if rec.session_type == 'type_single':
                if rec.state == 'new':
                    rec.session_remaining = '1/1'
                else:
                    rec.session_remaining = '1/0'
            elif rec.session_type == 'type_package':
                pac_count = 0; remain = 0
                for i in rec.appointment_line_id:
                    pac_count += 1
                    if i.state_line == 'draft':
                        remain += 1
                rec.session_remaining = str(pac_count) +'/'+ str(remain)
            else:
                rec.session_remaining = '1/1'

    @api.depends('du_service_categ_id', 'appointments_type_id')
    def get_description(self):
        for res in self:
            if res.du_service_categ_id:
                res.descriptions = str(res.du_service_categ_id.name) + " / " + str(res.appointments_type_id.name)
            else:
                res.descriptions = ''

    @api.depends('booked_by', 'creation_date_time')
    def get_created_by_details(self):
        for res in self:
            if res.booked_by:
                res.created_by = str(res.booked_by.name) + " on " + str(res.creation_date_time)
            else:
                res.created_by = ''
    # Task
    @api.depends('appointment_line_id')
    def get_confirm_count(self):
        for record in self:
            rec = self.env['appointment.line.id'].search(
                [('state_line', '=', 'draft'), ('appointment_id', '=', record.id)])
            count = len(rec)
            record.booked_count = count

    # Task
    @api.depends('appointment_line_id')
    def get_count(self):
        for record in self:
            rec = self.env['appointment.line.id'].search([('appointment_id', '=', record.id)])
            count = len(rec)
            record.package_count = count

    # Task
    @api.depends('package_count', 'booked_count')
    def get_package(self):
        for packs in self:
            pack_total = packs.package_count or ''
            pack_booked = packs.booked_count or ''
            if packs.session_type == 'type_package':
                if pack_booked:
                    packs.pack_differ = str(pack_booked) + "/" + str(pack_total)
                else:
                    packs.pack_differ = "0/" + str(pack_total)
            else:
                packs.pack_differ = ''

    # Task
    @api.depends('appointment_line_id', 'amount_confirm', 'amount_total')
    def get_confirm_amount(self):
        for record in self:
            rec = self.env['appointment.line.id'].search(
                [('state_line', '=', 'confirm'), ('appointment_id', '=', record.id)])
            res = self.env['appointment.line.id'].search([('appointment_id', '=', record.id)])
            count = len(rec)
            total = len(res)
            amt = int(record.amount_total)
            if total == 0:
                record.amount_confirm = ''
            else:
                record.amount_confirm = (amt / total) * count

    # Task
    @api.depends('amount_total', 'amount_confirm')
    def get_amt_differ(self):
        for amt in self:
            amt_total = int(amt.amount_total) or '0'
            amt_due = amt.amount_confirm or '0'
            if amt.session_type == 'type_package':
                if amt_due:
                    amt.amount_differ = str(amt_due) + "/" + str(amt_total)
                else:
                    amt.amount_differ = "0/" + str(amt_total)
            else:
                amt.amount_differ = ''

    def _default_employee_type(self):
        emp_typ = self.env['hr.employee.category'].search([('name','=','Therapist')])
        return emp_typ

    # added pos state for free session payment 30-06-22
    @api.depends('apt_sale_amount','payment_status_apt','amount_due','total_advance_amount_paid','pos_order_id.amount_paid','pos_order_id.state','website_payment_status')
    def _compute_payment_from_payment(self):
        for rec in self:
            rec.apt_sale_amount = 0.0
            rec.payment_status_apt = 'no_paid'
            if rec.pos_order_id:
                if rec.is_package_claim != True:
                    if rec.pos_order_id.state == 'draft' and rec.pos_order_id.amount_paid == 0:
                        rec.payment_status_apt = 'no_paid'
                    elif rec.pos_order_id.amount_paid > 0 and rec.pos_order_id.amount_paid < rec.pos_order_id.amount_total:
                        rec.payment_status_apt = 'partially_paid'
                    elif rec.pos_order_id.state in ('paid','done','invoiced'):
                        rec.payment_status_apt = 'paid'
                    elif rec.pos_order_id.amount_paid == rec.pos_order_id.amount_total:
                        rec.payment_status_apt = 'paid'
                    else:
                        rec.payment_status_apt = 'no_paid'
            else:
                # rec.payment_status_apt = 'no_paid'
                if rec.website_payment_status == 'paid':
                    rec.payment_status_apt = 'paid'
                else:
                    rec.payment_status_apt = 'no_paid'
            if rec.is_package_claim == True:
                rec.payment_status_apt = rec.apt_package_parent_id.payment_status_apt
    employee_type_apointment = fields.Many2one('hr.employee.category',string='Employee Type', default=_default_employee_type)
    payment_status_apt = fields.Selection([('no_paid','Not Paid'),('partially_paid','Partially Paid'),('payment_received','Paid'),('paid','Paid')],compute='_compute_payment_from_payment',default='no_paid', store=True)

    @api.constrains('booking_date')
    def checking_booking_date(self):
        if self.booking_date:
            current_time = datetime.strftime(datetime.now(), "%d/%m/%Y %H:%M:%S")
            set_time = datetime.strftime(datetime.now(), "%d/%m/%Y 21:00:00")
            cur_dt = datetime.strftime(self.booking_date, "%d/%m/%Y %H:%M:%S")
            next_date = date.today() + timedelta(days = 1)
            if set_time < current_time:
                if self.booking_date == next_date:
                    raise UserError(_("You Can't able to Book Appointment for Tomorrow, After 9.00 PM"))

    @api.onchange('therapist_id')
    def _onchange_therapist_id_availability(self):
        if self.therapist_id:
            lstt = []; date_list = ''
            resp = {'domain': {'available_dates': "[('id', 'not in', False)]"}}

            avail_id = self.env['availability.availability'].search([('facilitator','=',self.therapist_id.id),\
                    ('date_range','=','ongoing'),('available_date','>', datetime.now().date().strftime("%Y-%m-%d"))])

            for i in avail_id:
                date_id = self.env['date.date'].search([('date','=',i.available_date.strftime("%Y-%m-%d"))],limit=1)
                if date_id:   
                    lstt.append(date_id.id)
                    date_list += date_id.date.strftime("%m/%d/%Y") +','
            date_list = date_list[:-1]
            self.available_dates_list = date_list
            resp['domain']['available_dates'] = "[('id', 'in', %s)]" % lstt
            return resp

    @api.onchange('available_booking_date','available_dates_list')
    def _onchange_available_dates_availability(self):
        if self.available_booking_date:
            self.booking_date = datetime.strptime(self.available_booking_date, "%m/%d/%Y")

    @api.onchange('type_partner')
    def _onchange_type_partner_domain_relese(self):
        if self.type_partner != 'type_existing':
            self.partner_id = False
            self.show_history = False
            lstt = []
            resp = {'domain': {'extras_partner_id': "[('id', 'not in', False)]"}}
            resp['domain']['extras_partner_id'] = "[('id', 'in', %s)]" % lstt
            return resp

    @api.onchange('extras_partner_id')
    def _onchange_extras_partner_id(self):
        if self.extras_partner_id:
            self.partner_id = self.extras_partner_id.id

    @api.onchange('partner_id')
    def _onchange_partner_id_balance(self):
        if self.partner_id:
            self.customer_balance = self.partner_id.customer_balance


    @api.onchange('s_service_categ_id')
    def _onchange_s_service_categ_id_opl(self): #due to domain not wrk dummy field have added
        if self.s_service_categ_id:
            self.package_discount = self.s_service_categ_id.discount

    @api.onchange('du_service_categ_id')
    def _onchange_du_service_categ_id_opl(self): #due to domain not wrk dummy field have added
        if self.du_service_categ_id:
            self.service_categ_id = self.du_service_categ_id.id

    @api.onchange('appointment_type','booking_mode')
    def _onchange_get_account(self):
        if self.appointment_type:
            revenue_id = self.env['appointment.revenue'].search([('account_id', '!=', False),
                ('type_appointment', '=', self.appointment_type),('booking_mode', '=', self.booking_mode)],limit=1)
            if revenue_id:
                self.account_id=revenue_id.account_id.id
            else:
                self.account_id =False

    @api.onchange('therapist_id')
    def onchange_therapist_change_opl(self):
        if 'except_false' not in self._context or self._context.get('except_false') != True:
            self.du_service_categ_id = self.service_categ_id = self.appointments_type_id = self.time_id = self.time_slot_id = False

    def save_redirect(self):
        if self.session_type == "type_package" and not self.appointment_line_id:
            raise UserError(_('Please Update the Package and Click Book'))
        menu_id = self.env.ref('ppts_custom_apt_mgmt.menu_ppts_Appointments').id
        if 'appointment_visit_wiz' in self._context and self._context.get('appointment_visit_wiz') == True:
            if self.package_line_id:
                self.package_line_id.with_context({'claim_operation': False}).action_claim_pack()
                return {'type': 'ir.actions.act_window_close'}
            else:
                if self.pos_order_id or self.booking_mode == "online" or self.payment_status_apt != "no_paid":
                    return {
                        "url": "/web?debug=0#&model=appointment.appointment&view_type=list&cids=&menu_id="+str(menu_id),
                        'target' : 'self',
                        "type": "ir.actions.act_url"
                    }
        else:
            # open the payment wizard if appointment is not paid 25-07-22
            if not self.pos_order_id :
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Pay Now'),
                    'res_model': 'apt.payment.confirmation',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_appointments_id': self.id
                    },
                }

    @api.onchange('session_type')
    def onchange_session_type_narcos(self):
        if self.session_type and 'default_is_package_claim' not in self._context and self._context.get('default_is_package_claim') != True:
            self.booking_date = self.therapist_id = self.du_service_categ_id = \
                self.service_categ_id = self.appointments_type_id = self.time_id = \
                    self.time_slot_id = self.apt_room_id = False
        if self.pre_booking ==True and self.session_type == "type_package":
            self.pre_booking =False
        
    @api.onchange('therapist_id','session_type','change_time')
    def _onchange_service_ids_domain_opl(self):
        lstt = []
        resp = {'domain': {'du_service_categ_id': "[('id', 'not in', False)]"}}
        if self.therapist_id and self.booking_date:
            availability = self.env['availability.availability'].search([\
                ('available_date','=',datetime.strftime(self.booking_date, "%Y-%m-%d")),
                ('facilitator','=',self.therapist_id.id),('date_range','=','ongoing'),('availability','=','available'),
                ], limit=1)
            
            for i in availability.service_categ_id:
                if i.id not in lstt:
                    lstt.append(i.id)

        # domain filter for package 28-06-22
        if self.therapist_id and self.session_type == 'type_package':
            for i in self.therapist_id.pay_rate_ids:
                if i.service_category_type_id:
                    lstt.append(i.service_category_type_id.id)
        if self.therapist_id and self.session_type == 'type_single' and self.pre_booking:
            for i in self.therapist_id.pay_rate_ids:
                if i.service_category_type_id:
                    lstt.append(i.service_category_type_id.id)


       

        resp['domain']['du_service_categ_id'] = "[('id', 'in', %s)]" % lstt
        return resp

    @api.onchange('therapist_id','service_categ_id','session_type','change_time')
    def _onchange_sub_service_ids_domain(self):
        lst = []
        res = {'domain': {'appointments_type_id': "[('id', 'not in', False)]"}}
        if self.therapist_id and self.service_categ_id and not self.pre_booking and self.session_type == 'type_single' and self.booking_date:
            if self.state=='new':
                self.change_time=True

            availability = self.env['availability.availability'].search([\
                ('available_date','=',datetime.strftime(self.booking_date, "%Y-%m-%d")),
                ('facilitator','=',self.therapist_id.id),('date_range','=','ongoing'),('availability','=','available'),
                ], limit=1)

            for i in availability.sub_categ_id:
                if i.id not in lst and self.service_categ_id.id == i.service_categ_id.id: 
                    lst.append(i.id)
        
        elif self.therapist_id and self.service_categ_id and self.pre_booking or self.session_type == 'type_package':
            for i in self.therapist_id.pay_rate_ids:
                if i.appoinment_type_id.id not in lst and self.service_categ_id == i.service_category_type_id: 
                    lst.append(i.appoinment_type_id.id)

        res['domain']['appointments_type_id'] = "[('id', 'in', %s)]" % lst
        return res

    @api.onchange('service_categ_id','therapist_id','appointments_type_id','session_type','change_time','change_time','change_time')
    def _onchange_time_id_setfl_domain(self):
        lst = []
        res = {'domain': {'time_id': "[('id', 'not in', False)]"}}
        if self.therapist_id and self.service_categ_id and self.appointments_type_id:
            for i in self.therapist_id.pay_rate_ids:
                if i.duration_id.id not in lst and self.service_categ_id == i.service_category_type_id and \
                                            self.appointments_type_id == i.appoinment_type_id: 
                    lst.append(i.duration_id.id)
        res['domain']['time_id'] = "[('id', 'in', %s)]" % lst
        return res
    # pass the current date to appoointment date field
    @api.onchange('session_type')
    def pass_date(self):
        self.booking_date =fields.Date.context_today(self)

   
    @api.onchange('therapist_id','booking_date','session_type','pre_booking','change_time')
    def _onchange_booking_date(self):
        lst = []
        # res = {'domain': {'therapist_id': "[('id', 'not in', False)]"}}
        if self.booking_date and self.session_type == 'type_single':
            cur_dt = datetime.strftime(self.booking_date, "%d/%m/%Y %H:%M:%S")
            cur_dt_now = datetime.strftime(datetime.now(), "%d/%m/%Y %H:%M:%S")
            pcur_dt = datetime.strptime(cur_dt, "%d/%m/%Y %H:%M:%S")
            pcur_dt_now = datetime.strptime(cur_dt_now, "%d/%m/%Y %H:%M:%S") + timedelta(days = 1)
            # booking date < current time
            ven_booking_date = self.booking_date
            # ven_current_date = datetime.strptime((datetime.strftime(datetime.now(), "%d/%m/%Y")), "%d/%m/%Y")
            timezone = pytz.timezone(self.env.user.tz or 'UTC')
            crnt_date = datetime.now().replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
            ven_current_date = crnt_date.strftime('%Y-%m-%d')
            

            _logger.info(ven_booking_date)
            _logger.info(ven_current_date)

            
            if self.booking_date:
                self.change_time = True

            if str(ven_booking_date) < ven_current_date:
                raise UserError('Appointments should be booked for Future Date..!')

            # changed to get the availability therapist 30-06-22
            availability = self.env['availability.availability'].search([('available_date','=',datetime.strftime(self.booking_date, "%Y-%m-%d")),('date_range','=','ongoing'),('state','=','availability_created')])
            for i in availability:

                if i.facilitator.id not in lst:

                    lst.append(i.facilitator.id)

        if self.session_type == 'type_package':
            categ_id = self.env['hr.employee.category'].search([('name', '=', 'Therapist')])
            emp_ids = self.env['hr.employee'].search([('employee_type', '=', categ_id.id),('location_ids','in',self.company_id.id)])
            for i in emp_ids:
                lst.append(i.id)
        if self.session_type == 'type_single' and self.pre_booking:
            categ_id = self.env['hr.employee.category'].search([('name', '=', 'Therapist')])
            emp_ids = self.env['hr.employee'].search([('employee_type', '=', categ_id.id),('location_ids','in',self.company_id.id)])
            for i in emp_ids:
                lst.append(i.id)

        # res['domain']['therapist_id'] = "[('id', 'in', %s)]" % lst

        return {'domain': {'therapist_id': [('id','in',lst)]}}


    
        # return res

# set domain changes in 13-06-22
    @api.onchange('change_time','time_slot_id','time_id')
    def _onchange_time_id_ero(self):
        # res = {'domain': {'time_slot_id': "[('id', 'not in', False)]"}}
        # res = []
        time_slot_ids = []
        if self.time_id:
            search_appointment = self.env['appointment.appointment'].sudo().search([
                ('booking_date','=',self.booking_date),('partner_id','=',self.partner_id.id)])

            if search_appointment:
                time_slot_ids = []
                for app in search_appointment:
                    time_slot_ids.append(app.time_slot_id.id)
        return {'domain': {'time_slot_id': [('id', 'in', time_slot_ids)]}}
                # res['domain']['time_slot_id'] = "[('id', 'not in', {})]".format(time_slot_ids)
        # return res

    @api.depends('booking_date')
    def _Compute_booking_date_date(self):
        for r in self:
            if r.booking_date:
                selected = fields.Datetime.from_string(r.booking_date)
                import calendar
                r.date_day = calendar.day_name[selected.weekday()]

    @api.onchange('time_slot_id','time_id','booking_date','change_time')
    def _onchange_time_slot_id(self):
        res = {'domain': {'apt_room_id': "[('id', 'not in', False)]"}}
        if self.time_id:
            time_val = str(timedelta(minutes=int(self.time_id.duration)))[:-3]
            time_val = time_val.replace(':', '.')
            # self.write({'duration': float(time_val)})

        if self.time_slot_id:
            self.start_time_str = self.time_slot_id.start_time
            self.end_time_str = self.time_slot_id.end_time

            start_time = datetime.strptime(str(self.time_slot_id.start_time), "%H:%M")
            start_time = start_time.strftime("%H.%M")
            self.start_time = float(start_time)
            self.end_time = abs(float(start_time) + self.duration)

            search_appointment = self.env['appointment.appointment'].sudo().search([('booking_date','=',self.booking_date),('time_slot_id','=',self.time_slot_id.id)])

            if search_appointment:
                room_ids = []
                for app in search_appointment:
                    room_ids.append(app.apt_room_id.id)
                res['domain']['apt_room_id'] = "[('id', 'not in', {})]".format(room_ids)
        
        return res

    def mass_move_to_pos(self):
        for od in self.ids:
            self.env['appointment.appointment'].browse(od).action_move_to_pos_bulk()
        return

    @api.onchange('pac_pos_order_line_id')
    def _onchange_pac_pos_order_line_id(self):
        if self.pac_pos_order_line_id:
            apt_package = self.env['appointment.package'].search([('product_id','=',self.pac_pos_order_line_id.product_id.id)])
            if apt_package:
                self.s_service_categ_id = apt_package.id

    @api.onchange('pac_pos_order_id')
    def _onchange_pac_pos_order_id(self):
        if self.pac_pos_order_id: self.pac_pos_atv = True; self.pos_order_id = self.pac_pos_order_id.id
        else: self.pac_pos_atv = False; self.s_service_categ_id = False; self.pac_pos_order_line_id = False; self.pos_order_id = False

    @api.depends('appointment_line_id')
    def _compute_appointment_line_id_count(self):
        self.cancel_count = 0
        for i in self.appointment_line_id:
            if i.state_line == 'cancel':
               self.cancel_count += 1

    @api.onchange('therapist_id','service_categ_id','appointments_type_id','time_id','time_slot_id','single_tax_ids','single_discount')
    def _onchange_amount_for_service(self):
        for rec in self:
            rec.unit_price = 0.0
            if rec.therapist_id and rec.service_categ_id and rec.appointments_type_id:
                for i in rec.therapist_id.pay_rate_ids:
                    if rec.service_categ_id == i.service_category_type_id and \
                                rec.appointments_type_id == i.appoinment_type_id and \
                                    rec.time_id == i.duration_id:
                        rec.unit_price = i.unit_price
                        discount_price = i.unit_price - (rec.unit_price*rec.single_discount)/100
                        taxed = 0.0
                        for tax in rec.single_tax_ids:
                            amount_taxed = self.env['account.tax'].search([('id', '=', tax._origin.id)]).amount
                            taxed = (discount_price*amount_taxed)/100
                        rec.single_subtotal = discount_price + taxed


    def coupon(self): 
        return {'type': 'ir.actions.act_window',
                'name': _('Coupon'),
                'res_model': 'apt.coupon',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_sale_id': self.sale_order_id.id},
                }

    def promotion(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Coupon'),
                'res_model': 'apt.promo',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_sale_id': self.sale_order_id.id},
                }

    def move_to_pos_client(self):
        payrate = self.env['hr.employee.payrate'].search([('service_category_type_id','=',self.service_categ_id.id),\
                    ('appoinment_type_id','=',self.appointments_type_id.id),('duration_id','=',self.time_id.id),\
                    ('employee_id','=',self.therapist_id.id)])
        
        def product_tax(product_id, amount):
            if product_id:
                total_included = 0
                for tax in product_id.taxes_id:
                    taxes = tax.compute_all(amount, self.currency_id, 1, product=product_id.id, partner=False)
                    t2 = taxes['total_included'] - amount
                    total_included += t2
                return total_included

        if self.pos_order_id:
            if self.env.user.has_group('ppts_custom_apt_mgmt.partner_pos_order_user'):
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Dashboard',
                    'view_mode': 'kanban,tree,form',
                    'res_model': 'pos.config',
                    'domain':"['|',('user_ids', 'in', uid),('user_ids','=',False)]"
                }
            else:
                # raise UserError(_('Pos order has been created/n ')%(self.pos_order_id.name))
                raise UserError(_("Pos order has been created. \n Sale ID - %s \n Pos ID - %s" % (self.sequence,self.pos_order_id.pos_reference)))

        else:
            lst = []
            if self.session_type == 'type_single':
                lst.append([0, 0, {
                            'full_product_name':self.appointments_type_id.product_id.name,
                            'product_id': self.appointments_type_id.product_id.id,
                            'qty': 1,
                            'price_subtotal': payrate.unit_price,
                            'price_subtotal_incl': payrate.unit_price + product_tax(self.appointments_type_id.product_id, payrate.unit_price),
                            'discount': 0,
                            'price_unit': payrate.unit_price,
                            'name': self.name,
                            'default_product': True,
                        }])
            elif self.session_type == 'type_package':
                for line in self.appointment_line_id:
                    lst.append([0, 0, {
                            'full_product_name':self.appointments_type_id.product_id.name,
                            'product_id': self.appointments_type_id.product_id.id,
                            'qty': 1,
                            'price_subtotal': payrate.unit_price,
                            'price_subtotal_incl': payrate.unit_price + product_tax(self.appointments_type_id.product_id, payrate.unit_price),
                            'discount': self.s_service_categ_id.discount,
                            'price_unit': payrate.unit_price,
                            'name': self.name,
                            'appt_line_id': line.id,
                            'default_product': True,
                        }])
            if self.topay_cancellation_charge > 0 and self.cancel_options == 'now':
                product_id = self.env['product.product'].search([('name','=','Cancellation Charges')],limit=1)
                lst.append([0, 0,{
                    'full_product_name': product_id.name,
                    'product_id': product_id.id,
                    'qty': 1,
                    'price_subtotal': self.topay_cancellation_charge,
                    'price_subtotal_incl': self.topay_cancellation_charge + product_tax(product_id, self.topay_cancellation_charge),
                    'discount': 0,
                    'price_unit': self.topay_cancellation_charge,
                    'name': self.note_cancellation_charge,
                    'default_product': True,
                }])
            if self.topay_no_show_charges > 0 and self.noshow_options == 'now':
                    product_id = self.env['product.product'].search([('name','=','No Show Charges')],limit=1)
                    lst.append([0, 0,{
                        'full_product_name': product_id.name,
                        'product_id': product_id.id,
                        'qty': 1,
                        'price_subtotal': self.topay_no_show_charges,
                        'price_subtotal_incl': self.topay_no_show_charges + product_tax(product_id, self.topay_no_show_charges),
                        'discount': self.single_discount,
                        'price_unit': self.topay_no_show_charges,
                        'name': self.note_no_show,
                        'default_product': True,
                    }])
            return {
                    'type': 'ir.actions.act_window',
                    'name': _('Pay Now'),
                    'res_model': 'apt.order.confirmation',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_appointments_id': self.id,
                        'default_partner_id': self.partner_id.id,
                        'default_lines': lst,
                    },
            }

    @api.depends('appointment_line_id.price_subtotal','time_id')
    def _amount_all_apt(self):
        for appointment in self:
            amount_untaxed = amount_tax = amount_discount = amount_promo=amount_rc_coupon =amount_unit_price_tot= 0.0
            if appointment.session_type == 'type_package':
                for i in appointment.appointment_line_id:
                    amount_untaxed += i.price_subtotal
                    amount_unit_price_tot += i.unit_price
                    amount_discount += i.amount_discount
                    amount_tax += i.tax_amount
            else:
                if appointment.time_id:
                    taxed = 0.0
                    payrate = self.env['hr.employee.payrate'].search(
                        [('service_category_type_id', '=', appointment.service_categ_id.id), \
                         ('appoinment_type_id', '=', appointment.appointments_type_id.id), ('duration_id', '=', appointment.time_id.id),
                         ('duration_id', '=', appointment.time_id.id), \
                         ('employee_id', '=', appointment.therapist_id.id)])

                    if appointment.appointments_type_id.product_id.taxes_id:
                        for tax in (appointment.appointments_type_id.product_id.taxes_id):
                            if tax.company_id.id== appointment.company_id.id:
                                amount_taxed = self.env['account.tax'].search([('id', '=', tax._origin.id)]).amount
                                taxed = (payrate.unit_price * amount_taxed) / 100

                    amount_untaxed = payrate.unit_price
                    amount_unit_price_tot = payrate.unit_price
                    amount_discount = 0.0
                    amount_tax = taxed
            appointment.update({
                    'amount_unit_price_tot': amount_unit_price_tot,
                    'amount_discount': amount_discount,
                    'amount_tax': amount_tax,
                    'amount_total': amount_untaxed + amount_tax,
                    'amount_due':amount_untaxed + amount_tax,
                })

    @api.onchange('partner_id','show_history','extras_partner_id')
    def _onchange_update_partner_history(self):
        if self.partner_id:
            partner_ids = self.env['appointment.appointment'].search([('partner_id','=',self.partner_id.id)])
            self.apt_partner_history = [(6, 0, partner_ids.ids)]
            cc_partner_ids = self.env['appointment.appointment'].search([('partner_id', '=', self.partner_id.id),('due_cancellation_charge', '>',0)])
            cc_due = nos_due = 0.0
            note=note_no_show='Info : '
            for partner in cc_partner_ids:
                cc_due += partner.due_cancellation_charge
                note+=("Booking Date : "+str(partner.creation_date)+" Appointment Date : "+str(partner.booking_date)+" Session : " + partner.session_type)
            self.topay_cancellation_charge = cc_due
            self.note_cancellation_charge = note
            nosh_partner_ids = self.env['appointment.appointment'].search(
                [('partner_id', '=', self.partner_id.id), ('no_show_charges', '>', 0)])
            for nos in nosh_partner_ids:
                nos_due += nos.no_show_charges
                note_no_show+=("Booking Date : "+str(nos.creation_date)+" Appointment Date : "+str(nos.booking_date)+" Session : " + nos.session_type)
            if nos_due > 0.0: self.pay_no_show = True
            self.topay_no_show_charges = nos_due
            self.note_no_show = note_no_show

    @api.onchange('partner_id')
    def _onchange_update_name(self):
        if self.partner_id:
            self.name = "Appointment for : " + self.partner_id.name
            self.reffer_type_id = self.partner_id.reffer_type_id.id

    @api.onchange('reffer_type_id')
    def _onchange_reffer_type_id(self):
        if self.reffer_type_id and self.partner_id:
            self.partner_id.reffer_type_id = self.reffer_type_id.id

    def action_two_step_void(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Void',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'apt.two.step.void',
            'context': {
                'default_appointments_id': self.id,
            },
        }

    def action_void(self):
        if self.session_type == 'type_single' and self.is_package_claim == False:
            if self.payment_status_apt == 'no_paid':
                self.state = 'void'

            elif self.payment_status_apt in ('payment_received','paid'):
                self.state = 'void'
                if self.pos_order_id:
                    move_id = self.env['account.move'].search([('payment_reference','=',self.pos_order_id.name)],limit=1)
                    wiz_id = self.env['account.move.reversal'].sudo().create({"move_ids": [(4, move_id.id)]})
                    wiz_id.with_context(active_ids=move_id.id).sudo().reverse_moves()
                    wiz_id.new_move_ids.action_post()

        elif self.session_type == 'type_single' and self.is_package_claim == True:
            self.state = 'void'
            self.package_line_id.state_line = 'draft'
            self.apt_package_parent_id.state = 'confirm'
            self.package_line_id.single_session_id = False

        elif self.session_type == 'type_package':
            line_id = self.env['appointment.line.id'].search([('appointment_id','=',self.id),('state_line','!=','draft')])
            def_lo_line = self.env['appointment.line.id'].search([('appointment_id','=',self.id)])
            if self.payment_status_apt == 'no_paid':
                if not line_id:
                    self.state = 'void'
                    for k in def_lo_line:
                        k.unlink()
                else:
                    raise UserError("If the session is used in the package, void cannot be used")
            elif self.payment_status_apt in ('payment_received','paid'):
                if not line_id:
                    self.state = 'void'
                    for k in def_lo_line:
                        k.unlink()
                    if self.pos_order_id:
                        move_id = self.env['account.move'].search([('payment_reference','=',self.pos_order_id.name)],limit=1)
                        wiz_id = self.env['account.move.reversal'].sudo().create({"move_ids": [(4, move_id.id)]})
                        wiz_id.with_context(active_ids=move_id.id).sudo().reverse_moves()
                        wiz_id.new_move_ids.action_post()
                else:
                    raise UserError("If the session is used in the package, void cannot be used")        
        else:
            _logger.info('Void Nothing')

    def action_confirm(self):
        for rec in self:
            rec.write({'state': 'confirm', 'color': 5})
            if rec.session_type=='type_single':
                for res in self.apt_partner_historys:
                    if res.state_line == 'confirm':
                        is_claim=True
                        self.write({'package_line_id': res.id, 'parent_id': res.appointment_id.id})
                        self.package_line_id.write({'time_id': False})
                        self.package_line_id.write({'apt_room_id': self.apt_room_id,
                                                    'booking_start_date': self.booking_date,
                                                    'time_id': self.time_id.id,
                                                    'time_slot_id': self.time_slot_id.id,
                                                    'duration': self.duration,
                                                    'start_time_str': self.start_time_str,
                                                    'end_time_str': self.end_time_str,
                                                    'start_time': self.start_time,
                                                    'end_time': self.end_time,
                                                    })
                        self.package_line_id.confirm_package()
                        rec.is_package_claim=True
                        self._compute_payment_from_payment()
        product_id = self.env['product.template'].search([('name', '=', 'Cancellation Charges')], limit=1)
        account = self.env['account.account'].search([('name', '=', 'Cancellation Charges'),
                                                      ('company_id', '=', self.company_id.id)],
                                                     limit=1)
        if not product_id:
            self.create_new_product_cancel()
        if not account:
            self.create_new_account_cancel()
        ns_account = self.env['account.account'].search([('name', '=', 'No Show Charges'), ('company_id', '=', self.company_id.id)], limit=1)
        ns_product_id = self.env['product.product'].search([('name', '=', 'No Show Charges')], limit=1)
        if not ns_product_id:
            self.create_new_product_noshow()
        if not ns_account:
            self.create_new_account_noshow()
        ad_account = self.env['account.account'].search([('name', '=', 'Adjustment on Existing Balance'),('company_id', '=', self.company_id.id)], limit=1)
        ad_product_id = self.env['product.product'].search([('name', '=', 'Adjustment on Existing Balance')], limit=1)
        if not ad_product_id:
            self.create_new_product_adjust()
        if not ad_account:
            self.create_new_account_adjust()
        if self.session_type == 'type_single':
            if not self.booking_date or not self.therapist_id or not self.du_service_categ_id or not \
                self.service_categ_id or not self.appointments_type_id or not self.time_id or not \
                    self.time_slot_id or not self.apt_room_id:
                raise UserError("Please Fill the mandatory before confirm")

    def action_move_to_pos(self, line_ids=False, cheque=False, payment_method_id=False,shipping_handling_overall=0):
        for rec in self:

            def create_order():
                pos_lines = []
                promotion_rec = []
                coupon_rec = []
                if line_ids:
                    for p_order in line_ids:
                        l_id = self.env['appointment.order.retail.product'].browse(p_order)
                        if l_id.apt_order_confirmation_id.apt_promotion:
                            promotion_rec = l_id.apt_order_confirmation_id._create_new_no_code_promo_reward_lines()
                        if l_id.apt_order_confirmation_id.apt_coupon_code:
                            coupon_rec = l_id.apt_order_confirmation_id.apply_coupon(l_id.apt_order_confirmation_id, l_id.apt_order_confirmation_id.apt_coupon_code)                        
                        pos_lines.append([0, 0, {
                            'apt_service_category': rec.service_categ_id.id,
                            'full_product_name': l_id.product_id.name,
                            'product_id': l_id.product_id.id,
                            'qty': l_id.qty ,
                            'price_subtotal': l_id.price_subtotal,
                            'price_subtotal_incl':l_id.price_subtotal_incl,
                            'commission_recipient':l_id.commission_recipient,
                            'order_id': rec.pos_order_id.id,
                            'discount': l_id.discount if l_id.discount_type == 'percentage' else 0.0,
                            # 'absolute_discount': l_id.discount or 0.0,
                            'tax_ids': l_id.tax_ids.ids,
                            'tax_ids_after_fiscal_position': l_id.tax_ids.ids,
                            'price_unit': l_id.price_unit,
                            'name': l_id.product_id.name,
                            'appt_line_id': l_id.appt_line_id.id,
                        }])
                    if promotion_rec:
                        promotion_data = [dict([key, str(value)]
                               for key, value in dicts.items())
                               for dicts in promotion_rec]
                        promotion_datas = promotion_data[0]
                        del promotion_datas['is_reward_line']
                        promotion_datas['full_product_name'] = promotion_datas.pop('name')
                        promotion_datas['tax_ids_after_fiscal_position'] = promotion_datas.pop('tax_ids')
                        promotion_datas['product_id'] = int(promotion_datas['product_id'])
                        promotion_datas['price_subtotal'] = promotion_datas['price_unit']
                        promotion_datas['price_subtotal_incl'] = promotion_datas['price_unit']
                        pos_lines.append([0, 0, promotion_datas])                    
                    if coupon_rec:
                        if type(coupon_rec) == dict:
                            if coupon_rec['not_found']:
                                raise UserError(_('%s ') % (coupon_rec['not_found']))
                        else:
                            pass
                        coupon_data = [dict([key, str(value)]
                               for key, value in dicts.items())
                               for dicts in coupon_rec]                        
                        coupon_datas = coupon_data[0]
                        del coupon_datas['is_reward_line']
                        coupon_datas['full_product_name'] = coupon_datas.pop('name')
                        coupon_datas['tax_ids_after_fiscal_position'] = coupon_datas.pop('tax_ids')
                        coupon_datas['product_id'] = int(coupon_datas['product_id'])
                        coupon_datas['price_subtotal'] = coupon_datas['price_unit']
                        coupon_datas['price_subtotal_incl'] = coupon_datas['price_unit']
                        pos_lines.append([0, 0, coupon_datas])
                    if shipping_handling_overall > 0:
                        get_prod = self.env['product.product'].search([('shipping_handling_charge','=',True)],limit=1)
                        values = ([0, 0, {
                        'full_product_name': get_prod.name,
                        'product_id': get_prod.id,
                        'qty': 1,
                        'price_subtotal': shipping_handling_overall,
                        'price_subtotal_incl':shipping_handling_overall,
                        'order_id': rec.pos_order_id.id,
                        'discount': 0.00,
                        'absolute_discount': 0.00,
                        'amount_discount':0.00,
                        'tax_ids_after_fiscal_position': False,
                        'price_unit': shipping_handling_overall,
                        'name': get_prod.name,
                        }])
                        pos_lines.append(values)
                sale_id = self.env['pos.order'].create({
                    'partner_id': rec.partner_id.id,
                    'pricelist_id': 1,
                    'appt_sale_id': rec.id,
                    'session_id': pos_session_id.id,
                    'session_type': rec.session_type,
                    'amount_tax': 0.0,
                    'amount_paid': 0.0,
                    'amount_return': 0.0,
                    'amount_total': 0.0,
                    'state': 'draft',
                    'booking_type': 'appointment',
                    'sale_type_for': 'appointment',
                    'apt_booking_date': rec.booking_date,
                    'apt_booked_by': rec.booked_by.id,
                    'company_id': rec.company_id.id,
                    'name': rec.sequence,
                    'pos_reference': pos_seq,
                    'cheque':cheque,
                    'payment_method_id': payment_method_id,
                    'lines': pos_lines,
                })
                rec.pos_order_id = sale_id.id
            pos_session_id = self.env['pos.session'].search([('state', '=', 'opened')], limit=1)
            if not pos_session_id:
                raise UserError(_("Please create a POS session to create POS order and confirm the Appointment"))           
            seq = self.env['ir.sequence'].search([('name','=','POS APT'),('code','=','POS APT')])
            if seq:
                pos_seq = seq.next_by_id()
            else:
                seq =  self.env['ir.sequence'].create({'name': 'POS APT','code':'POS APT','active':True,'implementation':'no_gap','prefix':'POS/APT','padding':5,'number_increment':1,'number_next_actual':1})
                pos_seq = seq.next_by_id()
            if self.cancel_options == 'ignore':
                rec.reset_cancel_charges()
            if rec.crm_id:
                if rec.crm_id.stage_id.create_contact and rec.crm_id.stage_id.is_register:
                    rec.crm_id.free_register = True
                if rec.crm_id.stage_id.is_register and not rec.crm_id.stage_id.create_contact:
                    rec.crm_id.paid_register = True
                if rec.crm_id.stage_status:
                    rec.crm_id.stage_status = False
            if rec.session_type == 'type_single' and not rec.is_package_claim:
                # if not self.booking_date or not self.time_slot_id:
                #     raise UserError("Date or Time slot not assigned in the appointment!!")
                if rec.pos_order_id:
                    rec.pos_order_id.sudo().write({
                        'partner_id': rec.partner_id.id,
                        'pricelist_id': 1,
                        'appt_sale_id': rec.id,
                        'partner_invoice_id': rec.partner_id.id,
                        'partner_shipping_id': rec.partner_id.id,
                        'session_type': rec.session_type,
                    })
                else:
                    if pos_session_id:
                        create_order()
                    else:
                        raise UserError(
                            _("Please create a POS session to create POS order and confirm the Appointment"))
                self.appointment_remainder_before_du()
                reven_id = self.env['appointment.revenue'].search([('booking_mode','=',self.booking_mode),('type_appointment','=',self.appointment_type),('company_id','=',self.company_id.id)],limit=1)
                payrate = self.env['hr.employee.payrate'].search([('service_category_type_id','=',self.service_categ_id.id),\
                    ('appoinment_type_id','=',self.appointments_type_id.id),('duration_id','=',self.time_id.id),\
                    ('employee_id','=',self.therapist_id.id)])
                if not self.appointments_type_id.product_id.available_in_pos:
                    self.appointments_type_id.product_id.available_in_pos = True
                if self.due_adjustment:
                    product_id = self.env['product.product'].search([('name','=','Adjustment on Existing Balance')],limit=1)
                    adjust_line = self.env['pos.order.line'].sudo().create({
                        'apt_service_category': self.service_categ_id.id,
                        'full_product_name': product_id.name,
                        'product_id': product_id.id,
                        'qty': 1,
                        'price_subtotal': rec.due_adjustment*(-1),
                        'price_subtotal_incl': rec.due_adjustment*(-1),
                        'order_id': rec.pos_order_id.id,
                        'discount': False,
                        'tax_ids_after_fiscal_position': rec.single_tax_ids,
                        'price_unit': rec.due_adjustment,
                        'name':'Adjustment on Existing Balance' ,
                    })
                if rec.sale_order_id:
                    wiz_id = self.env['sale.advance.payment.inv'].sudo().create({"advance_payment_method": "delivered"})
                    invoice_id = wiz_id.with_context(active_ids=rec.sale_order_id.id).sudo().create_invoices()
                    rec.invoice_id = rec.sale_order_id.order_line[0].invoice_lines[0].move_id.id
                    rec.invoice_id.appointment_ref_id = rec.id
                    inv_lines=self.env['account.move.line'].sudo().search([
                        ("move_id", "=", rec.invoice_id.id),("name", "=", rec.appointments_type_id.name)])
                    for i in inv_lines:
                        i.write({'account_id': reven_id.account_id.id})
            
            # Package 
            else:
                if rec.sale_order_id:
                    rec.sale_order_id.sudo().write({
                        'partner_id': rec.partner_id.id,
                        'pricelist_id': 1,
                        'appt_sale_id': rec.id,
                        'session_type': rec.session_type,
                    })
                else:
                    if pos_session_id:
                        create_order()
                    else:
                        raise UserError(
                            _("Please create a POS session to create POS order and confirm the Appointment"))

                if not self.appointments_type_id.product_id.available_in_pos:
                    self.appointments_type_id.product_id.available_in_pos = True

                # for line in self.appointment_line_id:
                #     order_line = self.env['pos.order.line'].sudo().create({
                #         'product_id': self.appointments_type_id.product_id.id,
                #         'qty': 1,
                #         'order_id': sale_id.id,
                #         'discount': line.discount,
                #         'tax_ids_after_fiscal_position': line.package_tax_ids,
                #         'price_unit': line.unit_price,
                #         'appt_sale_id': self.id,
                #         'appt_line_id': line.id,
                #         'apt_service_category': line.service_categ_id.id,
                #         'full_product_name': self.appointments_type_id.product_id.name,
                #         'price_subtotal_incl': line.price_subtotal,
                #         'price_subtotal': line.price_subtotal,
                #         'name': rec.name,
                #     })

                # if self.cancel_charge_applied:

                #     product_id = self.env['product.product'].search([('name', '=', 'Cancellation Charges')], limit=1)

                #     cc_line = self.env['pos.order.line'].sudo().create({
                #         'apt_service_category': self.service_categ_id.id,
                #         'full_product_name': product_id.name,
                #         'product_id': product_id.id,
                #         'qty': 1,
                #         'price_subtotal': rec.topay_cancellation_charge,
                #         'price_subtotal_incl': rec.topay_cancellation_charge,
                #         'order_id': rec.pos_order_id.id,
                #         'discount': rec.single_discount,
                #         'tax_ids_after_fiscal_position': rec.single_tax_ids,
                #         'price_unit': rec.topay_cancellation_charge,
                #         'name': rec.note_cancellation_charge,
                #     })

                #     if cc_line:
                #         rec.due_cancellation_charge = 0.0
                #         rec.topay_cancellation_charge = 0.0
                #         rec.cancel_options = 'now'

                #         cc_partner_ids = self.env['appointment.appointment'].search(
                #             [('partner_id', '=', self.partner_id.id), ('due_cancellation_charge', '>', 0)])

                #         for cp in cc_partner_ids:
                #             cp.due_cancellation_charge = 0.0

                # if self.pay_no_show:

                #     product_id = self.env['product.product'].search([('name','=','No Show Charges')],limit=1)

                #     nos_line = self.env['pos.order.line'].sudo().create({
                #         'apt_service_category': self.service_categ_id.id,
                #         'full_product_name': product_id.name,
                #         'product_id': product_id.id,
                #         'qty': 1,
                #         'price_subtotal': rec.topay_no_show_charges,
                #         'price_subtotal_incl': rec.topay_no_show_charges,
                #         'order_id': rec.pos_order_id.id,
                #         'discount': rec.single_discount,
                #         'tax_ids_after_fiscal_position': rec.single_tax_ids,
                #         'price_unit': rec.topay_no_show_charges,
                #         'name': rec.note_no_show,
                #     })

                #     if nos_line:
                #         rec.no_show_charges=0.0
                #         rec.topay_no_show_charges=0.0
                #         rec.pay_no_show=False

                #         cc_partner_ids = self.env['appointment.appointment'].search(
                #             [('partner_id', '=', self.partner_id.id), ('no_show_charges', '>', 0)])

                #         for cp in cc_partner_ids:
                #             cp.no_show_charges=0.0

                if self.due_adjustment:
                    product_id = self.env['product.product'].search([('name','=','Adjustment on Existing Balance')],limit=1)

                    adjust_line = self.env['pos.order.line'].sudo().create({
                        'apt_service_category': self.service_categ_id.id,
                        'full_product_name': product_id.name,
                        'product_id': product_id.id,
                        'qty': 1,
                        'price_subtotal': rec.due_adjustment*(-1),
                        'price_subtotal_incl': rec.due_adjustment*(-1),
                        'order_id': rec.pos_order_id.id,
                        'discount': False,
                        'tax_ids_after_fiscal_position': rec.single_tax_ids,
                        'price_unit': rec.due_adjustment,
                        'name':'Adjustment on Existing Balance' ,
                    })

            if self.topay_cancellation_charge > 0 and self.cancel_options == 'now' or self.cancel_options == 'ignore':
                self.due_cancellation_charge=0.0
                self.topay_cancellation_charge=0.0
                self.cancel_options='now'

                cc_partner_ids = self.env['appointment.appointment'].search(
                    [('partner_id', '=', self.partner_id.id), ('due_cancellation_charge', '>', 0)])

                for cp in cc_partner_ids:
                    cp.due_cancellation_charge=0.0
            
            if self.topay_no_show_charges > 0 and self.noshow_options == 'now' or self.noshow_options == 'ignore':
                self.no_show_charges=0.0
                self.topay_no_show_charges=0.0
                self.pay_no_show=False

                cc_partner_ids = self.env['appointment.appointment'].search(
                    [('partner_id', '=', self.partner_id.id), ('no_show_charges', '>', 0)])

                for cp in cc_partner_ids:
                    cp.no_show_charges=0.0

            rec.pos_order_id._onchange_amount_all()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Dashboard',
                'view_mode': 'kanban,tree,form',
                'res_model': 'pos.config',
                'domain':"['|',('user_ids', 'in', uid),('user_ids','=',False)]"
            }
    

    def action_arrived(self):
        for rec in self:
            rec.write({'state': 'arrive','color': 6})

            if rec.session_type=='type_single':
                for line in rec.appointment_line_id:
                    line.arrived_date=datetime.today()

    def reset_cancel_charges(self):
        cc_partner_ids = self.env['appointment.appointment'].search(
            [('partner_id', '=', self.partner_id.id), ('due_cancellation_charge', '>', 0)])

        # if self.cancel_options == 'ignore':
        for cc in cc_partner_ids:
            cc.due_cancellation_charge=0.0

    def action_done(self):
        for rec in self:
            if rec.session_type=='type_single' and rec.payment_status_apt == 'paid':
                rec.write({'state': 'done', 'color': 9})
            else:
                for k in self.appointment_line_id:
                    if k.state_line == 'draft': 
                        raise UserError(_("Package session not used Fully. Please perform Partial Cancel Process to Move next Stage."))
                    else:
                        self.write({'state':'done'})

            # if rec.pos_order_id.amount_paid:
            #     rec.payment_status_apt = 'paid'

            if rec.payment_status_apt == 'no_paid':
                return {'type': 'ir.actions.act_window',
                        'name': _('Payment'),
                        'res_model': 'apt.complete',
                        'target': 'new',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'context': {'default_appointments_id': self.id},
                        }
            else:
                rec.write({'state': 'done', 'color': 9})

        return True

    def create_invoice(self):
        if self.session_type=='type_package':
            for k in self.appointment_line_id:
                if k.state_line == 'draft': 
                    raise UserError(_("Package session not used Fully. Please perform Partial Cancel Process to Move next Stage."))
            
            if not self.invoice_id:    
                invoice_confirm=self.sale_order_id.sudo().action_confirm()
                wiz_id = self.env['sale.advance.payment.inv'].sudo().create({"advance_payment_method": "delivered"})
                invoice_id=wiz_id.with_context(active_ids=self.sale_order_id.id).sudo().create_invoices()
                if invoice_id :
                    reven_id = self.env['appointment.revenue'].search([('booking_mode','=',self.booking_mode),
                                                                       ('type_appointment','=',self.appointment_type)],limit=1)

                    self.invoice_id = self.sale_order_id.order_line[0].invoice_lines[0].move_id.id
                    self.invoice_id.appointment_ref_id = self.id


                    for line in self.appointment_line_id:
                        
                        inv_lines=self.env['account.move.line'].sudo().search([
                            ("move_id", "=", self.invoice_id.id),("name", "=", line.appointments_type_id.name)])
                        if inv_lines:
                            inv_lines.write({'account_id': reven_id.account_id.id})

    
    def action_two_step_cancel(self):
        self.action_cancel()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cancellation Options',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'apt.two.step.cancel',
            'context': {
                'default_appointments_id': self.id,
                'default_cancellation_type': self.pre_cancellation_type,
            },
        }

    def action_cancel_and_refund(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'name': _('Payment'),
            'res_model': 'account.payment',
            'target': 'new',
            'views': [(False, "form")],
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_payment_type': 'outbound',
                'default_appointments_id': self.id,
                'default_amount': self.pos_order_id.amount_paid,
            },
        }

    def action_cancel(self):
        self.ensure_one()
        if self.session_type == 'type_single':
            app_time = self.booking_date.strftime("%d/%m/%Y")
            app_time = datetime.strptime(app_time+' '+ self.time_slot_id.start_time+':00', "%d/%m/%Y %H:%M:%S")
            now = datetime.now()
            if self.env.user.tz == 'Asia/Calcutta': now = datetime.now() + timedelta(hours=5,minutes=30)
            elif self.env.user.tz == 'Asia/Dubai': now = datetime.now() + timedelta(hours=4)

            if self.appointments_type_id.cancel_interval_range == 'hour':
                cancel_date = app_time - timedelta(hours = self.appointments_type_id.cancel_interval_number)
                if now > cancel_date:
                    self.cc_cancellation_charge = abs(self.appointments_type_id.cancel_interval_price)
                    self.pre_cancellation_type = 'late'
                elif now < cancel_date:
                    self.pre_cancellation_type = 'early'

            elif self.appointments_type_id.cancel_interval_range == 'day':
                cancel_date = app_time - timedelta(days = self.appointments_type_id.cancel_interval_number)
                if now > cancel_date:
                    self.cc_cancellation_charge = abs(self.appointments_type_id.cancel_interval_price)
                    self.pre_cancellation_type = 'late'
                else:
                    self.pre_cancellation_type = 'early'
            else:
                print('null')

        if self.session_type == 'type_package':
            if self.pac_pos_order_id: 
                self.invoice_id = self.pac_pos_order_id.session_move_id.id
            # else:
            #     if not self.invoice_id: self.create_invoice()

            self.cc_total_invoiced = 0.0
            self.cc_confirmed = 0.0
            self.cc_cancelled = 0.0
            self.cc_cancellation_charge = 0.0
            self.cc_subtotal = 0.0
            self.cc_refund = 0.0
            self.cc_confirmed_items = 0.0
            self.cc_cancelled_items = 0.0
            for i in self.appointment_line_id:
                if i.avail_id: i.avail_id.sudo().unlink()

            # product_id = self.env['product.template'].search([('name','=','Cancellation Charges')],limit=1)
            # sale_id = self.env['sale.order.line'].search([('product_id','=',product_id.id),('order_id','=',self.sale_order_id.id)],limit=1)
            product_id = self.env['account.account'].search([('name', '=', 'Cancellation Charges'), ('company_id', '=', self.company_id.id)], limit=1)

            count = 0;total = 0;charge_percentage = 0.0;sale_total = 0.0;charge_amt = 0.0;cost_cancel = 0.0
            cost_confirm=0.0

            lst_id = []
            conf_lst_id = []
            for i in self.appointment_line_id:
                if not i.state_line == 'confirm':
                    cost_cancel += i.price_subtotal
                    lst_id.append(i.id)
                    count += 1
                elif i.state_line == 'confirm':
                    cost_confirm += i.price_subtotal
                    conf_lst_id.append(i.id)
                total += 1

            set_org_price = False

            for i in self.s_service_categ_id.package_cancel_charge_ids:
                if i.domain == 'equal':
                    if count == i.package_of_cancel and total == i.package_of_total:
                        charge_percentage = i.original_rate
                        if i.original_rate_charge == True: set_org_price = True
                        else: set_org_price = False

                elif i.domain == 'is_not_equal':
                    if count != i.package_of_cancel and total == i.package_of_total:
                        charge_percentage = i.original_rate
                        if i.original_rate_charge == True: set_org_price = True
                        else: set_org_price = False

                elif i.domain == 'greater_than':
                    if count > i.package_of_cancel and total == i.package_of_total:
                        charge_percentage = i.original_rate
                        if i.original_rate_charge == True: set_org_price = True
                        else: set_org_price = False

                elif i.domain == 'less_than':
                    if count < i.package_of_cancel and total == i.package_of_total:
                        charge_percentage = i.original_rate
                        if i.original_rate_charge == True: set_org_price = True
                        else: set_org_price = False

                elif i.domain == 'greater_than_equal':
                    if count >= i.package_of_cancel and total == i.package_of_total:
                        charge_percentage = i.original_rate
                        if i.original_rate_charge == True: set_org_price = True
                        else: set_org_price = False

                elif i.domain == 'less_than_equal':
                    if count <= i.package_of_cancel and total == i.package_of_total:
                        charge_percentage = i.original_rate
                        if i.original_rate_charge == True: set_org_price = True
                        else: set_org_price = False

                else: charge_percentage = 0.0; set_org_price = False

            if product_id:
                for k in conf_lst_id:
                    apl_id = self.env['appointment.line.id'].browse(k)
                    if charge_percentage:
                        apl_id.cancel_charge = apl_id.unit_price * charge_percentage / 100
                    else:
                        apl_id.cancel_charge = apl_id.unit_price-apl_id.price_subtotal

                self.cc_cancel_atv = True
                if set_org_price == True:
                    set_cancel_op = 0.0
                    for jj in self.appointment_line_id:
                        self.cc_total_invoiced += jj.price_subtotal
                        if jj.state_line == 'confirm':
                            self.cc_confirmed += jj.unit_price
                            set_cancel_op += jj.cancel_charge#price_subtotal
                            self.cc_confirmed_items += 1
                        if not jj.state_line == 'confirm':
                            self.cc_cancelled += jj.unit_price
                            self.cc_cancelled_items += 1

                    self.cc_cancellation_charge = set_cancel_op
                    self.cc_refund = self.cc_total_invoiced - self.cc_confirmed

                else:
                    for jj in self.appointment_line_id:
                        if jj.state_line == 'confirm':
                            self.cc_confirmed += jj.price_subtotal
                            self.cc_confirmed_items += 1
                            self.cc_cancellation_charge += jj.cancel_charge
                            self.cc_total_invoiced += jj.price_subtotal

                        if not jj.state_line == 'confirm':
                            self.cc_cancelled += jj.price_subtotal
                            self.cc_cancelled_items += 1

                        self.cc_refund = abs(self.cc_total_invoiced - self.cc_confirmed - self.cc_cancellation_charge)

                self.refund_enable = True
                self.apt_refund_amt = self.cc_refund


    def action_reschedule(self):
        for rec in self:
            rec.sudo().write({'state': 'new','color':2,'reschedule_flag':True})
            appointment_id= rec
            creation_date= rec.creation_date
            booking_date= rec.booking_date
            booked_by= rec.booked_by.id
            company_id= rec.company_id.id
            location_id= rec.location_id.id

            resch_id = rec.env['appointment.resch.line'].sudo().create(
                    {
                    'appointments_id':rec,
                    'creation_date': creation_date,
                    'booking_date': booking_date,
                    'booked_by': rec.booked_by.id,
                    'therapist_id': rec.therapist_id.id,
                    'service_categ_id': rec.service_categ_id.id,
                    'appointments_type_id': rec.appointments_type_id.id,
                    'company_id': rec.company_id.id,
                    'booking_start_date': booking_date,
                    'time_slot_id': rec.time_slot_id.id,
                    'time_id': rec.time_id.id,
                    'resch_date': datetime.today()
            })
        self.sale_order_id = False
        self.invoice_id = False
        # self.time_id = False
        # self.time_slot_id = False
        self.change_time = False
        self.cc_cancellation_charge = 0.0

    def add_package_line(self):
        def create_line_apt():
            for lst_id in self.s_service_categ_id:
                for j in range(int(lst_id.package_qty)):
                    vals = {
                        'appointments_package_id': lst_id.id,
                        'appointment_id': self.id,
                        'expiry_date': self.expiry_date,
                        'service_categ_id': self.service_categ_id.id,
                        'appointments_type_id': self.appointments_type_id.id,
                        'discount_type': 'type_percentage',
                        'discount': lst_id.discount,
                        'amount_discount': lst_id.discount,
                        'therapist_id': self.therapist_id.id,
                        'appointment_type': self.appointment_type,
                        'time_id': self.time_id.id
                    }
                    resch_id = self.env['appointment.line.id'].create(vals)

        if not self.s_service_categ_id: raise ValidationError(_("Select any Package."))
        elif self.appointment_line_id: raise ValidationError(_("Package already exist on package line, Please delete before adding packages"))
        else: create_line_apt()
        
        return True

    def remove_package_line(self):
        if self.appointment_line_id:
            for i in self.appointment_line_id:
                i.unlink()
        else: raise ValidationError(_("Nothing to delete"))

    def whatsapp_sent(self, partner_id=None, tmpl_id=None, pt=None, apt=None):
        server_url = self.env['ir.config_parameter'].sudo().get_param('ppts_watsapp_integration.server_url')
        access_token = self.env['ir.config_parameter'].sudo().get_param('ppts_watsapp_integration.access_token')
        mobile = ''
        if pt == 'mailing_list':
            ptr_id = self.env['mailing.contact'].sudo().browse(int(partner_id))
            mobile = ptr_id.mobile
        elif pt == 'res_partner':
            ptr_id = self.env['res.partner'].sudo().browse(int(partner_id))
            mobile = ptr_id.mobile
        elif pt == 'hr_employee':
            ptr_id = self.env['hr.employee'].sudo().browse(int(partner_id))
            mobile = ptr_id.mobile_phone
        elif pt == 'event_registration':
            ptr_id = self.env['event.registration'].sudo().browse(int(partner_id))
            mobile = ptr_id.mobile

        template_id = self.env['mail.whatsapp'].sudo().browse(int(tmpl_id))
        mod_id = self.env['appointment.appointment'].sudo().browse(int(apt))
        parms = []
        if template_id.parameter_ids:
            for i in template_id.parameter_ids:
                dict_prams = {}
                if i.field_id.ttype == 'many2one':
                    value = eval('obj.' + i.field_id.name, {'obj': mod_id})
                    dict_prams['name'] = i.name;dict_prams['value'] = value.name
                    parms.append(dict_prams)
                elif i.field_id.ttype == 'char' or i.field_id.ttype == 'integer' or i.field_id.ttype == 'text':
                    value = eval('obj.' + i.field_id.name, {'obj': mod_id})
                    dict_prams['name'] = i.name;dict_prams['value'] = value
                    parms.append(dict_prams)
                elif i.field_id.ttype == 'many2many':
                    many_val = ''
                    value = eval('obj.' + i.field_id.name, {'obj': mod_id})
                    for k in value:
                        many_val += k.name+','
                    many_val = many_val[:-1]
                    dict_prams['name'] = i.name;dict_prams['value'] = many_val
                    parms.append(dict_prams)
                else:
                    _logger.info('None')
        try:
            if ptr_id:
                url = server_url + "/api/v1/sendTemplateMessage"
                querystring = {"whatsappNumber": mobile}
                payload = """{\"parameters\":"""+str(parms)+""",
                                \"template_name\":\""""+str(template_id.template_name)+"""\",
                                \"broadcast_name\":\"test_ppts_broadcast\"
                                }"""
                headers = {
                    "Content-Type": "application/json-patch+json",
                    "Authorization": access_token
                }
                response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
                result = json.loads(response.text)
                _logger.info(response.text)
        except:
                _logger.info('--------No Network-------')

    remainder_complete = fields.Boolean('Remainder Completed')

    def appointment_remainder_before_du(self):
        note_id = self.env['appointment.notification'].search([('notification_active','=',True)],limit=1)
        if note_id.attendee_remain_2hrs_active_notification == True:
            model_id = self.env['ir.model'].search([('model','=','res.partner')],limit=1)
            mail_id = self.env['mailing.mailing'].create({
                    'subject': self.name+" "+"2 hrs to go",
                    'mailing_model_id': model_id.id,
                    'mailing_domain': "[['id','=',"+str(self.partner_id.id)+"]]",
                    'whatsapp_template':note_id.attendee_remain_2hrs_whatsapp.id,
                    "body_arch": """Hi %s, 
                                    Gentel remainder of the appointment %s 2 hrs to go
                                    """ % (self.partner_id.name, self.name)
                })

            date = self.booking_date.strftime("%Y-%m-%d")
            date = date+' '+self.start_time_str+':00'
            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            date = date - timedelta(hours = 7, minutes=30)
            date = date.strftime("%Y-%m-%d %H:%M:%S")

            wiz_id = self.env['mailing.mailing.schedule.date'].sudo().create({"schedule_date": date,"mass_mailing_id": mail_id.id})
            wiz_id.with_context(active_ids=mail_id.id).sudo().set_schedule_date()

        if note_id.attendee_remain_1day_active_notification == True:
            model_id = self.env['ir.model'].search([('model','=','res.partner')],limit=1)
            mail_id = self.env['mailing.mailing'].create({
                    'subject': self.name+" "+"1 day to go",
                    'mailing_model_id': model_id.id,
                    'mailing_domain': "[['id','=',"+str(self.partner_id.id)+"]]",
                    'whatsapp_template':note_id.attendee_remain_2hrs_whatsapp.id,
                    "body_arch": """Hi %s, 
                                    Gentel remainder of the appointment %s 1 day to go
                                    """ % (self.partner_id.name, self.name)
                })

            date = self.booking_date.strftime("%Y-%m-%d")
            date = date+' '+self.start_time_str+':00'
            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            date = date - timedelta(hours = 5, minutes=30)
            date = date - timedelta(days=1)
            date = date.strftime("%Y-%m-%d %H:%M:%S")

            wiz_id = self.env['mailing.mailing.schedule.date'].sudo().create({"schedule_date": date,"mass_mailing_id": mail_id.id})
            wiz_id.with_context(active_ids=mail_id.id).sudo().set_schedule_date()

    @api.model
    def create(self, vals):
        if vals.get('sequence', ' ') == ' ':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('appointment.appointment') or ' '

        res = super(CustomAppointments, self).create(vals)
        note_id = self.env['appointment.notification'].search([('notification_active','=',True)],limit=1)
        
        ctx = dict()
        now = datetime.now()
        if self.env.user.tz == 'Asia/Calcutta': now = datetime.now() + timedelta(hours=5,minutes=30)
        elif self.env.user.tz == 'Asia/Dubai': now = datetime.now() + timedelta(hours=4)
        
        res.creation_date_time = datetime.strftime(now, "%d/%m/%Y at %H:%M:%S")
        res.creation_datetime = datetime.now()
        res.change_time = False
        # if res.is_package_claim == True:
        #     count = 0
        #     for rec in res.apt_package_parent_id.appointment_line_id:
        #         if rec.state_line in ['draft']:
        #             count += 1
        #     count =  len(res.apt_package_parent_id.appointment_line_id) - count
        #     res.sequence += '-' + str(count)

        if note_id.apt_active_notification_create == True:
            for i in note_id.apt_create_mail_list:
                for il in self.env['mailing.contact'].sudo().search([]):
                    if il.email and i.id in il.subscription_list_ids.ids and i.apt_create_mail:
                        ctx.update({
                            'appointment_name': res.name,
                            })
                        for kk in i.apt_create_mail:
                            kk.sudo().with_context(ctx).send_mail(il.id, force_send=True)
                    if il.mobile and i.id in il.subscription_list_ids.ids and i.apt_create_whatsapp:
                        res.whatsapp_sent(partner_id=il.id,tmpl_id=i.apt_create_whatsapp.id,pt='mailing_list',apt=res.id)
            if res.partner_id.email and note_id.apt_create_mail_template:
                for kk in note_id.apt_create_mail_template:
                    kk.sudo().with_context(ctx).send_mail(res.id, force_send=True)
            if res.partner_id.mobile and note_id.apt_create_whatsapp:
                res.whatsapp_sent(partner_id=res.partner_id.id,tmpl_id=note_id.apt_create_whatsapp.id,pt='res_partner',apt=res.id)
        
        res.partner_id.reffer_type_id = res.reffer_type_id.id or False
        # pass the quick remarks and notes to respective customer 20-10-22
        res.partner_id.latest_quick_remarks = res.quick_remarks_id.name
        res.partner_id.latest_comment = res.notes

        msg_body = """Creation Date : """ + str(res.creation_date or 'N/A') + """ <br/> """ +\
            """Customer Name : """ + str(res.partner_id.name or 'N/A') + """ <br/> """ +\
            """Appointment Date : """ + str(res.booking_date or 'N/A') + """ <br/> """ +\
            """Type of Session: """ + str(dict(res._fields['session_type'].selection).get(res.session_type) or 'N/A')  + """ <br/> """ +\
            """Package: """ + str(res.s_service_categ_id.name or 'N/A') + """ <br/> """ +\
            """Duration: """ + str(res.time_id.name or 'N/A') + """ <br/> """ +\
            """Time Slots : """ + str(res.time_slot_id.name or 'N/A') + """ <br/> """ +\
            """Therapist : """ + str(res.therapist_id.name or 'N/A') + """ <br/> """ +\
            """Service Category : """ + str(res.du_service_categ_id.name or 'N/A') + """ <br/> """ +\
            """Sub Category : """ + str(res.appointments_type_id.name or 'N/A') + """ <br/> """ +\
            """Sales Rep : """ + str(res.booked_by.name or 'N/A') + """ <br/> """ +\
            """Payment Status : """ + str(dict(res._fields['payment_status_apt'].selection).get(res.payment_status_apt) or 'N/A') + """ <br/> """ +\
            """Quick Remarks : """ + str(res.quick_remarks_id.name or 'N/A') + """ <br/> """ +\
            """Notes : """ + str(res.notes or 'N/A') + """ <br/> """
        res.message_post(body=msg_body)
        if res.partner_id:
            res.partner_id.message_post(body=msg_body)

        if res.partner_id.lead_id:
            if res.partner_id.lead_id.stage_id.is_won == True:
                master_aboutus_id = self.env['master.aboutus'].search([('name','=','Social Media')])
                lead_id = self.env['crm.lead'].create({
                    'name':res.partner_id.name + '' + ' New Lead', 
                    'email_from':res.partner_id.email,
                    'first_name':res.partner_id.firstname,
                    'last_name':res.partner_id.lastname,
                    'mobile':res.partner_id.mobile,
                    'type': 'opportunity',
                    'partner_id':res.partner_id.id,
                    'master_aboutus':master_aboutus_id.id,
                    'appointment_id':res.id
                    })
                if res.quick_remarks_id:
                    crm_stage = self.env['crm.stage'].search([('quick_remarks_id','=',res.quick_remarks_id.id)],limit=1)
                    lead_id.stage_id = crm_stage
        if not res.partner_id.lead_id:
            master_aboutus_id = self.env['master.aboutus'].search([('name','=','Social Media')])
            lead_id = self.env['crm.lead'].create({
                'name':res.partner_id.name + '' + ' New Lead', 
                'email_from':res.partner_id.email,
                'first_name':res.partner_id.firstname,
                'last_name':res.partner_id.lastname,
                'mobile':res.partner_id.mobile,
                'type': 'opportunity',
                'partner_id':res.partner_id.id,
                'master_aboutus':master_aboutus_id.id,
                'appointment_id':res.id
                })
            if res.quick_remarks_id:
                crm_stage = self.env['crm.stage'].search([('quick_remarks_id','=',res.quick_remarks_id.id)],limit=1)
                lead_id.stage_id = crm_stage
            else:
                crm_stage = self.env['crm.stage'].search([('is_won','=',True)],limit=1)
                lead_id.stage_id = crm_stage

        return res

    def write(self, vals):
        # make false upate value flag based on write 28-06-22
        vals['change_time'] = False
        # pass the quick remarks and notes to respective customer 20-10-22
        self.partner_id.latest_quick_remarks = self.quick_remarks_id.name or False
        self.partner_id.latest_comment = self.notes
        if self._origin.id:
            # query = " UPDATE appointment_appointment SET altered_booked_by = %s WHERE id = %s; " % (str(self.env.uid), str(self._origin.id))
            # self.env.cr.execute(query)
            vals['altered_booked_by'] = self.env.uid
            # self.update({
            #     'altered_booked_by': self.env.uid,
            #     })
        return super(CustomAppointments, self).write(vals)

    def action_apt_room(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Order',
            'view_mode': 'tree,form',
            'res_model': 'event.meeting.room',
            'domain': [('appointment_id', '=', self.id)],
        }

    total_invoiced = fields.Float(compute='_invoice_total', string="Total Invoiced", groups='account.group_account_invoice,account.group_account_readonly')

    def _invoice_total(self):
        self.total_invoiced = 0.00
        pay_id = self.env['account.payment'].search([])
        if self._origin:
            for i in pay_id:
                if i.state == 'posted':
                    if i.appointments_id.id == self.id:
                        self.total_invoiced += float(i.amount)
                    if self.invoice_id and i.ref == self.invoice_id.name:
                        self.total_invoiced += float(i.amount)

    def action_apt_payment(self):
        if self.pos_atv == True or self.pac_pos_atv == True:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Payment',
                'view_mode': 'tree,form',
                'res_model': 'pos.payment',
                'domain': [('id', 'in', self.pos_order_id.payment_ids.ids or self.pac_pos_order_id.payment_ids.ids)],
            }
        else:
            context = dict(self.env.context or {})
            context.update(create=False)
            pay_ids = self.env['account.payment'].search([])
            lst = []
            if pay_ids:
                for i in pay_ids:
                    if i.state == 'posted':
                        if i.appointments_id.id == self.id:
                            lst.append(i.id)
                        if self.invoice_id and i.ref == self.invoice_id.name:
                            lst.append(i.id)
            return {
                'type': 'ir.actions.act_window',
                'context': context,
                'name': 'Payment',
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'domain': [('id','in',lst)],
            }


    def action_apt_invoice(self):
         return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'res_model': 'account.move',
        }

    def action_apt_credit_invoice(self):
         return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'form',
            'res_id': self.credit_note_id.id,
            'res_model': 'account.move',
        }

    def action_apt_so(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Order',
            'view_mode': 'tree,form',
            'res_model': 'pos.order',
            'domain': ['|',('id', '=', self.pos_order_id.id or self.pac_pos_order_id.id),('appt_sale_id', '=', self.id)],
        }

    def action_apt_po(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Order',
            'view_mode': 'tree,form',
            'res_model': 'pos.order',
            'domain': [('id', '=', self.pos_order_id.id or self.pac_pos_order_id.id)],
        }

    def action_create_payment(self):
        if self.session_type == 'type_single':
            if self.invoice_id:
                ret = {
                    'name': _('Create Event Payment'),
                    'res_model': 'account.payment.register',
                    'view_mode': 'form',
                    'context': {
                        'active_model': 'account.move',
                        'active_ids': self.invoice_id.id,
                    },
                    'target': 'new',
                    'type': 'ir.actions.act_window',
                }
                return ret
            else:
                raise UserError('Invoice is not available for this booking.')

    # @api.model
    def action_add_new_customer(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'name': _('Register New Client'),
            'res_model': 'res.partner',
            'target': 'new',
            'views': [(False, "form")],
            'context': {
                'default_res_model': 'appointment.appointment',
            },
        }

    def get_appointment_amount(self):
        payrate_id = self.env['hr.employee.payrate'].sudo().search([\
            ('employee_id','=', self.therapist_id.id ),\
                ('duration_id','=', self.time_id.id ),\
                    ('service_category_type_id','=', self.du_service_categ_id.id ),\
                        ('appoinment_type_id','=', self.appointments_type_id.id )\
                    ], limit=1)
        return payrate_id.unit_price

    def action_single_session_remaining_customer(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'name': _('Appointment'),
            'res_model': 'appointment.appointment',
            'res_id': self.id,
            'target': 'new',
            'views': [(False, "form")],
        }
        
    def redirect_to_appointment(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'name': _('Appointment'),
            'res_model': 'appointment.appointment',
            'res_id': self.id,
            'target': 'new',
        }

    def action_add_single_service(self):
        return {
            'name': _('Add Service'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'single.session.wizard',
            'views': [(False, 'form')],
            'view_id': 'single_session_wizard_form',
            'target': 'new',
            'context': {'default_appointments_id': self.id,'default_customer_id': self.partner_id.id}
        }

    def action_create_adv_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_model': 'account.payment',
            'view_id': 'account.view_account_payment_form',
            'target': 'new',
            'context': {    
                        'default_partner_id': self.partner_id.id,
                        'default_appointments_id':self.id,
                        'default_company_id': self.company_id.id,
                        }
        }

    def get_fields_to_ignore_in_search(self):
        return ['cc_cancel_atv', 'color', 'package_appointment_type', 'cc_cancelled_items', 'cc_confirmed_items',
                'credit_note_id', 'package_discount', 'single_discount', 'time_id', 'end_time_str',
                's_service_categ_id', 'pac_pos_atv',
                'altered_booked_by', 'du_service_categ_id', 'account_id', 'amount_unit_price_tot',
                'unit_price',
                'available_ids', 'cc_cancellation_charge', 'cc_cancelled', 'cc_confirmed', 'refund_id', 'currency_id',
                'amount_discount', 'customer_feedback', 'therapist_assistant_id', 'notes', 'invoice_id', 'location_id', 'name',
                'next_activity',
                'pos_order_id', 'pos_order_line_id', 'pac_pos_order_line_id', 'expiry_date', 'payment_status',
                'pos_atv', 'pac_pos_order_id',
                'customer_prescription', 'promo_code', 'amount_promo', 'amount_recharge_coupon', 'refund_enable',
                'cc_refund', 'remainder_complete',
                'reschedule_flag', 'appointment_resch_line', 'sale_order_id', 'sale_person_id', 'sequence',
                'appointment_line_id', 'use_rescheule',
                'source_id', 'start_time_str', 'state', 'single_subtotal', 'cc_subtotal',
                'amount_untaxed', 'tag_by_sub_healing_id',
                'tag_by_healing_id', 'tag_by_therapy_id', 'single_tax_ids', 'amount_tax', 'time_selection',
                'cc_total_invoiced',
                'discount_on_other', 'amount_total', 'amount_due', 'use_promo_code', 'invoice_fully_paid', 'online_web_link',
                'apt_payment_paid','use_partial_cancel','apt_booked_by','extras_partner_id',
                'apt_invoice_amt','apt_payment_amt','apt_refund_amt','apt_used_pack']

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(CustomAppointments, self).fields_get(allfields, attributes=attributes)
        for field in self.get_fields_to_ignore_in_search():
            if res.get(field):
                res.get(field)['searchable'] = False
                res.get(field)['sortable'] = False
        return res


    # @api.onchange('therapist_id')
    # def _eve_therapist_id(self):
    #     if self.therapist_id:
    #         get_event = self.env['event.event'].search([])
    #         for each_date in get_event.multi_date_line_ids:
    #             therapist_exists =self.env['multi.date.line'].search([('event_id.facilitator_evnt_ids' , 'in',self.therapist_id.ids),('event_id','!=', False),('event_id.id','!=',self._origin.id),
    #                                                             ('m_date_begin', '<=', self.booking_date), ('m_date_end', '>=', self.booking_date)])
    #             if therapist_exists: 
    #                 raise UserError("This Therapist is allocated to another event at this Time1")
    #             if not therapist_exists:
    #                 multi_date =self.env['multi.date.line'].search([('event_id.facilitator_evnt_ids' , 'in',self.therapist_id.ids)])
    #                 if multi_date:
    #                     for each_multi_date in multi_date:
    #                         if each_date.m_date_begin < each_multi_date.m_date_begin < each_date.m_date_end:
    #                             raise UserError("This Therapist is allocated to another event at this Time2")
    #                         if each_date.m_date_begin < each_multi_date.m_date_end < each_date.m_date_end:
    #                             raise UserError("This Therapist is allocated to another event at this Time3")
                
    #             appointment_ids =self.env['appointment.appointment'].search([('state','not in',('cancel','void')),('booking_date','!=',False),('booking_date','=',self.booking_date)])
    #             for each_apt in appointment_ids:                    
    #                 timezone = pytz.timezone(self.env.user.tz or 'UTC')
    #                 date_begin = each_date.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
    #                 date_end = each_date.m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
    #                 if each_apt.start_time_str and each_apt.end_time_str:
    #                     if each_apt.start_time_str <= date_begin.strftime("%H:%M") <= each_apt.end_time_str:
    #                         raise UserError("This Therapist is allocated to another Appointment at this Time")
    #                     if each_apt.start_time_str <= date_end.strftime("%H:%M") <= each_apt.end_time_str:
    #                         raise UserError("This Therapist is allocated to another Appointment at this Time")

    # @api.onchange('apt_room_id')
    # def onchange_room_id(self):
    #     get_event = self.env['event.event'].search([])
    #     for each_date in get_event.multi_date_line_ids:
    #         room_exists =self.env['multi.date.line'].search([('event_id.room_id' , '=',self.apt_room_id.id),
    #                                                         ('m_date_begin', '<=', self.booking_date), ('m_date_end', '>=', self.booking_date)])
    #         if room_exists: 
    #             raise UserError("This Room is allocated to another event at this Timezzzzz ")
    #         if not room_exists:
    #             multi_date =self.env['multi.date.line'].search([('event_id.room_id' , '=',self.apt_room_id.ids),('event_id','!=', False),('m_date_begin','=',self.booking_date),('m_date_end','=',self.booking_date)])                
    #             if multi_date:
    #                 for each_multi_date in multi_date:
    #                     if each_date.m_date_begin < each_multi_date.m_date_begin < each_date.m_date_end:
    #                         raise UserError("This Room is allocated to another event at this Time22 ")
    #                     if each_date.m_date_begin < each_multi_date.m_date_end < each_date.m_date_end:
    #                         raise UserError("This Room is allocated to another event at this Time33 ")
    #         appointment_ids =self.env['appointment.appointment'].search([('state','not in',('cancel','void')),('booking_date','!=',False),('booking_date','=',self.booking_date),('apt_room_id','=',self.apt_room_id.id)])
    #         for each_apt in appointment_ids:
    #             print(each_apt,'333333333333333333333333333333333333333')
    #             stop
    #             if each_apt.booking_date == self.booking_date:
    #                 timezone = pytz.timezone(self.env.user.tz or 'UTC')
    #                 date_begin = each_date.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
    #                 date_end = each_date.m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
    #                 if each_apt.start_time_str and each_apt.end_time_str:
    #                     if each_apt.start_time_str <= date_begin.strftime("%H:%M") <= each_apt.end_time_str:
    #                         raise UserError("This Room is allocated to another Appointment at this Time5656")
    #                     if each_apt.start_time_str <= date_end.strftime("%H:%M") <= each_apt.end_time_str:
    #                         raise UserError("This Room is allocated to another Appointment at this Time7878")
            # for each_apt in appointment_ids:
            #     if each_apt.start_time_str >= self.start_time_str and each_apt.end_time_str <= self.end_time_str:
            #         timezone = pytz.timezone(self.env.user.tz or 'UTC')
            #         date_begin = each_date.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
            #         date_end = each_date.m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
            #         if each_apt.start_time_str <= date_end.strftime("%H:%M") <= each_apt.end_time_str:
            #             raise UserError("This Room is allocated to another Appointment at this Time")

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    appointments_id = fields.Many2one('appointment.appointment', string='Appointment', copy=False, tracking=True)

    @api.model_create_multi
    def create(self, vals):
        res = super(AccountPayment, self).create(vals)
        acc=res.move_id.write({'name':'/','sequence_prefix':'','sequence_number':'0'})
        return res


class CustomAppointmentsLine(models.Model):
    _name = 'appointment.line.id'
    _description = 'Appointment Line'

    def _compute_package_expired_date(self):
        for rec in self:
            if rec and rec.appointments_type_id and rec.appointment_id.session_type=='type_package':
                rec.package_expired_date = False
                if rec.appointments_type_id.interval_range and rec.appointments_type_id.interval_number:
                    if rec.appointments_type_id.interval_range == "months":
                        rec.package_expired_date = rec.appointment_id.creation_date + relativedelta(months=+rec.appointments_type_id.interval_number)
                        rec.package_expired_date = rec.package_expired_date - timedelta(days = 1)
                        if rec.appointment_id.creation_date >= rec.package_expired_date:
                            rec.package_expired_av = True
                    elif rec.appointments_type_id.interval_range == "day":
                        rec.package_expired_date = rec.appointment_id.creation_date + relativedelta(days=+rec.appointments_type_id.interval_number)
                        rec.package_expired_date = rec.package_expired_date - timedelta(days = 1)
                        if rec.appointment_id.creation_date >= rec.package_expired_date:
                            rec.package_expired_av = True
            else:
                rec.package_expired_date = False

    appointment_id = fields.Many2one('appointment.appointment')
    partner_id = fields.Many2one('res.partner',string='Customer',related='appointment_id.partner_id')
    single_session_id = fields.Many2one('appointment.appointment')
    package_expired_av = fields.Boolean()
    package_expired_date = fields.Date('Expiry Date',compute="_compute_package_expired_date")

    state = fields.Selection(related='appointment_id.state',string='State', default='new')

    state_line = fields.Selection([('draft', 'Available'),('confirm', 'Used'),('cancel', 'Cancelled'),
                                   ('void', 'Void'),
                                   ('arrive', 'Arrived'),
                                   ('no_show', 'No Show'),
                                   ('done', 'Completed')
                                   ],default="draft",string="State")

    appointments_package_id = fields.Many2one('appointment.package', string='Package')
    service_categ_id = fields.Many2one('appointment.category', string='Service Category')
    appointments_type_id = fields.Many2one('calendar.appointment.type', string='Appointment Type')
    therapist_id = fields.Many2one('hr.employee', string='Therapist')
    therapist_assistant_id = fields.Many2one('hr.employee', string='Instructor')
    appointment_type = fields.Selection([('type_online', 'Online'),('type_onsite', 'On-site')],string='Appointment Platform',required=True)
    location_id = fields.Many2one('res.partner', string='Location', related="appointment_id.location_id")
    source_id = fields.Many2one('appointment.source', string='Source', related="appointment_id.source_id")
    company_id = fields.Many2one('res.company',related="appointment_id.company_id")
    cancel_charge = fields.Float('Cancellation Charges')
    cancellation_datetime = fields.Datetime(related='appointment_id.cancellation_datetime')
    booking_date = fields.Date(related='appointment_id.booking_date')
    time_slot_id = fields.Many2one('time.slot')
    cancellation_type = fields.Selection([('early','Early'),('late','Late')],string='Method')
    sequence = fields.Char(related='appointment_id.sequence')
    altered_booked_by = fields.Many2one('res.users',string='Modified By', related='appointment_id.altered_booked_by')
    descriptions = fields.Char(related='appointment_id.descriptions')
    session_type = fields.Selection(string='Type Of Session', related='appointment_id.session_type')
    # @api.onchange('service_categ_id')
    # def _onchange_service_categ_id(self):
    #     for rec in self:
    #         servive_emp=self.env['hr.employee'].search([('service_category_ids', 'in', rec.service_categ_id.id)])
    #     return {'domain': {'therapist_id': [('id','in',servive_emp.ids)]}}

    @api.onchange('service_categ_id','appointments_type_id','therapist_id','price_subtotal')
    def _pay_rate_calculate(self):
        if self.service_categ_id and self.appointments_type_id and self.therapist_id and self.price_subtotal:
            pay_rate_ids = self.env['hr.employee.payrate'].search([('employee_id','=',self.therapist_id.id),('appoinment_type_id','=',self.appointments_type_id.id),('service_category_type_id','=',self.service_categ_id.id)],limit=1)
            if pay_rate_ids:
                self.payrate_type = pay_rate_ids.staff_rate
                self.staff_rate_percentage = pay_rate_ids.staff_rate_percentage
                if pay_rate_ids.staff_rate == 'percentage_rate':
                    self.commision_amt = pay_rate_ids.staff_rate_percentage*self.price_subtotal/100
                elif pay_rate_ids.staff_rate == 'flat_rate':
                    self.commision_amt = abs(pay_rate_ids.staff_rate_percentage-self.price_subtotal)
                else:
                    self.commision_amt = 0

    booking_start_date = fields.Date(string='Start Date')
    expiry_date = fields.Date(string='Package Expiry Date',default=lambda self: self.expiry_date)
    start_time_str = fields.Selection(TIME,string='Start Time')
    start_time = fields.Float(string='Start Time')
    end_time_str = fields.Selection(TIME, string='End Time strrr')
    end_time = fields.Float(string='End Time',store=True)
    time_id = fields.Many2one('time.time',string='Duration')
    duration = fields.Float(string='Duration')
    apt_room_id = fields.Many2one('roomtype.master', string='Room')
    unit_qty = fields.Float(string='Unit',default=1)
    unit_price = fields.Float(string='Unit Price', compute='_compute_unit_price', store=True)
    discount_type = fields.Selection([
        ('type_nodisc', 'No Discount'),
        ('type_flat', 'Flat Rate'),
        ('type_percentage', 'Percentage')], default='type_nodisc',
        required=True,
        string="Disc. Type", help='Type of Discount to be Applied.')

    discount = fields.Float(string='Discount')
    amount_discount = fields.Float(string='Discount Amount')
    percentage_discount = fields.Float(string='Discount % value')
    price_after_dis = fields.Float(string='After Discount',compute='_onchange_price_after_dis',store=True)
    tax_ids = fields.Many2many('account.tax', 'apt_line_account_tax_tax_ids',string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    package_tax_ids = fields.Many2many('account.tax', 'apt_line_account_tax_package_tax_ids',string='Tax')
    tax_amount = fields.Float(string='Tax Amt')
    price_after_tax = fields.Float(string='After Tax')
    payrate_type = fields.Selection([('no_pay','No Pay'),('flat_rate','Flat Rate'),('percentage_rate','Percentage Rate')],default="no_pay", string="Payment Type")
    staff_rate_percentage = fields.Integer('EMP Pay Rate')
    commision_amt = fields.Float('Commision Amt')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_line_subtotal', store=True)

    sale_id=fields.Many2one('sale.order', string='Sale Order')
    sale_line_id=fields.Many2one('sale.order.line', string='Sale Order Line')
    invoice_id=fields.Many2one('account.move', string='Invoice')
    refund_id=fields.Many2one('account.move', string='Credit Note')
    receipt_id=fields.Many2one('account.payment', string='Receipt')
    calendar_id=fields.Many2one('calendar.event', string='calendar event')

    arrived_date = fields.Datetime(string='Arrived Date & Time')
    course_used = fields.Boolean(string='Course Used', default=False)
    attended_date = fields.Datetime(string='Attended Date & Time')
    course_cancelled = fields.Boolean(string='Course Cancelled', default=False)
    cancelled_date = fields.Datetime(string='Cancelled Date & Time', copy=False)
    set_confirmed = fields.Boolean('confirmed state')
    avail_id = fields.Many2one('availability.availability')

    payment_status_apt = fields.Selection(default='no_paid', related='appointment_id.payment_status_apt')



    @api.onchange('time_id')
    def _onchange_time_id(self):
        if self.time_id:
            time_val = str(timedelta(minutes=int(self.time_id.duration)))[:-3]
            time_val = time_val.replace(':','.')
            self.duration = float(time_val)
        else:
            self.duration = 0

    @api.onchange('therapist_id')
    def _onchange_service_ids_domain_opl(self):
        lstt = []
        self.service_categ_id = self.appointments_type_id = self.time_id = self.time_slot_id = False
        resp = {'domain': {'service_categ_id': "[('id', 'not in', False)]"}}
        if self.therapist_id:
            for i in self.therapist_id.pay_rate_ids:
                if i.service_category_type_id.id not in lstt: lstt.append(i.service_category_type_id.id)

        resp['domain']['service_categ_id'] = "[('id', 'in', %s)]" % lstt
        return resp

    @api.onchange('therapist_id','service_categ_id')
    def _onchange_sub_service_ids_domain(self):

        lst = []
        res = {'domain': {'appointments_type_id': "[('id', 'not in', False)]"}}
        if self.therapist_id and self.service_categ_id:
            for i in self.therapist_id.pay_rate_ids:
                if i.appoinment_type_id.id not in lst and self.service_categ_id == i.service_category_type_id: 
                    lst.append(i.appoinment_type_id.id)
        res['domain']['appointments_type_id'] = "[('id', 'in', %s)]" % lst
        return res

    @api.onchange('service_categ_id','therapist_id','appointments_type_id','du_service_categ_id','time_id','booking_start_date','amount_due')
    def _onchange_time_id_setfl_domain(self):

        lst = []
        self.time_id = self.time_slot_id = False
        res = {'domain': {'time_id': "[('id', 'not in', False)]"}}
        if self.therapist_id and self.service_categ_id and self.appointments_type_id:
            for i in self.therapist_id.pay_rate_ids:
                if i.duration_id.id not in lst and self.service_categ_id == i.service_category_type_id and \
                                            self.appointments_type_id == i.appoinment_type_id: 
                    lst.append(i.duration_id.id)
        res['domain']['time_id'] = "[('id', 'in', %s)]" % lst
        return res

    def move_to_pos_client(self):
        if self.appointment_id.pos_order_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Dashboard',
                'view_mode': 'kanban,tree,form',
                'res_model': 'pos.config',
                'domain':"['|',('user_ids', 'in', uid),('user_ids','=',False)]"
            }
        else:
            self.appointment_id.move_to_pos_client()

    def action_redirect_main_apt(self):
        rec = self.env['appointment.line.id'].search(
            [('state_line', '=', 'confirm'), ('appointment_id', '=', self.appointment_id.id)])
        if len(rec)>1 and not self.appointment_id.state == 'new':
            raise UserError(_("Not allowed to Void this Service. Some of the services are Availed Already..!!"))
        elif len(rec)==1 and self.appointment_id.state == 'new':
            raise UserError(_("Not allowed to Void this Service. Package is not Confirmed Yet..!!"))
        apt_id = self.env['appointment.appointment'].search([('package_line_id','=',self.id),('state','=','done')],limit=1)
        if apt_id:
            return {
                    'type': 'ir.actions.act_window',
                    'name': 'Appointment',
                    'view_mode': 'form',
                    'res_model': 'appointment.appointment',
                    'res_id': apt_id.id,
                    'target': 'new',
                }
        else:
            raise ValidationError(_("Appointment is not completed,Please complete a appointment to make void"))


    def confirm_package(self):
        if self.appointment_id.creation_date < self.package_expired_date:
            if not self.therapist_id:
                raise UserError(_("No Therapist Assigned"))
            elif not self.apt_room_id:
                raise UserError(_("No Room Assigned"))
            elif not self.booking_start_date:
                raise UserError(_("Start date have not Assigned"))
            elif not self.start_time_str:
                raise UserError(_("Start time have not Assigned"))
            elif not self.end_time_str:
                raise UserError(_("End time have not Assigned"))
            else:

                if self.appointment_id.sale_order_id:
                    if self.appointment_id.sale_order_id.state=='draft':
                        so_confirm=self.appointment_id.sale_order_id.sudo().action_confirm()

                    if self.appointment_id.sale_order_id.state=='sale':
                        line_vals=[]

                        vals = [0, 0, {
                            'product_id': self.appointments_type_id.product_id.id,
                            'name': self.appointments_type_id.product_id.name,
                            'account_id': self.appointment_id.account_id.id,
                            'partner_id': self.appointment_id.partner_id.id,
                            'quantity': 1,
                            'price_unit': self.unit_price,
                            'discount': self.discount,
                            'tax_ids': self.package_tax_ids,
                        }]

                        line_vals.append(vals)
                        cmp_id = self.env['account.journal'].search(
                            [('type', '=', 'sale'), ('company_id', '=', self.appointment_id.company_id.id)], limit=1)

                        acc_move_id = self.env['account.move'].create({
                            'move_type': 'out_invoice',
                            'invoice_date': date.today(),
                            'partner_id': self.appointment_id.partner_id.id,
                            'date': date.today(),
                            'invoice_origin': self.appointment_id.sale_order_id.name or '',
                            'journal_id': cmp_id.id,
                            'apt_order_id': self.appointment_id.sale_order_id.id,
                            'ref': self.appointment_id.sale_order_id.name or '',
                            'narration': self.appointment_id.name,
                            'invoice_line_ids': line_vals,
                        })

                        so_line = self.env['sale.order.line'].search([('appt_line_id', '=', self.id)])
                        so_line.write({'invoice_status': 'invoiced', 'qty_invoiced': 1})
                        so_id = self.appointment_id.sale_order_id
                        invoices = self.env['account.move'].search([('apt_order_id', '=', so_id.id)])
                        self.service_confirmed_date=date.today()
                        self.invoice_id=acc_move_id.id
                        self.invoice_id=acc_move_id.id
                        self.state='confirm'
                self.set_confirmed = True
                # self.avail_id = avail_id.id
                self.appointment_id.write({'state': 'ongoing'})
                self.state_line = 'confirm'
                self.remainder_appointment_before_package()
        else:
            raise ValidationError(_("Service expired"))

    @api.depends('appointments_type_id','therapist_id','service_categ_id','time_id')
    def _compute_unit_price(self):
        for rec in self:
            rec.unit_price = 0.0
            if rec.therapist_id and rec.service_categ_id and rec.appointments_type_id:
                for i in rec.therapist_id.pay_rate_ids:
                    if rec.service_categ_id == i.service_category_type_id and \
                                rec.appointments_type_id == i.appoinment_type_id and \
                                    rec.time_id == i.duration_id:
                        rec.unit_price = i.unit_price


    @api.depends('unit_price', 'unit_qty', 'discount', 'discount_type','amount_promotion','amount_rc_coupon')
    def _compute_line_subtotal(self):
        for rec in self:
            if rec.price_after_dis and rec.unit_qty:
                rec.price_subtotal=rec.price_after_dis*rec.unit_qty

    @api.onchange("apt_room_id", 'booking_start_date','end_time_str')
    def onchange_apt_room_id_change(self):
        if self.apt_room_id and self.booking_start_date and self.start_time_str  and self.end_time_str:

            a_start = str(self.booking_start_date) + ' 00:00:00'
            a_end = str(self.booking_start_date) + ' 23:59:59'

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

    @api.depends('unit_price','unit_qty','discount','discount_type','amount_promotion','amount_rc_coupon')
    def _onchange_price_after_dis(self):
        for rec in self:
            if rec.service_categ_id and rec.unit_qty:
                if rec.discount_type == 'type_flat':
                    if rec.discount>rec.unit_price:
                        raise ValidationError(_("Discount can't be greater than Product Price."))
                    else:
                        if rec.amount_promotion:
                            rec.price_after_dis = (rec.unit_price - rec.discount)-rec.amount_promotion
                        else:
                            rec.price_after_dis = rec.unit_price - rec.discount


                        rec.amount_discount = rec.discount
                        dp_price = (rec.amount_discount / rec.unit_price) * 100

                        rec.percentage_discount =dp_price

                elif rec.discount_type == 'type_percentage':
                    if rec.discount > 100:
                        raise ValidationError(_("Discount can't be greater than Product Price."))
                    else:
                        d_price = (rec.unit_price * rec.discount) / 100
                        rec.price_after_dis = rec.unit_price - d_price
                        rec.amount_discount = d_price
                        rec.percentage_discount = rec.discount
                else:
                    if rec.amount_promotion:
                        rec.price_after_dis = rec.unit_price - rec.amount_promotion
                    else:
                        rec.price_after_dis = rec.unit_price
                        rec.discount=''
                        rec.amount_discount=''

                if rec.amount_rc_coupon:
                    rec.price_after_dis = rec.price_after_dis - rec.amount_rc_coupon
                else:
                    rec.price_after_dis = rec.price_after_dis

    @api.onchange('unit_price','unit_qty','package_tax_ids','discount')
    def _onchange_price_after_tax_set(self):
        amount_taxed=taxed=0.0
        # for rec in self:
        if self.package_tax_ids:
            for tax in self.package_tax_ids:
                amount_taxed = self.env['account.tax'].search([('id', '=', tax._origin.id)]).amount
                taxed = (self.price_subtotal*amount_taxed)/100
        self.tax_amount=taxed

    @api.onchange('appointments_type_id')
    def _onchange_booking_date(self):
        for rec in self:
            rec.booking_start_date=rec.appointment_id.booking_date
            rec.expiry_date=rec.appointment_id.expiry_date

    # @api.depends('start_time','duration','start_time_str')
    # def _compute_endtime(self):
    #     for rec in self:
            # if rec.start_time_str:
            #     start_time = datetime.strptime(str(rec.start_time_str), "%H:%M")
            #     start_time = start_time.strftime("%H.%M")
            #     rec.start_time = float(start_time)
            #     rec.end_time = abs(rec.start_time + rec.duration)
            #     dsfsdee = '%.2f' % abs(rec.duration)
            #     stri = str(dsfsdee).split(".")
            #     d_end_start_time = datetime.strptime(str('%.2f' % abs((rec.start_time))), "%H.%M")
            #     new_time_end = d_end_start_time + timedelta(hours=int(stri[0]), minutes=int(stri[1]), seconds=0)
            #     str_new_time_end = new_time_end.strftime("%H:%M")
            #     rec.end_time_str = str(str_new_time_end)

    def action_arrived(self):
        for rec in self:
            rec.appointment_id.state = 'ongoing'
            rec.arrived_date=datetime.now()

    def create_event(self):
        for program in self:
            partner_ids = list(set([program.partner_id.id]))

            for apt in program:
                event = self.env['calendar.event'].create({
                    'name': _('%s with %s') % (apt.appointments_type_id.name, apt.therapist_id.name),
                    'start': datetime.now(),
                    'stop': datetime.now(),
                    'allday': False,
                    'duration': apt.duration,
                    'partner_ids': [(4, pid, False) for pid in partner_ids],
                    'appointment_type_id': apt.appointments_type_id.id,
                    'appointment_id': program.id,
                    'appointment_line_id': apt.id,
                })

    def remainder_appointment_before_package(self):
        note_id = self.env['appointment.notification'].search([('notification_active','=',True)],limit=1)
        if note_id.attendee_remain_2hrs_active_notification == True:
            model_id = self.env['ir.model'].search([('model','=','res.partner')],limit=1)
            mail_id = self.env['mailing.mailing'].create({
                    'subject': self.appointment_id.name+" "+"2 hrs to go",
                    'mailing_model_id': model_id.id,
                    'mailing_domain': "[['id','=',"+str(self.appointment_id.partner_id.id)+"]]",
                    'whatsapp_template':note_id.attendee_remain_2hrs_whatsapp.id,
                    "body_arch": """Hi %s, 
                                    Gentel remainder of the appointment %s 2 hrs to go
                                    """ % (self.appointment_id.partner_id.name, self.appointment_id.name)
                })

            date = self.booking_start_date.strftime("%Y-%m-%d")
            date = date+' '+self.start_time_str+':00'
            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            date = date - timedelta(hours = 7, minutes=30)
            date = date.strftime("%Y-%m-%d %H:%M:%S")

            wiz_id = self.env['mailing.mailing.schedule.date'].sudo().create({"schedule_date": date,"mass_mailing_id": mail_id.id})
            wiz_id.with_context(active_ids=mail_id.id).sudo().set_schedule_date()

        if note_id.attendee_remain_1day_active_notification == True:
            model_id = self.env['ir.model'].search([('model','=','res.partner')],limit=1)
            mail_id = self.env['mailing.mailing'].create({
                    'subject': self.appointment_id.name+" "+"2 hrs to go",
                    'mailing_model_id': model_id.id,
                    'mailing_domain': "[['id','=',"+str(self.appointment_id.partner_id.id)+"]]",
                    'whatsapp_template':note_id.attendee_remain_2hrs_whatsapp.id,
                    'body_arch': """Hi %s, 
                                    Gentel remainder of the appointment %s 2 hrs to go
                                    """ % (self.appointment_id.partner_id.name, self.appointment_id.name)
            })

            date = self.booking_start_date.strftime("%Y-%m-%d")
            date = date+' '+self.start_time_str+':00'
            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            date = date - timedelta(hours = 5, minutes=30)
            date = date - timedelta(days=1)
            date = date.strftime("%Y-%m-%d %H:%M:%S")

            wiz_id = self.env['mailing.mailing.schedule.date'].sudo().create({"schedule_date": date,"mass_mailing_id": mail_id.id})
            wiz_id.with_context(active_ids=mail_id.id).sudo().set_schedule_date()
# reschedule history

class CustomAptReschLine(models.Model):
    _name = 'appointment.resch.line'
    _description = 'Reschedule'

    appointments_id = fields.Many2many('appointment.appointment',string='Appointment')

    creation_date = fields.Date(string='Creation Date')
    resch_date = fields.Date(string='Rescheduled on')
    resch_by = fields.Many2one('res.users', string='Rescheduled By', default=lambda self: self.env.uid)

    booking_date = fields.Date(string='Appointment Date')
    booked_by = fields.Many2one('res.users', string='Booked By')
    therapist_id = fields.Many2one('hr.employee', string='Therapist')

    company_id = fields.Many2one('res.company', string='Company')

    location_id = fields.Many2one('res.partner', string='Location')

    booking_start_date = fields.Date(string='Start Date')
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time', store=True)
    duration = fields.Float(string='Duration')

    time_id = fields.Many2one('time.time', string='Duration')
    time_slot_id = fields.Many2one('time.slot', string="Start & End Time")
    service_categ_id = fields.Many2one('appointment.category',string='Service Category',copy=False)
    appointments_type_id = fields.Many2one('calendar.appointment.type',string='Appointment Type',copy=False)

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    service_used = fields.Boolean('Service Used ')
    service_used_count = fields.Float('Service Used')
    package_product = fields.Boolean(string='Package',related='product_id.package_product')
    event_ticket = fields.Boolean(string='Ticket',related='product_id.event_ticket')

    @api.model
    def create(self, values):
        if values.get('order_id') and not values.get('name'):
            # set name based on the sequence specified on the config
            config = self.env['pos.order'].browse(values['order_id']).session_id.config_id
            if config.sequence_line_id:
                values['name'] = config.sequence_line_id._next()
        if not values.get('name'):
            # fallback on any pos.order sequence
            values['name'] = self.env['ir.sequence'].next_by_code('pos.order.line')
        # values['service_used_count'] = values['qty']
        return super(PosOrderLine, self).create(values)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    package_product = fields.Boolean('Package')
    duration_ids = fields.Many2many('duration.price','product_product_duration_ids',string='Duration Price')


class ProductCategory(models.Model):
    _inherit = 'product.category'


    active = fields.Boolean('Active')
