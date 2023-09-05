from odoo import api, fields, models, _

class EventNotification(models.Model):
    _name = 'event.notification'
    _rec_name = 'name'
    _description = 'Event Notification'

    name = fields.Char('Name',default='Notification')
    mailing_list_id = fields.Many2one('mailing.list',string='Mailing List')
    notification_active = fields.Boolean('Notification Active')
    #create    
    event_active_notification_create = fields.Boolean('Active')
    event_create_mailing_list = fields.Many2many('mailing.list','mailing_event_create_mailing_list',string='Mailing List')

    #approve
    event_active_notification_approve = fields.Boolean('Active')
    event_approve_mailing_list = fields.Many2many('mailing.list','mailing_event_approve_mailing_list',string='Mailing List')
    event_approve_mail = fields.Many2many('mail.template','mail_event_approve_booking_mail_set',string='Email Template')
    event_approve_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')    

    #cancel
    event_active_notification_cancel = fields.Boolean('Active')
    event_cancel_mailing_list = fields.Many2many('mailing.list','mailing_event_cancel_mailing_list',string='Mailing List')
    event_cancel_mail = fields.Many2many('mail.template','mail_event_cancel_booking_mail_set',string='Email Template')
    event_cancel_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')  

    #reschedule
    event_active_notification_reschedule = fields.Boolean('Active')
    event_reschedule_mailing_list = fields.Many2many('mailing.list','mailing_event_reschedule_mailing_list',string='Mailing List')
    event_reschedule_mail = fields.Many2many('mail.template','mail_event_reschedule_mail_set',string='Email Template')
    event_reschedule_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    #room allocation
    room_active_notification_allocation = fields.Boolean('Active')
    room_allocation_mailing_list = fields.Many2many('mailing.list','mailing_room_allocation_mailing_list',string='Mailing List')
    room_allocation_mail = fields.Many2many('mail.template','mail_evnt_room_allocation_mail_set',string='Email Template')
    room_allocation_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    #event checklist
    event_active_notification_checklist = fields.Boolean('Active')
    event_checklist_mailing_list = fields.Many2many('mailing.list','mailing_event_checklist_mailing_list',string='Mailing List')
    event_checklist_mail = fields.Many2many('mail.template','mail_event_checklist_set',string='Email Template')
    event_checklist_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    #event attendee booking
    event_active_notification_attendee_booking = fields.Boolean('Active')
    event_attendee_booking_list = fields.Many2many('mailing.list','mailing_event_attendee_list_mailing_list',string='Mailing List')
    event_attendee_booking_mail = fields.Many2many('mail.template','mail_event_attendee_booking_mail_set',string='Email Template')
    event_attendee_booking_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')


    #event attendee confirmation
    event_active_notification_attendee_confirmation = fields.Boolean('Active')
    event_attendee_confirmation_list = fields.Many2many('mailing.list','mailing_event_attendee_confirmation_list_mailing_list',string='Mailing List')
    event_attendee_confirmation_mail = fields.Many2many('mail.template','mail_event_attendee_confirmation_mail_set',string='Email Template')
    event_attendee_confirmation_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    # event attendee cancellation
    attendees_booking_active_notification_cancellation = fields.Boolean('Active')
    event_attendee_cancel_list = fields.Many2many('mailing.list','mailing_event_attendee_cancel_list_mailing_list',string='Mailing List')
    event_attendee_cancel_mail = fields.Many2many('mail.template','mail_event_attendee_cancel_mail_set',string='Email Template')
    event_attendee_cancel_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    # event attendee waiting list
    attendees_waiting_active_notification_list = fields.Boolean('Active')
    event_attendee_waiting_list = fields.Many2many('mailing.list','mailing_event_attendee_waiting_list_mailing_list',string='Mailing List')
    event_attendee_waiting_list_mail = fields.Many2many('mail.template','mail_event_attendee_waiting_list_mail_set',string='Email Template')
    event_attendee_waiting_list_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    # event attendee remainder 2 hrs
    attendees_remainder_active_notification_2hrs = fields.Boolean('Active')
    event_attendee_remainder_2hrs_list = fields.Many2many('mailing.list','mailing_event_attendee_remainder_2hrs_list_mailing_list',string='Mailing List')
    event_attendee_remainder_2hrs_mail = fields.Many2many('mail.template','mail_event_attendee_remainder_2hrs_mail_set',string='Email Template')
    event_attendee_remainder_2hrs_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    # event attendee remainder 3 days
    attendees_remainder_active_notification_3days = fields.Boolean('Active')
    event_attendee_remainder_3days_list = fields.Many2many('mailing.list','mailing_event_attendee_remainder_3days_list_mailing_list',string='Mailing List')
    event_attendee_remainder_3days_mail = fields.Many2many('mail.template','mail_event_attendee_remainder_3days_mail_set',string='Email Template')
    event_attendee_remainder_3days_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    # event attendee remainder 1 days
    attendees_remainder_active_notification_1days = fields.Boolean('Active')
    event_attendee_remainder_1days_list = fields.Many2many('mailing.list','mailing_event_attendee_remainder_1days_list_mailing_list',string='Mailing List')
    event_attendee_remainder_1days_mail = fields.Many2many('mail.template','mail_event_attendee_remainder_1days_mail_set',string='Email Template')
    event_attendee_remainder_1days_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    # event attendee attended
    attendees_after_active_notification_event = fields.Boolean('Active')
    event_attendee_attended_list = fields.Many2many('mailing.list','mailing_event_attendee_attended_mailing_list',string='Mailing List')
    event_attendee_attended_mail = fields.Many2many('mail.template','mailing_event_attendee_attended_mail_set',string='Email Template')
    event_attendee_attended_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    # event payment remainder
    attendees_payment_active_notification_remainder = fields.Boolean('Active')
    event_attendee_payment_remainder_list = fields.Many2many('mailing.list','mailing_event_payment_remainder_mailing_list',string='Mailing List')
    event_attendee_payment_remainder_mail = fields.Many2many('mail.template','mailing_event_payment_remainder_mail_set',string='Email Template')
    event_attendee_payment_remainder_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    # event payment thx
    attendees_active_notification_payment = fields.Boolean('Active')
    event_attendee_payment_thx_list = fields.Many2many('mailing.list','mailing_event_payment_thx_mailing_list',string='Mailing List')
    event_attendee_payment_thx_mail = fields.Many2many('mail.template','mailing_event_payment_thx_mail_set',string='Email Template')
    event_attendee_payment_thx_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')
