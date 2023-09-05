from datetime import datetime
from odoo import api, fields, models, _
import re
import uuid
from odoo.exceptions import ValidationError,UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'



    session_count = fields.Integer('Session Count', compute='get_count')
    visit_history_ids = fields.Many2many('appointment.appointment','appointment_appointment_visit_history_ids',string='Visit')
    appointment_history_ids = fields.Many2many('appointment.appointment','appointment_appointment_appointment_history_ids',string='Appointments')
    session_single_history_ids = fields.Many2many('appointment.appointment','appointment_remaining_appointment_history_ids',string='Single Session')
    credit_note_history_ids = fields.Many2many('appointment.line.id','appointment_line_credit_note_history_ids',string='Cancellation')
    purchase_history_ids = fields.Many2many('pos.order','pos_order_purchase_history_ids', string='Purchase')
    available_for_use_history_ids = fields.Many2many('pos.order','pos_order_available_for_use_history_ids', string='Purchase ')
    inactive_for_use_history_ids = fields.Many2many('pos.order','pos_order_inactive_for_use_history_ids', string='Inactive')
    purchase_detailed_history_ids = fields.Many2many('pos.order.line','pos_order_line_purchase_detailed_history_ids', string='Purchase Detailed View')
    appointment_line_history_ids = fields.Many2many('appointment.line.id','appointment_line_id_appointment_line_history_ids', string='Session Remaining')
    unpaid_visit_history_id = fields.Many2many('pos.order','pos_order_unpaid_visit_history_ids',string='Unpaid ')
    unpaid_visit_history_ids = fields.Many2many('appointment.appointment','appointment_appointment_unpaid_visit_history_ids',string='Unpaid')
    customer_journal_ids = fields.Many2many('account.move.line','customer_journal_ids_account_move_line', string='Customer Journal')
    message_ids = fields.Many2many('mail.message','message_ids_mail_message', string='Logs')
    avail_for_use_history_ids = fields.Many2many('appointment.appointment','appointment_appointment_avail_for_use_ids',string='Available For Use')
    booked_apt_history_ids = fields.Many2many('appointment.appointment','appointment_appointment_booked_upcoming_ids',string='Upcoming Apt')
    apt_single_cancel_ids = fields.Many2many('appointment.appointment','appointment_appointment_single_cancel_ids',string='Session Cancel')
    website_sale_ids = fields.Many2many('sale.order','web_sale_order_ids',string="Website Orders")
    website_sale_line_ids = fields.Many2many('sale.order.line','web_sale_order_line_ids',string="Website Orders")
    total_visits = fields.Integer('Total Visits', compute='get_total_visits')
    total_hours_visits = fields.Char('Total Hours', compute='get_total_hours_visits')
    current_packages = fields.Char('Current Package ', compute='_compute_get_current_packages')
    dummy_for_default_get = fields.Char('Current Package', compute='_dummy_for_default_get')
    purchase_detail_view = fields.Boolean('Show ')
    website_detail_view = fields.Boolean('Show')
    date_range = fields.Selection([('show','Show All Dates'),('selected','Select Date Range')])
    visit_start_date = fields.Date('Start Date',tracking=True)
    visit_end_date = fields.Date('End Date', tracking=True)
    apt_date_range = fields.Selection([('show', 'Show All Dates'), ('selected', 'Select Date Range')],string='Date Range ')
    apt_start_date = fields.Date('Start Date ', tracking=True)
    apt_end_date = fields.Date('End Date ', tracking=True)
    apt_type_id = fields.Many2one('calendar.appointment.type',string='Type',copy=False,tracking=True)

    po_date_range = fields.Selection([('show', 'Show All Dates'), ('selected', 'Select Date Range')],string='PO Date Range')
    po_start_date = fields.Date('PO Start Date', tracking=True)
    po_end_date = fields.Date('PO End Date', tracking=True)

    ac_date_range = fields.Selection([('show', 'Show All Dates'), ('selected', 'Select Date Range')], string='Acdate Range')
    ac_start_date = fields.Date('Acstart Date', tracking=True)
    ac_end_date = fields.Date('Acend Date', tracking=True)

    topay_cancellation_charge = fields.Float('Cancellation Charges',compute="_compute_topay_cancellation_charge")
    topay_no_show_charges = fields.Float('No Show Charges to Pay',compute="_compute_topay_no_show_charges")
    event_visit_ids = fields.Many2many('event.registration','client_event_register_visit_rel','visit_client_id','visit_event_registration_id',string='Event Registration visit')

    event_history_ids = fields.Many2many('event.registration','client_event_register_rel','client_id','event_registration_id',string='Event Registration')
    gift_event_history_ids = fields.Many2many('event.registration','event_registration_gift','client_id','event_registration_id',string="Event Registration Gift")
    event_cancel_ids = fields.Many2many('event.registration','client_event_cancel_rel','client_id','event_registration_id',string='Event Cancel')
    invoice_details_ids = fields.Many2many('account.move','account_move_client_rel', string='Invoice Detail')
    check_bool =  fields.Boolean('Check Boolean',default=False)
    url = fields.Char(string="Link to Share ",help="Used to get the customer signature template.")
    sign_template_inv = fields.Boolean(string="Sign Template ",help="Help to invisible the sign template for the respective customers")
    call_history_partner_ids = fields.One2many('partner.call.history','partner_call_id',string="History of Calls")
    quick_remarks_id = fields.Many2one('appointment.quick.remark',string="Quick Remarks")
    comment = fields.Text(string="Notes")
    latest_quick_remarks = fields.Char("Latest Remarks",help='Quick Remarks')
    latest_comment = fields.Text('Latest Notes',help='Latest comment')
    campaign_partner_ids = fields.One2many('campaign.partner.remarks','partner_id',string="Campaign Partner Remarks")
    campaign_quick_remarks = fields.Char("Latest Remarks",help='Quick Remarks to show in list',compute='compute_list_view')
    campaign_latest_comment = fields.Text('Latest Notes',help='Latest comment to show in list',compute="compute_list_view")
    lead_id = fields.Many2one('crm.lead',string="Lead ID")

    def compute_list_view(self):
        for each in self:
            search_campaign_id = self.env['campaign.partner.remarks'].search([('partner_id','=',each.id),('campaign_id','=',self.env.context.get('campaign_id'))])
            each.campaign_quick_remarks = search_campaign_id.remarks
            each.campaign_latest_comment= search_campaign_id.comment

    def compute_update_data(self):
        if self.env.context.get('campaign_id'):
            search_campaign_id = self.env['campaign.partner.remarks'].search([('campaign_id','=',self.env.context.get('campaign_id')),('partner_id','=',self.id)])
            if search_campaign_id:
                search_campaign_id.unlink()
            self.update({'campaign_partner_ids': [(0, 0, {'remarks': self.quick_remarks_id.name,'campaign_id': self.env.context.get('campaign_id'),'comment': self.comment})]})
            # update the crm stages
            campaign_id = self.env['asterisk_dialer.campaign'].browse(self.env.context.get('campaign_id'))
            lead_id = self.env['crm.lead'].search([('campaign_lead_id','=',campaign_id.id),('partner_id','=',self.id)],limit=1)
            crm_stage = self.env['crm.stage'].search([('quick_remarks_id','=',self.quick_remarks_id.id)],limit=1)
            if crm_stage:
                lead_id.stage_id = crm_stage

        if self.env.context.get('params') and 'lead_id' in self.env.context['params']:
            lead_id = self.env['crm.lead'].browse(self.env.context['params']['lead_id'])
            self.lead_id = lead_id.id
            crm_stage = self.env['crm.stage'].search([('quick_remarks_id','=',self.quick_remarks_id.id)],limit=1)
            if crm_stage:
                lead_id.stage_id = crm_stage

        if not self.quick_remarks_id or not self.comment:
            raise ValidationError(_('Please Check Quick Remarks/Notes'))
        if self.quick_remarks_id and self.comment:
            self.latest_quick_remarks = self.quick_remarks_id.name
            self.latest_comment = self.comment
            self.comment =" "
            self.quick_remarks_id = False
        self.check_remarks()


        
    def check_remarks(self):
        msg_body = "Quick Remarks :" + str(self.latest_quick_remarks) + " <br/> " + "Notes :" + str(self.latest_comment) + " <br/> "
        self.message_post(body=msg_body)


    @api.model
    def create(self, vals):
        # create the lead While click the plus button near search bar
        res = super(ResPartner, self).create(vals)
        res.check_bool= True
        if 'params' in self.env.context:
            if 'create_partner' in self.env.context['params']:
                master_aboutus_id = self.env['master.aboutus'].search([('name','=','Social Media')])
                lead_id = self.env['crm.lead'].create({
                    'name':res.name + '' + ' New Lead', 
                    'email_from':res.email,
                    'first_name':res.firstname,
                    'last_name':res.lastname,
                    'mobile':res.mobile,
                    'type': 'opportunity',
                    'partner_id':res.id,
                    'master_aboutus':master_aboutus_id.id
                    })
                res.lead_id = lead_id
                if res.quick_remarks_id:
                    crm_stage = self.env['crm.stage'].search([('quick_remarks_id','=',res.quick_remarks_id.id)],limit=1)
                    lead_id.stage_id = crm_stage
        # call signature mail template 08-08-22
        # res.action_get_sign_template()
        return res     

