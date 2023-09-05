from odoo import api, fields, models, _
import re
from odoo.tools import float_is_zero
from datetime import datetime, timedelta, date
import pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from odoo import http, tools, _
from odoo.http import request, Response
import json, werkzeug
import requests
import urllib.request
import urllib
import logging
from odoo.exceptions import ValidationError, UserError


_logger = logging.getLogger(__name__)

#event mail sending
class EventStage(models.Model):
    _inherit = 'event.stage'

    template_id = fields.Many2one('mail.template', string='Email Template')

class EventType(models.Model):
    _inherit = 'event.type'

    @api.depends('use_mail_schedule')
    def _compute_event_type_mail_ids(self):
        for template in self:
            if not template.use_mail_schedule:
                template.event_type_mail_ids = [(5, 0)]
            elif not template.event_type_mail_ids:
                template.event_type_mail_ids = False

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        res = super(AccountPaymentRegister, self).action_create_payments()
        reg_id = self.env['event.registration'].search([],limit=1)
        reg_id.payment_thx_mail_set()
        return res

class EventRegistration(models.Model):
    _inherit = 'event.registration'

    def _compute_amount_due(self):
        self.set_dummy_amount_due = ''
        self.amount_due =0.0
        for rec in self:
            if rec.invoice_id:
                rec.amount_due = rec.invoice_id.amount_residual

    def payment_thx_mail_set(self):
        reg_id = self.env['event.registration'].search([])
        for rec in reg_id:
            if rec.payment_thx_mail == False and rec.payment_status == 'paid':
                note_id = self.env['event.notification'].search([],limit=1)
                ctx = dict()
                if note_id.attendees_active_notification_payment == True:
                    for i in note_id.event_attendee_payment_thx_list:
                        for il in self.env['mailing.contact'].sudo().search([]):
                            if il.email and i.id in il.subscription_list_ids.ids and note_id.event_attendee_payment_thx_mail:
                                ctx.update({
                                    'event':rec.event_id.name,
                                    'email':il.email,
                                    'customer_name':rec.name,
                                    })
                                for kk in note_id.event_attendee_payment_thx_mail:
                                    kk.sudo().with_context(ctx).send_mail(rec.id, force_send=True)
                            if il.mobile and i.id in il.subscription_list_ids.ids and note_id.event_attendee_payment_thx_whatsapp:
                                rec.event_id.whatsapp_sent(partner_id=il.id,tmpl_id=note_id.event_attendee_payment_thx_whatsapp.id,pt='mailing_list',apt=rec.id)

                    if rec.email and note_id.event_attendee_payment_thx_mail:
                        for emp in note_id.event_attendee_payment_thx_mail:
                            ctx.update({
                                'event':rec.event_id.name,
                                'email':rec.email,
                                'customer_name':rec.name,
                                })
                            emp.sudo().with_context(ctx).send_mail(rec.id, force_send=True)
                            rec.payment_thx_mail == True

                    if rec.mobile and note_id.event_attendee_payment_thx_whatsapp:
                        rec.event_id.whatsapp_sent(partner_id=rec.id,tmpl_id=note_id.event_attendee_payment_thx_whatsapp.id,pt='event_registration',apt=rec.id)

    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id)
    paid_attendees = fields.Selection([('paid','Paid'),('unpaid','Unpaid')],default='unpaid',string="Event Payment Status")
    invoice_id = fields.Many2one('account.move',string="Invoice")
    company_currency_id = fields.Many2one('res.currency', readonly=True, string='Currency', related="company_id.currency_id")
    amount_due = fields.Monetary('Amount Due',currency_field='company_currency_id',compute='_compute_amount_due')

    amount_total = fields.Monetary('Amount Total',currency_field='company_currency_id')
    set_dummy_amount_due = fields.Char('Dummy Amount Due')

    expire = fields.Boolean('Expired',readonly=True)
    total_expire = fields.Boolean('Total Expires')
    total_expire_can = fields.Boolean('Cancel Expires')

    expire_id = fields.Many2one('event.registration')
    expire_datetime = fields.Datetime('Expire Datetime')
    quick_remarks_id = fields.Many2one('appointment.quick.remark',string='Quick Remarks',tracking=True)
    notes = fields.Text(string='Internal Notes',tracking=True)

    payment_thx_mail = fields.Boolean('Payment Thx Mail')
    ack_2hrs_mail = fields.Boolean('ack_2hrs_mail')

    event_expire_date = fields.Datetime(string="Expire Date", related='event_id.date_end')
    partner_balance = fields.Monetary('Balance',currency_field='company_currency_id',related='partner_id.account_balance')
    account_balance = fields.Monetary('Customer Balance ', related='partner_id.account_balance',currency_field='company_currency_id')
    customer_balance = fields.Float(' Customer Balance ',compute="_compute_partner_balance")
    pre_cancellation_type = fields.Selection([('early', 'Early'), ('late', 'Late')], string='Method')
     #,related='partner_id.account_balance'
    web = fields.Boolean('Web', compute='check_web') #,related='event_id.website_published'
    signed = fields.Boolean('Signed In')
    cancel_notes = fields.Text(string="Cancellation Reason",tracking=True)

    def check_web(self):
        for rec in self:
            if rec.event_id.type_event == 'type_online':
                rec.web = True
            else:
                rec.web = False

    def _compute_partner_balance(self):
        self.customer_balance= 0.0
        for each in self:
            if each.partner_id:
                each.customer_balance = each.partner_id.customer_balance


    def action_set_done(self):
        res = super(EventRegistration, self).action_set_done()
        self.signed = True

        note_id = self.env['event.notification'].search([],limit=1)
        ctx = dict()
        if note_id.attendees_after_active_notification_event == True:
            for i in note_id.event_attendee_attended_list:
                for il in self.env['mailing.contact'].sudo().search([]):
                    if il.email and i.id in il.subscription_list_ids.ids and note_id.event_attendee_attended_mail:
                        ctx.update({
                            'event':self.event_id.name,
                            'email':il.email,
                            'customer_name':self.name,
                            })
                        for kk in note_id.event_attendee_attended_mail:
                            kk.sudo().with_context(ctx).send_mail(self.id, force_send=True)
                    if il.mobile and i.id in il.subscription_list_ids.ids and note_id.event_attendee_attended_whatsapp:
                        self.event_id.whatsapp_sent(partner_id=il.id,tmpl_id=note_id.event_attendee_attended_whatsapp.id,pt='mailing_list',apt=self.id)

            if self.email and note_id.event_attendee_attended_mail:
                for emp in note_id.event_attendee_attended_mail:
                    ctx.update({
                        'event':self.event_id.name,
                        'email':self.email,
                        'customer_name':self.name,
                        })
                    emp.sudo().with_context(ctx).send_mail(self.id, force_send=True)

            if self.mobile and note_id.event_attendee_attended_whatsapp:
                self.event_id.whatsapp_sent(partner_id=self.id,tmpl_id=note_id.event_attendee_attended_whatsapp.id,pt='event_registration',apt=self.id)
        
        return res

    def action_cancel(self):
        res = super(EventRegistration, self).action_cancel()

        note_id = self.env['event.notification'].search([],limit=1)
        ctx = dict()
        if note_id.attendees_booking_active_notification_cancellation == True:
            for i in note_id.event_attendee_cancel_list:
                for il in self.env['mailing.contact'].sudo().search([]):
                    if il.email and i.id in il.subscription_list_ids.ids and note_id.event_attendee_cancel_mail:
                        ctx.update({
                            'event':self.event_id.name,
                            'email':il.email,
                            'customer_name':self.name,
                            })
                        for kk in note_id.event_attendee_cancel_mail:
                            kk.sudo().with_context(ctx).send_mail(self.id, force_send=True)
                    if il.mobile and i.id in il.subscription_list_ids.ids and note_id.event_attendee_cancel_whatsapp:
                        self.event_id.whatsapp_sent(partner_id=il.id,tmpl_id=note_id.event_attendee_cancel_whatsapp.id,pt='mailing_list',apt=self.id)

            if self.email and note_id.event_attendee_cancel_mail:
                for emp in note_id.event_attendee_cancel_mail:
                    ctx.update({
                        'event':self.event_id.name,
                        'email':self.email,
                        'customer_name':self.name,
                        })
                    emp.sudo().with_context(ctx).send_mail(self.id, force_send=True)

            if self.mobile and note_id.event_attendee_cancel_whatsapp:
                self.event_id.whatsapp_sent(partner_id=self.id,tmpl_id=note_id.event_attendee_cancel_whatsapp.id,pt='event_registration',apt=self.id)
        return res

    @api.model
    def create(self, vals):
        res = super(EventRegistration, self).create(vals)

        note_id = self.env['event.notification'].search([],limit=1)
        ctx = dict()
        if note_id.event_active_notification_attendee_booking == True:
            for i in note_id.event_approve_mailing_list:
                for il in self.env['mailing.contact'].sudo().search([]):
                    if il.email and i.id in il.subscription_list_ids.ids and note_id.event_attendee_booking_mail:
                        ctx.update({
                            'event':res.event_id.name,
                            'email':il.email,
                            'customer_name':res.name,
                            })
                        for kk in note_id.event_attendee_booking_mail:
                            kk.sudo().with_context(ctx).send_mail(il.id, force_send=True)
                    if il.mobile and i.id in il.subscription_list_ids.ids and note_id.event_attendee_booking_whatsapp:
                        res.event_id.whatsapp_sent(partner_id=il.id,tmpl_id=note_id.event_attendee_booking_whatsapp.id,pt='mailing_list',apt=res.id)
            if res.email and note_id.event_attendee_booking_mail:
                for emp in note_id.event_attendee_booking_mail:
                    ctx.update({
                        'event':res.event_id.name,
                        'email':res.email,
                        'customer_name':res.name,
                        })
                    emp.sudo().with_context(ctx).send_mail(res.event_id.id, force_send=True)
            if res.mobile and note_id.event_attendee_booking_whatsapp:
                res.event_id.whatsapp_sent(partner_id=res.id,tmpl_id=note_id.event_attendee_booking_whatsapp.id,pt='event_registration',apt=res.id)

        
        if res.partner_id.lead_id and res.partner_id.lead_id.stage_id.is_won == True:
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
                'event_reg_id':res.id
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
                'event_reg_id':res.id
                })
            if res.quick_remarks_id:
                crm_stage = self.env['crm.stage'].search([('quick_remarks_id','=',res.quick_remarks_id.id)],limit=1)
                lead_id.stage_id = crm_stage 
            else:
                crm_stage = self.env['crm.stage'].search([('is_won','=',True)],limit=1)
                lead_id.stage_id = crm_stage
                


        return res

    def write(self, vals):
        # update the lead stages based on the quick remarks
        result = super(EventRegistration,self).write(vals)
        for rec in self:
            if rec.quick_remarks_id and rec.event_payment_status != 'paid':
                get_lead_id = self.env['crm.lead'].search([('event_reg_id','=',rec.id)],limit=1)
                crm_stage = self.env['crm.stage'].search([('quick_remarks_id','=',rec.quick_remarks_id.id)],limit=1)
                get_lead_id.stage_id = crm_stage
            else:
                get_lead_id = self.env['crm.lead'].search([('event_reg_id','=',rec.id)],limit=1)
                crm_stage = self.env['crm.stage'].search([('is_won','=',True)],limit=1)
                get_lead_id.stage_id = crm_stage

        return result

    def attendees_invoice(self):
        return {
            'name': 'Attendees Invoice',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'account.move',
            'domain': [('id','=',self.invoice_id.id)],
        }

    def unpaid_attendees_remind_mail(self):
        context = dict(self._context or {})
        if context.get('active_ids'):
            self_ids = self.env['event.registration'].search([('id','in',context.get('active_ids'))])
            for rec in self_ids:
                note_id = self.env['event.notification'].search([],limit=1)
                ctx = dict()
                if note_id.attendees_payment_active_notification_remainder == True:
                    for i in note_id.event_attendee_payment_remainder_list:
                        for il in self.env['mailing.contact'].sudo().search([]):
                            if il.email and i.id in il.subscription_list_ids.ids and note_id.event_attendee_payment_remainder_mail:
                                ctx.update({
                                    'event':rec.event_id.name,
                                    'email':il.email,
                                    'customer_name':rec.name,
                                    })
                                for kk in note_id.event_attendee_payment_remainder_mail:
                                    kk.sudo().with_context(ctx).send_mail(rec.id, force_send=True)
                            if il.mobile and i.id in il.subscription_list_ids.ids and note_id.event_attendee_payment_remainder_whatsapp:
                                rec.event_id.whatsapp_sent(partner_id=il.id,tmpl_id=note_id.event_attendee_payment_remainder_whatsapp.id,pt='mailing_list',apt=rec.id)
                    if rec.email and note_id.event_attendee_payment_remainder_mail:
                        for emp in note_id.event_attendee_payment_remainder_mail:
                            ctx.update({
                                'event':rec.event_id.name,
                                'email':rec.email,
                                'customer_name':rec.name,
                                })
                            emp.sudo().with_context(ctx).send_mail(rec.id, force_send=True)

                    if rec.mobile and note_id.event_attendee_payment_remainder_whatsapp:
                        rec.event_id.whatsapp_sent(partner_id=rec.id,tmpl_id=note_id.event_attendee_payment_remainder_whatsapp.id,pt='event_registration',apt=rec.id)

