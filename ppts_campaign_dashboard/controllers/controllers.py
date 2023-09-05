# -*- coding: utf-8 -*-
from odoo import http, tools, _
from odoo.http import request, Response
from datetime import datetime, timedelta
import json, werkzeug, pytz, urllib.request
import webbrowser, itertools


class AsteriskDialerCampaign(http.Controller):
    @http.route(['/get/asterisk_dialer_campaign_content'], type='http', auth="user", website=True, csrf=False)
    def asterisk_dialer_campaign_content(self, **post):
        values = []
        company_id = post['allowed_company[]']
        if request.env.user.has_group("asterisk_dialer.group_dialer_user"):
            campaign_id = request.env['asterisk_dialer.campaign'].sudo().search([('responsible_id.company_id.id','=',company_id),('responsible_id', '=', request.env.user.id)])
        else:
            campaign_id = request.env['asterisk_dialer.campaign'].sudo().search([('responsible_id.company_id.id','=',company_id)])
        tree_id = request.env.ref('custom_partner.view_partner_summary_tree_view').sudo().id
        form_id = request.env.ref('custom_partner.res_partner_history_history_from_view').sudo().id
        
        for i in campaign_id:
            contact_id = request.env['asterisk_dialer.contact'].sudo().search([('campaign', '=', i.id)])
            contact_list = []
            for each_contact in contact_id:
                contact_list.append(each_contact.model_object.id)

            # addionaly added the login detail info 28-07-22
            values.append({
                'campaign_name': i.name,
                'campaign_type': dict(i._fields['campaign_type'].selection).get(i.campaign_type),
                'create_date': i.login_detail,
                'progress': i.new_progress,
                'partner': contact_list,
                'tree_id': tree_id,
                'form_id': form_id,
                'company_id':i.responsible_id.company_id.id,
                'state': dict(i._fields['state'].selection).get(i.state),
                'campaign_id':i.id,
            })
        return json.dumps(values)
