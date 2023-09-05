from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import datetime
import logging
import pytz
from odoo.exceptions import UserError 


_logger = logging.getLogger(__name__)


class CustomAppointments(models.Model):
    _inherit = 'appointment.appointment'

    parent_appointment_no = fields.Char('Parent Appointment No.')
    partner_inv = fields.Boolean(string="Partner",help="If Enable this check box all the service info group field will readonly")



    @api.returns('self', lambda value: value.id)
    def copy(self, defaults=None):
        if not defaults:
            defaults = {}
        if self.env.context.get('new_product_id'):
            appointments_type = self.env['calendar.appointment.type'].search([
                ('product_id', '=', self.env.context.get('new_product_id'))], limit=1)
            if appointments_type:
                appointments_type_id = appointments_type.id
            else:
                appointments_type_id = False
            defaults.update({'partner_id': self.partner_id.id, 'appointments_type_id': appointments_type_id,
                             'pos_order_id': self.pos_order_id.id, 'therapist_id': self.therapist_id.id,
                             'du_service_categ_id': self.du_service_categ_id.id, 'available_booking_date': False,
                             'time_id': False, 'time_slot_id': False, 'apt_room_id': False,
                             'pre_booking': True, 'change_time': False, 'parent_appointment_no': self.sequence})
        return super(CustomAppointments, self).copy(defaults)
        
    def get_daily_slots(self, start, end, slot, date):
        dt = datetime.combine(date, datetime.strptime(start,"%H:%M").time())
        slots = [dt.time().strftime("%H:%M:%S")[:-3]]
        while (dt.time() < datetime.strptime(end,"%H:%M").time()):
            dt = dt + timedelta(minutes=slot)
            slots.append(dt.time().strftime("%H:%M:%S")[:-3])
        return slots

    def get_slots1(self, hours, duration):
        from datetime import datetime, timedelta
        import datetime

        slots = sorted([(hours[0], hours[0])] + [(hours[1], hours[1])])
        for start, end in ((slots[i][1], slots[i+1][0]) for i in range(len(slots)-1)):
            assert start <= end, "Cannot attend all appointments"
            slot_list = []
            while start + duration <= end:
                slot_list.append("{:%H:%M}-{:%H:%M}".format(start, start + duration))
                start += duration
            return slot_list

    def get_slots(self, hours, appointments, duration): 
        slot_list = []
        slots = sorted([(hours[0], hours[0])] + appointments + [(hours[1], hours[1])])
        for start, end in ((slots[i][1], slots[i+1][0]) for i in range(len(slots)-1)):
            assert start <= end, "Cannot attend all appointments"           
            while start + duration <= end:
                slot_list.append("{:%H:%M}-{:%H:%M}".format(start, start + duration))
                start += duration
        return slot_list

    @api.onchange('therapist_id','time_id','booking_date','change_time')
    def onchange_time_slot_change(self):
        from datetime import datetime, timedelta
        import datetime

        if self.therapist_id and self.time_id and self.booking_date:
            self.time_slot_id = False
            unavail_ids = self.env['availability.availability'].search([('facilitator','=',self.therapist_id.id),('availability','=','unavailable'),\
                        ('available_date','=',self.booking_date.strftime("%Y-%m-%d")),('date_range','=','ongoing'),('state','!=','draft')])
            unavail_data = []
            if unavail_ids:
                for unavail_id in unavail_ids:
                    unavail_date = unavail_id.available_date.strftime("%Y,%m,%d")
                    # hours = (datetime.datetime(2017, 9, 7, 10, 0), datetime.datetime(2017, 9, 7, 22, 0))
                    hours = (datetime.datetime(int(unavail_date[0:4]), int(unavail_date[5:7]), int(unavail_date[8:10]), int(unavail_id.start_time[:2]), int(unavail_id.start_time[3:])), datetime.datetime(int(unavail_date[0:4]), int(unavail_date[5:7]), int(unavail_date[8:10]), int(unavail_id.end_time[:2]), int(unavail_id.end_time[3:])))
                    unavail_data = self.get_slots1(hours, timedelta(minutes=self.time_id.duration))

            avail_ids = self.env['availability.availability'].search([('available_date','=',self.booking_date.strftime("%Y-%m-%d")),\
                    ('facilitator','=',self.therapist_id.id),('availability','=','available'),('state','!=','draft')])
            if avail_ids:
                booked_slots  = []
                final_slots = []
                for avail_id in avail_ids:

                    avail_date = avail_id.available_date.strftime("%Y,%m,%d")
                    # hours = (datetime.datetime(2017, 9, 7, 10, 0), datetime.datetime(2017, 9, 7, 22, 0))
                    hours = (datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(avail_id.start_time[:2]), int(avail_id.start_time[3:])), datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(avail_id.end_time[:2]), int(avail_id.end_time[3:])))
                    appointments_ids = self.env['appointment.appointment'].search([('booking_date','=',self.booking_date.strftime("%Y-%m-%d")),\
                            ('state','!=','cancel'),('therapist_id','=',self.therapist_id.id),('id','!=',self._origin.id)])
                    if appointments_ids:
                        for appointments_id in appointments_ids:
                            booked_slots.append(appointments_id.time_slot_id.id)
                    TIMESLOT = self.env['time.slot']
                    for lines in unavail_data:
                        unavail_name = TIMESLOT.search([('name','=',lines)])
                        if unavail_name:
                            booked_slots.append(unavail_name.id)
                    appointments_time_list = []
                    if booked_slots:    
                        booked_ids = TIMESLOT.search([('id','in',booked_slots)])
                        if booked_ids:                            
                            for book_id in booked_ids:
                                appointments_time = (datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(book_id.name[0:2]), int(book_id.name[3:5])), datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(book_id.name[6:8]), int(book_id.name[9:11])))
                                appointments_time_list.append(appointments_time)
                    data = self.get_slots(hours, appointments_time_list, timedelta(minutes=self.time_id.duration))
                    avail_slots = []
                    if data:
                        slot_id = TIMESLOT.search([('name','in',data)])
                        avail_slots = slot_id.ids
                    slots = [elem for elem in avail_slots if elem not in booked_slots]
                    # current time managing starts
                    from datetime import date, datetime, timedelta, time
                    if self.booking_date == date.today():
                        ad_data = []
                        dd = TIMESLOT.search([('id','in',slots)])
                        for ele in dd:
                            ad_data.append(ele.name)
                        full_time = datetime.now()
                        currnet_full_time = datetime.now() + timedelta(hours=5.50)
                        current_time = str(currnet_full_time.time().hour)+':'+ str(currnet_full_time.time().minute)
                        for line in ad_data:
                            if line[0:5] > current_time:
                                active_slots = TIMESLOT.search([('name','=',line)])
                                if active_slots:
                                    final_slots.append(active_slots.id)
                    else:
                        final_slots = slots
                    # current time managing ends
                    res = {'domain': {'time_slot_id': "[('id', 'not in', False)]"}}
                    res['domain']['time_slot_id'] = "[('id', 'in', %s)]" % final_slots
                    return res

    def get_all_time_slots(self, appointment_id, therapist_id, booking_date, time_id):
        from datetime import datetime, timedelta
        import datetime

        appointment_id = self.env['appointment.appointment'].browse(int(appointment_id))
        therapist_id = self.env['hr.employee'].browse(int(therapist_id))
        time_id = self.env['time.time'].browse(int(time_id))        
        
        unavail_ids = self.env['availability.availability'].search([('facilitator','=',therapist_id.id),('availability','=','unavailable'),\
                        ('available_date','=',booking_date),('date_range','=','ongoing'),('state','!=','draft')])
        unavail_data = []
        if unavail_ids:
            for unavail_id in unavail_ids:
                unavail_date = unavail_id.available_date.strftime("%Y,%m,%d")
                hours = (datetime.datetime(int(unavail_date[0:4]), int(unavail_date[5:7]), int(unavail_date[8:10]), int(unavail_id.start_time[:2]), int(unavail_id.start_time[3:])), datetime.datetime(int(unavail_date[0:4]), int(unavail_date[5:7]), int(unavail_date[8:10]), int(unavail_id.end_time[:2]), int(unavail_id.end_time[3:])))
                unavail_data = self.get_slots1(hours, timedelta(minutes=time_id.duration))

        avail_ids = self.env['availability.availability'].search([('available_date','=',booking_date),\
                ('facilitator','=',therapist_id.id),('availability','=','available'),('state','!=','draft')])
        if avail_ids:
            booked_slots  = []
            final_slots = []
            for avail_id in avail_ids:

                avail_date = avail_id.available_date.strftime("%Y,%m,%d")
                # hours = (datetime.datetime(2017, 9, 7, 10, 0), datetime.datetime(2017, 9, 7, 22, 0))
                hours = (datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(avail_id.start_time[:2]), int(avail_id.start_time[3:])), datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(avail_id.end_time[:2]), int(avail_id.end_time[3:])))
                appointments_ids = self.env['appointment.appointment'].search([('booking_date','=',booking_date),\
                        ('state','!=','cancel'),('therapist_id','=',therapist_id.id),('id','!=',appointment_id.id)])
                if appointments_ids:
                    for appointments_id in appointments_ids:
                        booked_slots.append(appointments_id.time_slot_id.id)
                TIMESLOT = self.env['time.slot']
                for lines in unavail_data:
                    unavail_name = TIMESLOT.search([('name','=',lines)])
                    if unavail_name:
                        booked_slots.append(unavail_name.id)
                appointments_time_list = []
                if booked_slots:    
                    booked_ids = TIMESLOT.search([('id','in',booked_slots)])
                    if booked_ids:                            
                        for book_id in booked_ids:
                            appointments_time = (datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(book_id.name[0:2]), int(book_id.name[3:5])), datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(book_id.name[6:8]), int(book_id.name[9:11])))
                            appointments_time_list.append(appointments_time)
                data = self.get_slots(hours, appointments_time_list, timedelta(minutes=time_id.duration))
                avail_slots = []
                if data:
                    slot_id = TIMESLOT.search([('name','in',data)])
                    avail_slots = slot_id.ids
                slots = [elem for elem in avail_slots if elem not in booked_slots]
                # current time managing starts
                from datetime import date, datetime, timedelta, time
                if datetime.strptime(booking_date, "%Y-%m-%d").date() == date.today():
                    ad_data = []
                    dd = TIMESLOT.search([('id','in',slots)])
                    for ele in dd:
                        ad_data.append(ele.name)
                    full_time = datetime.now()
                    currnet_full_time = datetime.now() + timedelta(hours=5.50)
                    current_time = str(currnet_full_time.time().hour)+':'+ str(currnet_full_time.time().minute)
                    for line in ad_data:
                        if line[0:5] > current_time:
                            active_slots = TIMESLOT.search([('name','=',line)])
                            if active_slots:
                                final_slots.append(active_slots.id)
                else:
                    final_slots = slots

                return final_slots

    @api.onchange('therapist_id','time_id','booking_date','time_slot_id')
    def onchange_time_slot_room_restrict_change(self):
        line_ids = []
        from datetime import datetime, timedelta
        if self.therapist_id and self.time_id and self.booking_date and self.time_slot_id:
            room_id = self.env['roomtype.master'].search([])
            for i in room_id:
                apt_id = self.env['appointment.appointment'].search([\
                    ('booking_date','=',self.booking_date.strftime("%Y-%m-%d")),\
                    ('apt_room_id','=',i.id)])
                if apt_id:
                    for s in apt_id:
                        if s.time_slot_id:
                            start_time = datetime.strptime(s.time_slot_id.start_time, '%H:%M').time()
                            end_time = datetime.strptime(s.time_slot_id.end_time, '%H:%M').time()
                            apt_start_time = datetime.strptime(self.time_slot_id.start_time, '%H:%M').time()
                            apt_end_time = datetime.strptime(self.time_slot_id.end_time, '%H:%M').time()
                            if start_time < apt_start_time < end_time or start_time < apt_end_time < end_time:
                                print("---")
                            elif apt_start_time == start_time and apt_end_time == end_time:
                                print("---")
                            else:
                                line_ids.append(i.id)
                else:
                    line_ids.append(i.id)
        res = {'domain': {'apt_room_id': "[('id', 'not in', False)]"}}
        res['domain']['apt_room_id'] = "[('id', 'in', %s),('room_maincateg_id.roomcateg_code','=','APT')]" % line_ids
        return res

    # Made some changes in validation 

    @api.onchange('apt_room_id')
    def onchange_apt_room_id(self):
        event_date_ids =self.env['multi.date.line'].search([('date_begin','=',self.booking_date),('event_id.room_id','=',self.apt_room_id.id)])
        for each_event in event_date_ids:
            timezone = pytz.timezone(self.env.user.tz or 'UTC')
            date_begin = each_event.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
            date_end = each_event.m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
            if self.start_time_str and self.end_time_str:
                # made changes in room validations 29-06-22
                if date_begin.strftime("%H:%M") >= self.start_time_str  and date_end.strftime("%H:%M") <= self.end_time_str:
                    raise UserError(_('This Room is allocated to another Event at this Time. \n Event Name - %s \n Event Reference - %s' % (each_event.event_id.name,each_event.event_id.event_seq)))

                # if self.start_time_str <= date_end.strftime("%H:%M") <= self.end_time_str:
                #     raise UserError(_('This Room is allocated to another Event at this Time. \n Event Name - %s \n Event Reference - %s' % (each_event.event_id.name,each_event.event_id.event_seq)))
    # Made some changes in validation 29-06-22
    @api.onchange('time_slot_id')
    def onchange_apt_time_slot_id(self):
        event_date_ids =self.env['multi.date.line'].search([('date_begin','=',self.booking_date),('event_id.facilitator_evnt_ids','=',self.therapist_id.id),('event_id.is_published','=',True)])
        for each_event in event_date_ids:  
            timezone = pytz.timezone(self.env.user.tz or 'UTC')
            date_begin = each_event.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
            date_end = each_event.m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
            if self.start_time_str and self.end_time_str:
                if date_begin.strftime("%H:%M") >= self.start_time_str  and date_end.strftime("%H:%M") <= self.end_time_str:
                    raise UserError(_("This Timing is allocated to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (each_event.event_id.name,each_event.event_id.event_seq)))
              

                if self.start_time_str <= date_begin.strftime("%H:%M"):
                    if self.start_time_str <= date_begin.strftime("%H:%M") and date_begin.strftime("%H:%M") < self.end_time_str:    
                        raise UserError(_("This Timing is allocated to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (each_event.event_id.name,each_event.event_id.event_seq)))
                    if self.start_time_str <= date_end.strftime("%H:%M") and date_end.strftime("%H:%M")  < self.end_time_str: 
                        raise UserError(_("This Timing is allocated to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (each_event.event_id.name,each_event.event_id.event_seq)))

                if self.start_time_str > date_begin.strftime("%H:%M"):
                    if self.start_time_str >= date_begin.strftime("%H:%M") and self.start_time_str < date_end.strftime("%H:%M"):    
                        raise UserError(_("This Timing is allocated to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (each_event.event_id.name,each_event.event_id.event_seq)))
            

        # raise waring if appointment created with same customer 01-07-22
        search_appointment = self.env['appointment.appointment'].sudo().search([
            ('booking_date','=',self.booking_date),('partner_id','=',self.partner_id.id)])
        for each_apt in search_appointment:
            if each_apt.sequence != self.sequence and self.change_time:
                if each_apt.start_time_str and each_apt.end_time_str and self.start_time_str:
                    if self.start_time_str <= each_apt.start_time_str:
                        if self.start_time_str <= each_apt.start_time_str and each_apt.start_time_str < self.end_time_str:
                            raise UserError(_("This Customer is allocated to another Appointment at this time. \n Customer Name - %s \n Appointment Reference - %s" % (each_apt.partner_id.name,each_apt.sequence)))
                        if self.start_time_str <= each_apt.end_time_str and each_apt.end_time_str  < self.end_time_str:
                            raise UserError(_("This Customer is allocated to another Appointment at this time. \n Customer Name - %s \n Appointment Reference - %s" % (each_apt.partner_id.name,each_apt.sequence)))

                    if self.start_time_str > each_apt.start_time_str:
                        if self.start_time_str >= each_apt.start_time_str and self.start_time_str < each_apt.end_time_str:
                            raise UserError(_("This Customer is allocated to another Appointment at this time. \n Customer Name - %s \n Appointment Reference - %s" % (each_apt.partner_id.name,each_apt.sequence)))


        # unavailability validation start 05-07-22
        get_avail_id = self.env['availability.availability'].sudo().search([
            ('available_date','=',self.booking_date),('facilitator','=',self.therapist_id.id),('availability','=','unavailable')])
        for rec in get_avail_id:
            avail_start = rec.start_time
            avail_end = rec.end_time
            if self.session_type == 'type_single':
                if self.start_time_str > avail_start and self.end_time_str < avail_end:
                    raise UserError(_("The unavailability created for the therapist at this time. \n Unavailable Reason - %s" % (rec.reason)))

                if self.start_time_str <= avail_start:
                    if self.start_time_str <= avail_start and avail_start < self.end_time_str:
                        raise UserError(_("The unavailability created for the therapist at this time. \n Unavailable Reason - %s" % (rec.reason)))
                    if self.start_time_str <= avail_end and avail_end  < self.end_time_str:
                        raise UserError(_("The unavailability created for the therapist at this time. \n Unavailable Reason - %s" % (rec.reason)))

                if self.start_time_str > avail_start:
                    if self.start_time_str >= avail_start and self.start_time_str < avail_end:
                        raise UserError(_("The unavailability created for the therapist at this time. \n Unavailable Reason - %s" % (rec.reason)))
            # unavailability validation start 05-07-22

                       # if self.start_time_str >= each_apt.end_time_str and self.end_time_str > each_apt.end_time_str:
                        #raise UserError(_("s Customer is allocated to another Appointment at this time. \n Customer Name - %s \n Appointment Reference - %s" % (each_apt.partner_id.name,each_apt.sequence)))
            # event_date_cust_ids =self.env['event.registration'].search([('partner_id','=',self.partner_id.id)])
            # for eve in event_date_cust_ids:
            #     for line in  eve.event_id.multi_date_line_ids:
            #         if self.booking_date >= line.date_begin :
            #             if line.date_begin.strftime("%H:%M") >= self.start_time_str:
            #                 stop
                        # if line.date_begin.strftime("%H:%M") == self.start_time_str:
                        #     stops

                # timezone = pytz.timezone(self.env.user.tz or 'UTC')
                # date_begin = each_event.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                # date_end = each_event.m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                # if self.start_time_str and self.end_time_str:
        




    # Raise warning if not below group members try to delete the record 01-07-22
    def unlink(self):
        for rec in self: 
            if not (self.env.user.has_group('ppts_custom_event_mgmt.group_admin')):
                raise UserError(_("You cannot delete an Appointment."))
        return super(CustomAppointments, self).unlink()


class CustomAppointmentsLine(models.Model):
    _inherit = 'appointment.line.id'

    time_slot_id = fields.Many2one('time.slot', string='Time Slots') 

    @api.onchange('time_slot_id')
    def _onchange_time_slot_id(self):
        if self.time_slot_id:
            self.start_time_str = self.time_slot_id.start_time
            self.end_time_str = self.time_slot_id.end_time

            start_time = datetime.strptime(str(self.time_slot_id.start_time), "%H:%M")
            start_time = start_time.strftime("%H.%M")
            self.start_time = float(start_time)
            self.end_time = abs(float(start_time) + self.duration)

    def get_daily_slots(self, start, end, slot, date):
        dt = datetime.combine(date, datetime.strptime(start,"%H:%M").time())
        slots = [dt.time().strftime("%H:%M:%S")[:-3]]
        while (dt.time() < datetime.strptime(end,"%H:%M").time()):
            dt = dt + timedelta(minutes=slot)
            slots.append(dt.time().strftime("%H:%M:%S")[:-3])
        return slots

    @api.onchange('therapist_id','time_id','booking_start_date')
    def onchange_time_slot_change(self):
        line_ids = []
        if self.therapist_id and self.time_id and self.booking_start_date:
            TIMESLOT = self.env['time.slot']
            def is_hour_between(avST, avEN):
                avail_id = self.env['availability.availability'].search([\
                    ('available_date','=',self.booking_start_date.strftime("%Y-%m-%d")),\
                    ('facilitator','=',self.therapist_id.id),('availability','=','unavailable')])
                kt = []
                for s in avail_id:
                    start = datetime.strptime(s.start_time, '%H:%M').time()
                    end = datetime.strptime(s.end_time, '%H:%M').time()
                    for j in range(1):
                        date_required = datetime.now().date() + timedelta(days=1)
                    T_Between = self.get_daily_slots(start=avST, end=avEN, slot=1, date=date_required)
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
            avail_id = self.env['availability.availability'].search([\
                ('available_date','=',self.booking_start_date.strftime("%Y-%m-%d")),\
                ('facilitator','=',self.therapist_id.id),('availability','=','available')])            
            lst = [];avl_lst = []
            for i in avail_id:
                start_time = i.start_time
                end_time = i.end_time
                slot_time = self.time_id.duration
                days = 1
                start_date = self.booking_start_date
                for j in range(days):
                    date_required = datetime.now().date() + timedelta(days=1)
                time_slot = self.get_daily_slots(start=start_time, end=end_time, slot=slot_time, date=date_required)
                for k in range(len(time_slot)):
                    lst.append((time_slot*2)[k:k+2])
            for o in lst:
                if is_hour_between(o[0],o[1]) == False:
                    slot_id = TIMESLOT.search([('start_time','=',o[0]),('end_time','=',o[1])])
                    line_ids.append(slot_id.id)
        res = {'domain': {'time_slot_id': "[('id', 'not in', False)]"}}
        res['domain']['time_slot_id'] = "[('id', 'in', %s)]" % line_ids
        return res
