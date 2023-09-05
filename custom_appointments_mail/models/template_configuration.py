from odoo import api, fields, models, _

class AppointmentNotification(models.Model):
    _name = 'appointment.notification'
    _description="AppointmentNotification"
    _rec_name = 'name'

    name = fields.Char('Name',default='Notification')
    notification_active = fields.Boolean('Notification Active')
    #apt create
    apt_active_notification_create = fields.Boolean('Create Active')
    apt_create_mail_list = fields.Many2many('mailing.list','mailing_apt_create_mail_list',string='Create Mailing List')
    apt_create_mail_template = fields.Many2many('mail.template','mailing_apt_create_mail_template_l',string='Create Email Template')
    apt_create_whatsapp = fields.Many2one('mail.whatsapp',string='Create Whatsapp Template')

    #apt aprrove
    apt_active_notification_approval = fields.Boolean('Approve Active')
    apt_approve_mail_list = fields.Many2many('mailing.list','mailing_apt_approve_mail_list',string='Approve Mailing List')
    apt_aprrove_mail_template = fields.Many2many('mail.template','mailing_apt_aprrove_mail_template_l',string='Approve Email Template')
    apt_approve_whatsapp = fields.Many2one('mail.whatsapp',string='Approve Whatsapp Template')

    #apt cancel
    apt_active_notification_cancel = fields.Boolean('Cancel Active')
    apt_cancel_mail_list = fields.Many2many('mailing.list','mailing_apt_cancel_mail_list',string='CancelMailing List')
    apt_cancel_mail_template = fields.Many2many('mail.template','mailing_apt_cancel_mail_template',string='CancelEmail Template')
    apt_cancel_whatsapp = fields.Many2one('mail.whatsapp',string='CancelWhatsapp Template')

    #apt reschedule
    apt_active_notification_reschedule = fields.Boolean('Reschedule Active')
    apt_reschedule_mail_list = fields.Many2many('mailing.list','mailing_apt_reschedule_mail_list',string='RescheduleMailing List')
    apt_reschedule_mail_template = fields.Many2many('mail.template','mailing_apt_reschedule_mail_template',string='RescheduleEmail Template')
    apt_reschedule_whatsapp = fields.Many2one('mail.whatsapp',string='RescheduleWhatsapp Template')

    #apt availability mail
    avail_active_notification_day = fields.Boolean('Availability Active')
    avail_day_mail_template = fields.Many2many('mail.template','mailing_avail_day_mail_template',string='Availability Email Template')
    avail_day_whatsapp = fields.Many2one('mail.whatsapp',string='Availability Whatsapp Template')

    #apt availability mail
    avail_active_notification_eve = fields.Boolean('Active')
    avail_eve_mail_template = fields.Many2many('mail.template','mailing_avail_eve_mail_template',string='Email Template')
    avail_eve_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    #room allocation mail
    room_active_notification = fields.Boolean('Allocation Active')
    room_allocation_mail_list = fields.Many2many('mailing.list','mailing_room_allocation_mail_list',string='Allocation Mailing List')
    room_allocation_mail_template = fields.Many2many('mail.template','mailing_room_allocation_mail_template',string='Allocation Email Template')
    room_allocation_whatsapp = fields.Many2one('mail.whatsapp',string='Allocation Whatsapp Template')

    #attendee reamainder mail 2hrs
    attendee_remain_2hrs_active_notification = fields.Boolean('Reamainder Active')
    attendee_remain_2hrs_mail_template = fields.Many2many('mail.template','mailing_attendee_remain_2hrs_template',string='Reamainder Email Template')
    attendee_remain_2hrs_whatsapp = fields.Many2one('mail.whatsapp',string='Reamainder Whatsapp Template')

    #attendee reamainder mail 1 days
    attendee_remain_1day_active_notification = fields.Boolean('ReamainderActive')
    attendee_remain_1day_mail_template = fields.Many2many('mail.template','mailing_attendee_remain_1day_template',string='ReamainderEmail Template')
    attendee_remain_1day_whatsapp = fields.Many2one('mail.whatsapp',string='ReamainderWhatsapp Template')

    #attendee thx mail
    attendee_thx_active_notification = fields.Boolean('ThanksActive')
    attendee_thx_mail_template = fields.Many2many('mail.template','mailing_attendee_thx_mail_template',string='ThanksEmail Template')
    attendee_thx_whatsapp = fields.Many2one('mail.whatsapp',string='ThanksWhatsapp Template')

    #attendee payment remainder
    attendee_payment_remainder_active_notification = fields.Boolean('PaymentActive')
    attendee_payment_remainder_mail_template = fields.Many2many('mail.template','mailing_attendee_payment_remainder_mail_template',string='PaymentEmail Template')
    attendee_payment_remainder_whatsapp = fields.Many2one('mail.whatsapp',string='PaymentWhatsapp Template')

    #attendee invoice payment
    attendee_invoice_payment_active_notification = fields.Boolean('Invoice Active')
    attendee_invoice_payment_mail_template = fields.Many2many('mail.template','mailing_attendee_invoice_payment_mail_template',string='Invoice Email Template')
    attendee_invoice_payment_whatsapp = fields.Many2one('mail.whatsapp',string='Invoice Whatsapp Template')