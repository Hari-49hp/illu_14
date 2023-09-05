# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db, Home
import json
from datetime import datetime

class WebsitePos(http.Controller):
    @http.route(['/pos/event/details'], type='http', auth="public", website=True, csrf=False)
    def pos_type(self, **post):
        if post['x']:
            if post['x'] == "event":
                event_id = request.env['event.event'].sudo().search([('stage_id.pipe_end','=',True)])
                event_dict = []
                for i in event_id:
                    event_dict.append({'value':i.id, 'name':i.name+' '+'('+datetime.strftime(i.date_begin, "%d-%m-%Y")+' '+'-'+' '+datetime.strftime(i.date_begin, "%d-%m-%Y")+')'})
                return json.dumps(event_dict)
            elif post['x'] == "appointment":
                appointment_id = request.env['calendar.event'].sudo().search([])
                appointment_dict = []
                for i in appointment_id:
                    if i.start_date and i.stop_date:
                        app_name = i.name+' '+'('+str(i.start_date or '')+' '+'-'+' '+str(i.stop_date or '')+')'
                    else:
                        app_name = i.name
                    appointment_dict.append({'value':i.id,'name': app_name})
                return json.dumps(appointment_dict)

    @http.route(['/pos/event/partner_event'], type='http', auth="public", website=True, csrf=False)
    def pos_event(self, **post):
        if post['x']:
            request.session['pos_event'] = request.session['pos_appointment'] = ''
            request.session['pos_event'] = post['x']

    @http.route(['/pos/event/partner_appointment'], type='http', auth="public", website=True, csrf=False)
    def pos_appointment(self, **post):
        if post['y']:
            request.session['pos_event'] = request.session['pos_appointment'] = ''
            request.session['pos_appointment'] = post['y']
