from odoo import http, tools, _
from odoo.http import request, Response
import odoo
import odoo.modules.registry
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.http_routing.models.ir_http import slug,unslug
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

_logger = logging.getLogger(__name__)

class WebsiteCalendar(http.Controller):

    @http.route(['/meditation'], type='http', auth="public", website=True, cros='*')
    def website_meditation_page(self, **post):
        return request.render('ppts_website_theme.website_meditation_page')

    @http.route(['/therapy'], type='http', auth="public", website=True, cros='*')
    def website_therapy_page(self, **post):
        return request.render('ppts_website_theme.website_therapy_page')


    @http.route(['/employee/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_employee_filter(self, **post):
        domain = []
        employee =[]
        platform_list = [post['browse_platform']]
        if 'browse_help' in post and post['browse_help'] != '':
            domain.append(('by_solution','=',int(post['browse_help'])))
        if 'browse_location' in post and post['browse_location'] != '' :
            domain.append(('company_id','=',int(post['browse_location'])))
        if 'browse_qualified' in post and post['browse_qualified'] != '' :
            domain.append(('by_support','=',int(post['browse_qualified'])))
        if 'browse_platform' in post and post['browse_platform'] != '' :
            # domain.append(('by_platform','=',post['browse_platform']))
            if 'browse_platform' in post and post['browse_platform'] == 'online' or 'onsite':
                platform_list.append('online/onsite')
                domain.append(('by_platform','in',platform_list))
            if 'browse_platform' in post and post['browse_platform'] == 'online/onsite':
                platform_list.append('online')
                platform_list.append('onsite')
                # domain.append(('by_platform','in',platform_list))
                domain.append(('by_platform','in',platform_list))
                print(domain,'hdjjduferwerasdjfiadjsadjadfjdsjfsjdf-')
        hr_ids = request.env['hr.employee'].sudo().search(domain, order='name asc')
        for each_employee in hr_ids:
            employee.append({
                    "id":each_employee.id,
                    'name':each_employee.name,
                    'job': each_employee.get_job_position_website(),
                    'location':each_employee.company_id.name,
                    'image':'/web/image?model=hr.employee&id=%s&field=image_1920' % (each_employee.id) if each_employee.image_1920 else '/web/image?model=hr.employee&id=%s&field=image_128',
                })
        return json.dumps(employee)

    @http.route(['/website/therapy/category'], type='http', auth="public", website=True, cros='*')
    def website_therapy_categ_page(self, **post):
        return request.render('ppts_website_theme.website_therapy_category_page')

    @http.route(['/employee/categ/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_categ_employee_filter(self, **post):
        domain = [];employee =[]
        emp_category = request.env['hr.employee.category'].sudo().search([('name','=','Therapist')],limit=1)
        domain.append(('employee_type','in',emp_category.id))
        platform_list=[post['categ_browse_platform']]
        if 'categ_browse_help' in post and post['categ_browse_help'] != '':
            domain.append(('by_solution','=',int(post['categ_browse_help'])))
        if 'categ_browse_location' in post and post['categ_browse_location'] != '' :
            domain.append(('company_id','=',int(post['categ_browse_location'])))
        if 'categ_browse_qualified' in post and post['categ_browse_qualified'] != '' :
            domain.append(('by_support','=',int(post['categ_browse_qualified'])))
        if 'categ_browse_platform' in post and post['categ_browse_platform'] != '' :
            
            # domain append based on current requirement 17/11/2022
            if 'categ_browse_platform' in post and post['categ_browse_platform'] == 'online' or 'onsite':
                platform_list.append('online/onsite')
                domain.append(('by_platform','in',platform_list))
            if 'categ_browse_platform' in post and post['categ_browse_platform'] == 'online/onsite':
                platform_list.append('online')
                platform_list.append('onsite')
                # domain.append(('by_platform','in',platform_list))

                domain.append(('by_platform','in',platform_list))
        hr_ids = request.env['hr.employee'].sudo().search(domain, order='name asc')
        for each_employee in hr_ids:
            employee.append({
                    "id":each_employee.id,
                    'name':each_employee.name,
                    'job': each_employee.get_job_position_website(),
                    'location':each_employee.company_id.name,
                    'image':'/web/image?model=hr.employee&id=%s&field=image_1920' % (each_employee.id) if each_employee.image_1920 else '/web/image?model=hr.employee&id=%s&field=image_128',
                })
        return json.dumps(employee)

    @http.route(['/training'], type='http', auth="public", website=True,cros='*')
    def training_main_page(self, **post):
        return request.render('ppts_website_theme.training_main_page')

    @http.route(['/training/main/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def training_main_filter(self, **post):
        domain = []
        event_data =[]
        event_val_id =[]
        domain.append(('event_service_categ_id.is_training','=',True))
        multiple_event_ids = request.env['multi.date.line'].sudo().search([('date_begin','=',datetime.strptime(post['multi_date'],'%d.%m.%Y'))])


        domain.append(('is_published_event','=',True))

        if 'platform' in post and post['platform'] != '':
            domain.append(('type_event','=',post['platform']))

        if 'course_name' in post and post['course_name'] != '[]':
            course_name = post['course_name'][1:-1].split(',')
            if course_name: 
                course_name = [int(item[1:-1]) for item in course_name]
                domain.append(('event_sub_categ_id','in',course_name))

        if 'levels' in post and post['levels'] != '[]':
            levels = post['levels'][1:-1].split(',')
            if levels: 
                levels = [int(item[1:-1]) for item in levels]
                domain.append(('class_level_id','in',levels))

        if 'country' in post and post['country'] != '[]':
            country = post['country'][1:-1].split(',')
            if country: 
                country = [int(item[1:-1]) for item in country]
                domain.append(('address_id.country_id','in',country))

        if 'city' in post and post['city'] != '[]':
            city = post['city'][1:-1].split(',')
            if city: 
                country = [int(item[1:-1]) for item in city]
                domain.append(('address_id.city_id','in',country))
        
        type_event_img = ''
        for each_multi_event in multiple_event_ids:
            event_val_id.append(each_multi_event.event_id.id)
        if event_val_id:
            domain.append(('id', 'in',event_val_id))

        event_ids = request.env['event.event'].sudo().search(domain, order='name asc')
        for each_event in event_ids:
            if each_event.type_event == 'type_online':
                type_event = 'Online'
                type_event_img = """ <img src="/ppts_website_theme/static/src/img/source_icons_laptop.svg" width="24px" height="24px" /> """
            elif each_event.type_event == 'type_onsite':
                type_event = 'Onsite'
                type_event_img = """ <img src="/ppts_website_theme/static/src/img/source_icons_yoga.svg" width="24px" height="24px" /> """
            else:
                type_event = 'Hybrid'
                type_event_img = """ <img src="/ppts_website_theme/static/src/img/source_icons_user.svg" width="24px" height="24px" /> """

            image_url = '/web/image?model=event.event&id=%s&field=image' % (each_event.id) \
                if each_event.image else '/ppts_website_theme/static/src/img/ue2.jpg'

            if each_event.event_multiple_date == 'oneday':
                event_date = each_event.s_start_date.strftime("%d %B")
            if each_event.event_multiple_date == 'multiday':
                event_start_date = each_event.multi_date_line_ids.ids[0]
                event_start_date = request.env['multi.date.line'].sudo().browse(event_start_date)
                event_end_date = each_event.multi_date_line_ids.ids[-1]
                event_end_date = request.env['multi.date.line'].sudo().browse(event_end_date)
                event_date = event_start_date.date_begin.strftime("%d %B") + ' To ' + event_end_date.date_begin.strftime("%d %B")

            event_data.append({
                    'id':each_event.id,
                    'image':image_url,
                    'platform': dict(each_event._fields['type_event'].selection).get(each_event.type_event),
                    'location':each_event.address_id.name,
                    'user': each_event.facilitator_evnt_ids[0].name,
                    'user_id': each_event.facilitator_evnt_ids[0].id,
                    'date': event_date,
                    'name':each_event.name,
                    'cost':each_event.get_event_price(),
                    'event_sub_categ_id': each_event.event_sub_categ_id.name,
                    'type_event_img': type_event_img,
                    })
        return json.dumps(event_data)

    @http.route(['/training/individual/page'], type='http', auth="public", website=True, cros='*')
    def website_traning_individual_page(self, **post):
        return request.render('ppts_website_theme.website_traning_individual_page')


    @http.route(['/training/<training_id>/individual/page'], type='http', auth="public", website=True, cros='*')
    def website_training_individual_page(self, training_id, **post):
        _, training_id = unslug(training_id) 
        training_id = request.env['calendar.appointment.type'].sudo().browse(training_id)
        values = {
            'training_id': training_id,
            }
        return request.render('ppts_website_theme.website_traning_individual_page',values)

        
    @http.route(['/event/most/popular'], type='http', auth="public", website=True, cros='*')
    def event_most_popular(self, **post):
        return request.render('ppts_website_theme.website_theme_event_most_popular')

    @http.route(['/training/individual/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def training_individual_filter(self, **post):
        domain = []
        event_data =[]
        domain.append(('is_published_event','=',True))

        if 'platform' in post and post['platform'] != '':
            domain.append(('type_event','=',post['platform']))

        if 'course_name' in post and post['course_name'] != '[]':
            course_name = post['course_name'][1:-1].split(',')
            if course_name: 
                course_name = [int(item[1:-1]) for item in course_name]
                domain.append(('event_sub_categ_id','in',course_name))

        if 'levels' in post and post['levels'] != '[]':
            levels = post['levels'][1:-1].split(',')
            if levels: 
                levels = [int(item[1:-1]) for item in levels]
                domain.append(('class_level_id','in',levels))

        if 'country' in post and post['country'] != '[]':
            country = post['country'][1:-1].split(',')
            if country: 
                country = [int(item[1:-1]) for item in country]
                domain.append(('address_id.country_id','in',country))

        if 'city' in post and post['city'] != '[]':
            city = post['city'][1:-1].split(',')
            if city: 
                country = [int(item[1:-1]) for item in city]
                domain.append(('address_id.city_id','in',country))
        
        event_ids = request.env['event.event'].sudo().search(domain, order='name asc')
        for each_event in event_ids:
            if each_event.type_event == 'type_online':
                type_event = 'Online'
            elif each_event.type_event == 'type_onsite':
                type_event = 'Onsite'
            else:
                type_event = 'Hybrid'
            image_url = '/web/image?model=event.event&id=%s&field=image' % (each_event.id) \
                if each_event.image else '/ppts_website_theme/static/src/img/ue2.jpg'

            event_data.append({
                    'id':each_event.id,
                    'image':image_url,
                    'platform':type_event,
                    'location':each_event.address_id.name,
                    'user':each_event.sale_incharge_id.name,
                    'date':each_event.s_start_date.strftime("%d %B") or '',
                    'name':each_event.name,
                    'cost':each_event.get_event_price(),

                    })
        return json.dumps(event_data)

    @http.route(['/healing/apprpage/page'], type='http', auth="public", website=True, cros='*')
    def website_healing_apprpage_page(self, **post):
        return request.render('ppts_website_theme.healing_apprpage_page')

    @http.route(['/website/retreats/page'], type='http', auth="public", website=True, cros='*')
    def website_retreats_page(self, **post):
        return request.render('ppts_website_theme.website_retreats_page')

    @http.route(['/welliness/retreats'], type='http', auth="public", website=True, cros='*')
    def website_welliness_retreats_page(self, **post):
        return request.render('ppts_website_theme.website_wellness_retreats_page')      



    @http.route(['/employee/filter/details'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_employee_filter_details(self, **post):
        domain = []
        employee =[]
        platform_list=[post['browse_platform']]
        if 'browse_help' in post and post['browse_help'] != '':
            domain.append(('by_solution','=',int(post['browse_help'])))
        if 'browse_location' in post and post['browse_location'] != '' :
            domain.append(('company_id','=',int(post['browse_location'])))
        if 'browse_qualified' in post and post['browse_qualified'] != '' :
            domain.append(('by_support','=',int(post['browse_qualified'])))
        if 'browse_platform' in post and post['browse_platform'] != '' :
            # domain append based on current requirement 21/11/2022
            if 'browse_platform' in post and post['browse_platform'] == 'online' or 'onsite':
                platform_list.append('online/onsite')
                domain.append(('by_platform','in',platform_list))
            if 'browse_platform' in post and post['browse_platform'] == 'online/onsite':
                platform_list.append('online')
                platform_list.append('onsite')
                # domain.append(('by_platform','in',platform_list))
                domain.append(('by_platform','in',platform_list))
            # domain.append(('by_platform','=',post['browse_platform']))
        hr_ids = request.env['hr.employee'].sudo().search(domain, order='name asc')
        for each_employee in hr_ids:
            employee.append({
                    "id":each_employee.id,
                    'name':each_employee.name,
                    'job': each_employee.get_job_position_website(),
                    'location':each_employee.company_id.name,
                    'image':'/web/image?model=hr.employee&id=%s&field=image_1920' % (each_employee.id) if each_employee.image_1920 else '/web/image?model=hr.employee&id=%s&field=image_128',
                })
        return json.dumps(employee)


    @http.route(['/all/welliness/retreats'], type='http', auth="public", website=True, cros='*')
    def website_all_welliness_retreats(self, **post):
        return request.render('ppts_website_theme.website_wellness_retreats_all_page')