# open wizard while click the cancel button event registration
    def cancel_registration(self):
        active_id = self._context.get('active_id')
        rec = self.env["event.registration"].browse(active_id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Event Cancellation',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'event.cancellation',
            'context': {
                'default_event_id': self.id,
                'default_event_cancel_charge':self.event_id.eve_cancel_charge,
                'default_eve_cancellation_type':'late'
            },
        }

    # def action_event_cancel(self):
    #     app_time = self.date_open.strftime("%d/%m/%Y")
    #     app_time = datetime.strptime(app_time, "%d/%m/%Y")
    #     now = datetime.now()
    #     if self.env.user.tz == 'Asia/Calcutta': now = datetime.now() + timedelta(hours=5,minutes=30)
    #     elif self.env.user.tz == 'Asia/Dubai': now = datetime.now() + timedelta(hours=4)

    #     if self.event_id.event_sub_categ_id.cancel_interval_range == 'hour':
    #         cancel_date = app_time - timedelta(hours = self.event_id.event_sub_categ_id.cancel_interval_number)
    #         if now > cancel_date:
    #             self.pre_cancellation_type = 'late'
    #         elif now < cancel_date:
    #             self.pre_cancellation_type = 'early'

    #     elif self.event_id.event_sub_categ_id.cancel_interval_range == 'day':
    #         cancel_date = app_time - timedelta(days = self.event_id.event_sub_categ_id.cancel_interval_number)
    #         if now > cancel_date:
    #             self.pre_cancellation_type = 'late'
    #         else:
    #             self.pre_cancellation_type = 'early'
    #     else:
    #         print('null')

    def expiry_mail_cron(self):
        evt_reg_id = self.env['event.registration'].search([('state','=','draft'),('expire','=',False),('total_expire_can','=',True)],order="id asc")
        lst = []
        if evt_reg_id:
            interval_number = self.env['ir.config_parameter'].get_param('custom_event_mail.interval_number')
            interval_type = self.env['ir.config_parameter'].get_param('custom_event_mail.interval_type')
            event = False;avail = False
            for i in evt_reg_id:
                if i.expire_id and i.expire_datetime and interval_number and interval_type:
                    event = i.event_id;avail = i
                    if i.event_id.seats_limited and i.event_id.seats_max and not i.event_id.seats_available < (1 if i.state == 'draft' else 0):
                        exp_dat = i.expire_datetime + timedelta(hours=5, minutes=30)
                        current_time = datetime.now() + timedelta(hours=5, minutes=30)
                        td = {interval_type:int(interval_number)}
                        exp_dat = exp_dat + timedelta(**td)
                        if current_time >= exp_dat:
                            i.expire_id.write({'expire':True})
                            template_id = self.env.ref('custom_event_mail.event_expired_ticket_for_registration')
                            template_id.send_mail(i.expire_id.id, force_send=True)
                            if len(evt_reg_id) > 1:
                                self.expiry_mail_cron_end()

        from datetime import date, datetime
        now = datetime.now()
        now = now + timedelta(hours = 5, minutes=30)
        event_id = self.env['event.event'].search([])
        for rr in event_id:
            if rr.date_begin:
                extact_time = rr.date_begin + timedelta(hours = 5, minutes=30)
                twodiff = extact_time - timedelta(hours = 2)
            if now > twodiff and now < extact_time:
                evt_reg_id = self.env['event.registration'].search([('id','=',rr.id),('ack_2hrs_mail','=',False),('state','=','open')])

                for rr in evt_reg_id:
                    if note_id.attendees_remainder_active_notification_2hrs == True:
                        for i in note_id.event_attendee_remainder_2hrs_list:
                            for il in self.env['mailing.contact'].sudo().search([]):
                                if il.email and i.id in il.subscription_list_ids.ids and note_id.event_attendee_remainder_2hrs_mail:
                                    ctx.update({
                                        'event':rr.event_id.name,
                                        'email':il.email,
                                        'customer_name':rr.name,
                                        })
                                    for kk in note_id.event_attendee_remainder_2hrs_mail:
                                        kk.sudo().with_context(ctx).send_mail(rr.id, force_send=True)
                                if il.mobile and i.id in il.subscription_list_ids.ids and note_id.event_attendee_remainder_2hrs_whatsapp:
                                    rr.event_id.whatsapp_sent(partner_id=il.id,tmpl_id=note_id.event_attendee_remainder_2hrs_whatsapp.id,pt='mailing_list',apt=rr.id)

                        if rr.email and note_id.event_attendee_remainder_2hrs_mail:
                            for emp in note_id.event_attendee_remainder_2hrs_mail:
                                ctx.update({
                                    'event':rr.event_id.name,
                                    'email':rr.email,
                                    'customer_name':rr.name,
                                    })
                                emp.sudo().with_context(ctx).send_mail(rr.id, force_send=True)
                                rr.ack_2hrs_mail = True

                        if rr.mobile and note_id.event_attendee_remainder_2hrs_whatsapp:
                            rr.event_id.whatsapp_sent(partner_id=rr.id,tmpl_id=note_id.event_attendee_remainder_2hrs_whatsapp.id,pt='event_registration',apt=rr.id)

    def expiry_mail_cron_end(self):
        event_ids = self.env['event.event'].search([('stage_id','=',2)])
        for j in event_ids:
            reg_id = self.env['event.registration'].search([('expire','=',False),('state','=','draft'),('event_id','=',j.id)],limit=1,order="id asc")
            if reg_id:
                template_id = self.env.ref('custom_event_mail.event_available_ticket_for_registration')
                template_id.send_mail(reg_id.id, force_send=True)
                set_id_exp = self.env['event.registration'].search([('event_id','=',reg_id.event_id.id)])
                for i in set_id_exp:
                    i.write({'expire_id':reg_id.id,'expire_datetime':datetime.now()})

    def event_remainder_mail_days(self, remainder_l = None):
        from datetime import date
        today = date.today()
        threedays_today = today - timedelta(days = int(remainder_l))
        event_id = self.env['event.event'].search([('date_begin','=',threedays_today),('stage_id','=',2)])

        note_id = self.env['event.notification'].search([],limit=1)
        ctx = dict()
        for ee in event_id:
            evt_reg_id = self.env['event.registration'].search([('event_id','=',ee.id),('state','=','open')])
            for rr in evt_reg_id:
                if note_id.attendees_remainder_active_notification_3days == True and int(remainder_l) == 3:
                    for i in note_id.event_attendee_remainder_3days_list:
                        for il in self.env['mailing.contact'].sudo().search([]):
                            if il.email and i.id in il.subscription_list_ids.ids and note_id.event_attendee_remainder_3days_mail:
                                ctx.update({
                                    'event':rr.event_id.name,
                                    'email':il.email,
                                    'customer_name':rr.name,
                                    })
                                for kk in note_id.event_attendee_remainder_3days_mail:
                                    kk.sudo().with_context(ctx).send_mail(rr.id, force_send=True)
                            if il.mobile and i.id in il.subscription_list_ids.ids and note_id.event_attendee_remainder_3days_whatsapp:
                                rr.event_id.whatsapp_sent(partner_id=il.id,tmpl_id=note_id.event_attendee_remainder_3days_whatsapp.id,pt='mailing_list',apt=rr.id)

                    if rr.email and note_id.event_attendee_remainder_3days_mail:
                        for emp in note_id.event_attendee_remainder_3days_mail:
                            ctx.update({
                                'event':rr.event_id.name,
                                'email':rr.email,
                                'customer_name':rr.name,
                                })
                            emp.sudo().with_context(ctx).send_mail(rr.id, force_send=True)

                    if rr.mobile and note_id.event_attendee_remainder_3days_whatsapp:
                        rr.event_id.whatsapp_sent(partner_id=rr.id,tmpl_id=note_id.event_attendee_remainder_3days_whatsapp.id,pt='event_registration',apt=rr.id)

                if note_id.attendees_remainder_active_notification_1days == True and int(remainder_l) == 1:
                    for i in note_id.event_attendee_remainder_1days_list:
                        for il in self.env['mailing.contact'].sudo().search([]):
                            if il.email and i.id in il.subscription_list_ids.ids and note_id.event_attendee_remainder_1days_mail:
                                ctx.update({
                                    'event':rr.event_id.name,
                                    'email':il.email,
                                    'customer_name':rr.name,
                                    })
                                for kk in note_id.event_attendee_remainder_1days_mail:
                                    kk.sudo().with_context(ctx).send_mail(rr.id, force_send=True)
                            if il.mobile and i.id in il.subscription_list_ids.ids and note_id.event_attendee_remainder_1days_whatsapp:
                                rr.event_id.whatsapp_sent(partner_id=il.id,tmpl_id=note_id.event_attendee_remainder_1days_whatsapp.id,pt='mailing_list',apt=rr.id)

                    if rr.email and note_id.event_attendee_remainder_1days_mail:
                        for emp in note_id.event_attendee_remainder_1days_mail:
                            ctx.update({
                                'event':rr.event_id.name,
                                'email':rr.email,
                                'customer_name':rr.name,
                                })
                            emp.sudo().with_context(ctx).send_mail(rr.id, force_send=True)

                    if rr.mobile and note_id.event_attendee_remainder_1days_whatsapp:
                        rr.event_id.whatsapp_sent(partner_id=rr.id,tmpl_id=note_id.event_attendee_remainder_1days_whatsapp.id,pt='event_registration',apt=rr.id)

    def invoice_payment(self):
        if self.invoice_id:
            ret= {
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

class EventEvent(models.Model):
    _inherit = 'event.event'

    follow_ups = fields.Many2many('hr.employee','hr_follow_ups',string='Follow Ups')

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
        parms = []
        if template_id.parameter_ids:
            for i in template_id.parameter_ids:
                mod_id = self.env[i.model_id.model].sudo().browse(int(apt))
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

    def unpaid_attendees(self):
        return {
            'name': 'Unpaid Attendees',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'event.registration',
            'domain': [('event_id','=',self.id),('paid_attendees','=','unpaid')],
        }

    @api.onchange("facilitator_evnt_ids")
    def _onchange_facilitator_evnt_ids_set(self):
        self.follow_ups = [(6,0, self.facilitator_evnt_ids.ids)]
        for i in self.evnt_assistant:
            self.follow_ups = [(4, i.id)]

    @api.onchange("evnt_assistant")
    def _onchange_evnt_assistant_set(self):
        self.follow_ups = [(6,0, self.evnt_assistant.ids)]
        for i in self.facilitator_evnt_ids:
            self.follow_ups = [(4, i.id)]

    @api.onchange("stage_id")
    def _onchange_stage_id(self):
        if self.stage_id and self.stage_id.template_id:
            template_id = self.stage_id.template_id
            event_id = int(re.search(r'\d+', str(self.id)).group())
            registration_id = self.env['event.registration'].search([('event_id','=',event_id),('state','=','open')])
            if registration_id:
                for i in registration_id:
                    template_id.send_mail(i.id,force_send=True)

    def get_event_facilitator_mail(self,evnt_assistant):
        f_mail_ids=''
        f_mail_ids_list=[]
        for assist in evnt_assistant:
            if assist.work_email:
                f_mail_ids=assist.work_email
                f_mail_ids_list.append(f_mail_ids)
        f_mail_ids = (', '.join(f_mail_ids_list))
        return f_mail_ids

    def get_facilitator_mail_id(self,evnt_assistant):
        f_mail_ids=''
        f_mail_ids_list=[]
        for assist in evnt_assistant:
            if assist.work_email:
                f_mail_ids=assist.work_email
                f_mail_ids_list.append(f_mail_ids)
        f_mail_ids = (', '.join(f_mail_ids_list))
        return f_mail_ids

    def get_checklist_mail_ids(self, evnt_id):
        mail_ids = ''
        mail_ids_list=[]
        checklist = self.env['check.list'].search([('event_id', '=', evnt_id)])
        if checklist:
            for clist in checklist.checklist_line_id:
                mail_id=clist.checklist_responsible.login
                if mail_id not in mail_ids_list:
                    mail_ids_list.append(mail_id)
        mail_ids=(', '.join(mail_ids_list))
        return mail_ids

    def approve_move_stage(self):
        if self.event_multiple_date =="multiday":
            if not self.multi_date_line_ids:
                raise UserError(_('Please Set Start Date and End Date'))
        res_approve = super(EventEvent, self).approve_move_stage()
        note_id = self.env['event.notification'].search([],limit=1)
        evt_reg_id = self.env['event.registration'].search([('event_id','=',self.id)])
        ctx = dict()
        if self.reschedule_enable==True:
            if note_id.event_active_notification_reschedule == True:
                for i in note_id.event_reschedule_mailing_list:
                    for il in self.env['mailing.contact'].sudo().search([]):
                        if il.email and i.id in il.subscription_list_ids.ids:
                            for j in i.event_reschedule_mail:
                                ctx.update({
                                    'name':self.name,
                                    'email':il.email,
                                    'customer_name':il.name,
                                    })
                                j.sudo().with_context(ctx).send_mail(self.id, force_send=True)
                        if il.mobile and i.id in il.subscription_list_ids.ids and i.event_reschedule_whatsapp:
                            self.whatsapp_sent(partner_id=il.id,tmpl_id=i.event_reschedule_whatsapp.id,pt='mailing_list',apt=self.id)
                for rr in evt_reg_id:
                    if rr.email and note_id.event_reschedule_mail:
                        for emp in note_id.event_reschedule_mail:
                            ctx.update({
                                'event':rr.event_id.name,
                                'email':rr.email,
                                'customer_name':rr.name,
                                })
                            emp.sudo().with_context(ctx).send_mail(rr.id, force_send=True)
                    if rr.mobile and note_id.event_reschedule_whatsapp:
                        rr.event_id.whatsapp_sent(partner_id=rr.id,tmpl_id=note_id.event_reschedule_whatsapp.id,pt='event_registration',apt=rr.id)

        if note_id.event_active_notification_approve == True:
            for i in note_id.event_approve_mailing_list:
                for il in self.env['mailing.contact'].sudo().search([]):
                    if il.email and i.id in il.subscription_list_ids.ids:
                        for j in i.event_approve_mail:
                            ctx.update({
                                'name':self.name,
                                'email':il.email,
                                'customer_name':il.name,
                                })
                            j.sudo().with_context(ctx).send_mail(il.id, force_send=True)
                    if il.mobile and i.id in il.subscription_list_ids.ids and i.event_approve_whatsapp:
                        self.whatsapp_sent(partner_id=il.id,tmpl_id=i.event_approve_whatsapp.id,pt='mailing_list',apt=self.id)

            for rr in evt_reg_id:
                if rr.email and note_id.event_approve_mail:
                    for emp in note_id.event_approve_mail:
                        ctx.update({
                            'event':rr.event_id.name,
                            'email':rr.email,
                            'customer_name':rr.name,
                            })
                        emp.sudo().with_context(ctx).send_mail(rr.id, force_send=True)

                if rr.mobile and note_id.event_approve_whatsapp:
                    rr.event_id.whatsapp_sent(partner_id=rr.id,tmpl_id=note_id.event_approve_whatsapp.id,pt='event_registration',apt=self.id)
        
        checklist = self.env['check.list'].search([('event_id', '=', self.id)])
        if checklist and note_id.event_active_notification_checklist == True:
            for i in note_id.event_checklist_mailing_list:
                for il in self.env['mailing.contact'].sudo().search([]):
                    if il.email and i.id in il.subscription_list_ids.ids:
                        for j in i.event_checklist_mail:
                            ctx.update({
                                'name':self.name,
                                'email':il.email,
                                'customer_name':il.name,
                                })
                            j.sudo().with_context(ctx).send_mail(il.id, force_send=True)
                    if il.mobile and i.id in il.subscription_list_ids.ids and i.event_checklist_whatsapp:
                        self.whatsapp_sent(partner_id=il.id,tmpl_id=i.event_checklist_whatsapp.id,pt='mailing_list',apt=self.id)

            for rr in evt_reg_id:
                if rr.email and note_id.event_checklist_mail:
                    for emp in note_id.event_checklist_mail:
                        ctx.update({
                            'event':rr.event_id.name,
                            'email':rr.email,
                            'customer_name':rr.name,
                            })
                        emp.sudo().with_context(ctx).send_mail(rr.id, force_send=True)

                if rr.mobile and note_id.event_checklist_whatsapp:
                    rr.event_id.whatsapp_sent(partner_id=rr.id,tmpl_id=note_id.event_checklist_whatsapp.id,pt='event_registration',apt=rr.id)

        if self.event_meeting_room_id and note_id.room_active_notification_allocation == True:
            for i in note_id.room_allocation_mailing_list:
                for il in self.env['mailing.contact'].sudo().search([]):
                    if il.email and i.id in il.subscription_list_ids.ids:
                        for j in i.room_allocation_mail:
                            ctx.update({
                                'room_name': self.room_id.room_type,
                                'room_booking_name': self.event_meeting_room_id.name,
                                'event_name':self.name,
                                'email':il.email,
                                'customer_name':il.name,
                                })
                            j.sudo().with_context(ctx).send_mail(il.id, force_send=True)
                    if il.mobile and i.id in il.subscription_list_ids.ids and i.room_allocation_whatsapp:
                        self.whatsapp_sent(partner_id=il.id,tmpl_id=i.room_allocation_whatsapp.id,pt='mailing_list',apt=self.id)

            for rr in evt_reg_id:
                if rr.email and note_id.room_allocation_mail:
                    for emp in note_id.room_allocation_mail:
                        ctx.update({
                            'event':rr.event_id.name,
                            'email':rr.email,
                            'customer_name':rr.name,
                            })
                        emp.sudo().with_context(ctx).send_mail(rr.id, force_send=True)

                if rr.mobile and note_id.room_allocation_whatsapp:
                    rr.event_id.whatsapp_sent(partner_id=rr.id,tmpl_id=note_id.room_allocation_whatsapp.id,pt='event_registration',apt=rr.id)

        return res_approve

    def cancel_event_stage(self):
        res_approve = super(EventEvent, self).cancel_event_stage()

        note_id = self.env['event.notification'].search([],limit=1)
        evt_reg_id = self.env['event.registration'].search([('event_id','=',self.id)])
        ctx = dict()
        if note_id.event_active_notification_cancel == True:
            for i in note_id.event_cancel_mailing_list:
                for il in self.env['mailing.contact'].sudo().search([]):
                    if il.email and i.id in il.subscription_list_ids.ids:
                        for j in i.event_cancel_mail:
                            ctx.update({
                                'name':self.name,
                                'email':il.email,
                                'customer_name':il.name,
                                })
                            j.sudo().with_context(ctx).send_mail(il.id, force_send=True)
                    if il.mobile and i.id in il.subscription_list_ids.ids and i.event_cancel_whatsapp.id:
                        self.whatsapp_sent(partner_id=il.id,tmpl_id=i.event_cancel_whatsapp.id,pt='mailing_list',apt=self.id)
        
                for part in self.follow_ups:
                    if part.work_email:
                        ctx.update({
                            'name':self.name,
                            'email':part.work_email,
                            'customer_name':part.name,
                            })
                        for kk in i.event_cancel_mail:
                            kk.sudo().with_context(ctx).send_mail(part.id, force_send=True)
                    if part.mobile_phone and i.event_cancel_whatsapp.id:
                        self.whatsapp_sent(partner_id=part.id,tmpl_id=i.event_cancel_whatsapp.id,pt='hr_employee',apt=self.id)

            for rr in evt_reg_id:
                if rr.email and note_id.event_cancel_mail:
                    for emp in note_id.event_cancel_mail:
                        ctx.update({
                            'event':rr.event_id.name,
                            'email':rr.email,
                            'customer_name':rr.name,
                            })
                        emp.sudo().with_context(ctx).send_mail(rr.id, force_send=True)

                if rr.mobile and note_id.event_cancel_whatsapp:
                    rr.event_id.whatsapp_sent(partner_id=rr.id,tmpl_id=note_id.event_cancel_whatsapp.id,pt='event_registration',apt=rr.id)

        if self.stage_id and self.stage_id.template_id:
            template_id = self.stage_id.template_id
            event_id = int(re.search(r'\d+', str(self.id)).group())
            registration_id = self.env['event.registration'].search([('event_id','=',event_id),('state','=','done')])

            if registration_id:
                for i in registration_id:
                    template_id.send_mail(i.id,force_send=True)


    def end_move_stage(self):
        res_approve = super(EventEvent, self).end_move_stage()
        if self.stage_id and self.stage_id.template_id:
            template_id = self.stage_id.template_id
            event_id = int(re.search(r'\d+', str(self.id)).group())
            registration_id = self.env['event.registration'].search(
                [('event_id', '=', event_id), ('state', '=', 'done')])

            if registration_id:
                for i in registration_id:
                    template_id.send_mail(i.id, force_send=True)

    def create_reschedule(self):
        res = super(EventEvent, self).create_reschedule()
        
        return res

class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    enable_reminder = fields.Boolean(string='Send Reminder',help='To send Email to Update Availability')

    def mail_remainder(self):
        if self.enable_reminder:
            today = datetime.today().date().strftime("%d/%m/%Y")
            today = datetime.strptime(today, "%d/%m/%Y")
            avail_id = self.env['availability.availability'].search([('facilitator','=',self.id),('availability','=','available'),('available_date','=',today)])
            tdelta = False
            for i in avail_id:
                s1 = i.start_time + ':00'
                s2 = i.end_time + ':00'
                FMT = '%H:%M:%S'
                if tdelta == False: 
                    tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
                else: 
                    tdelta += datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)

            tdelta = str(tdelta).split(':')[0]
            availability_minimum_mail = self.env['ir.config_parameter'].get_param('custom_event_mail.availability_minimum_mail')

            if availability_minimum_mail < tdelta:
                template_id = self.env.ref('custom_event_mail.employee_remainder_mail_event')
                template_id.send_mail(self.id,force_send=True)
