from odoo import http, tools, _
from odoo.http import request, Response
from datetime import datetime, timedelta
import json, werkzeug
import requests
import urllib.request
import urllib
import logging

_logger = logging.getLogger(__name__)

class POSWhatsappWizard(http.Controller):
    
    @http.route(['/pos/whatsapp/message/order_enable'], type='http', auth="public", website=True, csrf=False)
    def pos_whatsapp_message_order_enable(self, **post):
        config_id = request.env['pos.config'].sudo().browse(int(post['session_req_id']))
        if config_id.new_order_disable == True: return 'true'
        else: return 'false'


    @http.route(['/pos/whatsapp/message/automatic'], type='http', auth="public", website=True, csrf=False)
    def pos_whatsapp_message_automatic(self, **post):
        server_url = request.env['ir.config_parameter'].sudo().get_param('ppts_watsapp_integration.server_url')
        access_token = request.env['ir.config_parameter'].sudo().get_param('ppts_watsapp_integration.access_token')
        partner_id = request.env['res.partner'].sudo().browse(int(post['partner_id']))
        config_id = request.env['pos.config'].sudo().browse(int(post['session_req_id']))
        url = server_url + "/api/v1/sendTemplateMessage"
        if partner_id.mobile:
            querystring = {"whatsappNumber": partner_id.mobile}
            payload = "{\"parameters\":[{\"name\":\""+partner_id.name+"\",\"value\":\""+partner_id.name+"\"}],\"template_name\":\""+str(config_id.whatsapp_template_id.template_name)+"\",\"broadcast_name\":\""+ str(config_id.broadcast_name) +"\"}"
            headers = {
                "Content-Type": "application/json-patch+json",
                "Authorization": access_token
            }
            response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
            result = json.loads(response.text)
            _logger.info(response.text)
            return 'success' if result['result'] == True else 'failed' 
        else: return 'no_mobile'      


    @http.route(['/pos/whatsapp/message'], type='http', auth="public", website=True, csrf=False)
    def pos_whatsapp_message(self, **post):
        server_url = request.env['ir.config_parameter'].sudo().get_param('ppts_watsapp_integration.server_url')
        access_token = request.env['ir.config_parameter'].sudo().get_param('ppts_watsapp_integration.access_token')
        if post and server_url and access_token:
            if post['template_id'] == 'false':
                url = server_url + "/api/v1/sendSessionMessage/" + post['mobile']
                querystring = {"messageText":post['text_msg']}
                headers = {"Authorization": access_token}
                response = requests.request("POST", url, headers=headers, params=querystring)
                result = json.loads(response.text)
                _logger.info(response.text)
                return result['result']
            else:
                url = server_url + "/api/v1/sendTemplateMessage"
                querystring = {"whatsappNumber": post['mobile']}
                template_id = request.env['mail.whatsapp'].sudo().browse(int(post['template_id']))
                payload = "{\"parameters\":[{\"name\":\""+post['name']+"\",\"value\":\""+post['name']+"\"}],\"template_name\":\""+str(template_id.template_name)+"\",\"broadcast_name\":\"test_ppts_broadcast\"}"
                headers = {
                    "Content-Type": "application/json-patch+json",
                    "Authorization": access_token
                }
                response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
                result = json.loads(response.text)
                _logger.info(response.text)
                return 'success' if result['result'] == True else 'failed'



    @http.route(['/pos/whatsapp/template/sync'], type='http', auth="public", website=True, csrf=False)
    def pos_whatsapp_template_sync(self, **post):
        server_url = request.env['ir.config_parameter'].sudo().get_param('ppts_watsapp_integration.server_url')
        access_token = request.env['ir.config_parameter'].sudo().get_param('ppts_watsapp_integration.access_token')
        if server_url and access_token:
            url = server_url + "/api/v1/getMessageTemplates"
            querystring = {"pageSize":"0","pageNumber":"0"}
            headers = {"Authorization": access_token}
            response = requests.request("GET", url, headers=headers, params=querystring)
            response = json.loads(response.text)
            if response['result'] == 'success':
                for i in response['messageTemplates']:
                    if i['status'] == 'APPROVED':
                        last_modified = str(i['lastModified']).split('.')[0]
                        last_modified = last_modified.split('T');last_modified = datetime.strptime(last_modified[0]+' '+last_modified[1], "%Y-%m-%d %H:%M:%S")
                        template_id = request.env['mail.whatsapp'].sudo().search([('template_id','=',i['id'])])
                        lang_id = request.env['res.lang'].sudo().search([('code','=',i['language']['value'])])
                        parameters = []
                        if template_id:
                            if 'customParams' in i:
                                for j in i['customParams']:
                                    prms_ids = request.env['mail.whatsapp.parameter'].sudo().create({'name': j['paramName']})
                                    parameters.append(prms_ids.id)
                            template_id.sudo().write({
                                'template_id':i['id'],
                                'template_name':i['elementName'],
                                'category':i['category'],
                                'language_id': lang_id.id if lang_id else False,
                                'last_modified': last_modified,
                                'parameter_ids': [(6, 0, parameters)]
                                })
                        else:
                            if 'customParams' in i:
                                for j in i['customParams']:
                                    parameters.append((0, 0, {'name': j['paramName']}))
                            request.env['mail.whatsapp'].sudo().create({
                                'template_id': i['id'],
                                'template_name': i['elementName'],
                                'category': i['category'],
                                'language_id': lang_id.id if lang_id else False,
                                'last_modified': last_modified,
                                'parameter_ids': parameters
                                })


    @http.route(['/mail/whatsapp/template'], type='http', auth="public", website=True, csrf=False)
    def mail_whatsapp_template(self, **post):
        dict1 = {}
        whatsapp_id = request.env['mail.whatsapp'].search([])
        for i in whatsapp_id:
            dict1[i.id] = str(i.template_name)
        return json.dumps(dict1)


    @http.route(['/mailing/list/partner/import'], type='http', auth="public", website=True, csrf=False)
    def mailing_list_partner_import(self, **post):
        partner_id = request.env['res.partner'].sudo().search([])
        for i in partner_id:
            mail_id = request.env['mailing.contact'].sudo().search([('email','=',i.email)],limit=1)
            if mail_id:
                mail_id.write({
                    'name':i.name,
                    'tag_ids':i.category_id.ids,
                    'email':i.email,
                    'mobile':i.mobile,
                    'title_id':i.title.id,
                    'company_name':i.parent_id.name,
                    'country_id':i.country_id.id,
                })
            else:
                request.env['mailing.contact'].sudo().create({
                    'name':i.name,
                    'tag_ids':i.category_id.ids,
                    'email':i.email,
                    'mobile':i.mobile,
                    'title_id':i.title.id,
                    'company_name':i.parent_id.name,
                    'country_id':i.country_id.id,
                })


