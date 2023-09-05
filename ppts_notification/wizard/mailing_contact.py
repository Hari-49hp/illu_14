from datetime import date, datetime, timedelta, time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
import pytz

class MailingContactWizard(models.TransientModel):
    _name = "mailing.contact.wizard"
    _description ="MailingContactWizard"

    contacts_mailing_list = fields.Many2many('mailing.list',string='Mailing List')
    contacts_mailing = fields.Many2many('mailing.contact',string='Contacts')

    def add_mailing(self):
    	for i in self.contacts_mailing:
    		for j in self.contacts_mailing_list:
    			mail_id = self.env['mailing.contact.subscription'].search([('list_id','=',j.id),('contact_id','=',i.id)])
    			if not mail_id:
    				self.env['mailing.contact.subscription'].create({
	    					'contact_id': i.id,
	    					'list_id': j.id,
    					})