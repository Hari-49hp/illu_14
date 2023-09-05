from odoo import http, tools, _
from odoo.http import request, Response
import odoo
import odoo.modules.registry
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
# from datetime import datetime, timedelta
import datetime
import json, werkzeug
import requests
import urllib.request
import urllib
from bs4 import BeautifulSoup
# from datetime import datetime
import logging
import base64
import pytz
import io
import re
from odoo import fields, http, SUPERUSER_ID, tools, _
import time

_logger = logging.getLogger(__name__)

class WebsiteAppointment(http.Controller):
    
    @http.route(['/appointment/checkout'], type='http', auth="public", website=True, cros='*')
    def website_appointment_page(self, **post):
        appointment_type = "no_free"
        therapist_id = False
        if 'appointment_type' in post and post['appointment_type'] != '':
            appointment_type = post['appointment_type']
            
        if 'therapist_id' in post and post['therapist_id'] != '':
            therapist_id = int(post['therapist_id'])
            
            
        render_vals = {
            "appointment_type":appointment_type,
            "therapist_id":therapist_id,
            }
        
        if 'sub_categ_id' in post and post['sub_categ_id'] != '':
            sub_categ_id = int(post['sub_categ_id'])
            sub_categ_id = request.env['calendar.appointment.type'].browse(sub_categ_id)
            render_vals.update({
                    "sub_categ_id":sub_categ_id.id,
                    "sub_categ_id_type_id" :sub_categ_id.service_categ_id.id,
                    "sub_categ_id_type" :'is_struggling' if sub_categ_id.service_categ_id.is_struggling else 'holistic',
                })
            
        
        return request.render('ppts_website_theme.website_appointment_page', render_vals)
    
    
    
        #user list
    @http.route(['/appointment/user/list'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_appointment_user_list(self, **post):
        users = []
        user_ids = request.env.user.partner_id if request.env.user.login != 'public' else []
        
        for user_id in user_ids:
            users.append({
                    "name":user_id.name,
                    'email':user_id.email or '',
                    'phone':user_id.mobile or '',
                    # 'country_id': user_id.country_id.id and user_id.country_id or False,
                    # 'city_id': user_id.city_id.id and user_id.city_id or False,
                    'street':user_id.street or '', 
                })
        return json.dumps(users)
    
    
    
    #Service list
    @http.route(['/appointment/service/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_appointment_service_filter(self, **post):
        domain = [];services =[]
        domain = [('website_publish','=',True),('category_type','=','healing')]
        # if 'categ_browse_help' in post and post['categ_browse_help'] != '':
        #     domain.append(('help_id','=',int(post['categ_browse_help'])))
        
        service_ids = request.env['appointment.category'].sudo().search(domain, order='name asc')
        
        if 'therapist_id' in post and post['therapist_id'] != '':
            therapist_id = request.env['hr.employee'].sudo().browse(int(post['therapist_id']))
            if therapist_id:
                service_ids = therapist_id.pay_rate_ids.mapped('service_category_type_id')
        
        for service in service_ids:
            services.append({
                    "id":service.id,
                    'name':service.name,
                    # 'image': service.image,
                    'maincateg_notes':service.maincateg_notes or '',
                    'image':'/web/image?model=appointment.category&id=%s&field=image' % (service.id),
                })
        return json.dumps(services)
    
    
    #Service stuggling list
    @http.route(['/appointment/service/struggling/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_appointment_service_struggling_filter(self, **post):
        domain = [];services =[]
        domain = [('website_publish','=',True),('is_struggling','=',True)]
        
        service_ids = request.env['appointment.category'].sudo().search(domain, order='name asc')
        domain = [('service_categ_id','in',service_ids.ids)]
        
        
        if 'therapist_id' in post and post['therapist_id'] != '':
            therapist_id = request.env['hr.employee'].sudo().browse(int(post['therapist_id']))
            if therapist_id:
                service_ids = therapist_id.pay_rate_ids.mapped('service_category_type_id')
                service_catg_ids = therapist_id.pay_rate_ids.mapped('appoinment_type_id')
                domain = [('service_categ_id','in',service_ids.ids),('id','in',service_catg_ids.ids),('service_categ_id.website_publish','=',True),('service_categ_id.is_struggling','=',True)]
        
        
        service_categ_ids = request.env['calendar.appointment.type'].sudo().search(domain, order='name asc')
        for service_categ_id in service_categ_ids:
            services.append({
                    "id":service_categ_id.id,
                    'name':service_categ_id.name,
                    'description':service_categ_id.description or '',
                    'image':'/web/image?model=calendar.appointment.type&id=%s&field=image' % (service_categ_id.id),
                })
        return json.dumps(services)
    
    # Service Category list
    @http.route(['/appointment/service/category/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_appointment_service_category_filter(self, **post):
        domain = [];services_categ =[]
        domain = [('website_publish','=',True)]
        if 'service_id' in post and post['service_id'] != '':
            domain.append(('service_categ_id','=',int(post['service_id'])))
            
        if 'therapist_id' in post and post['therapist_id'] != '':
            therapist_id = request.env['hr.employee'].sudo().browse(int(post['therapist_id']))
            if therapist_id:
                service_catg_ids = therapist_id.pay_rate_ids.mapped('appoinment_type_id')
                domain.append(('id','in',service_catg_ids.ids))
        
        services_categ_ids = request.env['calendar.appointment.type'].sudo().search(domain, order='name asc')
        for services_categ_id in services_categ_ids:
            services_categ.append({
                    "id":services_categ_id.id,
                    'name':services_categ_id.name,
                })
        return json.dumps(services_categ)
    
    #Location list
    @http.route(['/appointment/location/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_appointment_location_filter(self, **post):
        domain = [];company =[]
        domain = [('website_show_location','=',True)]
        
        company_ids = request.env['res.company'].sudo().search(domain, order='name asc')
        
        if 'therapist_id' in post and post['therapist_id'] != '':
            therapist_id = request.env['hr.employee'].sudo().browse(int(post['therapist_id']))
            if therapist_id:
                company_ids = therapist_id.company_id
        
        for company_id in company_ids:
            company.append({
                    "id":company_id.id,
                    'name':company_id.name,
                })
        return json.dumps(company)
    
    
    # Service Therapist list
    @http.route(['/appointment/service/therapist/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_appointment_service_therapist_filter(self, **post):
        
        print(post)
        domain = [];services_therapist =[]
        therapist_domain = [('name','=','Therapist')]
        therapist_type_id = request.env['hr.employee.category'].sudo().search(therapist_domain, limit=1)
        
        if therapist_type_id:
            domain = [('employee_type','in',therapist_type_id.ids)]
        
        if 'company_id' in post and post['company_id'] != '':
            domain.append(('company_id','=',int(post['company_id'])))
            
        if 'therapist_id' in post and post['therapist_id'] != '':
            domain.append(('id','=',int(post['therapist_id'])))
            
        if 'service_sub_id' in post and post['service_sub_id'] != '':
            employee_ids=[]
            service_ids = request.env['hr.employee.payrate'].sudo().search([('appoinment_type_id','=',int(post['service_sub_id']))])
            if service_ids:
                employee_ids = service_ids.mapped('employee_id').ids
                if employee_ids:
                    service_availability_ids = request.env['availability.availability'].sudo().search([('availability','=','available'),('facilitator','in',employee_ids),('cus_start_date','>=',datetime.datetime.now().strftime('%Y-%m-%d'))])
                    if service_availability_ids:
                        employee_ids = service_availability_ids.mapped('facilitator').ids
            
            domain.append(('id','in',employee_ids))
        elif not ('therapist_id' in post and post['therapist_id'] != ''):
            domain.append(('id','in',[0]))
        
        therapist_ids = request.env['hr.employee'].sudo().search(domain, order='name asc')
        
        for therapist_id in therapist_ids:
            
            platform = 'Online'
            
            lang = ''
            
            if therapist_id.lang_ids:
                lang = therapist_id.lang_ids.mapped('name')
            
            if therapist_id.by_platform:
                platform = 'Online' if therapist_id.by_platform == 'online' else 'Onsite' if therapist_id.by_platform == 'onsite' else "Online/Onsite"
            
            services_therapist.append({
                    "id":therapist_id.id,
                    'name':therapist_id.name,
                    'country_id':therapist_id.country_id and therapist_id.country_id.name or '',
                    'about_empolyee':therapist_id.about_employee or '',
                    'platform':platform,
                    'location_id':therapist_id.company_id and therapist_id.company_id.name or '',
                    'lang_ids': lang and ','.join(map(str, lang)) or '',
                    'image':'/web/image?model=hr.employee&id=%s&field=image_1920' % (therapist_id.id),
                })
        print(services_therapist)
        return json.dumps(services_therapist)
  
        # Appointment Slots
    @http.route(['/appointment/service/slot/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_appointment_service_slot_filter(self, **post):
        domain = [];slots =[];domain1sess=[];
        if 'service_id' in post and post['service_id'] != '' and 'service_categ_id' in post and post['service_categ_id'] != '' and 'therapist_id' in post and post['therapist_id'] != '' and 'booking_date' in post and post['booking_date'] != '' and 'time_id' in post and post['time_id'] != '':
            domain1sess = [('employee_id','=',int(post['therapist_id'])),('duration_id','=',int(post['time_id'])),('service_category_type_id','=',int(post['service_id'])),('appoinment_type_id','=',int(post['service_categ_id']))]
            payrate_ids = request.env['hr.employee.payrate'].sudo().search(domain1sess, limit=1)
            if payrate_ids:
                slots_ids = request.env['appointment.appointment'].sudo().get_appoinment_time_slot(int(post['therapist_id']), post['booking_date'], int(post['time_id']))
                
                if slots_ids:
                    for slots_id in slots_ids:
                        slots.append({
                                "id":slots_id.id,
                                'name':slots_id.name,
                            })
        
        return json.dumps(slots)
    
    
    
            # Appointment  count Slots
    @http.route(['/appointment/service/slot/count/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_appointment_service_slot_count_filter(self, **post):
        domain = slot_count = domain1sess = [] ;
        service_id= False
        if 'service_id' in post:
            service_sub_categ_id = request.env['calendar.appointment.type'].sudo().browse(int(post['service_categ_id']))
            service_id = request.env['appointment.category'].sudo().browse(service_sub_categ_id.service_categ_id.id).id
        if service_id and 'service_categ_id' in post and post['service_categ_id'] != '' and 'therapist_id' in post and post['therapist_id'] != '' and 'booking_date' in post and post['booking_date'] != '' and 'time_id' in post and post['time_id'] != '':
            domain1sess = [('employee_id','=',int(post['therapist_id'])),('duration_id','=',int(post['time_id'])),('service_category_type_id','=',service_id),('appoinment_type_id','=',int(post['service_categ_id']))]
            payrate_ids = request.env['hr.employee.payrate'].sudo().search(domain1sess, limit=1)
            if payrate_ids:
                start = time.time()
                for i in json.loads(post['booking_date']):
                    slots = []
                    slots_ids = request.env['appointment.appointment'].sudo().get_appoinment_time_slot(int(post['therapist_id']), i, int(post['time_id']), service_id, int(post['service_categ_id']))
                    end = time.time()

                    if slots_ids:
                        for slots_id in slots_ids:
                            slots.append({
                                    "id":slots_id.id,
                                    'name':slots_id.name,
                                })
                        slot_count.append({
                            "date": i,
                            "count":str(len(slots)),
                        })
                    else:
                        slot_count.append({
                            "date": i,
                            "count": 'N/A',
                        })
            else:
                for date in json.loads(post['booking_date']):
                    slot_count.append({
                        "date": date,
                        "count": 'N/A',
                    })
                    
        return json.dumps(slot_count)
    
            # Appointment  session
    @http.route(['/appointment/service/session/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_appointment_service_session_filter(self, **post):
        
        domain = [];domain1sess=[];service_session =[]
        
        # if 'therapist_id' in post and post['therapist_id'] != '':
        #     domain = [('employee_type','=',therapist_id)]
            
        if 'service_id' in post and post['service_id'] != '':
            domain = [('ser_categ','in',[int(post['service_id'])])]
            domain1sess = [('service_category_type_id','=',int(post['service_id']))]
        
        if 'service_categ_id' in post and post['service_categ_id'] != '':
            domain = domain+[('sub_categ','in',[int(post['service_categ_id'])])]
            domain1sess = domain1sess+[('appoinment_type_id','=',int(post['service_categ_id']))]
            
        if 'therapist_id' in post and post['therapist_id'] != '' and 'time_id' in post and post['time_id'] != '':
            domain1sess = domain1sess + [('employee_id','=',int(post['therapist_id'])),('duration_id','=',int(post['time_id']))]
            payrate_ids = request.env['hr.employee.payrate'].sudo().search(domain1sess, limit=1)
            
            for payrate_id in payrate_ids:
                service_session.append({
                    "id":payrate_id.id,
                    "employee_id":payrate_id.employee_id.id,
                    "duration_id":payrate_id.duration_id.id,
                    'unit_price':payrate_id.unit_price,
                    'type':'single',
                    "discount_text":"",
                    'name':"One Session",
                })
            
            
            
        service_session_ids = request.env['appointment.package'].sudo().search([], order='sequence asc')
        for service_session_id in service_session_ids:
            service_session.append({
                    "id":service_session_id.id,
                    "discount":service_session_id.discount,
                    "discount_text":"with "+str(service_session_id.discount)+"% OFF" if service_session_id.discount else "",
                    'name':service_session_id.name,
                    'type':'package',
                })
            
        
        return json.dumps(service_session)
    
    
                # Create Appointment  count Slots
    @http.route(['/appointment/service/create'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_appointment_service_create(self, **post):
        domain = []; appointment = []
        data = {}
        du_service_categ_id = appointment_type = appointments_type_id = company_id = therapist_id = booking_date = time_slot_id = session_type = s_service_categ_id = time_id = type_partner = partner_id = street = payrate_id = False;
        if 'data[selected_service_id]' in post and post['data[selected_service_id]'] != '':
            du_service_categ_id = int(post['data[selected_service_id]'])
            
        if 'data[selected_service_categ_id]' in post and post['data[selected_service_categ_id]'] != '':
            appointments_type_id = int(post['data[selected_service_categ_id]'])
            if not du_service_categ_id:
                 du_service_categ_id = request.env['calendar.appointment.type'].sudo().browse(appointments_type_id).service_categ_id.id
            
        if 'data[platform]' in post and post['data[platform]'] != '':
            if post['data[platform]'] == "online":
                appointment_type = "type_online"
            else:
                appointment_type = "type_onsite"
                
        if 'data[selected_service_location_id]' in post and post['data[selected_service_location_id]'] != '':
            company_id = int(post['data[selected_service_location_id]'])
        if 'data[selected_service_therapist_id]' in post and post['data[selected_service_therapist_id]'] != '':
            therapist_id = int(post['data[selected_service_therapist_id]'])
            
        if 'data[selected_appointment_date]' in post and post['data[selected_appointment_date]'] != '':
            booking_date = post['data[selected_appointment_date]']
            booking_month = str(int(booking_date[6]))
            
            if booking_month == '10':
                booking_date = booking_date[:5] + booking_month + booking_date[6+1:]
            else:
                booking_date = booking_date[:6] + booking_month + booking_date[6+1:]
                
        if 'data[selected_appointment_slot_id]' in post and post['data[selected_appointment_slot_id]'] != '':
            time_slot_id = int(post['data[selected_appointment_slot_id]'])
            
        if 'data[appointment_time_id]' in post and post['data[appointment_time_id]'] != '':
            time_id = int(post['data[appointment_time_id]'])
            
        if 'data[street]' in post and post['data[street]'] != '':
            street = post['data[street]']
            
        if 'data[selected_appointment_session_type]' in post and post['data[selected_appointment_session_type]'] != '':
            if post['data[selected_appointment_session_type]'] == "single":
                session_type = "type_single"
            else:
                session_type = "type_package"
                if 'data[selected_appointment_package_session_id]' in post and post['data[selected_appointment_package_session_id]'] != '':
                    s_service_categ_id = int(post['data[selected_appointment_package_session_id]'])
                    
        email = phone = name = city_id = customer_appointment_id = country_id = False;
        partner_vals = {}
                    
        if 'data[customer_name]' in post and post['data[customer_name]'] != '':
            name = post['data[customer_name]']
        
        if 'data[email]' in post and post['data[email]'] != '':
            email = post['data[email]']
            
        if 'data[phone]' in post and post['data[phone]'] != '':
            phone = post['data[phone]']
            
        if 'data[appointment_country_id]' in post and post['data[appointment_country_id]'] != '' and post['data[appointment_country_id]']:
            country_id = int(post['data[appointment_country_id]'])
        if 'data[appointment_city_id]' in post and post['data[appointment_city_id]'] != '' and post['data[appointment_city_id]']:
            city_id = int(post['data[appointment_city_id]'])
            
        if email or phone:
            
            if email:
                partner_id = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
                if partner_id:
                    type_partner = "type_existing"
                    
            elif phone:
                partner_id = request.env['res.partner'].sudo().search([('phone', '=', phone)], limit=1)
                if partner_id:
                    type_partner = "type_existing"
                    
        partner_vals.update({
            'mobile':phone,
            'email': email,
            'name':name,
            'street':street,
            'city_id': city_id,
            'country_id':country_id,
            })
        
        if not partner_id:
            type_partner = "type_new"
            lead_source_id = request.env['master.refferal'].sudo().search([('name', '=', 'Website')], limit=1)
            if not lead_source_id:
                lead_source_id = request.env['master.refferal'].sudo().create({'name':'Website'})
            
            if lead_source_id:
                partner_vals.update({'reffer_type_id':lead_source_id.id})
            
            partner_id = request.env['res.partner'].sudo().create(partner_vals)
        else:
            try:
                partner_id.write(partner_vals)
            except Exception as e:
                if email:
                    partner_vals = {}
                    partner_vals.update({
                        'street':street,
                        'city_id': city_id,
                        'country_id':country_id,
                        })
                    partner_id.write(partner_vals)
        free_apt_categ = request.env['appointment.category'].sudo().search([('name','ilike','Free Assessment')],limit=1)
        free_consultation = request.env['calendar.appointment.type'].sudo().search([('id','=',appointments_type_id),('service_categ_id','=',free_apt_categ.id)],limit=1)
        data.update({
            'booking_mode' : "online",
            'du_service_categ_id' : du_service_categ_id,
            'service_categ_id' : du_service_categ_id,
            'appointment_type' : appointment_type,
            'appointments_type_id' : appointments_type_id,
            'company_id' : company_id,
            'therapist_id':therapist_id,
            'booking_date':booking_date,
            'time_slot_id':time_slot_id,
            'session_type':session_type,
            's_service_categ_id':s_service_categ_id,
            'time_id':time_id,
            'type_partner':type_partner,
            'partner_id':partner_id.id,
            'extras_partner_id':partner_id.id,
            'reffer_type_id':partner_id.reffer_type_id.id,
            'website_payment_status':False
            # 'email': email,
            # 'mobile':phone,
            })
        if 'data[customer_appointment_id]' in post and post['data[customer_appointment_id]'] != '':
            customer_appointment_id = int(post['data[customer_appointment_id]']) 
            if customer_appointment_id:
                customer_appointment_id = request.env['appointment.appointment'].sudo().browse(customer_appointment_id)
                customer_appointment_id.write(data)
                if free_consultation:
                    customer_appointment_id.website_payment_status = 'paid'
                customer_appointment_id.partner_id.write(partner_vals)
                
        else:
            customer_appointment_id = request.env['appointment.appointment'].sudo().create(data)
            customer_appointment_id.sudo().create_SO_from_Website()
            if free_consultation:
                customer_appointment_id.website_payment_status = 'paid'
            # create the lead from website
            master_aboutus_id = request.env['master.aboutus'].search([('name','=','Social Media')])
            source_id = request.env['utm.source'].sudo().search([('name','ilike','Website')],limit=1)
            lead_id = request.env['crm.lead'].create({
                    'name':partner_id.name + '' + ' New Lead', 
                    'email_from':partner_id.email,
                    'first_name':partner_id.firstname,
                    'last_name':partner_id.lastname,
                    'mobile':partner_id.mobile,
                    'type': 'opportunity',
                    'partner_id':partner_id.id,
                    'master_aboutus':master_aboutus_id.id,
                    'appointment_id':customer_appointment_id.id,
                    'source_id':source_id.id
                })     
        appointment.append({
            "customer_appointment_id":customer_appointment_id.id,
        })

        return json.dumps(appointment)
    
    
class WebsiteSale(WebsiteSale):
    
    
    @http.route(['/appointment/checkout/shop/cart'], type='http', auth="public", website=True, sitemap=False, csrf=False, cros='*')
    def appointment_checkout_shop_cart(self, **post):
        print(post,'---------------------')
        
        customer_appointment_id = False
        values = {}
        
        if 'appointment_id' in post and post['appointment_id'] != '':
            customer_appointment_id = request.env['appointment.appointment'].sudo().browse(int(post['appointment_id'])) 
            
        if customer_appointment_id:
            request.session['appoinment_ref'] = customer_appointment_id.sequence
            order = customer_appointment_id.sale_order_id
            print(1111111111)
            print('\n\n\n\n\n\norder----->',order.order_line[0].price_unit)
        else:
            print(2222222222)
            order = request.website.sale_get_order()
        
        request.session['sale_order_id'] = order.id
        values = {}
         
        values.update({
             'website_sale_order': order,
             'date': fields.Date.today(),
             'suggested_products': [],
        })
        print('\n\n\n\n\n\norder2----->',order.order_line[0].price_unit)
        if order:
            _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()
            
        # order = request.website.sale_get_order()
        
        # if not order.partner_shipping_id:
        #     order.partner_shipping_id = order.partner_id.id
        
        render_values = self._get_shop_payment_values(order, **post)
        render_values['only_services'] = order and order.only_services or False

        # if render_values['errors']:
        #     render_values.pop('acquirers', '')
        #     render_values.pop('tokens', '')
            
            
        render_values.update({'event':False})

        print('\n\n\n\n\n\norder20000----->',order.order_line[0].price_unit)

        # return request.render("ppts_website_theme.appointment_checkout_website_sale_payment", render_values)
        return request.render("website_sale.payment", render_values)
        # return request.render("website_sale.cart", values)
    
    
    
    @http.route(['/website_sale/payment/process'], type="http", auth="public", website=True, sitemap=False)
    def website_sale_payment_status_page(self, **kwargs):
        
        appoinment_id = False
        order = request.website.sale_get_order()
        if order:
            for sale_order_id in order:
                    appoinment_id = request.env['appointment.appointment'].sudo().search([('sale_order_id','=',sale_order_id.id)])
                    if appoinment_id:
                        break
        
        customer_event_id = False
        if appoinment_id:
            render_ctx = {
                'email':'',
                'appoinment_ref':'',
                'success':False,
                'appoinment_id':False,
            }
            
            order = request.website.sale_get_order()
            if order:
                appoinment_ref = ""
                appoinment_id = False
                appoinment_obj_id = False
                success = False
                for sale_order_id in order:
                    appoinment_id = request.env['appointment.appointment'].sudo().search([('sale_order_id','=',sale_order_id.id)])
                    if appoinment_id:
                        appoinment_ref = appoinment_id.sequence
                        appoinment_obj_id = appoinment_id
                        appoinment_id = appoinment_id.id
                        
                        if sale_order_id.amount_total <= 0:
                            appoinment_obj_id.website_payment_status = "paid"
                            appoinment_obj_id._compute_payment_from_payment()
                            
                        
                        if appoinment_obj_id and appoinment_obj_id.website_payment_status == "paid":
                            success = True
                        else:
                            success = False
                            
                    render_ctx.update({
                        'email':sale_order_id.partner_id.email or '',
                        'appoinment_ref':appoinment_ref or '',
                        'success':success or '',
                        'appoinment_id':appoinment_id,
                        })
            
            
            return request.render("ppts_website_theme.website_appointment_payment_success_page", render_ctx)
        else:
            customer_event_id = request.session.get('customer_event_id',False)
            customer_sale_id = request.session.get('customer_sales_id',False)
            success = False
            event_id = request.env['event.event'].sudo().browse(customer_event_id)
            order = request.website.sale_get_order()
            
            event_reg_id = request.env['event.registration'].sudo().search([('sale_order_id','=',order.id)], limit=1)
            
            if event_reg_id and event_reg_id.website_payment_status == "paid":
                success = True
            
            render_ctx = {
                'email':order.partner_id.email or '',
                'event_ref':event_id.name or '',
                'success':success,
                'event_id':event_id.id,
                'sale_id':order.id,
            }
            
            
            return request.render("ppts_website_theme.website_appointment_payment_success_page", render_ctx)
        
            
            
            
    # Appointment checkout city filters
    @http.route(['/checkout/city/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_checkout_city_filter(self, **post):
        domain = []
        city = []
        if 'browse_country' in post and post['browse_country'] != '':
            domain.append(('country_id','=',int(post['browse_country'])))
        city_master = request.env['city.master'].sudo().search(domain)
        for rec in  city_master:
            city.append({
                    "id":rec.id,
                    'name':rec.name
                })
        return json.dumps(city)    
    
    
    
    
    
