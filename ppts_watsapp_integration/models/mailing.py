import base64

import requests

from odoo import api, fields, models, _
from dateutil import rrule
import re
import pytz
import babel.dates
from odoo import tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from odoo.tools.misc import get_lang

from datetime import date, timedelta, datetime
from dateutil.relativedelta import * 
import time
from odoo.http import request, Response
import json, werkzeug
import requests
import urllib.request
import urllib
import logging

_logger = logging.getLogger(__name__)

class MailingMailing(models.Model):   
    _inherit = "mailing.mailing"

    whatsapp_template = fields.Many2one('mail.whatsapp',string='Whatsapp Template')

    @api.model
    def _process_mass_mailing_queue(self):
        mass_mailings = self.search([('state', 'in', ('in_queue', 'sending')), '|', ('schedule_date', '<', fields.Datetime.now()), ('schedule_date', '=', False)])
        for mass_mailing in mass_mailings:
            user = mass_mailing.write_uid or self.env.user
            mass_mailing = mass_mailing.with_context(**user.with_user(user).context_get())
            if len(mass_mailing._get_remaining_recipients()) > 0:
                mass_mailing.state = 'sending'
                mass_mailing.action_send_mail()

                if mass_mailing.whatsapp_template:
	                domain = mass_mailing.mailing_domain
	                domain = domain.split(',');domain = domain[-1].replace(']]','')
	                model_id = self.env['ir.model'].search([('id','=',mass_mailing.mailing_model_id.id)])
	                model_c = model_id.model.replace('.','_')
	                wht = self.env[model_id.model].search([("id","=",int(domain))])

	                for i in wht:
		                mass_mailing.whatsapp_sent(partner_id=i.id,tmpl_id=mass_mailing.whatsapp_template.id,pt=model_c)

            else:
                mass_mailing.write({
                    'state': 'done',
                    'sent_date': fields.Datetime.now(),
                    'kpi_mail_required': not mass_mailing.sent_date,
                })

        mailings = self.env['mailing.mailing'].search([
            ('kpi_mail_required', '=', True),
            ('state', '=', 'done'),
            ('sent_date', '<=', fields.Datetime.now() - relativedelta(days=1)),
            ('sent_date', '>=', fields.Datetime.now() - relativedelta(days=5)),
        ])
        if mailings:
            mailings._action_send_statistics()

    def whatsapp_sent(self, partner_id=None, tmpl_id=None, pt=None):
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

        if ptr_id:
            url = server_url + "/api/v1/sendTemplateMessage"
            querystring = {"whatsappNumber": mobile}
            template_id = self.env['mail.whatsapp'].sudo().browse(int(tmpl_id))
            payload = "{\"parameters\":[{\"name\":\""+ptr_id.name+"\",\"value\":\""+ptr_id.name+"\"}],\"template_name\":\""+str(template_id.template_name)+"\",\"broadcast_name\":\"test_ppts_broadcast\"}"
            headers = {
                "Content-Type": "application/json-patch+json",
                "Authorization": access_token
            }
            response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
            result = json.loads(response.text)
            _logger.info(response.text)