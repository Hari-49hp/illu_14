from odoo import http, tools, _
from odoo.http import request, Response
from datetime import datetime, timedelta
import json, werkzeug, pytz, urllib.request
import webbrowser, itertools
import logging
_logger = logging.getLogger(__name__)

class BookingActivities(http.Controller):
    @http.route(['/event/calendar','/appointment/calendar','/booking'], type='http', auth="user", website=True, csrf=False)
    def event_website_calendar(self, **post):
        values = request.params.copy()
        return request.render('ppts_mindbody_calendar.booking_activities_calendar_template',values)

    @http.route(['/booking_activities/resources'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_resources(self, **post):
        facilitator = [];facilitator_check = []
        if post:
            date = post['date'].split(' ')
            date = datetime.strptime(date[2]+'-'+date[1]+'-'+date[3], "%d-%b-%Y")
            date = date.strftime("%Y-%m-%d")
            available_id = request.env['availability.availability'].sudo().search([('available_date','=',date),('location_id','in',request.env.user.company_ids.ids)])
            for i in available_id:
                if i.facilitator.id not in facilitator_check:
                    facilitator_check.append(i.facilitator.id)
                    facilitator.append({'id':i.facilitator.id, 'title':i.facilitator.name})
            mult_date_ids = request.env['multi.date.line'].sudo().search([('date_begin','>=',date),('date_end','<=',date)])
            if mult_date_ids:
                event_ids = mult_date_ids.mapped('event_id').filtered(lambda rec:rec.stage_id.name == "Published" and rec.address_id.id in request.env.user.company_ids.ids)
                for facilitator_id in event_ids.facilitator_evnt_ids:
                    if facilitator_id.id not in facilitator_check:
                        facilitator_check.append(facilitator_id.id)
                        facilitator.append({'id':facilitator_id.id, 'title':facilitator_id.name})
        return json.dumps(facilitator)

    @http.route(['/booking_activities/availability'], type='http', auth="user", website=True, csrf=False, cors='*')
    def booking_activities_availability(self, **post):
        availability = [];
        availabilityl = [];
        selected_companies = request.env.company.id

        available_id = request.env['availability.availability'].sudo().search([('date_range','=','ongoing'),('location_id','in',request.env.user.company_ids.ids), ('state','in', ['unavailability_created','availability_created'])]) #,('location_id','in',selected_companies.ids)
        for i in available_id:
            date_start = datetime.strptime(i.available_date.strftime("%Y-%m-%d")+' '+i.start_time, "%Y-%m-%d %H:%M")
            date_end = datetime.strptime(i.available_date.strftime("%Y-%m-%d")+' '+i.end_time, "%Y-%m-%d %H:%M")

            date_start = date_start - timedelta(hours=4, minutes=00)
            date_end = date_end - timedelta(hours=4, minutes=00)
            
            date_start = str(date_start.strftime("%Y-%m-%d %H:%M")).split(" ")
            date_end = str(date_end.strftime("%Y-%m-%d %H:%M")).split(" ")
            
            if i.availability == 'available':
                availability.append({
                    'resourceId': i.facilitator.id, 
                    'extendedPropsRId': i.facilitator.id, 
                    'title': i.facilitator.name,
                    'start': date_start[0]+'T'+date_start[1]+':00Z',
                    'end': date_end[0]+'T'+date_end[1]+':00Z',
                    'color': 'blue',
                    'rendering': 'background',
                    'dow': [6],
                    'state': 'availability',
                    "event_type": 'available',
                    'res_id': str(i.facilitator.id),
                })
            else:
                availability.append({
                    'resourceId': i.facilitator.id, 
                    'extendedPropsRId': i.facilitator.id, 
                    'title': i.reason,
                    'start': date_start[0]+'T'+date_start[1]+':00Z',
                    'end': date_end[0]+'T'+date_end[1]+':00Z',
                    'state': 'unavailability',
                    'res_id': str(i.facilitator.id),
                    "POP_OVER": '<ul></ul>',
                    "event_type": 'unavailable',
                    "className": 'Unavailability-Resource',
                    'url': '/web#id=%s&action=%s&model=availability.availability&view_type=form&menu_id=%s' % (str(i.id), str(request.env.ref('ppts_employee_availability.availability_action_view').id), str(request.env.ref('ppts_employee_availability.menu_ppts_availability').id)),
                })

        appointments_id = request.env['appointment.appointment'].sudo().search([('session_type','=','type_single'),('company_id','in',request.env.user.company_ids.ids)])
        event_id = request.env['event.event'].sudo().search([('id','=',11)])

        for i in appointments_id:
            cart = ''
            if i.time_slot_id and i.booking_date:

                date_start = datetime.strptime(i.booking_date.strftime("%Y-%m-%d")+' '+i.time_slot_id.start_time, "%Y-%m-%d %H:%M")
                date_end = datetime.strptime(i.booking_date.strftime("%Y-%m-%d")+' '+i.time_slot_id.end_time, "%Y-%m-%d %H:%M")
                
                date_start = date_start - timedelta(hours=4, minutes=00)
                date_end = date_end - timedelta(hours=4, minutes=00)
                
                date_start = str(date_start.strftime("%Y-%m-%d %H:%M")).split(" ")
                date_end = str(date_end.strftime("%Y-%m-%d %H:%M")).split(" ")
                APT_STATUS = '';POP_OVER = '';
                
                url = "/web?debug=0#id=%s&model=appointment.appointment&view_type=form&cids=&menu_id=%s" \
                            % (str(i.id), str(request.env.ref('ppts_custom_apt_mgmt.menu_ppts_Appointments').id))
                if i.pos_order_id:
                    cart =  """ <li>
                                    <a href=%s class="checkout" title="">
                                    <span id="popover-edit-today-schedule"> <i class="fas fa-shopping-cart"></i> View Cart </span>
                                    </a>
                                </li> """ % ("/web?debug=0#id="+ str(i.pos_order_id.id or i.pac_pos_order_id.id) +"&model=pos.order&view_type=form&cids=&menu_id="+str(request.env.ref('point_of_sale.menu_point_root').id))
                else:
                    cart =  """ <li>
                                    <a href=%s class="checkout" title="">
                                    <span id="popover-edit-today-schedule"> <i class="fas fa-store-alt"></i> Checkout </span>
                                    </a>
                                </li> """ % ("/booking/appointment/move_to_pos/"+str(i.id))

                if i.state == 'new': 
                    APT_STATUS = 'event-status-new'
                    POP_OVER = """  <ul id="context-menu" class="popoverlist context-menu context-right ctx-right POP-event-status-new while-event-available">
                                    <li><a class="popover-container-close-btn"><i class="fas fa-times"></i></a></li>
                                    %s
                                    <li>
                                        <a href=%s class="checkout">
                                        <span class="popover-add-availability"> <i class="fas fa-clipboard-check"></i> Mark Confirm</span>
                                        </a>
                                    </li>
                                    <li>
                                        <a href=%s class="checkout">
                                        <span class="popover-add-availability"><i class="fas fa-edit"></i> Modify</span>
                                        </a>
                                    </li>
                                </ul> """ % (cart,"/booking/appointment/confirm/"+str(i.id),url)
                elif i.state == 'confirm':
                    APT_STATUS = 'event-status-confirm'

                    # noshow_progress = ""
                    # if i.is_no_show_done == False:
                    #     noshow_progress = """ 
                    #                 <li>
                    #                     <a id="popover-apt-confirm-no_show-model" href="javascript:void(0)"  class="checkout">
                    #                     <span class="popover-add-availability"><i class="fas fa-door-closed"></i> Confim- No Show </span>
                    #                     </a>
                    #                 </li> """
                    #  <li>
                    #                     <a id="popover-apt-no-show-model" href=%s class="checkout">
                    #                     <span class="popover-add-availability" style="cursor: default;"> <i class="fas fa-door-closed"></i> No Show </span>
                    #                     </a>
                    #                 </li>
                    POP_OVER = """  <ul id="context-menu" class="popoverlist context-menu context-right ctx-right POP-event-status-confirm while-event-available">
                                    <li><a class="popover-container-close-btn"><i class="fas fa-times"></i></a></li>
                                    %s
                                    <li>
                                        <a href=%s class="checkout">
                                        <span class="popover-add-availability"> <i class="fas fa-plane-arrival"></i> Mark Arrived </span>
                                        </a>
                                    </li>
                                    <li>
                                        <a href=%s class="checkout">
                                        <span class="popover-add-availability"> <i class="fas fa-clipboard-list"></i> Reschedule </span>
                                        </a>
                                    </li>
                                    <li>
                                        <a id="popover-apt-cancel-model" href="javascript:void(0)" class="checkout">
                                        <span class="popover-add-availability" style="cursor: default;"> <i class="fas fa-ban"></i> Cancel </span>
                                        </a>
                                    </li>
                                   
                                    <li>
                                        <a id="popover-apt-confirm-no_show-model" href="javascript:void(0)"  class="checkout">
                                        <span class="popover-add-availability"><i class="fas fa-door-closed"></i> Confim- No Show </span>
                                        </a>
                                    </li>
                                    <li>
                                        <a href=%s class="checkout">
                                        <span class="popover-add-availability"><i class="fas fa-edit"></i> View Appointment </span>
                                        </a>
                                    </li>
                                </ul> """ % (cart ,"/booking/appointment/arrive/"+str(i.id),"/booking/appointment/reschedule/"+str(i.id), url)
                elif i.state == 'arrive': 
                    APT_STATUS = 'event-status-arrive'
                    POP_OVER = """  <ul id="context-menu" class="popoverlist context-menu context-right ctx-right POP-event-status-arrive while-event-available">
                                    <li><a class="popover-container-close-btn"><i class="fas fa-times"></i></a></li>
                                    %s
                                    <li>
                                        <a href=%s class="checkout">
                                        <span class="popover-add-availability"> <i class="far fa-check-circle"></i> Mark Completed </span>
                                        </a>
                                    </li>
                                   
                                    <li>
                                        <a href=%s class="checkout">
                                        <span class="popover-add-availability"><i class="fas fa-edit"></i> View Appointment </span>
                                        </a>
                                    </li>
                                </ul> """ % (cart, "/booking/appointment/done/"+str(i.id), url)
                elif i.state == 'done':
                    APT_STATUS = 'event-status-done'
                    POP_OVER = """  <ul id="context-menu" class="popoverlist context-menu context-right ctx-right POP-event-status-done while-event-available">
                                    <li><a class="popover-container-close-btn"><i class="fas fa-times"></i></a></li>
                                    %s
                                    <li>
                                        <a href=%s class="checkout">
                                        <span class="popover-add-availability"><i class="fas fa-edit"></i> View Appointment </span>
                                        </a>
                                    </li>
                                </ul> """ % (cart, url)

                elif i.state == 'no_show':
                    APT_STATUS = 'event-status-no-show'

                    POP_OVER = """  <ul id="context-menu" class="popoverlist context-menu context-right ctx-right POP-event-status-done while-event-available">
                                    <li><a class="popover-container-close-btn"><i class="fas fa-times"></i></a></li>
                                    %s
                                    <li>
                                        <a href=%s class="checkout">
                                        <span class="popover-add-availability"><i class="fas fa-edit"></i> View Appointment</span>
                                        </a>
                                    </li>
                                </ul> """ % (cart, url)

                elif i.state == 'cancel': 
                    APT_STATUS = 'event-status-cancel'
                    POP_OVER = """  <ul id="context-menu" class="popoverlist context-menu context-right ctx-right POP-event-status-cancel while-event-available">
                                    <li><a class="popover-container-close-btn"><i class="fas fa-times"></i></a></li>
                                    %s
                                    <li>
                                        <a href=%s class="checkout">
                                        <span class="popover-add-availability"><i class="fas fa-edit"></i> View Appointment </span>
                                        </a>
                                    </li>
                                </ul> """ % (cart, url)

                availability.append({
                    'resourceId': i.therapist_id.id, 
                    'extendedPropsRId': i.therapist_id.id, 
                    'therapist_id': i.therapist_id.id, 
                    'title': i.name,
                    "event_type": 'appointment',
                    'start': date_start[0]+'T'+date_start[1]+':00Z',
                    'end': date_end[0]+'T'+date_end[1]+':00Z',
                    'tooltip_duration': i.time_slot_id.start_time+'-'+i.time_slot_id.end_time,
                    'time_id': i.time_id.id,
                    'time_slot_id': i.time_slot_id.id,
                    "className": APT_STATUS,
                    "tool_tip_className": APT_STATUS,
                    "sub_category_name": i.appointments_type_id.name, 
                    "sub_category_id": str(i.appointments_type_id.id), 
                    "service_category_id": i.service_categ_id.id, 
                    "service_category_name": i.service_categ_id.name, 
                    "appointment_type": i.appointment_type, 
                    "company_id": str(i.company_id.id),
                    "appointment_date": date_start[0],
                    "partner_name": i.partner_id.name,
                    "appointment_id": i.id,
                    "partner_id": i.partner_id.id,
                    "partner_phone": i.partner_id.mobile or '',
                    "partner_email": i.partner_id.email or '',
                    "partner_seaquence": i.partner_id.sequence or '',
                    "room_name": i.apt_room_id.room_type,
                    "room_id": i.apt_room_id.id,
                    "cc_cancellation_charge": i.cc_cancellation_charge,
                    "state": i.state,
                    "note": i.notes or '',
                    "cancel_notes": i.cancel_notes or '',
                    "POP_OVER": POP_OVER,
                    "payment_status": i.payment_status_apt ,
                    "isfavourite" : i.isfavourite,
                    'booking_mode':i.booking_mode
                })

            # availability.append({
            #     'resourceId': 259, 
            #     'extendedPropsRId': 259, 
            #     'title': 'Test Event', 
            #     'start': '2021-10-29T10:00:00Z', 
            #     'end': '2021-10-29T15:00:00Z', 
            #     'className': 'event-status-done'
            #     })

        event_id = request.env['event.event'].sudo().search([('address_id','in',request.env.user.company_ids.ids)])
        for e in event_id.filtered(lambda l: l.stage_id.name==("Published")):
            for facilitator in e.facilitator_evnt_ids:
                for multi in e.multi_date_line_ids:
                    date_start = datetime.strptime(multi.date_begin.strftime("%Y-%m-%d")+' '+ multi.hour_time_begin+':'+ multi.min_time_begin, "%Y-%m-%d %H:%M")
                    date_end = datetime.strptime(multi.date_begin.strftime("%Y-%m-%d")+' '+ multi.hour_time_end+':'+ multi.min_time_end, "%Y-%m-%d %H:%M")
                    
                    date_start = date_start - timedelta(hours=4, minutes=00)
                    date_end = date_end - timedelta(hours=4, minutes=00)
                    
                    date_start = str(date_start.strftime("%Y-%m-%d %H:%M")).split(" ")
                    date_end = str(date_end.strftime("%Y-%m-%d %H:%M")).split(" ")


                    availability.append({
                        'resourceId': facilitator.id, 
                        'extendedPropsRId': facilitator.id,
                        'title': e.name,
                        'start': date_start[0]+'T'+date_start[1]+':00Z',
                        'end': date_end[0]+'T'+date_end[1]+':00Z',
                        'tooltip_duration': '09:00-10:00', 
                        'className': 'booking-calendar-event-el-box', 
                        'tool_tip_className': 'booking-calendar-event-el-tooltip', 
                        'sub_category_name': '', 
                        'service_category_name': '', 
                        'company_id': e.address_id.id, 
                        'partner_name': e.name,
                        'partner_phone': '',
                        'partner_seaquence': ' ',
                        "event_type": 'event',
                        'room_name': 'Green Room',
                        'note': '',
                        'POP_OVER': '  ',
                        # 'event_url': "/event/attendee/redirect/%s" % (str(e.id))
                        'event_url': "/web#action=" + str(request.env.ref('event.act_event_registration_from_event').id) + "&active_id=%s&model=event.registration&view_type=list&cids=1&menu_id=%s" % (str(e.id), str( request.env.ref('event.event_main_menu').id ))
                    })
                        
        return json.dumps(availability)

    @http.route(['/booking_activities/appointment/create'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_appointment_create(self, **post):
        if post['client_id'] and post['booking_date'] and post['therapist_id_hidden'] and post['service_categ_id'] and \
            post['sub_categ_id'] and post['appointment_platform'] and post['time_id'] and post['time_slot_id'] and post['room_id']:
            client_id = request.env['res.partner'].sudo().browse(int(post['client_id']))
            client_id.write({
                'mobile':post['client_mobile'],
                'email':post['client_email'],
            })
            time_slot_id = request.env['time.slot'].browse(int(post['time_slot_id']))
            request.env['appointment.appointment'].sudo().create({
                'name': 'Appointment for '+ post['client_name'],
                'partner_id': int(post['client_id']),
                'booking_date': post['booking_date'],
                'therapist_id': int(post['therapist_id_hidden']),
                'du_service_categ_id': int(post['service_categ_id']),
                'service_categ_id': int(post['service_categ_id']),
                'appointments_type_id': int(post['sub_categ_id']),
                'appointment_type': post['appointment_platform'],
                'time_id': int(post['time_id']),
                'time_slot_id': int(post['time_slot_id']),
                'start_time_str': time_slot_id.start_time,
                'end_time_str': time_slot_id.end_time,
                'apt_room_id': int(post['room_id']),
                'notes': post['apt_notes'] or '',
                'company_id': request.env.company.id or request.env.user.company_id.id
            })
        return werkzeug.utils.redirect("/booking")

    @http.route(['/event/attendee/redirect/<int:event_id>'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_event_attendee_redirect(self, event_id=None, **post):
        return request.redirect("/web#action=" + str(request.env.ref('event.act_event_registration_from_event').id) + "&active_id=%s&model=event.registration&view_type=list&cids=1&menu_id=%s" % (str(event_id), str( request.env.ref('event.event_main_menu').id )))
        # return werkzeug.utils.redirect("/web#active_id=%s&model=event.registration&view_type=list&cids=1&menu_id=%s" % (str(event_id), str( request.env.ref('event.event_main_menu').id )))

    @http.route(['/booking_activities/appointment/edit'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_appointment_edit(self, **post):
        if post['client_id'] and post['booking_date'] and post['therapist_id_hidden'] and post['service_categ_id'] and \
            post['sub_categ_id'] and post['appointment_platform'] and post['time_id'] and post['time_slot_id'] and post['room_id']:

            client_id = request.env['res.partner'].sudo().browse(int(post['client_id']))
            client_id.write({
                'mobile':post['client_mobile'],
                'email':post['client_email'],
            })
            time_slot_id = request.env['time.slot'].browse(int(post['time_slot_id']))
            appointment_id = request.env['appointment.appointment'].sudo().browse(int(post['appointment_id_hidden']))
            appointment_id.sudo().write({
                'name': 'Appointment for '+ post['client_name'],
                'partner_id': int(post['client_id']),
                'booking_date': post['booking_date'],
                'therapist_id': int(post['therapist_id_hidden']),
                'du_service_categ_id': int(post['service_categ_id']),
                'service_categ_id': int(post['service_categ_id']),
                'appointments_type_id': int(post['sub_categ_id']),
                'appointment_type': post['appointment_platform'],
                'time_id': int(post['time_id']),
                'time_slot_id': int(post['time_slot_id']),
                'start_time_str': time_slot_id.start_time,
                'end_time_str': time_slot_id.end_time,
                'apt_room_id': int(post['room_id']),
                'notes': post['apt_notes'] or '',
                'company_id': request.env.company.id or request.env.user.company_id.id,
                'isfavourite': True if post.get("is_favourite_check") == "yes" else False,
            })
        return werkzeug.utils.redirect("/booking")

    @http.route(['/booking_activities/appointment/cancel'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_appointment_cancellation(self, **post):
        appointment_id = request.env['appointment.appointment'].sudo().browse(int(post['cc_cancellation_appointment_id']))
        wiz_id = request.env['apt.two.step.cancel'].sudo().create({
                                'appointments_id': appointment_id.id,
                                'cancellation_type': post.get('cancellation_type'),
                                'cancel_reason_template': int(post.get('cancel_reason_template')),
                                'cancel_options': post.get('cancel_options'),
                                'note': post.get('note'),
                            })

        if post.get('submit-type') == 'cancel-and-create-appointment':
            wiz_id.cancel_and_create()
        elif post.get('submit-type') == 'cancel-appointment':
            wiz_id.cancel_apt()

        return werkzeug.utils.redirect("/booking")
        
    @http.route(['/booking_activities/appointment/noshow'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_appointment_noshow(self, **post):
        appointment_id = request.env['appointment.appointment'].sudo().browse(int(post['cc_noshow_appointment_id']))
        wiz_id = request.env['apt.two.step.cancel'].sudo().create({
                                'appointments_id': appointment_id.id,
                                'noshow_options': post.get('noshow_options'),
                                'no_show_charges': int(post.get('no_show_charges')),
                                'note': post.get('note'),
                            })
        wiz_id.process_no_show()
        return werkzeug.utils.redirect("/booking")

    @http.route(['/get/rebook/appointment/client'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_get_rebook_appointment_client(self, **post):
        appointment_id = request.env['appointment.appointment'].sudo().search([\
            ('booking_date','<=', datetime.now().date().strftime("%m/%d/%Y") ), ('partner_id','=',int(post.get('partner_id')))])
        dates = [];content = {}
        for j in appointment_id: dates.append(j.booking_date)
        dates = list(set(dates))
        for i in dates:
            lst = []
            dates_appointment_id = request.env['appointment.appointment'].sudo().search([\
            ('booking_date','=', i ), ('partner_id','=',int(post.get('partner_id')))])
            date = i.strftime("%a, %d %B %Y")
            for t in dates_appointment_id:
                pos_price = t.pos_order_id.amount_total if t.pos_order_id else ' '
                lst.append( 
                    t.appointments_type_id.name+'%'+t.therapist_id.name+'%'+str(pos_price)+'%'+str(t.service_categ_id.id)+'%'+str(t.appointments_type_id.id)+'%'+t.appointment_type
                    )
            content[date] = lst
        return json.dumps(content)

    @http.route(['/booking_activities/get/cancellation/details'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_get_cancellation_details(self, **post):
        appointment_id = request.env['appointment.appointment'].sudo().browse(int(post['cc_cancellation_appointment_id']))
        appointment_id.action_cancel()
        lst = [{
            'cancellation_type': appointment_id.pre_cancellation_type,
            'cc_cancellation_charge': appointment_id.cc_cancellation_charge,
        }]
        return json.dumps(lst)
        
    @http.route(['/booking_activities/get/noshow/details'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_get_noshow_details(self, **post):
        APPOINTMENT = request.env['appointment.appointment'].sudo()
        appointment_id = APPOINTMENT.browse(int(post['appointment_id']))
        cc_partner_ids = APPOINTMENT.search([('partner_id', '=', appointment_id.partner_id.id), \
                                                        ('no_show_charges', '>', 0)])
        cc_due = 0.0;note = 'Info : ';apt_state = 'Info : '
        for due_ns in cc_partner_ids:
            cc_due += due_ns.no_show_charges
            note += ("Booking Date : " + str(due_ns.creation_date) + " Appointment Date : " + str(
                due_ns.booking_date) + " Session : " + due_ns.session_type)
            apt_state = due_ns.payment_status_apt

        lst = [{
            'appointments_id': appointment_id.id,
            'is_no_show': True,
            'no_show_charges': cc_due,
            'note': note,
            'is_paid': apt_state,
        }]

        return json.dumps(lst)

    @http.route(['/booking/appointment/noshow/<int:apt_id>'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_make_apt_no_show(self, apt_id=None,**post):
        appointment_id = request.env['appointment.appointment'].sudo().browse(apt_id)
        appointment_id.action_no_show()
        # return werkzeug.utils.redirect("/booking")

    @http.route(['/booking/appointment/move_to_pos/<int:apt_id>'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_appointment_move_to_pos(self, apt_id=None,**post):
        appointment_id = request.env['appointment.appointment'].sudo().browse(apt_id)
        Confirmation = request.env['apt.order.confirmation'].sudo()
        wiz_id = request.env['apt.payment.confirmation'].sudo().create({'appointments_id':apt_id})
        wiz_id.pay_now()
        retail_id = Confirmation.search([('appointments_id','=',apt_id)],limit=1)
        return werkzeug.utils.redirect(\
            "/web?debug=0#id=%s&model=apt.order.confirmation&view_type=form&cids=&menu_id=" % (str(retail_id.id)))

    @http.route(['/booking_activities/unavailability/create'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_unavailability_create(self, **post):
        if post['av_therapist_id'] and post['av_available_date'] and post['av_start_date'] and post['av_end_date']\
            and post['av_start_time'] and post['av_end_time'] and post['reason']:
            request.env['availability.availability'].sudo().create({
                'facilitator': int(post['av_therapist_id']),
                'availability': 'unavailable',
                'reason': post['reason'],
                'available_date': post['av_available_date'],
                'cus_start_date': post['av_start_date'],
                'cus_end_date': post['av_end_date'],
                'start_time': post['av_start_time'],
                'end_time': post['av_end_time'],
                'date_range': 'ongoing',
            })
        return werkzeug.utils.redirect("/booking")
        
    @http.route(['/booking_activities/availability/create'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_availability_create(self, **post):
        if post['av_therapist_id'] and post['av_available_date']\
            and post['av_start_time'] and post['av_end_time']:
            request.env['availability.availability'].sudo().create({
                'facilitator': int(post['av_therapist_id']),
                'availability': 'available',
                'available_date': post['av_available_date'],
                'cus_start_date': post['av_available_date'],
                'cus_end_date': post['av_available_date'],
                'start_time': post['av_start_time'],
                'end_time': post['av_end_time'],
                'date_range': 'ongoing',
            })
        return werkzeug.utils.redirect("/booking")
        

    @http.route(['/booking_activities/filter/company'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_filter_company(self, **post):
        Dropdown = ''
        company_id = request.env['res.company'].sudo().search([])
        for i in company_id:
            Dropdown += '<option value="'+ str(i.id) +'" data-oe-model="'+ str(i.id) +'">'+ i.name +'</option>'
        return Dropdown

    @http.route(['/booking_activities/filter/services'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_filter_services(self, **post):
        print("JJJJJJJJJJJJJJJJJJ",post)
        if post.get('location_custom_non_all') and post.get('location_custom_non_all') != 'all':
            website_id_booking = request.env['res.company'].sudo().search(
                [('id', '=', int(post.get('location_custom_non_all')))])
            print("website_id_bookinggg", website_id_booking.ids)
            Dropdown = ''
            service_id = request.env['appointment.category'].sudo().search([])
            for i in service_id:
                Dropdown += '<optgroup data-service-id="' + str(i.id) + '" label="' + i.name + '" data-max-options="2">'
                sub_category_id = request.env['calendar.appointment.type'].sudo().search(
                    [('service_categ_id', '=', i.id),('company_id','in',website_id_booking.ids)])
                for j in sub_category_id:
                    Dropdown += '<option value="' + str(j.id) + '" data-oe-model="' + str(
                        j.id) + '">' + j.name + '</option>'
                print("iiiiiiiiiiiiii",sub_category_id)
                Dropdown += '</optgroup>'
        else:
            Dropdown = ''
            service_id = request.env['appointment.category'].sudo().search([])
            for i in service_id:
                Dropdown += '<optgroup data-service-id="' + str(i.id) + '" label="' + i.name + '" data-max-options="2">'
                sub_category_id = request.env['calendar.appointment.type'].sudo().search(
                    [('service_categ_id', '=', i.id)])
                for j in sub_category_id:
                    Dropdown += '<option value="' + str(j.id) + '" data-oe-model="' + str(
                        j.id) + '">' + j.name + '</option>'
                Dropdown += '</optgroup>'

        return Dropdown

    @http.route(['/booking_activities/filter/instructors'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_filter_instructors(self, **post):
        Dropdown = ''
        facilitator = request.env['hr.employee.category'].sudo().search([('name','=','Facilitator')])
        therapist = request.env['hr.employee.category'].sudo().search([('name','=','Therapist')])
        employee_id = request.env['hr.employee'].sudo().search(['|',('employee_type','in',facilitator.id),('employee_type','in',therapist.id)])
        for i in employee_id:
            Dropdown += '<option value="'+ str(i.id) +'">'+ i.name +'</option>'
        return Dropdown

    @http.route(['/booking_activities/filter/customer_detail'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_filter_customer_detail(self, **post):
        print("POSTTTTTTTTTTTTT",post)
        if post.get('website_id'):
            website_name = post.get('website_id').split("Super Admin")
            website_id = request.env['res.company'].sudo().search([('name','ilike',website_name[0].strip())])
           

        if post.get('selected_country_id') and  post.get('selected_country_id') != 'all':
            website_id_booking = request.env['res.company'].sudo().search([('id','=',int(post.get('selected_country_id')))])
           

        if post.get('selected_country_id_booking') and  post.get('selected_country_id_booking') != 'all':
            website_id_booking_first = request.env['res.company'].sudo().search([('id','=',int(post.get('selected_country_id_booking')))])
           

        # if post.get('selected_country_id') == 'all':
        #
        #     print("websiteee locationnnnnnnnnnniffffff")
        # else:
        #     # website_id_location = request.env['res.company'].sudo().browse(
        #     #     [('id', '=', int(post.get('selected_country_id')))])
        #     print("websiteee locationnnnnnnnnnn")


        if post.get('booking_date'):
            # same employee will not show for same timeslot bookings
            apt_id = request.env['appointment.appointment'].sudo().search([('booking_date','=',post['booking_date'])])
            slot_id = request.env['time.slot'].sudo().browse([int(post['time_slot_id'])])

                
            occupied_partner_ids = []
            if apt_id:
                try:
                    apt_ids = apt_id.filtered(lambda l: slot_id.start_time > l.time_slot_id.start_time and slot_id.start_time < l.time_slot_id.end_time)
                    occupied_partner_ids = apt_ids.partner_id.ids
                except Exception as e:
                    apt_ids = False
                    occupied_partner_ids = []
                    _logger.info("@exception@@@@@@@@@@@@@@ {}".format(e))
            
            
            if occupied_partner_ids:
                partner_id = request.env['res.partner'].sudo().search([('is_a_customer','=', True),('is_company','=',False),('user_ids','=',False),('id','not in',occupied_partner_ids)])
                print("partner_id22222222222222222222222222==",partner_id)
            else:
                if post.get('selected_country_id') != 'all' and post.get('selected_country_id_booking') != 'all':

                    partner_id = request.env['res.partner'].sudo().search(
                        [('is_a_customer', '=', True), ('location_ids', 'in', website_id_booking.ids),
                         ('is_company', '=', False),
                         ('user_ids', '=', False)])
                    

                else:
                    partner_id = request.env['res.partner'].sudo().search(
                        [('is_a_customer', '=', True), ('is_company', '=', False), ('user_ids', '=', False)])
                    
        elif  post.get('website_id') :
            partner_id = request.env['res.partner'].sudo().search(
                [('is_a_customer', '=', True), ('location_ids', 'in', website_id.ids), ('is_company', '=', False),
                 ('user_ids', '=', False)])
            

        elif  post.get('selected_country_id_booking') and  post.get('selected_country_id_booking') != 'all':
            partner_id = request.env['res.partner'].sudo().search(
                [('is_a_customer', '=', True), ('location_ids', 'in', website_id_booking_first.ids),
                 ('is_company', '=', False),
                 ('user_ids', '=', False)])
            

        else:
            partner_id = request.env['res.partner'].sudo().search([('is_a_customer','=', True),('is_company','=',False),('user_ids','=',False)])
            

        partner = []
        menu_id = request.env['ir.ui.menu'].sudo().search([('sequence','=',68)])
        for i in partner_id:
            partner.append({
                    'id': str(i.id),
                    'value': str(i.name),
                    'label': i.name or '',
                    'email': i.email or '',
                    'mobile': i.mobile or '',
                    'img': '/web/image?model=res.partner&id=%s&field=image_1920' % (i.id),
                    'url': "/web?debug=0#id="+ str(i.id) +"&action="+str(request.env.ref('custom_partner.action_client_edit').id)+"&model=res.partner&view_type=form&cids=&menu_id=" + str(menu_id.id)
                })
        return json.dumps(partner)

    # @http.route(['/booking_activities/get/service_categ'], type='http', auth="public", website=True, csrf=False, cors='*')
    # def booking_activities_get_service_categ(self, **post):
    #     print("post======",post)
    #     Dropdown = '<option value=""> </option>'
    #     lst = []
    #     employee_id = request.env['hr.employee'].sudo().browse(int(post['therapist_id']))
    #     for i in employee_id.pay_rate_ids:
    #         if i.service_category_type_id.id not in lst: 
    #             lst.append(i.service_category_type_id.id)
    #     for j in lst:
    #         service_id = request.env['appointment.category'].sudo().browse(int(j))
    #         Dropdown += '<option value="'+ str(service_id.id) +'">'+ service_id.name +'</option>'
    #     return Dropdown

    @http.route(['/booking_activities/get/service_categ'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_get_service_categ(self, **post):
        Dropdown = '<option value=""> </option>'
        lst = []
        employee_id = request.env['hr.employee'].sudo().browse(int(post['therapist_id']))

        for i in employee_id.availability_ids.filtered(lambda l: l.available_date.strftime("%Y-%m-%d")==post.get("date_value")):
                
            for l in i.service_categ_id:
                if l.id not in lst: 
                    lst.append(l.id)
        for j in lst:
            service_id = request.env['appointment.category'].sudo().browse(int(j))
            Dropdown += '<option value="'+ str(service_id.id) +'">'+ service_id.name +'</option>'
        return Dropdown

    @http.route(['/booking_activities/get/sub_categ'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_get_sub_categ(self, **post):
        Dropdown = '<option value=""> </option>'
        lst = []
        if post['service_categ_id'] != '':
            employee_id = request.env['hr.employee'].sudo().browse(int(post['therapist_id']))
            custom_pay_rate_ids = request.env['hr.employee.payrate'].sudo().search([\
            ('employee_id','=', int(post.get('therapist_id')))])


            if post['custom_time_min']:
                for i in employee_id.availability_ids.filtered(lambda l: l.available_date.strftime("%Y-%m-%d")==post.get("date_value")):   
                    for l in i.sub_categ_id.filtered(lambda l: l.service_categ_id.id==int(post['service_categ_id'])):
                    
                        if l.id not in lst: 
                            lst.append(l.id)
                custom_lst=[]
                for i in custom_pay_rate_ids:
                    if i.duration_id.name.split(' ')[0]==post['custom_time_min']:
                        custom_lst.append(i.appoinment_type_id.id)
                
                final_lst= list(set(lst) & set(custom_lst))
                for j in final_lst:
                    service_id = request.env['calendar.appointment.type'].sudo().browse(int(j))
                    Dropdown += '<option value="'+ str(service_id.id) +'">'+ service_id.name +'</option>'
            else:
                for i in employee_id.availability_ids.filtered(lambda l: l.available_date.strftime("%Y-%m-%d")==post.get("date_value")):   
                    for l in i.sub_categ_id.filtered(lambda l: l.service_categ_id.id==int(post['service_categ_id'])):
                    
                        if l.id not in lst: 
                            lst.append(l.id)
                for j in lst:
                    service_id = request.env['calendar.appointment.type'].sudo().browse(int(j))
                    Dropdown += '<option value="'+ str(service_id.id) +'">'+ service_id.name +'</option>'
                
        return Dropdown

    @http.route(['/booking_activities/get/time_id'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_get_time_id(self, **post):
        Dropdown = '<option value=""> </option>'
        lst = []
        if post['service_categ_id'] != '' and post['sub_categ_id'] != '':
            employee_id = request.env['hr.employee'].sudo().browse(int(post['therapist_id']))
            for i in employee_id.pay_rate_ids:
                if i.duration_id.id not in lst and int(post['service_categ_id']) == i.service_category_type_id.id and \
                                            int(post['sub_categ_id']) == i.appoinment_type_id.id:
                        lst.append(i.duration_id.id)
            for j in lst:
                time_id = request.env['time.time'].sudo().browse(int(j))
                Dropdown += '<option value="'+ str(time_id.id) +'">'+ time_id.name +'</option>'
        return Dropdown

    @http.route(['/booking_activities/get/time_slot_id'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_get_time_slot_id(self, **post):
        Dropdown = '<option value=""> </option>'
        lst = []
        if post['service_categ_id'] != '' and post['sub_categ_id'] != '' and post['time_id'] != '':
            line_ids = []
            TIMESLOT = request.env['time.slot'].sudo()
            def get_daily_slots(start, end, slot, date):
                dt = datetime.combine(date, datetime.strptime(start,"%H:%M").time())
                slots = [dt.time().strftime("%H:%M:%S")[:-3]]
                while (dt.time() < datetime.strptime(end,"%H:%M").time()):
                    dt = dt + timedelta(minutes=slot)
                    slots.append(dt.time().strftime("%H:%M:%S")[:-3])
                return slots
            def is_hour_between(avST, avEN):
                avail_id = request.env['appointment.appointment'].sudo().search([\
                    ('booking_date','=',post['booking_date']),\
                    ('therapist_id','=',int(post['therapist_id'])),('state','!=','cancel')])
                kt = []
                for s in avail_id:
                    if s.time_slot_id:
                        start = datetime.strptime(s.time_slot_id.start_time, '%H:%M').time()
                        end = datetime.strptime(s.time_slot_id.end_time, '%H:%M').time()
                        for j in range(1):
                            date_required = datetime.now().date() + timedelta(days=1)

                        T_Between = get_daily_slots(start=avST, end=avEN, slot=1, date=date_required)
                        T_Between.pop()
                        for T in T_Between:
                            av_start = datetime.strptime(T, '%H:%M').time()
                            is_between = False
                            is_between |= start < av_start < end #and start <= av_end <= end 
                            kt.append(is_between)
                if True in kt: 
                    is_between = True 
                else:
                    is_between = False

                return is_between

            avail_id = request.env['availability.availability'].sudo().search([\
                ('available_date','=',post['booking_date']),\
                ('facilitator','=',int(post['therapist_id'])),('availability','=','available')])
            lst = [];avl_lst = []
            for i in avail_id:
                start_time = i.start_time
                end_time = i.end_time
                time_id = request.env['time.time'].sudo().browse(int(post['time_id']))
                slot_time = time_id.duration
                days = 1
                start_date = post['booking_date']
                for j in range(days):
                    date_required = datetime.now().date() + timedelta(days=1)
                time_slot = get_daily_slots(start=start_time, end=end_time, slot=slot_time, date=date_required)
                for k in range(len(time_slot)):
                    lst.append((time_slot*2)[k:k+2])
                lst.pop()
                for o in lst:
                    if is_hour_between(o[0],o[1]) == False:
                        slot_id = request.env['time.slot'].sudo().search([('start_time','=',o[0]),('end_time','=',o[1])])
                        if slot_id:
                            Dropdown += '<option value="'+ str(slot_id.id) +'">'+ slot_id.name +'</option>'
        return Dropdown

    @http.route(['/booking_activities/get/room_id'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_get_room_id(self, **post):
        Dropdown = '<option value=""> </option>'
        lst = []
        if post['therapist_id'] != '' and post['time_id'] != '' and post['time_slot_id'] != '':
            available_room_id = request.env['roomtype.master'].sudo().search([('room_maincateg_id.roomcateg_code','=','APT')])
            slot_id = request.env['time.slot'].sudo().browse([int(post['time_slot_id'])])
            
            apt_id = request.env['appointment.appointment'].sudo().search([\
                ('booking_date','=',post['booking_date'])])
            

            if apt_id:
                apt_id = apt_id.filtered(lambda l: slot_id.start_time >=l.time_slot_id.start_time and slot_id.start_time <l.time_slot_id.end_time)
                occupied_room_ids = apt_id.apt_room_id.ids
                available_room_id = request.env['roomtype.master'].sudo().search([('id','not in',occupied_room_ids),('room_maincateg_id.roomcateg_code','=','APT')])
            lst = available_room_id.ids

            if lst: 
                for r in lst:
                    room_c_id = request.env['roomtype.master'].sudo().browse(r)
                    Dropdown += '<option value="'+ str(room_c_id.id) +'">'+ room_c_id.room_type +'</option>'

        return Dropdown

    @http.route(['/booking/url/redirect/<action_id>'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_get_url(self, action_id = None,**post):
        url = ''
        if action_id == 'customer_create':
            url = "/web?debug=0#id=&action="+ str(request.env.ref('custom_partner.action_client').id) + "&model=res.partner&view_type=form&cids=&create_partner=true&menu_id=" + str(request.env.ref('contacts.menu_contacts').id)
        if action_id == 'add_client':
            url = "/web?debug=0#id=&model=res.partner&view_type=form&cids=&menu_id=" + str(request.env.ref('contacts.menu_contacts').id) + "&action_id=" + str(request.env.ref('custom_partner.action_client').id)
        
        if action_id == 'client_list_view':
            url = "/web?debug=0#&model=res.partner&view_type=list&cids=&menu_id=" + str(request.env.ref('contacts.menu_contacts').id) + "&action_id=" + str(request.env.ref('custom_partner.action_client').id)
        
        if action_id == 'appointment_report_view':
            url = "/web#action=" + str(request.env.ref('ppts_custom_apt_mgmt.appointment_line_id_action_view').id) + "&model=appointment.line.id&view_type=list&cids=&menu_id=" + str(request.env.ref('ppts_custom_apt_mgmt.menu_appointments_report').id)

        if action_id == 'add_availability_view':
             url = "/web#action="+ str(request.env.ref('ppts_employee_availability.availability_action_view').id) +"&model=availability.availability&view_type=form&cids=&menu_id=" + str(request.env.ref('ppts_employee_availability.menu_ppts_availability').id)
            
        if action_id == 'availability_list_view':
            url = "/web#action="+ str(request.env.ref('ppts_employee_availability.availability_action_view').id) +"&model=availability.availability&view_type=list&cids=&menu_id=" + str(request.env.ref('ppts_employee_availability.menu_ppts_availability').id)
            
        if action_id == 'add_appointment_list_view' or action_id == 'home_classic_list':
            url = "/web#action="+ str(request.env.ref('ppts_custom_apt_mgmt.appointments_appointments_action_view').id) +"&model=appointment.appointment&view_type=list&cids=&menu_id=" + str(request.env.ref('ppts_custom_apt_mgmt.menu_ppts_Appointments').id)
        
        if action_id == 'add_appointment_form_view':
            url = "/web#action="+ str(request.env.ref('ppts_custom_apt_mgmt.appointments_appointments_action_view').id) +"&model=appointment.appointment&view_type=form&cids=&menu_id=" + str(request.env.ref('ppts_custom_apt_mgmt.menu_ppts_Appointments').id)
        
        return werkzeug.utils.redirect(url)

    @http.route(['/booking/id/redirect/<action_menu_id>/<int:action_id>'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_activities_get_url_base_id(self, action_menu_id = None, action_id = None,**post):
        url = ''
        if action_menu_id == 'employee_form':
            url = "/web#id="+ str(action_id) +"&action=502&model=hr.employee&view_type=form&cids=&menu_id=846"
        
        return werkzeug.utils.redirect(url)

    @http.route(['/booking/appointment/<state>/<apt_id>'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_appointment_action_url(self, state = None, apt_id = None,**post):
        appointment_id = request.env['appointment.appointment'].sudo().browse(int(apt_id))
        if state == 'confirm' and appointment_id.state == 'new':
            appointment_id.action_confirm()
        
        if appointment_id.state == 'confirm':
            if state == 'arrive':
                appointment_id.action_arrived()
            
            if state == 'reschedule':
                appointment_id.action_reschedule()

            if state == 'cancel':
                appointment_id.action_cancel()
        
        if appointment_id.state == 'arrive':
            pass
            if state == 'done':
                appointment_id.action_done()
            
            if state == 'cancel':
                appointment_id.action_cancel()

        if state == 'move_to_pos':
            appointment_id.action_move_to_pos()

        return werkzeug.utils.redirect("/booking")

    @http.route(['/booking_activities/appointment/reschedule'], type='http', auth="public", website=True, csrf=False, cors='*')
    def booking_appointment_reschedule(self, **post):
        appointment_id = request.env['appointment.appointment'].sudo().browse(int(post.get('re_apt_id')))
        if appointment_id:
            duration = request.env['time.time'].sudo().search([('duration','=', int(post.get('re_duration')))],limit=1)
            time_slot = request.env['time.slot'].sudo().search([('start_time','=', str(post.get('re_start_time'))),\
                ('end_time','=', str(post.get('re_end_time')))],limit=1)

            def reschedule():
                appointment_id.write({
                    'time_slot_id': time_slot.id,
                    'time_id': duration.id,
                })

            if appointment_id.state == 'new':
               reschedule()
            elif appointment_id.state in ('confirm','arrive'):
                appointment_id.action_reschedule()
                reschedule()
            return werkzeug.utils.redirect("/booking")
        
    @http.route(['/therapist/get/service/duration'], type='http', auth="public", website=True, csrf=False, cors='*')
    def therapist_get_service_duration(self, **post):
        duration = request.env['time.time'].sudo().search([('duration','=', int(post.get('duration')))],limit=1)
        print(duration,'durationdurationduration')
        appointment_id = request.env['hr.employee.payrate'].sudo().search([\
            ('employee_id','=', int(post.get('therapist'))),('duration_id','=', duration.id)])
        
        print(appointment_id,'appointment_idappointment_idappointment_id')
        return 'True' if appointment_id else 'False'

    @http.route(['/therapist/get/service/sub_ids'], type='http', auth="public", website=True, csrf=False, cors='*')
    def therapist_get_service_sub_ids(self, **post):
        # duration = request.env['time.time'].sudo().search([('duration','=', int(post.get('duration')))],limit=1)
        # print(duration,'durationdurationduration')
        appointment_id = request.env['hr.employee.payrate'].sudo().search([\
            ('employee_id','=', int(post.get('therapist'))),\
                ('duration_id','=', int(post.get('duration'))),\
                    ('service_category_type_id','=', int(post.get('services_categ_id'))),\
                        ('appoinment_type_id','=', int(post.get('sub_categ_id')))\
                    ])
        return 'True' if appointment_id else 'False'

    @http.route(['/get/service/duration'], type='http', auth="public", website=True, csrf=False, cors='*')
    def therapist_get_service_duration_it(self, **post):
        return str(request.env['time.time'].sudo().search([('duration','=', int(post.get('duration')))],limit=1).id)

    @http.route(['/get/service/time_slot'], type='http', auth="public", website=True, csrf=False, cors='*')
    def therapist_get_service_time_slot_it(self, **post):
        time_slot = request.env['time.slot'].sudo().search([('start_time','=', str(post.get('startTime'))),\
                ('end_time','=', str(post.get('endTime')))],limit=1)
        if not time_slot:
            t_id = request.env['time.slot'].sudo().create({
                'name': str(post.get('startTime')+'-'+post.get('endTime')),
                'start_time': str(post.get('startTime')),
                'end_time': str(post.get('endTime')),
            })
            return str(t_id.id)
        return str(time_slot.id)

    @http.route(['/get/direct/time_slot'], type='http', auth="public", website=True, csrf=False, cors='*')
    def therapist_get_direct_time_slot_it(self, **post):
        slots = request.env['appointment.appointment'].sudo().get_all_time_slots\
            (post.get('appointment'), \
                post.get('therapist'), \
                    post.get('appointment_date'), \
                        post.get('duration')) 

        dictt = {}
        for i in slots:
            time_slot = request.env['time.slot'].sudo().browse(i)
            dictt[time_slot.id] = time_slot.name
            
        if post.get('time_slot_id', False) and post.get('time_slot_id', False) not in slots:
            time_slot = request.env['time.slot'].sudo().browse(int(post.get('time_slot_id', False)))
            dictt[time_slot.id] = time_slot.name
            
        return json.dumps(dictt)

    @http.route(['/edit/duration/details'], type='http', auth="public", website=True, csrf=False, cors='*')
    def therapist_edit_duration_details(self, **post):
        pay_rate_ids = request.env['hr.employee.payrate'].sudo().search([\
            ('employee_id','=', int(post.get('therapist'))),\
                ('service_category_type_id','=', int(post.get('service_categ_id')))
                    ('appoinment_type_id','=', int(post.get('sub_categ_id')))\
                    ])

        dictt = {}
        for i in pay_rate_ids:
            print('00000000000000')
            print(i.duration_id.name)
            dictt[i.duration_id.id] = i.duration_id.name


        return json.dumps(dictt)

    

    @http.route(['/therapist/edit/custom'], type='http', auth="public", website=True, csrf=False, cors='*')
    def therapist_edit_custom(self, **post):
        duration_custom = request.env['time.time'].sudo().browse(int(post.get('durationcustom')))
        print(duration_custom,duration_custom.name,'durationdurationduration')
        custom_split_duration= duration_custom.name.split(' ')[0]
       
        # appointment_id = request.env['hr.employee.payrate'].sudo().search([\
        #     ('employee_id','=', int(post.get('therapist'))),('duration_id','=', duration.id)])
       
        return custom_split_duration

        

