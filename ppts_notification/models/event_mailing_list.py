# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MailingList(models.Model):
    _inherit = 'mailing.list'

    #event create
    event_create_mail = fields.Many2many('mail.template','mail_event_create_mail',string='Create Email Template')
    event_create_whatsapp = fields.Many2one('mail.whatsapp',string=' Create Whatsapp Template')

    #event approval
    event_approve_mail = fields.Many2many('mail.template','mail_event_approve_mail',string='Approval Email Template')
    event_approve_whatsapp = fields.Many2one('mail.whatsapp',string='Approval Whatsapp Template')

    #event cancel
    event_cancel_mail = fields.Many2many('mail.template','mail_event_cancel_mail',string='Cancel Email Template')
    event_cancel_whatsapp = fields.Many2one('mail.whatsapp',string='Cancel Whatsapp Template')

    #event reschedule
    event_reschedule_mail = fields.Many2many('mail.template','mail_event_reschedule_mail',string='Reschedule Email Template')
    event_reschedule_whatsapp = fields.Many2one('mail.whatsapp',string='Reschedule Whatsapp Template')

    #room allocation
    room_allocation_mail = fields.Many2many('mail.template','mail_room_allocation_mail',string='Allocation Email Template')
    room_allocation_whatsapp = fields.Many2one('mail.whatsapp',string=' Allocation Whatsapp Template')

    #event checklist
    event_checklist_mail = fields.Many2many('mail.template','mail_event_checklist_mail',string='Checklist Email Template')
    event_checklist_whatsapp = fields.Many2one('mail.whatsapp',string='Checklist Whatsapp Template')

    # #event attendee booking
    # event_attendee_booking_mail = fields.Many2many('mail.template','mail_event_attendee_booking_mail',string='Email Template')
    # event_attendee_booking_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    # #event attendee booking confirmation
    # event_attendee_confirmation_mail = fields.Many2many('mail.template','mail_event_attendee_confirmation_mail',string='Email Template')
    # event_attendee_confirmation_whatsapp = fields.Many2one('mail.whatsapp',string='Whatsapp Template')
