from odoo import http, tools, _
from odoo.http import request, Response
from datetime import datetime, timedelta
import json, werkzeug
import requests
import urllib.request
import urllib
from bs4 import BeautifulSoup
from datetime import datetime

class WebsiteCalendar(http.Controller):
    @http.route(['/event/calendar/resources/pass/session'], type='http', auth="public", website=True, csrf=False)
    def event_calendar_resources_pass_session(self, **post):
        if post:
            if 'header_location' in post:
                if post['header_location'] == 'all':
                    request.session['header_location'] = 'all'
                else:
                    location_ids = request.env['venue.venue'].search([('id','=',int(post['header_location']))],limit=1)
                    request.session['header_location'] = location_ids.id

            if 'header_services' in post:
                if post['header_services'] == 'all':
                    request.session['header_services'] = 'all'
                else:
                    service_ids = request.env['appointment.category'].search([('id','=',int(post['header_services']))],limit=1)
                    request.session['header_services'] = service_ids.id

            if 'header_instructor' in post:
                if post['header_instructor'] == 'all':
                    request.session['header_instructor'] = 'all'
                else:
                    header_instructor = post['header_instructor'].split(",")
                    for i in range(0, len(header_instructor)): 
                        header_instructor[i] = int(header_instructor[i])
                    request.session['header_instructor'] = header_instructor

            if 'header_gender' in post:
                if post['header_gender'] == 'all':
                    request.session['header_gender'] = 'all'
                else:
                    request.session['header_gender'] = post['header_gender']

            if 'header_filter_reset' in post:
                if post['header_filter_reset'] == "True":
                    request.session['header_filter_reset'] = 'all'
                else:
                    request.session['header_filter_reset'] = 'false'

            return 'True'

    @http.route(['/event/calendar/resources',
                 '/event/calendar/resources/<event_details>/<apt_evnt>'], type='http', auth="public",  methods=['GET'], website=True)
    def event_website_calendar_resources(self, event_details = None, apt_evnt = None, **post):
        resources = [];events = [];domain = []
        if post:
            if 'header_filter_reset' in request.session:
                if request.session['header_filter_reset'] == 'all':
                    request.session['header_instructor'] = 'all'
                    request.session['header_services'] = 'all'
                    request.session['header_location'] = 'all'
                    request.session['header_gender'] = 'all'
                    request.session['header_filter_reset'] = 'false'

            if 'header_location' in request.session:
                if request.session['header_location'] != 'all':
                    domain.append(('location','=',int(request.session['header_location'])))
            if 'header_services' in request.session:
                if request.session['header_services'] != 'all':
                    domain.append(('service_category_ids','in',int(request.session['header_services'])))

            if 'header_instructor' in request.session:
                if request.session['header_instructor'] != 'all':
                    domain.append(('facilitator','in',request.session['header_instructor']))

            if 'header_gender' in request.session:
                if request.session['header_gender'] != 'all':
                    domain.append(('gender','=',request.session['header_gender']))

            date_st = post['start'].split('T')
            availability_ids = request.env['availability.availability'].sudo().search(domain)
            for i in availability_ids:
                if i.available_date and i.start_time and i.end_time and i.date_range == 'ongoing':
                    if date_st[0] == i.available_date.strftime("%Y-%m-%d"):
                        resources.append({
                            'id': i.facilitator.id,
                            'title': i.facilitator.name,
                            'location': i.facilitator.location.id,
                            'gender': i.facilitator.gender
                        })
                        date_start = datetime.strptime(i.available_date.strftime("%Y-%m-%d")+' '+i.start_time, "%Y-%m-%d %H:%M")
                        date_end = datetime.strptime(i.available_date.strftime("%Y-%m-%d")+' '+i.end_time, "%Y-%m-%d %H:%M")
                        date_start = date_start - timedelta(hours=5, minutes=30)
                        date_end = date_end - timedelta(hours=5, minutes=30)
                        date_start = str(date_start.strftime("%Y-%m-%d %H:%M")).split(" ")
                        date_end = str(date_end.strftime("%Y-%m-%d %H:%M")).split(" ")

                        if i.availability == 'available':
                            services_fas = ''
                            for s in i.facilitator.service_category_ids:
                                services_fas += s.name + '</br>'
                            events.append({
                                'id': i.facilitator.id,
                                'resourceId': i.facilitator.id,
                                'title': i.facilitator.name,
                                'start': date_start[0]+'T'+date_start[1]+':00Z',
                                'end': date_end[0]+'T'+date_end[1]+':00Z',
                                'className': 'fc-bg-facilitator-available-grey-color',
                                'display': 'background',
                                'event': 'False',
                                'services': services_fas or 'No services'
                            })

                        elif i.availability == 'unavailable':
                            if i.availabile_type == 'event' and apt_evnt == 'evnt':
                                events.append({
                                    'id': i.facilitator.id,
                                    'resourceId': i.facilitator.id,
                                    'title': i.event_id.name,
                                    'start': date_start[0]+'T'+date_start[1]+':00Z',
                                    'end': date_end[0]+'T'+date_end[1]+':00Z',
                                    'className': 'fc-bg-facilitator-event-default-color',
                                    'url': '/web#action=493&active_id='+ str(i.event_id.id) +'&model=event.registration&view_type=list&cids=&menu_id=341',
                                    'event_type': i.availabile_type,
                                    'location': i.location.id,
                                    'event': 'True',
                                    'gender': i.facilitator.gender,
                                })
                            elif i.availabile_type == 'unavailable':
                                events.append({
                                    'id': i.facilitator.id,
                                    'resourceId': i.facilitator.id,
                                    'title': "Unavailable",
                                    'start': date_start[0]+'T'+date_start[1]+':00Z',
                                    'end': date_end[0]+'T'+date_end[1]+':00Z',
                                    'className': 'fc-bg-facilitator-unavailable',
                                })
                            elif i.availabile_type == 'other':
                                events.append({
                                    'id': i.facilitator.id,
                                    'resourceId': i.facilitator.id,
                                    'title': i.reason,
                                    'start': date_start[0]+'T'+date_start[1]+':00Z',
                                    'end': date_end[0]+'T'+date_end[1]+':00Z',
                                    'className': 'fc-bg-facilitator-break',
                                })
                            elif i.availabile_type == 'appoinment' and i.appointment_id:
                                ap_new = 0;ap_confirm = 0;ap_arrive = 0;ap_done = 0;ap_cancel = 0;class_name = ''
                                if i.appointment_id.state == 'new':
                                    ap_new += 1
                                    class_name = 'fc-bg-facilitator-appoinment-new'
                                    tooltip_name = 'tooltip-header-new'
                                if i.appointment_id.state == 'partially_cancelled' or i.appointment_id.state == 'ongoing':
                                    class_name = 'fc-bg-facilitator-appoinment-confirm'
                                    tooltip_name = 'tooltip-header-confirm'
                                if i.appointment_id.state == 'confirm':
                                    ap_confirm += 1
                                    class_name = 'fc-bg-facilitator-appoinment-confirm'
                                    tooltip_name = 'tooltip-header-confirm'
                                if i.appointment_id.state == 'arrive':
                                    ap_arrive += 1
                                    class_name = 'fc-bg-facilitator-appoinment-arrive'
                                    tooltip_name = 'tooltip-header-arrive'
                                if i.appointment_id.state == 'done':
                                    ap_done += 1
                                    class_name = 'fc-bg-facilitator-appoinment-done'
                                    tooltip_name = 'tooltip-header-done'
                                if i.appointment_id.state == 'cancel':
                                    ap_cancel += 1
                                    class_name = 'fc-bg-facilitator-appoinment-cancel'
                                    tooltip_name = 'tooltip-header-cancel'
                                # if i.appointment_id.state == 'partially_cancelled'
                                app_ids = [];app_ss = False
                                for j in i.appointment_id.appointment_line_id.appointments_type_id:
                                    app_ids.append(j.id)
                                if len(app_ids) != 0:
                                    app_ss = app_ids[0]
                                events.append({
                                    'id': i.facilitator.id,
                                    'resourceId': i.facilitator.id,
                                    'title': i.appointment_id.name,
                                    'start': date_start[0]+'T'+date_start[1]+':00Z',
                                    'end': date_end[0]+'T'+date_end[1]+':00Z',
                                    'className': class_name,
                                    'status': i.appointment_id.state,
                                    'location': i.location.id,
                                    'event': 'True',
                                    'gender': i.facilitator.gender,
                                    'client': i.appointment_id.partner_id.name,
                                    'client_id': i.appointment_id.partner_id.id,
                                    'phone': i.appointment_id.partner_id.phone or '',
                                    'mobile': i.appointment_id.partner_id.mobile or '',
                                    'event_type_appoinment': 'True',
                                    'tooltip_name':tooltip_name,
                                    'ap_new':ap_new,
                                    'ap_confirm':ap_confirm,
                                    'ap_arrive':ap_arrive,
                                    'ap_done':ap_done,
                                    'ap_cancel':ap_cancel,
                                    'fac-name': i.facilitator.name,
                                    'fac_name': i.facilitator.name,
                                    'client-name': i.appointment_id.partner_id.name,
                                    'client_name': i.appointment_id.partner_id.name,
                                    'client-id': i.appointment_id.partner_id.id,
                                    'client_id': i.appointment_id.partner_id.id,
                                    'client_phone': i.appointment_id.partner_id.phone or '',
                                    'client_email': i.appointment_id.partner_id.email or '',
                                    'appointment_type_id': i.appointment_line_id.id,
                                    'ap_start_time': i.start_time,
                                    'ap_end_time': i.end_time,
                                    'ap_length': i.appointment_line_id.duration,
                                    'ap_id': i.id,
                                    'ap_date': i.available_date.strftime("%Y-%m-%d"),
                                    'ap_line_id': i.appointment_line_id.id,
                                    'app_line_id': i.id,
                                    'notes': i.appointment_id.notes or '',
                                    'app_id': i.appointment_id.id,
                                    'fac_id': i.facilitator.id,
                                    'sale_id': i.sale_order_line.id,
                                    'appointments_type_id': app_ss,
                                    'apt_room_id':i.appointment_line_id.apt_room_id.id or '',
                                    'invoice_status': i.invoice_status,
                                    'balance': i.balance,
                                    'currency_id': i.sale_order_line.currency_id.name or 'AED',
                                    'invoice_status': 'paid' if i.invoice_status == 'invoiced' else 'unpaid',
                                })
                            # 2021-01-24T00:00:00Z
            if event_details == 'events':return json.dumps(events)
            else:return json.dumps(resources)

    @http.route(['/event/calendar/resources/week'], type='http', auth="public",  methods=['GET'], website=True)
    def event_website_calendar_resources_week(self, **post):
        events = []
        availability_ids = request.env['availability.availability'].sudo().search([('availability','=','unavailable')])
        for i in availability_ids:
            services_fas = []
            for s in i.facilitator.service_category_ids:
                services_fas.append(s.id)
            if i.start_time and i.end_time:
                date_start = datetime.strptime(i.available_date.strftime("%Y-%m-%d")+' '+i.start_time, "%Y-%m-%d %H:%M")
                date_end = datetime.strptime(i.available_date.strftime("%Y-%m-%d")+' '+i.end_time, "%Y-%m-%d %H:%M")
                date_start = date_start - timedelta(hours=5, minutes=30)
                date_end = date_end - timedelta(hours=5, minutes=30)
                date_start = str(date_start.strftime("%Y-%m-%d %H:%M")).split(" ")
                date_end = str(date_end.strftime("%Y-%m-%d %H:%M")).split(" ")
                if i.availabile_type == "event":
                    events.append({
                            'id': i.facilitator.id,
                            'resourceId': i.facilitator.id,
                            'title': i.event_id.name,
                            'start': date_start[0]+'T'+date_start[1]+':00Z',
                            'className': 'fc-bg-facilitator-event-default-color',
                            'url': '/web#action=493&active_id='+ str(i.event_id.id) +'&model=event.registration&view_type=list&cids=&menu_id=341',
                            'event_type': i.availabile_type,
                            'location': i.location.id,
                            'event': 'True',
                            'gender': i.facilitator.gender,
                            'services': services_fas,
                        })
                elif i.availabile_type == 'appoinment' and i.appointment_id:
                    ap_new = ap_confirm = ap_arrive = ap_done = ap_cancel = 0;class_name = '';tooltip_name = ''
                    if i.appointment_id.state == 'new':
                        ap_new += 1
                        class_name = 'fc-bg-facilitator-appoinment-new'
                        tooltip_name = 'tooltip-header-new'
                    if i.appointment_id.state == 'confirm':
                        ap_confirm += 1
                        class_name = 'fc-bg-facilitator-appoinment-confirm'
                        tooltip_name = 'tooltip-header-confirm'

                    if i.appointment_id.state == 'ongoing':
                        ap_confirm += 1
                        class_name = 'fc-bg-facilitator-appoinment-confirm'
                        tooltip_name = 'tooltip-header-confirm'
                    
                    if i.appointment_id.state == 'partially_cancelled':
                        ap_confirm += 1
                        class_name = 'fc-bg-facilitator-appoinment-confirm'
                        tooltip_name = 'tooltip-header-confirm'
                    
                    if i.appointment_id.state == 'arrive':
                        ap_arrive += 1
                        class_name = 'fc-bg-facilitator-appoinment-arrive'
                        tooltip_name = 'tooltip-header-arrive'
                    if i.appointment_id.state == 'done':
                        ap_done += 1
                        class_name = 'fc-bg-facilitator-appoinment-done'
                        tooltip_name = 'tooltip-header-done'
                    if i.appointment_id.state == 'cancel':
                        ap_cancel += 1
                        class_name = 'fc-bg-facilitator-appoinment-cancel'
                        tooltip_name = 'tooltip-header-cancel'
                    events.append({
                            'id': i.facilitator.id,
                            'resourceId': i.facilitator.id,
                            'title': i.appointment_id.name,
                            'start': date_start[0]+'T'+date_start[1]+':00Z',
                            'end': date_end[0]+'T'+date_end[1]+':00Z',
                            'className': class_name,
                            'status': i.appointment_id.state,
                            'location': i.location.id,
                            'event': 'True',
                            'gender': i.facilitator.gender,
                            'client': i.appointment_id.partner_id.name or '',
                            'phone': i.appointment_id.partner_id.phone or '',
                            'event_type_appoinment': 'True',
                            'tooltip_name':tooltip_name,
                            'ap_new':ap_new,
                            'ap_confirm':ap_confirm,
                            'ap_arrive':ap_arrive,
                            'ap_done':ap_done,
                            'ap_cancel':ap_cancel,
                            'services': services_fas,
                            'invoice_status': 'paid' if i.invoice_status == 'to invoice' else 'unpaid',
                            'balance': i.balance,
                            'currency_id': i.sale_order_line.currency_id.name,
                        })
        return json.dumps(events)

    @http.route(['/event/calendar/add-unavailability'], type='http', auth="public", website=True, csrf=False)
    def event_website_calendar_add_unavailability(self, **post):
        available_ids = request.env['hr.employee'].sudo().search([('name','=',post['unavail_name'])])
        if 'facilitator_unavail_name' in request.session: request.session.pop('facilitator_unavail_name') 
        request.session['facilitator_unavail_name'] = available_ids.id
        return 'True'
    
    @http.route(['/event/calendar/view-profile'], type='http', auth="public", website=True, csrf=False)
    def event_website_calendar_view_profile(self, **post):
        available_ids = request.env['hr.employee'].sudo().search([('name','=',post['unavail_name'])])
        url = '/web#id='+str(available_ids.id)+'&action=481&model=hr.employee&view_type=form&cids=&menu_id=321'
        return url

    @http.route(['/event/calendar/resources/resajax'], type='http', auth="public", website=True, csrf=False)
    def event_website_calendar_resources_resajax(self, **post):
        resources = [];exception_id = {}
        if 'date' in post:
            availability_ids = request.env['availability.availability'].sudo().search([('available_date','!=',False)])
            if availability_ids:    
                for i in availability_ids:
                    if post['date'] == i.available_date.strftime("%Y-%m-%d"):
                        resources.append(i.facilitator.id)
                hr_ids = request.env['hr.employee'].sudo().search([])
                for i in hr_ids:
                    if i.id not in resources:
                        exception_id[i.id] = i.name
        return json.dumps(exception_id)

    @http.route(['/event/calendar/resources/location/resajax'], type='http', auth="public", website=True, csrf=False)
    def event_website_calendar_resources_location_resajax(self, **post):
        exception_id = {}
        company_ids = request.env['venue.venue'].sudo().search([])
        for i in company_ids:
            exception_id[i.id] = i.name
        return json.dumps(exception_id)

    @http.route(['/event/calendar/resources/services/resajax'], type='http', auth="public", website=True, csrf=False)
    def event_website_calendar_resources_services_resajax(self, **post):
        exception_id = {}
        categ_ids = request.env['appointment.category'].sudo().search([])
        for i in categ_ids:
            exception_id[i.id] = i.name
        return json.dumps(exception_id)

    @http.route(['/event/calendar/resources/instructor/resajax'], type='http', auth="public", website=True, csrf=False)
    def event_website_calendar_resources_instructor_resajax(self, **post):
        exception_id = {}
        availability_ids = request.env['availability.availability'].sudo().search([])
        if availability_ids:
            for i in availability_ids:
                if i.date_range == 'ongoing':
                    if post['date'] == i.available_date.strftime("%Y-%m-%d"):
                        exception_id[i.facilitator.id] = i.facilitator.name
                    if post['date'] == 'True':
                        exception_id[i.facilitator.id] = i.facilitator.name
            return json.dumps(exception_id)

    @http.route(['/event/calendar/add/availability'], type='http', auth="public", website=True, csrf=False)
    def event_website_calendar_add_availability(self, **post):
        if post:
            facilitator = request.env['hr.employee'].sudo().search([('name','=',post['facilitator'])],limit=1)
            services = request.httprequest.form.getlist('services')
            services = list(map(int, services))
            if facilitator:
                avail = request.env['availability.availability'].sudo().create({
                    'facilitator':facilitator.id,
                    'service_category_ids': services,
                    'availability':'available',
                    'location_id':int(post['location']),
                    'available_date':datetime.strptime(post['date-add-avail'], "%Y-%m-%d"),
                    'start_time':post['start_time_cu'],
                    'end_time':post['end_time_cu'],
                    'privacy':post['privacy'],
                })
        return request.redirect('/event/calendar')

    @http.route(['/event/type/css'], type='http', auth="public", website=True, csrf=False)
    def event_type_css(self, **post):
        class_code = {}
        event_type_ids = request.env['event.type'].sudo().search([])
        for i in event_type_ids:
            if i.website_class and i.website_color_code:
                class_code[i.website_color_code] = i.website_class
        return json.dumps(class_code)

    @http.route(['/facilitator/list'], type='http', auth="public", website=True, csrf=False)
    def products_list_faci(self, **post):
        partners = [];partner_ids = request.env['hr.employee'].sudo().search([])
        for i in partner_ids:
            partners.append(i.name)
        return json.dumps(partners)

    @http.route(['/partner/list'], type='http', auth="public", website=True, csrf=False)
    def partner_list(self, **post):
        partners = [];partner_ids = request.env['res.partner'].sudo().search([])
        for i in partner_ids:
            partners.append(i.name)
        return json.dumps(partners)

    @http.route(['/appointment/services'], type='http', auth="public", website=True, csrf=False)
    def app_services_list(self, **post):
        partners = {};partner_ids = request.env['calendar.appointment.type'].sudo().search([])
        for i in partner_ids:
            partners[i.id] = i.name
        return json.dumps(partners)
    
    @http.route(['/appointment/rooms'], type='http', auth="public", website=True, csrf=False)
    def app_services_rooms(self, **post):
        room_dict = {};room_id = request.env['roomtype.master'].sudo().search([('room_maincateg_id.roomcateg_code','=','APT')])
        for i in room_id:
            room_dict[i.id] = i.room_type
        return json.dumps(room_dict)

    @http.route(['/partner/list/search'], type='http', auth="public", website=True, csrf=False)
    def partner_list_search(self, **post):
        if post and 'partner' in post:   
            partner_id = request.env['res.partner'].sudo().search([('name','=',post['partner'])],limit=1)
            return str(partner_id.phone or '') + '$$' + str(partner_id.email or '') + '$$' + str(partner_id.id)
    
    @http.route(['/appointment/services/get/details'], type='http', auth="public", website=True, csrf=False)
    def appointment_services_get_details(self, **post):
        if post:
            app_type_id = request.env['calendar.appointment.type'].sudo().search([('id','=',post['service_app'])])
            return str(app_type_id.appointment_duration)

    @http.route(['/event/calendar/appointment/create'], type='http', auth="public", website=True, csrf=False, methods=['GET', 'POST'])
    def event_calendar_appointment_create(self, **post):
        check_availability = request.env['availability.availability'].sudo().search([('partner_id','=',int(post.get('editAvail-client-name-id'))),('available_date','=',post.get('editAvail-client-date-fi'))], limit=1)
        if check_availability:
            if post.get('start_time_app')>=check_availability.start_time and post.get('start_time_app')<=check_availability.end_time:
                values = {'appointment_result': "Another appointment scheduled already."}
                request.session['appointment_result'] = "Another appointment scheduled already."
                return request.redirect('/event/calendar?result=error')
            elif post.get('end_time_app')>=check_availability.start_time and post.get('end_time_app')<=check_availability.end_time:
                values = {'appointment_result': "Another appointment scheduled already."}
                request.session['appointment_result'] = "Another appointment scheduled already."
                return request.redirect('/event/calendar?result=error')

        if post:
            partner_id = request.env['res.partner'].search([('name','=',post['editAvail-client-name-fi'])])
            appointment_id = request.env['appointment.appointment'].sudo().create({
                'partner_id':partner_id.id,
                'booking_date':datetime.strptime(post['editAvail-client-date-fi'], "%Y-%m-%d"),
                'notes':str(post.get('note_app')),
                })
            values = {'appointment_result': "Appointment created successfully"}
            request.session['appointment_result'] = "Appointment created successfully"
            return request.redirect('/event/calendar?result=success')
        
    
    @http.route(['/event/calendar/appointment/edit'], type='http', auth="public", website=True, csrf=False, methods=['GET', 'POST'])
    def event_calendar_appointment_edit(self, **post):                   
        if post.get("app_line_id"):
            check_unavailablity = request.env['availability.availability'].sudo().search([('facilitator','=',int(post.get('fac_id'))),('available_date','=',post.get('editAvail-client-date-fi')),('appointment_line_id','!=',int(post.get("app_line_id"))),('availability','=','unavailable')])
        else:
            check_unavailablity = request.env['availability.availability'].sudo().search([('facilitator','=',int(post.get('fac_id'))),('available_date','=',post.get('editAvail-client-date-fi')),('availability','=','unavailable')])
        
        if check_unavailablity:
            start_time_app = datetime.strptime(str(post.get('editAvail-client-date-fi')+" "+post.get('start_time_app')), "%Y-%m-%d %H:%M")

            end_time_app = datetime.strptime(str(post.get('editAvail-client-date-fi')+" "+post.get('end_time_app')), "%Y-%m-%d %H:%M")

            for i in check_unavailablity:

                start_time = datetime.strptime(str(post.get('editAvail-client-date-fi')+" "+i.start_time), "%Y-%m-%d %H:%M")

                end_time = datetime.strptime(str(post.get('editAvail-client-date-fi')+" "+i.end_time), "%Y-%m-%d %H:%M")

                if start_time_app>=start_time and start_time_app<=end_time:
                    values = {'appointment_result': "Another appointment scheduled already."}
                    request.session['appointment_result'] = "Another appointment scheduled already."
                    return request.redirect('/event/calendar')
                elif end_time_app>=start_time and end_time_app<=end_time:
                    values = {'appointment_result': "Another appointment scheduled already."}
                    request.session['appointment_result'] = "Another appointment scheduled already."
                    return request.redirect('/event/calendar')

        if post.get("app_line_id"):
            check_availability = request.env['availability.availability'].sudo().search([('facilitator','=',int(post.get('fac_id'))),('available_date','=',post.get('editAvail-client-date-fi')),('appointment_line_id','!=',int(post.get("app_line_id"))),('availability','=','available')])
        else:
            check_availability = request.env['availability.availability'].sudo().search([('facilitator','=',int(post.get('fac_id'))),('available_date','=',post.get('editAvail-client-date-fi')),('availability','=','available')])
        
       
        if check_availability:

            start_time_app = datetime.strptime(str(post.get('editAvail-client-date-fi')+" "+post.get('start_time_app')), "%Y-%m-%d %H:%M")

            end_time_app = datetime.strptime(str(post.get('editAvail-client-date-fi')+" "+post.get('end_time_app')), "%Y-%m-%d %H:%M")

            check_availability_result = False
            for i in check_availability:

                start_time = datetime.strptime(str(post.get('editAvail-client-date-fi')+" "+i.start_time), "%Y-%m-%d %H:%M")

                end_time = datetime.strptime(str(post.get('editAvail-client-date-fi')+" "+i.end_time), "%Y-%m-%d %H:%M")

                if start_time_app>=start_time and start_time_app<=end_time and end_time_app>=start_time and end_time_app<=end_time:
                    
                    check_availability_result = True
          

            if post and check_availability_result:
                partner_id = request.env['res.partner'].sudo().search([('name','=',post['editAvail-client-name-fi'])])

                if post.get('services_offer'):
                    service_offer = request.env['calendar.appointment.type'].sudo().browse(int(post.get('services_offer')))
                else:
                    service_offer = False

                partner_id.email = post.get('editAvail-client-email-fi')
                partner_id.phone = ""
                partner_id.mobile = post.get('editAvail-client-phone-fi')
                if post.get("app_id") and post.get("app_line_id"):
                    get_app = request.env['appointment.appointment'].sudo().browse(int(post.get("app_id")))
                    get_app_line = request.env['appointment.line.id'].sudo().browse(int(post.get("app_line_id")))
                    get_app.sudo().update({
                        'partner_id':partner_id.id,
                        'booking_date':datetime.strptime(post['editAvail-client-date-fi'], "%Y-%m-%d"),
                        'notes':str(post.get('note_app')),
                        'name': 'Appointment for : {}'.format(partner_id.name),
                        })
                    
                    get_app_line.sudo().update({
                        'booking_start_date':datetime.strptime(post['editAvail-client-date-fi'], "%Y-%m-%d"),
                        'start_time_str': post.get('start_time_app'),
                        'end_time': float(post.get('end_time_app').replace(":",".")),
                        'therapist_id':int(post.get('fac_id')) if post.get('fac_id') else False,
                        'appointments_type_id': int(post.get('services_offer')) if post.get('services_offer') else False,
                        'duration':float(post.get('length_app').replace(":",".")) if post.get('length_app') else 0,
                        'appointment_id': get_app.id,
                        'apt_room_id': int(post.get('resource_app')) if post.get('resource_app') else False,
                        'service_categ_id': service_offer.service_categ_id.id if service_offer else False,
                        })
                
                    request.session['appointment_result'] = "Appointment updated successfully"
                    return request.redirect('/event/calendar')
                else:
                    # get_app = request.env['appointment.appointment'].sudo().browse(int(post.get("app_id")))

                    # get_app_line = request.env['appointment.line.id'].sudo().browse(int(post.get("app_line_id")))

                    app_id = request.env['appointment.appointment'].sudo().create({
                        'partner_id':partner_id.id,
                        'booking_date':datetime.strptime(post['editAvail-client-date-fi'], "%Y-%m-%d"),
                        'notes':str(post.get('note_app')),
                        'name': 'Appointment for : {}'.format(partner_id.name),
                        'email': post.get('editAvail-client-email-fi'),
                        'service_categ_id': service_offer.service_categ_id.id if service_offer else False,
                        'appointments_type_id': int(post.get('services_offer')) if post.get('services_offer') else False,
                        'therapist_id':int(post.get('fac_id')) if post.get('fac_id') else False,
                        'apt_room_id': int(post.get('resource_app')) if post.get('resource_app') else False,
                        'duration':float(post.get('length_app').replace(":",".")) if post.get('length_app') else 0,
                        'start_time_str': post.get('start_time_app'),
                        'end_time': float(post.get('end_time_app').replace(":",".")),
                        'session_type':'type_single',
                        })
                    wiz_id = request.env['single.session.wizard'].sudo().create({
                        "appointments_id": app_id.id,
                        'booking_date':datetime.strptime(post['editAvail-client-date-fi'], "%Y-%m-%d"),
                        'service_categ_id': service_offer.service_categ_id.id if service_offer else False,
                        'apt_room_id': int(post.get('resource_app')) if post.get('resource_app') else False,
                        'duration':float(post.get('length_app').replace(":",".")) if post.get('length_app') else 0,
                        'start_time_str': post.get('start_time_app'),
                        'end_time': float(post.get('end_time_app').replace(":",".")),
                        'end_time_str': post.get('end_time_app'),
                        'therapist_id':int(post.get('fac_id')) if post.get('fac_id') else False,
                        'appointments_type_id': int(post.get('services_offer')) if post.get('services_offer') else False,
                        })
                    wiz_id.add_appointment_wiz()
                    app_id.action_confirm()

                    # app_line_id = request.env['appointment.line.id'].sudo().create({
                    #     'booking_start_date':datetime.strptime(post['editAvail-client-date-fi'], "%Y-%m-%d"),
                    #     'start_time_str': post.get('start_time_app'),
                    #     # 'end_time_str': post.get('end_time_app'),
                    #     'end_time': float(post.get('end_time_app').replace(":",".")),
                    #     'therapist_id':int(post.get('fac_id')) if post.get('fac_id') else False,
                    #     'appointments_type_id': int(post.get('services_offer')) if post.get('services_offer') else False,
                    #     'duration':float(post.get('length_app').replace(":",".")) if post.get('length_app') else 0,
                    #     'appointment_id': app_id.id,
                    #     'apt_room_id': int(post.get('resource_app')) if post.get('resource_app') else False,
                    #     'service_categ_id': service_offer.service_categ_id.id if service_offer else False,
                    #     })
                    # print(post.get('end_time_app'),'kklklklkllllllllllllll')
                    
                
                    request.session['appointment_result'] = "Appointment Created successfully"
                    return request.redirect('/event/calendar')
            else:
                request.session['appointment_result'] = "There is no available slots."
                return request.redirect('/event/calendar')
    
    

    @http.route(['/clear/session'], type='http', auth="public", website=True, csrf=False)
    def clear_session(self, **post):
        request.session['appointment_result'] = ""

    @http.route(['/get/sale/order/details'], type='http', auth="public", website=True, csrf=False)
    def get_sale_order_details(self, **post):
        dict1 = {}
        if post and 'sale_id' in post:
            sale_id = request.env['sale.order.line'].search([('order_id','=',int(post['sale_id']))])
            for i in sale_id:
                dict1[i.id] = {
                    'product_name': i.product_id.name,
                    'product_id': i.product_id.id,
                    'product_price': i.price_total,
                    'product_currency': i.currency_id.name,
                    'description': i.name,
                    'partner_name': i.order_id.partner_id.name,
                    'partner_id': i.order_id.partner_id.id,
                    'date': i.order_id.date_order.strftime("%d %B %Y"),
                    'sales_person': i.order_id.user_id.name,
                    'address': i.order_id.partner_id.contact_address_complete,
                    'subtotal': i.order_id.amount_untaxed,
                    'taxes': i.order_id.amount_tax,
                    'total': i.order_id.amount_total,
                    'order_id': i.order_id.id,
                    'line_id': i.id,
                }
        return json.dumps(dict1)
    
    @http.route(['/products/list'], type='http', auth="public", website=True, csrf=False)
    def products_list_get_value_default(self, **post):
        dict1 = {}
        product_id = request.env['product.product'].search([("type","=","service")])
        for i in product_id:
            dict1[i.id] = {
                'product_name': i.name,
            }
        return json.dumps(dict1)

    @http.route(['/products/list/get'], type='http', auth="public", website=True, csrf=False)
    def products_list_get(self, **post):
        dict1 = {}
        if post and 'product' in post:
            product_id = request.env['product.product'].search([('name','=',post['product'])])
            for i in product_id:
                dict1[i.id] = {
                    'product_name': i.name,
                    'product_id': i.id,
                    'product_price': i.sale_price,
                }
        return json.dumps(dict1)

    @http.route(['/pos/cart/line'], type='http', auth="public", website=True, csrf=False)
    def pos_cart_line(self, **post):
        dict1 = {}
        if post and 'partner_id' in post:
            product_id = request.env['pos.cart.line'].search([('partner_id','=',int(post['partner_id']))])
            for i in product_id:
                dict1[i.id] = {
                    'product_name': i.product_id.name,
                    'product_id': i.product_id.id,
                    'pos_id': i.id,
                }
        return json.dumps(dict1)

    @http.route(['/pos/line/rmv'], type='http', auth="public", website=True, csrf=False)
    def pos_line_rmv(self, **post):
        if post and 'line_id' in post:
            line_id = request.env['pos.cart.line'].search([('id','=',int(post['line_id']))])
            line_id.unlink()

    @http.route(['/pos/line/add'], type='http', auth="public", website=True, csrf=False)
    def pos_line_add(self, **post):
        if post and 'product' in post:
            product_id = request.env['product.product'].search([('name','=',post['product'])],limit=1)
            request.env['pos.cart.line'].create({
                'product_id':product_id.id,
                'partner_id':int(post['partner'])
                })

    @http.route(['/pos/line/add_cart'], type='http', auth="public", website=True, csrf=False)
    def pos_line_add_cart(self, **post):
        dict1 = {}
        if post and 'partner_id' in post:
            line_id = request.env['pos.cart.line'].search([('partner_id','=',int(post['partner_id']))])
            for i in line_id:
                sale_line_id = request.env['sale.order.line'].create({
                    'product_id': i.product_id.id,
                    'order_id': int(post['order_id']),
                })
                dict1[i.id] = {
                    'product_name': i.product_id.name,
                    'product_id': i.product_id.id,
                    'product_price': i.product_id.product_tmpl_id.list_price,
                    'product_currency': i.product_id.product_tmpl_id.currency_id.name,
                    'sale_line_id': sale_line_id.id,
                }
                i.unlink()
        return json.dumps(dict1)

    @http.route(['/pos/line/add_cart'], type='http', auth="public", website=True, csrf=False)
    def pos_line_add_cart(self, **post):
        dict1 = {}
        if post and 'partner_id' in post:
            line_id = request.env['pos.cart.line'].search([('partner_id','=',int(post['partner_id']))])
        for i in line_id:
            sale_line_id = request.env['sale.order.line'].create({
                'product_id': i.product_id.id,
                'order_id': int(post['order_id']),
            })
            dict1[i.id] = {
                'product_name': i.product_id.name,
                'product_id': i.product_id.id,
                'product_price': i.product_id.product_tmpl_id.list_price,
                'product_currency': i.product_id.product_tmpl_id.currency_id.name,
                'sale_line_id': sale_line_id.id,
            }
            i.unlink()
        return json.dumps(dict1)

    @http.route(['/pos/process/checkout'], type='http', auth="public", website=True, csrf=False)
    def pos_process_checkout(self, **post):
        if post and 'order_id' in post:
            sale_id = request.env['sale.order'].search([('id','=',int(post['order_id']))])
            order = {}
            paid_status = 'unpaid'
            if sale_id.is_partially_paid == True:paid_status = 'partially_paid'
            elif sale_id.is_fully_paid == True:paid_status = 'paid'
            if sale_id.is_fully_paid == False:
                if sale_id.payment_link:
                    order['paid_status'] = paid_status
                    order['url'] = sale_id.payment_link
                else:
                    pay_id = request.env['payment.link.wizard'].sudo().create({
                        "res_id": sale_id.id,
                        "res_model": "sale.order",
                        "partner_id": sale_id.partner_id.id,
                        "description": sale_id.name,
                        "amount_max": sale_id.amount_total,
                        "amount": sale_id.amount_total,
                        "currency_id": sale_id.currency_id.id
                        })
                    order['url'] = pay_id.link
                    order['paid_status'] = paid_status
                    sale_id.payment_link = pay_id.link
                return json.dumps(order)
                
    @http.route(['/popover/action/confirm/<app_id>'], type='http', auth="public", website=True, csrf=False)
    def popover_action_confirm(self, app_id=None, **post):
        appointment_id = request.env['appointment.appointment'].search([('id','=',int(app_id))])
        appointment_id.state = 'confirm'
        return werkzeug.utils.redirect('/event/calendar')

    @http.route(['/popover/action/arrive/<app_id>'], type='http', auth="public", website=True, csrf=False)
    def popover_action_arrive(self, app_id=None, **post):
        appointment_id = request.env['appointment.appointment'].search([('id','=',int(app_id))])
        appointment_id.state = 'arrive'
        return werkzeug.utils.redirect('/event/calendar')

    @http.route(['/popover/action/cancel_early/<app_id>'], type='http', auth="public", website=True, csrf=False)
    def popover_action_cancel_early(self, app_id=None, **post):
        appointment_id = request.env['appointment.appointment'].search([('id','=',int(app_id))])
        # appointment_id.state = 'cancel'
        appointment_id.action_cancel()
        return werkzeug.utils.redirect('/event/calendar')

    @http.route(['/sale/order/line/rmv/<line_id>'], type='http', auth="public", website=True, csrf=False)
    def sale_order_line_rmv(self, line_id=None, **post):
        sale_line_id = request.env['sale.order.line'].browse(int(line_id))
        sale_line_id.unlink()

    @http.route(['/event/fasi/location'], type='http', auth="public", website=True, csrf=False)
    def event_fasi_location(self, **post):
        dict1 = {}
        location_id = request.env['res.company'].search([])
        for i in location_id:
            dict1[i.id] = str(i.name)
        return json.dumps(dict1)
    

    @http.route(['/availability/services/type'], type='http', auth="public", website=True, csrf=False)
    def availability_services_type(self, **post):
        dict1 = {}
        location_id = request.env['appointment.category'].search([])
        for i in location_id:
            dict1[i.id] = str(i.name)
        return json.dumps(dict1)

    @http.route(['/rebook/app/calendar'], type='http', auth="public", website=True, csrf=False)
    def rebook_app_calendar(self, **post):
        partner_id = request.env['res.partner'].sudo().search([('name','=',post['partner'])],limit=1)
        app_id = request.env['appointment.appointment'].sudo().search([('partner_id','=',partner_id.id)])

    @http.route(['/app/payment/status'], type='http', auth="public", website=True, csrf=False)
    def app_payment_status(self, **post):
        app_id = request.env['availability.availability'].sudo().search([('id','=',int(post['ap_id']))])
        if app_id.invoice_status == 'invoiced':
            return 'paid'
        else:
            return 'unpaid'

    @http.route(['/event/calendar/promo'], type='http', auth="public", website=True, csrf=False)
    def event_calendar_promo(self, **post):
        if post and 'promo' in post and 'order' in post:
            promo = post['promo']
            order = request.env['sale.order'].browse(int(post['order']))
            pricelist = request.env['product.pricelist'].sudo().search([('code', '=', promo)], limit=1)
            coupon_status = request.env['sale.coupon.apply.code'].sudo().apply_coupon(order, promo)
            if coupon_status.get('not_found'):
                return 'nopromo'
            elif coupon_status.get('error'):
                return 'nopromo'
            return 'applied'

        # request.website.sale_get_order(code=promo)

    @http.route(['/pos/session/list/wiz'], type='http', auth="public", website=True, csrf=False)
    def pos_session_list_wiz(self, **post):
        dict1 = {}
        session_id = request.env['pos.config'].search([('current_session_state','in',['opened','new_session'])])
        for i in session_id:
            dict1[i.id] = str(i.name)
        return json.dumps(dict1)

    @http.route(['/pos/session/list/redirect/<sess_id>/<app_id>/<apt_id>'], type='http', auth="public", website=True, csrf=False)
    def pos_session_list_redirect(self, app_id=None, sess_id=None, apt_id=None, **post):
        if sess_id:
            request.session['apt_redirect_id'] = apt_id
            session_id = request.env['pos.config'].browse(int(sess_id))
            session_id.write({'default_partner_id':int(app_id),'new_order_disable':True})
            return werkzeug.utils.redirect("/pos/ui?config_id="+ str(session_id.id) +"#cids=1")

    @http.route(['/pos/session/to/redirect/home'], type='http', auth="public", website=True, csrf=False)
    def pos_session_to_redirect_home(self, **post):
        if 'apt_redirect_id' in request.session:
            return request.redirect('/web#id='+request.session['apt_redirect_id']+'&action=673&model=appointment.appointment&view_type=form&cids=&menu_id=479')