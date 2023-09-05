from odoo import http, tools, _
from odoo.http import request, Response
from datetime import datetime, timedelta
import json, werkzeug
import requests
import urllib.request
import urllib
from bs4 import BeautifulSoup
from datetime import datetime

class RoomCalendar(http.Controller):
    @http.route(['/room/dashbord'], type='http', auth="public", website=True, csrf=False)
    def room_calendar_dashbord(self, **post):
        values = {}
        return request.render('ppts_mindbody_calendar.room_dashbord_mindbody',values)

    @http.route(['/room/dashbord/booking'], type='http', auth="public", website=True, csrf=False)
    def room_calendar_dashbord_booking(self, **post):
        values = {}
        print(post,'pppppppppp')
        return request.render('ppts_mindbody_calendar.room_booking_form',values)

    @http.route(['/room/calendar/resources',
        '/room/calendar/<event_details>'], type='http', auth="public",  methods=['GET'], website=True)
    def room_calendar_resources(self, event_details=None, **post):
        resources = [];events = [];domain = []
        room_id = request.env['roomtype.master'].search([('room_maincateg_id.roomcateg_code','=','APT')])
        for i in room_id:
            resources.append({ 
                'id': i.id,
                'title': i.room_type, 
                })

        if event_details == 'events':
            print(post)
            date_st = post['start'].split('T')
            availability_ids = request.env['availability.availability'].sudo().search([])
            print(availability_ids,'availability_idsavailability_idsavailability_ids')
            for i in availability_ids:
                if i.room_id and i.available_date and i.start_time and i.end_time:
                    date_start = datetime.strptime(i.available_date.strftime("%Y-%m-%d")+' '+i.start_time, "%Y-%m-%d %H:%M")
                    date_end = datetime.strptime(i.available_date.strftime("%Y-%m-%d")+' '+i.end_time, "%Y-%m-%d %H:%M")
                    date_start = date_start - timedelta(hours=5, minutes=30)
                    date_end = date_end - timedelta(hours=5, minutes=30)
                    date_start = str(date_start.strftime("%Y-%m-%d %H:%M")).split(" ")
                    date_end = str(date_end.strftime("%Y-%m-%d %H:%M")).split(" ")
                    services_fas = []
                    for s in i.facilitator.service_category_ids:
                        services_fas.append(s.id)
                    
                    if i.availabile_type == 'event':
                        events.append({
                                'id': i.room_id.id,
                                'resourceId': i.room_id.id,
                                'title': i.event_id.name or i.appointment_id.name,
                                'start': date_start[0]+'T'+date_start[1]+':00Z',
                                'end': date_end[0]+'T'+date_end[1]+':00Z',
                                'className': 'room-bmk-event',
                                'display': 'background',
                                'location_id': i.location.id,
                                'services':services_fas,
                                'av_type': 'event',
                            })
                    elif i.availabile_type == 'appoinment':
                        events.append({
                            'id': i.room_id.id,
                            'resourceId': i.room_id.id,
                            'title': i.event_id.name or i.appointment_id.name,
                            'start': date_start[0]+'T'+date_start[1]+':00Z',
                            'end': date_end[0]+'T'+date_end[1]+':00Z',
                            'className': 'room-bmk-appointment',
                            'display': 'background',
                            'location_id': i.location.id,
                            'services':services_fas,
                            'av_type': 'appointment',
                        })

            return json.dumps(events)
        else:return json.dumps(resources)

    @http.route(['/room/booking/appointment/create'], type='http', auth="public", website=True, csrf=False)
    def room_booking_appointment_create(self, **post):
        print(post,'pppppppppsdgfsdgp')

        # {'CSRFToken': 'SQlchIBKZ7', 'frmOnStep': '', 
        # 'frmreqReferredByBiz': 'False', 'frmreqGenderBiz': 'False', 
        # 'optClientName': '1', 'optLocation': '1', 
        # 'optServicesCategory': '1', 'optVisitType': '0', 
        # 'frmLastVTID': '0', 'optRoom': '3', 'optSupervisor': '1', 
        # 'room_appDate': '2021-02-24', 'optStartTime': '11:00', 
        # 'optEndTime': '14:30', 'txtNotes': 'ASDAFDASFDASF', 
        # 'frmPmtRefNo': '0', 'frmRtnAction': 'main_resrc.asp', 
        # 'frmRtnScreen': 'rsrc_sch'}

        partner_name = request.env["res.partner"].browse(int(post['optClientName']))
        app_id = request.env["appointment.appointment"].create({
            "name": "Appointment for "+ partner_name.name, 
            "partner_id": int(post['optClientName']),
            "booking_date": datetime.strptime(post['room_appDate'], "%Y-%m-%d"),
            })
        app_line_id = request.env["appointment.line.id"].create({
            "service_categ_id": int(post['optServicesCategory']),
            "therapist_id": int(post['optSupervisor']),
            "apt_room_id": int(post['optRoom']),
            "start_time_str": post['optStartTime'],
            "end_time_str": post['optEndTime'],
            "appointment_id": app_id.id,
            "appointments_type_id": int(post['optVisitType']),
            })
        print(app_id,'app_idapp_idapp_idapp_idapp_idapp_idapp_id')

        return request.render('ppts_mindbody_calendar.room_booking_form_success')

    @http.route(['/event/calendar/partners_list'], type='http', auth="public", website=True, csrf=False)
    def event_website_calendar_partners_list(self, **post):
        exception_id = {}
        company_ids = request.env['res.partner'].sudo().search([])
        for i in company_ids:
            exception_id[i.id] = i.name
        return json.dumps(exception_id)

    @http.route(['/event/calendar/employee_list'], type='http', auth="public", website=True, csrf=False)
    def event_website_calendar_employee_list(self, **post):
        exception_id = {}
        company_ids = request.env['hr.employee'].sudo().search([])
        for i in company_ids:
            exception_id[i.id] = i.name
        return json.dumps(exception_id)

    @http.route(['/event/calendar/app_type_list'], type='http', auth="public", website=True, csrf=False)
    def event_website_calendar_app_type_list(self, **post):
        exception_id = {}
        company_ids = request.env['calendar.appointment.type'].sudo().search([])
        for i in company_ids:
            exception_id[i.id] = i.name
        return json.dumps(exception_id)

    @http.route(['/event/calendar/app_location'], type='http', auth="public", website=True, csrf=False)
    def event_website_calendar_app_location(self, **post):
        exception_id = {}
        company_ids = request.env['res.partner'].sudo().search([('company_id','=',False),('company_id','=',)])
        for i in company_ids:
            exception_id[i.id] = i.name
        return json.dumps(exception_id)

