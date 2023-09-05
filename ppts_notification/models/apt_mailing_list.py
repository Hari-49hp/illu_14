# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MailingListApt(models.Model):
    _inherit = 'mailing.list'

    #apt create
    apt_create_mail = fields.Many2many('mail.template','mailing_apt_create_email_template',string='Create EmailTemplate')
    apt_create_whatsapp = fields.Many2one('mail.whatsapp',string='Create WhatsappTemplate')

    #apt approve
    apt_aprrove_mail = fields.Many2many('mail.template','mailing_apt_aprrove_mail_setup',string='Approve EmailTemplate')
    apt_approve_whatsapp = fields.Many2one('mail.whatsapp',string='Approve WhatsappTemplate')

    #apt Cancel
    apt_cancel_mail = fields.Many2many('mail.template','mailing_apt_cancel_email_template',string='Cancel EmailTemplate')
    apt_cancel_whatsapp = fields.Many2one('mail.whatsapp',string='Cancel WhatsappTemplate')

    #apt reschedule
    apt_reschedule_mail = fields.Many2many('mail.template','mailing_apt_reschedule_email_template',string='Reschedule EmailTemplate')
    apt_reschedule_whatsapp = fields.Many2one('mail.whatsapp',string='Reschedule WhatsappTemplate')

class MailingContact(models.Model):
    _inherit = 'mailing.contact'

    def import_partner_to_mailing_list(self):
        return {
            'name': _('Add Mailing List'),
            'res_model': 'mailing.contact.wizard',
            'view_mode': 'form',
            'context': {
                'default_contacts_mailing': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