# while create the customer mail will send that customer with signature copy 08-08-22
    def action_send_sign_template(self):
        get_sign_template = self.env['sign.template'].search([('is_customer_template','=',True)])
        if get_sign_template:
            if get_sign_template.responsible_count > 1:
                self.url = False
            else:
                if not get_sign_template.share_link:
                    get_sign_template.share_link = str(uuid.uuid4())
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                self.url = "%s/sign/%s" % (base_url, get_sign_template.share_link)
                template_id = self.env.ref('custom_partner.customer_sign_mail_template')
                if template_id:
                    template_id.send_mail(self.id,force_send=True)
                    self.sign_template_inv = True
                    # Animation will appear once the email send successfully 12-09-22
                    message = self._get_animation_message()
                    if message:
                        return {
                            'effect': {
                                'fadeout': 'slow',
                                'message': message,
                                'img_url': '/web/static/src/img/smile.svg',
                                'type': 'rainbow_man'
                            }
                        }
    # Animation message 12-09-22
    def _get_animation_message(self):
        for rec in self:
            message = _('Mail sent Successfully.....!')
            return message

    # overwrite the base sign template return functionality to open the tree view once click the button 12-09-22
    def open_signatures(self):
        self.ensure_one()
        request_ids = self.env['sign.request.item'].search([('partner_id', '=', self.id)]).mapped('sign_request_id')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Signature(s)'),
            'view_mode': 'tree,form,kanban',
            'res_model': 'sign.request',
            'domain': [('id', 'in', request_ids.ids)],
            'context': {
                'search_default_reference': self.name,
                'search_default_signed': 1,
                'search_default_in_progress': 1,
            },
        }


    def _compute_topay_cancellation_charge(self):
        for rec in self:
            cc_partner_ids = self.env['appointment.appointment'].search([('partner_id', '=', rec.id),\
                ('due_cancellation_charge', '>',0)])
            cc_due = 0.0
            for partner in cc_partner_ids:
                cc_due += partner.due_cancellation_charge
            rec.topay_cancellation_charge = cc_due

    def _compute_topay_no_show_charges(self):
        for rec in self:
            nosh_partner_ids = self.env['appointment.appointment'].search([('partner_id', '=', rec.id),\
                ('no_show_charges', '>', 0)])
            nos_due = 0.0
            for nos in nosh_partner_ids:
                nos_due += nos.no_show_charges
            rec.topay_no_show_charges = nos_due

    def _dummy_for_default_get(self):
        for rec in self:
            rec.dummy_for_default_get = ''
            rec.populate_visit_values()
            rec.event_registration_values()
            rec.account_invoice_values()
            rec.action_sale_order_values()
            rec.action_sale_order_line_values()

    def action_sale_order_values(self):
        sale_line_id = self.env['sale.order'].search([('customer_id','=',self.id),('state','=','sale')])
        self.website_sale_ids = sale_line_id.ids
    def action_sale_order_line_values(self):
        sale_line_id = self.env['sale.order.line'].search([('order_id.customer_id','=',self.id)])
        self.website_sale_line_ids = sale_line_id.ids
    
    def event_registration_values(self):
        event_id = self.env['event.registration'].search(['|',('partner_id','=',self.id),('extras_partner_id','=',self.id)])
        self.event_history_ids = event_id.ids or False
        event_partner_id = self.env['event.registration'].search([('gift_name_partner_id','=',self.id),('type_booking','=','type_gift')])
        if event_partner_id.partner_id != event_partner_id.gift_name_partner_id:
            self.gift_event_history_ids = event_partner_id.ids or False

        event_cancel_id = self.env['event.registration'].search([('partner_id','=',self.id),('state','=','cancel')])
        self.event_cancel_ids = event_cancel_id.ids or False
        visit_event_registration = self.env['event.registration'].search([('partner_id','=',self.id),('state','=','done')])
        self.event_visit_ids = visit_event_registration.ids or False

    def account_invoice_values(self):
        account_id = self.env['account.move'].search([('partner_id','=',self.id),('move_type','=','out_invoice')])
        self.invoice_details_ids = account_id.ids or False

    def populate_visit_values(self):
        if self:
            apt_id = self.env['appointment.appointment'].search([('partner_id','=',self.id)])
            visit_id = self.env['appointment.appointment'].search([('partner_id','=',self.id),('state','=','done')])
            self.appointment_history_ids = apt_id.ids or False; self.visit_history_ids = visit_id.ids or False
            single_remain_apt_ids = self.env['appointment.appointment'].search([('partner_id','=',self.id),\
                ('state','=','new'),('session_type','=','type_single'),('booking_date','=',False)])
            self.session_single_history_ids = single_remain_apt_ids.ids or False
            cancel_id = self.env['appointment.line.id'].search([('partner_id','=',self.id),('state_line','=','cancel')])
            self.credit_note_history_ids = cancel_id.ids or False
            single_cancel_id = self.env['appointment.appointment'].search([('partner_id','=',self.id),('state','=','cancel')])
            self.apt_single_cancel_ids = single_cancel_id.ids or False
            purchase_id = self.env['pos.order'].search([('partner_id','=',self.id)])
            self.purchase_history_ids = purchase_id.ids or False
            lines = []
            for i in purchase_id:
                for j in i.lines:
                    lines.append(j.id)
            self.purchase_detailed_history_ids = lines or False
            purchase_lst = []
            purchase_use_id = self.env['appointment.appointment'].search([('partner_id','=',self.id),('state','=','new'),\
                ('session_type','=','type_single')])
            purchase_sid = self.env['appointment.appointment'].search([('partner_id','=',self.id),('state','=',['new','confirm','ongoing']),\
                ('session_type','=','type_package')]) #,('payment_status_apt','in',['payment_received','paid'])
            for i in purchase_use_id:
                if i.pos_order_id: purchase_lst.append(i.pos_order_id.id)
            for i in purchase_sid:
                if i.pos_order_id: 
                    for line in i.appointment_line_id:
                        if i.pos_order_id.id not in purchase_lst and line.state_line == 'draft': 
                            purchase_lst.append(i.pos_order_id.id)
            av_for_use_ids = self.env['appointment.appointment'].search([('partner_id','=',self.id),('state','=','new'),('session_type','=','type_single')])
            self.avail_for_use_history_ids = av_for_use_ids.ids or False
            booked_apt_ids = self.env['appointment.appointment'].search([('partner_id','=',self.id),('state','=','confirm'),('session_type','=','type_single')])
            self.booked_apt_history_ids = booked_apt_ids.ids or False            
            self.available_for_use_history_ids = purchase_lst or False
            remaining_id = self.env['appointment.line.id'].search([
                ('appointment_id.partner_id','=',self.id),('state_line','=','draft')])
            self.appointment_line_history_ids = remaining_id.ids or False
            apt_id = self.env['appointment.appointment'].search([('partner_id','=',self.id),('state','not in',['no_show','cancel']),\
                ('payment_status_apt','in',['no_paid','partially_paid'])])
            apt = []
            for i in apt_id:
                if i.pos_order_id: apt.append(i.pos_order_id.id)
            self.unpaid_visit_history_id = apt or False
            inactive_id = self.env['appointment.appointment'].search([('partner_id','=',self.id),('state','=','done'),('pos_order_id','!=',False)])
            inactive = []
            for i in inactive_id:
                inactive.append(i.pos_order_id.id)
            self.inactive_for_use_history_ids = inactive or False
            journal_id = self.env['account.move.line'].search([('partner_id','=',self.id),('display_type', 'not in', ('line_section', 'line_note'))])
            self.customer_journal_ids = journal_id.ids or False
            message_id = self.env['mail.message'].search([('partner_id','=',self.id),('message_type','!=','email')])
            self.message_ids = message_id.ids or False
            return True

    @api.onchange("ac_start_date")
    def compute_ac_dates(self):
        if self.ac_date_range == 'selected':
            rec = self.customer_journal_ids.search([('partner_id','=',self.ids),('date', '>=', self.ac_start_date), ('date', '<=', self.ac_end_date),('display_type', 'not in', ('line_section', 'line_note'))])
            for records in rec:
                self.customer_journal_ids = rec.ids or False

    @api.onchange("ac_date_range")
    def all_dates(self):
        if self.ac_date_range == 'show':
            visit_id = self.customer_journal_ids.search([('display_type', 'not in', ('line_section', 'line_note'))])
            self.customer_journal_ids = visit_id.ids or False

    @api.onchange("po_date_range")
    def get_all_pos(self):
        if self.po_date_range == 'show':
            purchase_id = self.purchase_history_ids.search([('partner_id', '=', self.ids)])
            self.purchase_history_ids = purchase_id.ids or False

    @api.onchange("po_start_date")
    def purchase_filter(self):
        if self.po_date_range == 'selected':
            d1 = datetime.strftime(self.po_start_date, "%Y-%m-%d 00:00:00")
            d2 = datetime.strftime(self.po_end_date, "%Y-%m-%d 00:00:00")
            rec = self.purchase_history_ids.search([('date_order', '>=', d1),('date_order', '<=', d2),
                 ('partner_id', '=', self.ids)])
            for records in rec:
                self.purchase_history_ids = rec.ids or False

    @api.onchange("apt_type_id")
    def get_apt_type(self):
        rec = self.appointment_history_ids.search([('partner_id', '=', self.ids),('appointments_type_id','=',self.apt_type_id.id)])
        self.appointment_history_ids = rec.ids or False

    @api.onchange("apt_start_date")
    def compute_apt_dates(self):
        if self.apt_date_range == 'selected':
            rec = self.appointment_history_ids.search(
                [('booking_date', '>=', self.apt_start_date), ('booking_date', '<=', self.apt_end_date),('partner_id','=',self.ids)])
            for records in rec:
                self.appointment_history_ids = rec.ids or False

    @api.onchange("apt_date_range")
    def apt_all_dates(self):
        if self.apt_date_range == 'show':
            apt_id = self.appointment_history_ids.search([('partner_id','=',self.ids)])
            self.appointment_history_ids = apt_id.ids or False

    @api.onchange("visit_start_date")
    def compute_dates(self):
        if self.date_range == 'selected':
            rec = self.visit_history_ids.search([('booking_date', '>=', self.visit_start_date),('booking_date', '<=', self.visit_end_date),('state', '=', 'done')])
            for records in rec:
                self.visit_history_ids = rec.ids or False

    @api.onchange("date_range")
    def all_dates(self):
        if self.date_range == 'show':
            visit_id = self.visit_history_ids.search([('state', '=', 'done')])
            self.visit_history_ids = visit_id.ids or False

    def get_total_visits(self):
        self.total_visits = len(self.visit_history_ids)

    def get_total_hours_visits(self):
        if self.visit_history_ids:
            time_total = 0.00
            for i in self.visit_history_ids:
                time_total += i.time_id.duration
                mins_visits = int(time_total)
                total_hrs_visits = int(mins_visits / 60)
                total_mins_visits = int(mins_visits % 60)
                self.total_hours_visits = "{}:{} Hours".format(int(total_hrs_visits), int(total_mins_visits))
        else:
            self.total_hours_visits = 0

    def _compute_get_current_packages(self):
        self.current_packages = ''; cache = ''
        remaining_id = self.env['appointment.appointment'].search([('partner_id','=',self.id),('session_type','=','type_package')])
        for i in remaining_id:
            serv = ''
            for j in i.appointment_line_id:
                if j.state_line == 'draft': serv = '/' + i.appointments_type_id.name
            cache += serv
        self.current_packages = cache[1:]

    def attendees_report(self):
        action = self.env.ref('custom_partner.action_event_registration_attendees_view')
        return {
            'name': 'Attendees Report',
            'type': 'ir.actions.act_window',
            'views': [(action.id, 'pivot'),(False, 'kanban'),(False, 'tree'),(False, 'form'),(False, 'calendar'),(action.id, 'graph')],
            'target': 'current',
            'res_model': 'event.registration',
            'view_mode': 'pivot,kanban,tree,form,calendar,graph',
            'domain': [('partner_id', '=', self.id)],
        }

    def action_partner_appt(self):
        self.populate_visit_values()
        self.event_registration_values()
        return {
                'type': 'ir.actions.act_window',
                'name': 'Contact',
                'view_mode': 'form',
                'res_model': 'res.partner',
                'view_id': False,
                'views': [(self.env.ref('custom_partner.res_partner_history_history_from_view').id, 'form')],
                'res_id': self.id,
                # 'clear_breadcrumb': True,
                'target': 'main',
                }
    
    def go_contact_view(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Contact',
                'view_mode': 'form',
                'res_model': 'res.partner',
                'view_id': False,
                'views': [(self.env.ref('base.view_partner_form').id, 'form')],
                'res_id': self.id,
                'target': 'main',
                # 'context': {'default_appointment_history_ids': apt_id.ids,},
                }

    def book_appointment(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Appointment',
                'view_mode': 'form',
                'res_model': 'appointment.appointment',
                'target': 'current',
                'context': {
                            'default_partner_id': self.id, 
                            'appointment_visit_wiz': False,
                            },
                }
    # old method for book event
    # def book_event(self):
    #     return {
    #             'type': 'ir.actions.act_window',
    #             'name': 'Event',
    #             'view_mode': 'tree,form',
    #             'res_model': 'event.event',
    #             'target': 'current',
    #             'context': {},
    #             }

    def book_event(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Event Registration',
                'view_mode': 'form',
                'res_model': 'event.registration',
                'target': 'current',
                'context': {
                            'default_partner_id': self.id, 
                            },
                }



    def go_to_pos(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Point of Sale',
                'view_mode': 'kanban,tree,form',
                'res_model': 'pos.config',
                'target': 'new',
                }

    @api.depends('name')
    def get_count(self):
        for record in self:
            rec = self.env['appointment.appointment'].search([('partner_id','=',self.id)])
            count = len(rec)
            record.session_count = count

    # To redirect respective customer with edit mode 04-8-22
    def redirect_to_contact_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contact',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'view_id': False,
            'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},
            'views': [(self.env.ref('custom_partner.res_partner_history_history_from_view').id,'form')],
            'flags': {'initial_mode': 'edit'},
            'res_id':self.id,

            }

