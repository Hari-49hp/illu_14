from odoo import http, tools, _
from odoo.http import request, Response
import odoo
import odoo.modules.registry
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import datetime, timedelta
import json, werkzeug
import requests
import urllib.request
import urllib
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import base64
import pytz
import io
import re
from odoo import fields, http, SUPERUSER_ID, tools, _

_logger = logging.getLogger(__name__)

class WebsiteEvent(http.Controller):
    
    @http.route(['/event/checkout'], type='http', auth="public", website=True, cros='*')
    def website_appointment_page(self, **post):
        
        print(post)
    
        render_vals = {
            "appointment_type":"appointment_type",
            "therapist_id":"therapist_id",
            }
    
        return request.render('ppts_website_theme.website_event_checkout_page', render_vals)
    
    
    
        #user list
    @http.route(['/event/details'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_event_details(self, **post):
        event = []; event_ids = [];
        
        if 'event_id' in post and post['event_id'] != '':
            event_ids = request.env['event.event'].sudo().browse(int(post['event_id']))
        
        for event_id in event_ids:
            platform = '';duration = ''; event_date = '';
            if event_id.type_event == 'type_online':
                platform = 'Online'
            elif event_id.type_event == 'type_onsite':
                platform = 'Onsite'
            elif event_id.type_event == 'type_hybrid':
                platform = 'Online/Onsite'
                
            if event_id.event_multiple_date == 'oneday':
                
                duration = str(event_id.hour_time_begin)+':'+str(event_id.min_time_begin)+' To '+str(event_id.hour_time_end)+':'+str(event_id.min_time_end)
                event_date = str(event_id.s_start_date.day or '')+' '+str(event_id.s_start_date.strftime("%B") or '')
                
            elif event_id.event_multiple_date == 'multiday':
                
                
                event_start_date = event_id.multi_date_line_ids.ids[0]
                event_start_date = request.env['multi.date.line'].sudo().browse(event_start_date)
                event_end_date = event_id.multi_date_line_ids.ids[-1]
                event_end_date = request.env['multi.date.line'].sudo().browse(event_end_date)
                
                
                event_date = str(event_start_date.date_begin.day or '')+' '+str(event_start_date.date_begin.strftime("%B") or '')+' To '+str(event_end_date.date_begin.day or '')+' '+str(event_end_date.date_begin.strftime("%B") or '')
                duration = str(event_start_date.hour_time_begin)+':'+str(event_start_date.min_time_begin)+' To '+str(event_end_date.hour_time_end)+':'+str(event_end_date.min_time_end)
            
            for ticket_id in event_id.event_ticket_ids:
                event_ticket_price = ticket_id.full_price
                # Event ticket displayed in website using below condition 09-09-22
                if ticket_id.ticket_type == 'online':
                    event.append({
                            'event_id': event_id.id,
                            'ticket_id': ticket_id.id,
                            "name":event_id.name,
                            "ticket_name":ticket_id.name,
                            'location': event_id.address_id.name if event_id.address_id else "",
                            'platform': platform,
                            'duration': duration,
                            'event_date': event_date,
                            'facilitator': event_id.get_facilitator_name(),
                            'price': ticket_id.full_price,
                            'ticket_price':event_ticket_price,
                        })
                
        return json.dumps(event)
    
    
    
                    # Create event  
    @http.route(['/event/ticket/create'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_event_ticket_create(self, **post):
        
        print(post)
        
        events = []; data = {}; event_id = ''; receiver_name = ''; receiver_email = ''; receiver_mobile = '';
        
        if 'queryString[event_id]' in post and post['queryString[event_id]'] != '':
            event_id = request.env['event.event'].sudo().browse(int(post['queryString[event_id]']))
            
            if event_id:
                for ticket_id in event_id.event_ticket_ids:
                    data.update({
                        'ticket_id_'+str(ticket_id.id):post.get('queryString[ticket_id_'+str(ticket_id.id)+']',0),
                        })
                    
                if 'queryString[receiver_name]' in post and post['queryString[receiver_name]'] != '':
                    receiver_name = post['queryString[receiver_name]'].replace('%20', ' ')
                    data.update({'receiver_name': post['queryString[receiver_name]'].replace('%20',' ')})
                if 'queryString[receiver_email]' in post and post['queryString[receiver_email]'] != '':
                    receiver_email = post['queryString[receiver_email]']
                    data.update({'receiver_email': post['queryString[receiver_email]']})
                if 'queryString[receiver_mobile]' in post and post['queryString[receiver_mobile]'] != '':
                    receiver_mobile = post['queryString[receiver_mobile]']
                    data.update({'receiver_mobile': post['queryString[receiver_mobile]']})
            
            
        email = phone = name = city_id = customer_appointment_id = country_id = False;
        partner_vals = {}
                    
        if 'data[event_customer_name]' in post and post['data[event_customer_name]'] != '':
            data.update({'customer_name': post['data[event_customer_name]']})
        
        if 'data[event_email]' in post and post['data[event_email]'] != '':
            data.update({'email': post['data[event_email]']})
            
        if 'data[event_phone]' in post and post['data[event_phone]'] != '':
            data.update({'phone': post['data[event_phone]']})
            
        if 'data[event_appointment_country_id]' in post and post['data[event_appointment_country_id]'] != '' and post['data[event_appointment_country_id]']:
            data.update({'country_id': int(post['data[event_appointment_country_id]'])})
        
        if 'data[event_appointment_city_id]' in post and post['data[event_appointment_city_id]'] != '' and post['data[event_appointment_city_id]']:
            data.update({'city_id': int(post['data[event_appointment_city_id]'])})
            
        if 'data[event_street]' in post and post['data[event_street]'] != '' and post['data[event_street]']:
            data.update({'street': post['data[event_street]']})
            
            
        if event_id:
            sale_id = event_id.sudo().create_event_SO_from_Website(data)
       
            events.append({
                    "customer_sale_id":sale_id,
                    "customer_event_id":event_id.id,
                })
            if sale_id:
                # create the lead from website
                get_event_reg_id = request.env['event.registration'].sudo().search([('sale_order_id','=',sale_id)],limit=1)
                sale_order_id = request.env['sale.order'].sudo().browse(sale_id)
                master_aboutus_id = request.env['master.aboutus'].search([('name','=','Social Media')])
                source_id = request.env['utm.source'].sudo().search([('name','ilike','Website')],limit=1)
                lead_id = request.env['crm.lead'].create({
                        'name':sale_order_id.customer_id.name + '' + ' New Lead', 
                        'email_from':sale_order_id.customer_id.email,
                        'first_name':sale_order_id.customer_id.firstname,
                        'last_name':sale_order_id.customer_id.lastname,
                        'mobile':sale_order_id.customer_id.mobile,
                        'type': 'opportunity',
                        'partner_id':sale_order_id.customer_id.id,
                        'master_aboutus':master_aboutus_id.id,
                        'event_reg_id':get_event_reg_id.id,
                        'source_id':source_id.id
                    })    
        # create the lead while event register in the website 13-07-22

        # get_about_us = request.env['master.aboutus'].search([('name','=','Social Media')])

        # crm_oppurtunity = request.env['crm.lead'].sudo().create({
        #     'type': 'opportunity',
        #     'name':event_id.name,
        #     'email_from':post['data[event_email]'],
        #     'mobile':post['data[event_phone]'],
        #     # 'city':post['data[event_city_id]'],
        #     # 'country_id':int(post['data[event_country_id]']),
        #     'street':post['data[event_street]'],
        #     'first_name':post['data[event_customer_name]'],
        #     'master_aboutus':get_about_us.id
        # })
        # get_partner_id = request.env['res.partner'].search([('name','=',post['data[event_customer_name]']),('mobile','=',post['data[event_phone]']),('email','=',post['data[event_email]'])],limit=1)

        # # update the partner using update 12-07-22
        # crm_oppurtunity.update({
        #     'partner_id':get_partner_id.id
        #     })
        # call the mail send function 12-07-22

        



        return json.dumps(events)
    
    
    
class WebsiteSale(WebsiteSale):
    
    
    @http.route(['/event/checkout/shop/cart'], type='http', auth="public", website=True, sitemap=False, csrf=False, cros='*')
    def event_checkout_cart(self, **post):
        
        values = {}
        order = False
        if 'customer_sale_id' in post and post['customer_sale_id'] != '':
            order = request.env['sale.order'].sudo().browse(int(post['customer_sale_id'])) 
            
            
        if 'customer_event_id' in post and post['customer_event_id'] != '':
            request.session['customer_event_id'] = int(post['customer_event_id'])
            
        
        
        if not order:
            order = request.website.sale_get_order()
        
        request.session['sale_order_id'] = order.id
        values = {}
        
        values.update({
             'website_sale_order': order,
             'date': fields.Date.today(),
             'suggested_products': [],
         })
        if order:
            # order.order_line.filtered(lambda l: not l.product_id.active).unlink()
            _order = order
            _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()
        
        
        # order = request.website.sale_get_order()
        
        if not order.partner_shipping_id:
            order.partner_shipping_id = order.partner_id.id
        
        # redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        # if redirection:
        #     return redirection
        
        render_values = self._get_shop_payment_values(order, **post)
        render_values['only_services'] = order and order.only_services or False
        
        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')
            
        render_values.update({'event':True})
        
        return request.render("website_sale.payment", render_values)
        
            

        return request.render("website_sale.cart", values)


   # Event checkout city filters
    @http.route(['/event_checkout/city/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_event_checkout_city_filter(self, **post):
        domain = []
        event_city = []
        if 'event_browse_country' in post and post['event_browse_country'] != '':
            domain.append(('country_id','=',int(post['event_browse_country'])))
        city_master = request.env['city.master'].sudo().search(domain)
        for rec in  city_master:
            event_city.append({
                    "id":rec.id,
                    'name':rec.name
                })
        return json.dumps(event_city)  
    
    
    
    
    
    
    
    
    
