from odoo import api, fields, models, _
import re
from odoo.tools import float_is_zero
from datetime import datetime

class CustomAppointments(models.Model):
    _inherit = 'appointment.appointment'

    def action_confirm(self):
        res = super(CustomAppointments, self).action_confirm()
        note_id = self.env['appointment.notification'].search([('notification_active','=',True)],limit=1)
        ctx = dict()
        if note_id.apt_active_notification_approval == True:
            for i in note_id.apt_approve_mail_list:
                for il in self.env['mailing.contact'].sudo().search([]):
                    if il.email and i.id in il.subscription_list_ids.ids and i.apt_aprrove_mail:
                        ctx.update({
                            'appointment_name': self.name,
                            })
                        for kk in i.apt_aprrove_mail:
                            kk.sudo().with_context(ctx).send_mail(il.id, force_send=True)
                    if il.mobile and i.id in il.subscription_list_ids.ids and i.apt_approve_whatsapp:
                        self.whatsapp_sent(partner_id=il.id,tmpl_id=i.apt_approve_whatsapp.id,pt='mailing_list',apt=self.id)
            if self.partner_id.email and note_id.apt_aprrove_mail_template:
                for kk in note_id.apt_aprrove_mail_template:
                    kk.sudo().with_context(ctx).send_mail(self.id, force_send=True)
            if self.partner_id.mobile and note_id.apt_approve_whatsapp:
                self.whatsapp_sent(partner_id=self.partner_id.id,tmpl_id=note_id.apt_approve_whatsapp.id,pt='res_partner',apt=self.id)
        return res

    def action_done(self):
        res = super(CustomAppointments, self).action_done()
        note_id = self.env['appointment.notification'].search([('notification_active','=',True)],limit=1)
        ctx = dict()
        if note_id.attendee_thx_active_notification == True:
            if self.partner_id.email and note_id.attendee_thx_mail_template:
                for kk in note_id.attendee_thx_mail_template:
                    kk.sudo().with_context(ctx).send_mail(self.id, force_send=True)
            if self.partner_id.mobile and note_id.attendee_thx_whatsapp:
                self.whatsapp_sent(partner_id=self.partner_id.id,tmpl_id=note_id.attendee_thx_whatsapp.id,pt='res_partner',apt=self.id)
        return res

    def action_cancel(self):
        res = super(CustomAppointments, self).action_cancel()
        for rec in self:
            note_id = self.env['appointment.notification'].search([('notification_active','=',True)],limit=1)
            ctx = dict()
            if note_id.apt_active_notification_cancel == True:
                for i in note_id.apt_cancel_mail_list:
                    for il in self.env['mailing.contact'].sudo().search([]):
                        if il.email and i.id in il.subscription_list_ids.ids and i.apt_cancel_mail:
                            ctx.update({
                                'appointment_name': rec.name,
                                })
                            for kk in i.apt_cancel_mail:
                                kk.sudo().with_context(ctx).send_mail(il.id, force_send=True)
                        if il.mobile and i.id in il.subscription_list_ids.ids and i.apt_cancel_whatsapp:
                            rec.whatsapp_sent(partner_id=il.id,tmpl_id=i.apt_cancel_whatsapp.id,pt='mailing_list',apt=self.id)
                if rec.partner_id.email and note_id.apt_cancel_mail_template:
                    for kk in note_id.apt_cancel_mail_template:
                        kk.sudo().with_context(ctx).send_mail(rec.id, force_send=True)
                if rec.partner_id.mobile and note_id.apt_cancel_whatsapp:
                    rec.whatsapp_sent(partner_id=rec.partner_id.id,tmpl_id=note_id.apt_cancel_whatsapp.id,pt='res_partner',apt=self.id)
        return res

    def action_reschedule(self):
        res = super(CustomAppointments, self).action_reschedule()
        for rec in self:
            note_id = self.env['appointment.notification'].search([('notification_active','=',True)],limit=1)
            ctx = dict()
            if note_id.apt_active_notification_reschedule == True:
                for i in note_id.apt_reschedule_mail_list:
                    for il in self.env['mailing.contact'].sudo().search([]):
                        if il.email and i.id in il.subscription_list_ids.ids and i.apt_reschedule_mail:
                            ctx.update({
                                'appointment_name': rec.name,
                                })
                            for kk in i.apt_reschedule_mail:
                                kk.sudo().with_context(ctx).send_mail(il.id, force_send=True)
                        if il.mobile and i.id in il.subscription_list_ids.ids and i.apt_reschedule_whatsapp:
                            rec.whatsapp_sent(partner_id=il.id,tmpl_id=i.apt_reschedule_whatsapp.id,pt='mailing_list',apt=self.id)
                if rec.partner_id.email and note_id.apt_reschedule_mail_template:
                    for kk in note_id.apt_reschedule_mail_template:
                        kk.sudo().with_context(ctx).send_mail(rec.id, force_send=True)
                if rec.partner_id.mobile and note_id.apt_reschedule_whatsapp:
                    rec.whatsapp_sent(partner_id=rec.partner_id.id,tmpl_id=note_id.apt_reschedule_whatsapp.id,pt='res_partner',apt=self.id)
        return res

    def get_record_ids(self):
        registration_id = self.env['appointment.appointment'].search([('state', '=', 'new')])
        records=[]
        for res in registration_id:
            tickets = {}
            tickets['type_partner'] = res.type_partner
            tickets['partner_id'] = res.partner_id.name
            tickets['partner_email'] = res.email
            records.append(tickets)
        return records

    def get_channel_mail_ids(self):
        channel_name = self.env['mail.channel'].search([('name', '=', 'appointment')])
        channel_partners = self.env['mail.channel.partner'].search([('channel_id', '=',channel_name.id)])
        mail_ids_list = []
        for email in channel_partners:
            mail_id = email.partner_email
            if mail_id not in mail_ids_list:
                mail_ids_list.append(mail_id)
        mail_ids = (', '.join(mail_ids_list))
        return mail_ids

    def appointment_remainder(self):
        cate_id = self.env['hr.employee.category'].search([('name','=','Facilitator')],limit=1)
        employee_id = self.env['hr.employee'].search([('employee_type','in',cate_id.id)])
        note_id = self.env['appointment.notification'].search([('notification_active','=',True)],limit=1)
        ctx = dict()
        now = datetime.now()
        for emp in employee_id:
            td = 0
            avail_id = self.env['availability.availability'].search([('facilitator','=',emp.id),('available_date','=',now.strftime("%Y-%m-%d"))])
            if avail_id:
                for av in avail_id:
                    s1 = av.start_time + ':00';s2 = av.end_time + ':00';FMT = '%H:%M:%S'
                    tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
                    tdelta = tdelta.seconds
                    td += int(tdelta)
                if td < 28800 and note_id.avail_active_notification_day == True:
                    if emp.work_email and note_id.avail_day_mail_template:
                        for kk in note_id.avail_day_mail_template:
                            kk.sudo().with_context(ctx).send_mail(emp.id, force_send=True)
                    if emp.mobile_phone and note_id.avail_day_whatsapp:
                        appt = self.env['appointment.appointment'].search([],limit=1)
                        appt.whatsapp_sent(partner_id=emp.id,tmpl_id=note_id.avail_day_whatsapp.id,pt='hr_employee')

        apt_id = self.env['appointment.appointment'].search([('invoice_id','=',True),('booking_date','=',now.strftime("%Y-%m-%d"))])
        for i in apt_id:
            if i.invoice_id.amount_total > 0 and note.attendee_payment_remainder_active_notification == True:
                if i.partner_id.email and note_id.attendee_payment_remainder_mail_template:
                    for kk in note_id.attendee_payment_remainder_mail_template:
                        kk.sudo().with_context(ctx).send_mail(i.id, force_send=True)
                if emp.partner_id.mobile and note_id.attendee_payment_remainder_whatsapp:
                    i.whatsapp_sent(partner_id=i.partner_id.id,tmpl_id=note_id.attendee_payment_remainder_whatsapp.id,pt='res_partner',apt=apt_id)









