from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
import re
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat

class ResPartner(models.Model):
    _inherit = 'res.partner'
#     _sql_constraints = [
#      ('name_uniq', 'unique(name)', 'Customer name already exist'),
#     ]

    #due to image not loaded from URL
    def _get_gravatar_image(self, email):
        return False

    @api.onchange('alternate_mobile', 'country_id', 'company_id')
    def _onchange_alternate_mobile_validation(self):
        if self.alternate_mobile:
            self.alternate_mobile = self.phone_format(self.alternate_mobile)

    @api.model
    def _default_branch_id(self):
        return self.env['master.branch'].search([('name','=','Abu Dhabi')])
    
    @api.model
    def _default_about(self):
        return self.env['master.aboutus'].search([('name','=','Social Media')])

    @api.model
    def set_current_company_default(self):
        return self.env['res.company'].search([('id', '=', self.env.company.id)]).ids

    def _get_company_allowed_domain(self):
        if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]
    
    name = fields.Char('Name')
    dob = fields.Date('Date of Birth ')
    vat = fields.Char(string='VAT ID')
    gender = fields.Selection([('male','Male'),('female','Female'),('other','Others')],string='Gender',default='male')
    branch_id = fields.Many2one('master.branch',string="Branch",default=_default_branch_id)
    online_id = fields.Many2one('master.online',string="Online")
    reffer_ids = fields.Many2one('master.refferal',string="Referral Type")
    blacklist_client = fields.Boolean('Black Listed')
    visited_by = fields.Selection([('person','In Person'),('online','Online')],string='Visit ')
    sequence = fields.Char('Sequence',readonly=True, required=True, copy=False, default=' ')    
    master_aboutus = fields.Many2one('master.aboutus',string="How Did You Hear About Us?",default=_default_about)
    master_intrestedin = fields.Many2one('master.intrestedin',string="What Services Are you Interested In?")
    master_struggling = fields.Many2one('master.struggling',string="Which Areas are you struggling with?")
    master_holistic = fields.Many2one('master.holistic',string="Which Holistic Approaches are you interested in?")
    master_membership = fields.Many2one('master.membership',string="Membership Status?")    
    date_first_visit = fields.Date('Date of First Visit')
    date_last_visit = fields.Date('Date of Last Visit')
    total_number_visit = fields.Char('Total Number Visits')
    average_visit_month = fields.Char('Average Visits Per Month')
    average_service_utilize = fields.Char('Average Service Utilization Per Visit')
    total_spend = fields.Char('Total Spend')
    total_sale = fields.Char('Total Sale')
    by_cash = fields.Char('By Cash')
    by_credit = fields.Char('Credit Card')
    membership_expires = fields.Date('Membership Expires')
    alternate_email = fields.Char("Alternate Email")
    alternate_mobile = fields.Char("Alternate Mobile")
    point_of_contact = fields.Char('Point Of Contact')
    job_title = fields.Many2one('hr.employee.category', string='Job Title')
    city_id = fields.Many2one('city.master',string='City ' , domain="[('country_id', '=?', country_id),('state_id','=?',state_id)]")
    location_ids = fields.Many2many('res.company',string='Locations', default=set_current_company_default ,domain=_get_company_allowed_domain)
    is_a_customer = fields.Boolean(string='Customer',default=True)
    is_a_vendor = fields.Boolean(string='Vendor')
    is_job_location = fields.Boolean(string='Is Job Location')
    sub_parent_id = fields.Many2one('res.partner')
    reffer_type_id = fields.Many2one('master.refferal',string="Lead Source")
    total_due = fields.Monetary('Balance',compute="_compute_set_credit")
    account_balance = fields.Monetary('Balance ', compute="get_account_balance")
    last_visit_details = fields.Char('Last Visit Details', compute='_get_last_visit_detail')
    next_visit_details = fields.Char('Next Appointment Details', compute='_get_next_visit_detail')
    customer_balance = fields.Float("Customer Balance",compute="get_customer_balance")
    website_quote = fields.Text('Website Quote')
    type = fields.Selection(selection_add=[], string='Address Type',
        default='private',
        help="Invoice & Delivery addresses are used in sales orders. Private addresses are only visible by authorized users.")
  

    def get_customer_balance(self):
        balance = 0
        self.customer_balance = 0
        for each in self:
            balance = each.custom_credit  or 0
            # apt_ids = self.env['appointment.appointment'].search([('partner_id', '=', each.id), ('pos_order_id', '=', False),('state','not in',('void','cancel','no_show'))])
            # if apt_ids:
            #     for each_balance in apt_ids:
            #         balance -= each_balance.amount_unit_price_tot + (each_balance.amount_unit_price_tot * 0.05 )
            #         each.customer_balance =balance
            # event_ids = self.env['event.registration'].search([('partner_id', '=', each.id), ('pos_order_id', '=', False),('state','=',"draft")])
            # if event_ids:
            #     for event_balance in event_ids:
            #         balance -= event_balance.ticket_price + (event_balance.ticket_price * 0.05 )
            #         each.customer_balance =balance
            pos_ids = self.env['pos.order'].search([('partner_id', '=', each.id),('state','!=',"cancel")])
            if pos_ids:
                for pos_balance in pos_ids:
                    balance -= (pos_balance.amount_total - pos_balance.amount_paid)
                    each.customer_balance = balance
            if each.customer_balance <= 0:
                account_ids = self.env['account.move'].search([('move_type', '=', "entry"), ('journal_id.code', '=', "PT"),('state','=','posted')])
                for each_account in account_ids:
                    for each_line in each_account.line_ids:
                        if each.id == each_line.partner_id.id and each_line.debit == 0 and each_line.credit != 0 :
                            balance = balance + each_line.credit
                each.customer_balance = balance

            else:
                each.customer_balance = balance

            website_invoice = self.env['account.move'].search([('move_type','=','out_invoice'),('payment_state','=','not_paid'),('partner_id','=',each.id),('sale_id','!=',False)])
            if website_invoice:
                amount = sum(inv.amount_residual for inv in website_invoice)
                balance = balance - amount
                each.customer_balance = balance



    def _get_last_visit_detail(self):
        for record in self:
            apt = []; today = date.today(); record.last_visit_details = ''
            last_visit = self.env['appointment.appointment'].search(
                [('partner_id', '=', record.id), ('state', '=', 'done'),
                 ('booking_date', '<=', today)], order='booking_date desc')
            event_last_visit = self.env['event.registration'].search(
                [('partner_id', '=', record.id), ('event_payment_status', '=', 'paid')],order ="write_date desc",limit=1)
            record.last_visit_details = "No Records Found !"
            if last_visit:
                for i in last_visit:
                    if i.booking_date and i.time_slot_id:
                        date_str = i.booking_date.strftime("%d/%m/%Y")
                        date_time = datetime.strptime(date_str + ' ' + i.time_slot_id.start_time, "%d/%m/%Y %H:%M")
                        apt.append(date_time)
                        input = max(apt)
                        x_time = input.strftime("%H:%M")
                        res = self.env['appointment.appointment'].search([('partner_id', '=', record.id), ('state', '=', 'done'),
                             ('booking_date', '=', input.strftime("%Y-%m-%d")), ('time_slot_id.start_time', '=', x_time)])
                        record.last_visit_details = res.booking_date.strftime("%d/%m/%Y") + ' ' + str(res.time_slot_id.name.split('-')[0]) + ' - ' + str(res.appointments_type_id.name)
            else:
                # get the last visit based on the event 20-09-22
                for event in event_last_visit.event_id:
                    if event.stage_id.pipe_end == True:
                        multi_date = self.env['multi.date.line'].search([('event_id.id' , '=',event.id),('event_id.active', '=', True)],order="m_date_begin desc",limit=1)
                        if multi_date:
                            event_date = multi_date.m_date_begin.strftime("%Y-%m-%d")
                            if event_date <= str(today):
                                time = multi_date.hour_time_begin + ':'+multi_date.min_time_begin
                                record.last_visit_details = multi_date.date_end.strftime("%d/%m/%Y") + ' ' + time + ' - ' + multi_date.event_id.event_sub_categ_id.name
                       

    def _get_next_visit_detail(self):
        for record in self:
            apt = [];today = date.today(); record.next_visit_details = ''
            next_visit = self.env['appointment.appointment'].search([('partner_id', '=', record.id), ('state', 'not in', ['done', 'cancel']),
                 ('booking_date', '>=', today)], order='booking_date asc')
            event_next_visit = self.env['event.registration'].search(
                [('partner_id', '=', record.id), ('event_payment_status', 'not in', ['paid','payment_received','refund'])],order ="write_date desc",limit=1)
            record.next_visit_details = "No Records Found !"
            if next_visit:
                for i in next_visit:
                    if i.booking_date and i.time_slot_id:
                        date_str = i.booking_date.strftime("%d/%m/%Y")
                        date_time = datetime.strptime(date_str + ' ' + i.time_slot_id.start_time, "%d/%m/%Y %H:%M")
                        apt.append(date_time)
                        input = min(apt)
                        x_time = input.strftime("%H:%M")
                        recs = self.env['appointment.appointment'].search(
                            [('partner_id', '=', record.id), ('state', 'not in', ['done', 'cancel']),
                             ('booking_date', '=', input.strftime("%Y-%m-%d")), ('time_slot_id.start_time', '=', x_time)])
                        if recs:
                            for rec in recs:
                                record.next_visit_details = rec.booking_date.strftime("%d/%m/%Y") + ' ' + \
                                    str(rec.time_slot_id.name.split('-')[0]) + ' - ' + str(rec.appointments_type_id.name or '')
            else:
                # get the next visit based on the event 20-09-22
                for event in event_next_visit.event_id:
                    if  event.stage_id.is_waiting == True or event.stage_id.is_published == True:
                        multi_date =self.env['multi.date.line'].search([('event_id.id' , '=',event.id)],order= 'm_date_begin asc',limit=1)
                        if multi_date:
                            event_date = multi_date.m_date_begin.strftime("%Y-%m-%d")
                            if event_date >= str(today):
                                time = multi_date.hour_time_begin + ':'+multi_date.min_time_begin
                                record.next_visit_details = multi_date.date_end.strftime("%d/%m/%Y") + ' ' + time + ' - ' + multi_date.event_id.event_sub_categ_id.name
                        
                

    def _compute_set_credit(self):
        for rec in self:
            rec.total_due = 0
            account_types = []
            receivable_type = self.env.ref('account.data_account_type_receivable').id
            payable_type = self.env.ref('account.data_account_type_payable').id
            account_types.extend([receivable_type, payable_type])
            domain = [('partner_id', '=', rec.id), ('amount_residual', '!=', 0),
                    ('account_id.user_type_id', 'in', account_types)]
            domain += [('move_id.state', '=', 'posted')]
            customer_balance = sum([x.amount_residual for x in self.env['account.move.line'].search(domain)])
            rec.total_due = abs(customer_balance) if customer_balance < 0 else 0
            return rec.total_due

    def get_account_balance(self):
        for rec in self:
            if rec.total_due < 0:
                rec.account_balance = rec.total_due + -(rec.total_due)*2
            elif rec.total_due >0:
                rec.account_balance = rec.total_due + -(rec.total_due)*2
            else:
                rec.account_balance = 0

    @api.model
    def create(self,vals):
        if vals.get('company_type')=='person' or vals.get('company_type')=='company':
            if vals.get('company_type') == 'person':
                firstname_id = self.search([('firstname','=',vals.get('firstname')),('lastname','=',vals.get('lastname'))])
                if firstname_id:
                    raise UserError(_('Customer name already exist.'))
            else:
                if vals.get('name'):
                    customer_id = self.search([('name','=',vals['name'])])
                    if customer_id:
                        raise UserError(_('Customer name already exist'))
            if vals['email'] != False and not vals['email'] == "" :
                email_id = self.search(['|',('email','=',vals['email']),('alternate_email','=',vals['email'])])
                if email_id:
                    raise UserError(_('Email already exist'))
            if 'phone' in vals and vals['phone'] != False:
                phone_id = self.search(['|','|',('phone','=',vals['phone']),('mobile','=',vals['phone']),('alternate_mobile','=',vals['phone'])])
                if phone_id:
                    raise UserError(_('Phone number already exist'))
            if 'mobile' in vals and vals['mobile'] != False:
                phone_id = self.search(['|','|',('phone','=',vals['mobile']),('mobile','=',vals['mobile']),('alternate_mobile','=',vals['mobile'])])
                if phone_id:
                    raise UserError(_('Mobile number already exist'))
            if 'alternate_mobile' in vals and vals['alternate_mobile'] != False and not vals['alternate_mobile'] == '':
                phone_id = self.search(['|','|',('phone','=',vals['alternate_mobile']),('mobile','=',vals['alternate_mobile']),('alternate_mobile','=',vals['alternate_mobile'])])
                if phone_id:
                    raise UserError(_('Alternate Mobile number already exist'))
            if 'alternate_email' in vals and vals['alternate_email'] != False and not vals['alternate_email'] == '':

                email_id = self.search(['|',('email','=',vals['alternate_email']),('alternate_email','=',vals['alternate_email'])])
                if email_id:
                    raise UserError(_('Alternate Email already exist'))
            if 'phone' in vals:
                if (vals['phone'] == vals['mobile'] and (vals['phone'] or vals['mobile'])) or (vals['phone'] == vals['alternate_mobile'] and (vals['phone'] or vals['alternate_mobile'])) or (vals['alternate_mobile'] == vals['mobile'] and (vals['alternate_mobile'] or vals['mobile'])):
                    raise UserError(_('Phone number and mobile numbers should not be same'))
            if 'email' in vals:
                if vals['alternate_email'] == vals['email'] and (vals['email'] or vals['alternate_email']):
                    raise UserError(_('Email and Alternate Email should not be same'))
            sequence_id = self.env['ir.sequence'].next_by_code('res.partner') or ' '
            vals['sequence'] = str(sequence_id)                
        return super(ResPartner, self).create(vals)

    def write(self,vals):
        for each in self:
            if vals.get('firstname') or vals.get('lastname'):
                firstname_id = self.search([('firstname','=',vals.get('firstname') or each.firstname),('lastname','=',vals.get('lastname') or each.lastname),('id','!=', each.id)])
                if firstname_id:
                    raise UserError(_('Customer name already exist.'))
            if vals.get('name'):
                customer_id = self.search([('name','=',vals['name']),('id','!=', each.id)])
                if customer_id:
                    raise UserError(_('Customer name already exist'))
            if vals.get('email') and not vals['email'] == "":
                email_id = self.search(['|',('email','=',vals['email']),('alternate_email','=',vals['email']),('id','!=', each.id)])
                if email_id:
                    raise UserError(_('Email already exist'))
            if vals.get('phone'):
                phone_id = self.search(['|','|',('phone','=',vals['phone']),('mobile','=',vals['phone']),('alternate_mobile','=',vals['phone']),('id','!=', each.id)])
                if phone_id:
                    raise UserError(_('Phone number already exist'))
            if vals.get('mobile'):
                phone_id = self.search(['|','|',('phone','=',vals['mobile']),('mobile','=',vals['mobile']),('alternate_mobile','=',vals['mobile']),('id','!=', each.id)])
                if phone_id:
                    raise UserError(_('Mobile number already exist'))
            if vals.get('alternate_mobile') and not vals.get('alternate_mobile') == '':
                phone_id = self.search(['|','|',('alternate_mobile','=',vals['alternate_mobile']),('phone','=',vals['alternate_mobile']),('mobile','=',vals['alternate_mobile']),('id','!=', each.id)])
                if phone_id:
                    raise UserError(_('Alternate Mobile number already exist'))
            if vals.get('alternate_email') and not vals['alternate_email'] == '':
                phone_id = self.search(['|',('email','=',vals['alternate_email']),('alternate_email','=',vals['alternate_email']),('id','!=', each.id)])
                if phone_id:
                    raise UserError(_('Alternate Email already exist'))
            if ((vals.get('phone') or each.phone) == (vals.get('mobile') or each.mobile) and (vals.get('phone') or vals.get('mobile'))) or ((vals.get('phone') or each.phone) == (vals.get('alternate_mobile') or each.alternate_mobile) and (vals.get('phone') or vals.get('alternate_mobile'))) or ((vals.get('alternate_mobile') or each.alternate_mobile) == (vals.get('mobile') or each.mobile) and (vals.get('alternate_mobile') or vals.get('mobile'))):
                raise UserError(_('Phone number and mobile numbers should not be same'))
            if (vals.get('alternate_email') or each.alternate_email) == (vals.get('email') or each.alternate_email) and (vals.get('email') or vals.get('alternate_email')):
                raise UserError(_('Email and Alternate Email should not be same'))
        return super(ResPartner, self).write(vals)

    @api.onchange("sub_parent_id")
    def _onchange_address_type_for_sub_parent(self):
        if self.sub_parent_id:
            self.type = 'private'

    @api.onchange("dob")
    def _compute_dob(self):
        if self.dob:
            if datetime.strptime(str(self.dob), '%Y-%m-%d').date() >= datetime.now().date():
                self.dob = ''

class AccountMove(models.Model):
    _inherit = 'account.move'

    gift_voucher = fields.Float('Gift Voucher')

    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
                # 'default_gift_voucher':self.gift_voucher
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

class ResCompany(models.Model):
    _inherit = 'res.company'

    abbreviation = fields.Char('Abbreviation')
    landmark = fields.Char('Landmark')

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    gift_voucher = fields.Float('Gift Voucher')

    def _create_payment_vals_from_wizard(self):
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        payment_vals['gift_voucher'] = self.gift_voucher
        return payment_vals