class PartnerCallHistory(models.Model):
    _name = "partner.call.history"
    _description ="Partner Call History"

    remarks = fields.Html(string="Notes")
    call_date = fields.Datetime(string="Date")
    user_id = fields.Many2one('res.users',string="User")
    partner_call_id = fields.Many2one('res.partner')
    quick_remark = fields.Char(string="Quick Remarks")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    event_sale_id = fields.Many2one('event.event',string="Event")

class PosCartLine(models.Model):
    _name = 'pos.cart.line'
    _description = 'Pos Cart Line'

    partner_id = fields.Many2one('res.partner',string="Partner")
    product_id = fields.Many2one('product.product',string="Product")


class SignTemplate(models.Model):
    _inherit = "sign.template"

    is_customer_template = fields.Boolean(string="Is Customer Template")

    # Raise the warning for customer template multi selection 06-09-22
    @api.constrains('is_customer_template')
    def action_validate_template(self):
        get_cust_sign_template = self.search([('is_customer_template','=',True),('id','!=',self.id)],limit=1)
        if get_cust_sign_template and self.is_customer_template:
            raise UserError(_("Customer template already assigned. \n Template Name - %s" % (get_cust_sign_template.name)))


     
class CampaignPartnerRemarks(models.Model):
    _name = "campaign.partner.remarks"
    _description ="Partner Call History"

    remarks = fields.Char(string="Quick Remarks")
    campaign_id = fields.Many2one('asterisk_dialer.campaign',string="Campaign")
    partner_id = fields.Many2one('res.partner',string="Partner")
    comment = fields.Text(string="Notes")
