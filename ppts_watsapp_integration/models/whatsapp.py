# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
import requests
from odoo import api, exceptions, fields, models, _
from requests.auth import HTTPBasicAuth
import json
import requests
# python3.6 -m pip install wati_api pbr simplejson requests

class WhatsappIntegration(models.Model):   
    _name = "mail.whatsapp"
    _description="WhatsappIntegration"
    _rec_name = "template_name"
    
    template_id = fields.Char('ID', readonly=True)
    template_name = fields.Char('Template Name', readonly=True)
    category = fields.Selection([('ACCOUNT_UPDATE','Account Update'),('ALERT_UPDATE','Alert Update'),('APPOINTMENT_UPDATE','Appointment Update'),('AUTO_REPLY','Auto Reply'),('ISSUE_RESOLUTION','Issue Resolution'),('PAYMENT_UPDATE','Payment Update'),('PERSONAL_FINANCE_UPDATE','Personal Finance Update'),('RESERVATION_UPDATE','Reservation Update'),('SHIPPING_UPDATE','Shipping Update'),('TICKET_UPDATE','Ticket Update'),('TRANSPORTATION_UPDATE','Transportation Update')],'Category', readonly=True)
    language_id = fields.Many2one('res.lang',string='Language', readonly=True)
    last_modified = fields.Datetime('Last Modified', readonly=True)
    parameter_ids = fields.One2many('mail.whatsapp.parameter', 'whatsapp_id', string='Parameters')

class WhatsappIntegrationLine(models.Model):   
    _name = "mail.whatsapp.parameter"
    _description="WhatsappIntegrationLine"

    name = fields.Char('Parameter Name')
    model_id = fields.Many2one('ir.model', string='Model')
    field_id = fields.Many2one('ir.model.fields', string='Fields')
    whatsapp_id = fields.Many2one('mail.whatsapp', string='Whatsapp')