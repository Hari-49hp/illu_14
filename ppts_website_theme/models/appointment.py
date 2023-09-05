# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
import logging
from odoo import models, fields, api, tools, release, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta
import datetime
import pytz


logger = logging.getLogger(__name__)


class Appointment(models.Model):
    _inherit = 'appointment.appointment'
    
    
    website_payment_status = fields.Selection([('no_paid','Not Paid'),('partially_paid','Partially Paid'),('payment_received','Paid'),('paid','Paid')],default='no_paid')
    
    
    @api.depends('apt_sale_amount','payment_status_apt','amount_due','total_advance_amount_paid','pos_order_id.amount_paid')
    def _compute_payment_from_payment(self):
        
        response = super(Appointment, self)._compute_payment_from_payment()
        
        for rec in self:
            if rec.sale_order_id and rec.booking_mode == "online":
                if rec.website_payment_status == "paid":
                    rec.payment_status_apt = 'paid'
                    # update the lead stage based on website payment status
                    get_source_id = self.env['utm.source'].sudo().search([('name','ilike','Website')],limit=1)
                    get_lead_id = self.env['crm.lead'].sudo().search([('appointment_id','=',rec.id),('source_id','=',get_source_id.id)])
                    if get_lead_id:
                        crm_stage = self.env['crm.stage'].search([('is_won','=',True)],limit=1)
                        get_lead_id.stage_id = crm_stage 
                else:
                    rec.payment_status_apt = 'no_paid'
    
    
    def create_SO_from_Website(self):
        payrate_id = self.env['hr.employee.payrate'].sudo().search([('service_category_type_id','=',self.service_categ_id.id),\
                    ('appoinment_type_id','=',self.appointments_type_id.id),('duration_id','=',self.time_id.id),\
                    ('employee_id','=',self.therapist_id.id)], limit=1)
        if payrate_id:
            pass
            if not self.sale_order_id:
                lst = []
                sale_id = self.env['sale.order'].sudo().create({
                        'partner_id': self.partner_id.id,
                        'pricelist_id': self.partner_id.property_product_pricelist.id,
                        'company_id': self.company_id.id,
                        'order_line': lst,
                        'state': 'sent',
                        'web_apt_id':self.id,
                        'descriptions':'Appointment',
                        'customer_id':self.partner_id.id,
                        'partner_inv_id':self.partner_id.id,
                        'partner_ship_id':self.partner_id.id,
                        'type':'apt'
                    })

                if self.session_type == 'type_single':
                    line_id = self.env['sale.order.line'].sudo().create({
                        'product_id': self.appointments_type_id.product_id.id,
                        'name': self.appointments_type_id.product_id.name + '(' + sale_id.web_apt_id.sequence + ')',
                        'product_uom_qty': 1,
                        'product_uom': self.appointments_type_id.product_id.uom_id.id,
                        'price_unit': payrate_id.unit_price,
                        'order_id': sale_id.id,
                        'price_subtotal': payrate_id.unit_price,
                    })

                    query = " UPDATE sale_order_line SET price_unit = %s WHERE id = %s; " % (str(payrate_id.unit_price), str(sale_id.id))
                    self.env.cr.execute(query)

                elif self.session_type == 'type_package':
                    self.add_package_line()
                    for i in range(0, int(self.s_service_categ_id.package_qty)): 
                        self.env['sale.order.line'].sudo().create({
                            'product_id': self.appointments_type_id.product_id.id,
                            'name': self.appointments_type_id.product_id.name,
                            'product_uom_qty': 1,
                            'product_uom': self.appointments_type_id.product_id.uom_id.id,
                            'price_unit': payrate_id.unit_price,
                            'discount': self.s_service_categ_id.discount,
                            'order_id': sale_id.id,
                        })
                
                self.sale_order_id = sale_id.id
                sale_id.action_confirm()


    def get_appoinment_time_slot(self, therapist_id, booking_date, time_id, service_id=False, service_categ_id=False):               
        from datetime import date,datetime, timedelta
        import datetime
        
        therapist_id = self.env['hr.employee'].sudo().browse(therapist_id)
        time_id = self.env['time.time'].sudo().browse(time_id)
        
        if therapist_id and time_id and booking_date:
            unavail_ids = self.env['availability.availability'].search([('available_date','>=',date.today()),('facilitator','=',therapist_id.id),('availability','=','unavailable'),\
                        ('available_date','=',booking_date),('date_range','=','ongoing'),('state','!=','draft')])
            unavail_data = []
            if unavail_ids:
                for unavail_id in unavail_ids:
                    unavail_date = unavail_id.available_date.strftime("%Y,%m,%d")
                    hours = (datetime.datetime(int(unavail_date[0:4]), int(unavail_date[5:7]), int(unavail_date[8:10]), int(unavail_id.start_time[:2]), int(unavail_id.start_time[3:])), datetime.datetime(int(unavail_date[0:4]), int(unavail_date[5:7]), int(unavail_date[8:10]), int(unavail_id.end_time[:2]), int(unavail_id.end_time[3:])))
                    unavail_data = self.get_slots1(hours, timedelta(minutes=time_id.duration))

            avail_ids = self.env['availability.availability'].search([('available_date','>=',date.today()),('available_date','=',booking_date),\
                    ('facilitator','=',therapist_id.id),('availability','=','available'),('state','!=','draft')])
            if avail_ids:
                booked_slots  = []
                avail_slot_ids = []
                for avail_id in avail_ids:

                    avail_date = avail_id.available_date.strftime("%Y,%m,%d")
                    # hours = (datetime.datetime(2017, 9, 7, 10, 0), datetime.datetime(2017, 9, 7, 22, 0))
                    hours = (datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(avail_id.start_time[:2]), int(avail_id.start_time[3:])), datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(avail_id.end_time[:2]), int(avail_id.end_time[3:])))
                    appointments_ids = self.env['appointment.appointment'].search([('booking_date','>=',date.today()),('booking_date','=',booking_date),\
                            ('state','!=','cancel'),('therapist_id','=',therapist_id.id),('id','!=',self._origin.id)])
                    if appointments_ids:
                        for appointments_id in appointments_ids:
                            booked_slots.append(appointments_id.time_slot_id.id)
                    # event booked slots
                    events_id = self.env['multi.date.line'].sudo().search([('date_begin','>=',booking_date),('date_end','<=',booking_date),('event_id.facilitator_evnt_ids','in',therapist_id.ids)])
                    for evnt in events_id:
                        if str(evnt.hour_time_begin) and str(evnt.min_time_begin) and str(evnt.hour_time_end) and str(evnt.min_time_end):
                            get_slot_begin = str(evnt.hour_time_begin) + ':'+ str(evnt.min_time_begin)
                            get_slot_end = str(evnt.hour_time_end) + ':'+ str(evnt.min_time_end)
                            event_times = get_slot_begin +'-'+get_slot_end
                            get_time_slot = self.env['time.slot'].sudo().search([('name','ilike',event_times)])
                            if get_time_slot:
                                booked_slots.append(get_time_slot.id)
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
                    avail_slots_ids =[]
                    if data:
                        slot_id = TIMESLOT.search([('name','in',data)])
                        avail_slots = slot_id
                        avail_slots_ids = slot_id.ids
                    slots = [elem for elem in avail_slots if elem not in booked_slots]
                    slots_ids = [elem for elem in avail_slots_ids if elem not in booked_slots]

                    # current time managing starts

                    from datetime import date, datetime, timedelta, time
                    if booking_date == date.today().strftime("%Y-%m-%d"):
                        ad_data = []
                        dd = TIMESLOT.search([('id','in',slots_ids)])
                        for ele in dd:
                            ad_data.append(ele.name)
                        full_time = datetime.now()
                        currnet_full_time = datetime.now() + timedelta(hours=5.50)
                        current_time = str(currnet_full_time.time().hour)+':'+ str(currnet_full_time.time().minute)
                        for line in ad_data:
                            if line[0:5] > current_time:
                                active_slots = TIMESLOT.search([('name','=',line)])
                                if active_slots:
                                    avail_slot_ids.append(active_slots)
                    else:
                        avail_slot_ids = slots 
                    return avail_slot_ids                   
                
        

    # def get_appoinment_slots(self, hours, duration):
    #     slots = sorted([(hours[0], hours[0])] + [(hours[1], hours[1])])
    #     for start, end in ((slots[i][1], slots[i+1][0]) for i in range(len(slots)-1)):
    #         assert start <= end, "Cannot attend all appointments"
    #         slot_list = []
    #         while start + duration <= end:
    #             # print ('sssssssss',"{:%H:%M}-{:%H:%M}".format(start, start + duration))
    #             slot_list.append("{:%H:%M}-{:%H:%M}".format(start, start + duration))
    #             start += duration
    #         return slot_list

    # def get_appoinment_time_slot(self, therapist_id, booking_date, time_id, service_id=False, service_categ_id=False):
    #     slots = []
        
    #     if (not therapist_id) or (not booking_date) or (time_id):
    #         therapist_id = self.env['hr.employee'].sudo().browse(therapist_id)
    #         time_id = self.env['time.time'].sudo().browse(time_id)        

    #     if therapist_id and booking_date:
    #         self.time_slot_id = False
       
    #         avail_id = self.env['availability.availability'].sudo().search([('available_date','>=',date.today()),('available_date','=',booking_date),\
    #                 ('facilitator','=',therapist_id.id),('availability','=','available'),('state','!=','draft')], limit=1)
    #         # print('avail_id',avail_id)
    #         if avail_id:
               
    #             avail_date = avail_id.available_date.strftime("%Y,%m,%d")

    #             if avail_date == date.today().strftime("%Y,%m,%d"):
    #                 timezone = pytz.timezone(self.env.user.tz or 'UTC')

    #                 now = datetime.datetime.now(timezone)
    #                 hour = now.hour
    #                 minutes = now.minute
    #                 if int(avail_id.start_time[:2]) <= hour:
    #                     hours = (datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(hour+1), int(avail_id.start_time[3:])), datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(avail_id.end_time[:2]), int(avail_id.end_time[3:])))
    #                 else:
    #                     hours = (datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(avail_id.start_time[:2]), int(avail_id.start_time[3:])), datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(avail_id.end_time[:2]), int(avail_id.end_time[3:])))
    #             else:
    #                 hours = (datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(avail_id.start_time[:2]), int(avail_id.start_time[3:])), datetime.datetime(int(avail_date[0:4]), int(avail_date[5:7]), int(avail_date[8:10]), int(avail_id.end_time[:2]), int(avail_id.end_time[3:])))
    #             appointments_id = self.env['appointment.appointment'].sudo().search([('booking_date','>=',date.today()),('booking_date','=',booking_date),\
    #                     ('state','!=','cancel'),('therapist_id','=',therapist_id.id)])  
                
    #             booked_slots  = []
    #             if appointments_id:
    #                 for app_id in appointments_id:
    #                     booked_slots.append(app_id.time_slot_id.id)
    #             # Event booked slots
    #             events_id = self.env['multi.date.line'].sudo().search([('date_begin','>=',booking_date),('date_end','<=',booking_date),('event_id.facilitator_evnt_ids','in',therapist_id.ids)])
    #             for evnt in events_id:
    #                 if str(evnt.hour_time_begin) and str(evnt.min_time_begin) and str(evnt.hour_time_end) and str(evnt.min_time_end):
    #                     get_slot_begin = str(evnt.hour_time_begin) + ':'+ str(evnt.min_time_begin)
    #                     get_slot_end = str(evnt.hour_time_end) + ':'+ str(evnt.min_time_end)
    #                     event_times = get_slot_begin +'-'+get_slot_end
    #                     get_time_slot = self.env['time.slot'].sudo().search([('name','ilike',event_times)])
    #                     if get_time_slot:
    #                         for events in get_time_slot:
    #                             booked_slots.append(events.id)

    #             TIMESLOT = self.env['time.slot']

               
    #             data = self.get_appoinment_slots(hours, timedelta(minutes=time_id.duration))
    #             avail_slots = []
    #             if data:

    #                 slot_ids = TIMESLOT.sudo().search([('name','in',data)])
    #             else:
    #                 slot_ids = []

    #             avail_slot_ids = [elem for elem in slot_ids if elem.id not in booked_slots]
    #             return avail_slot_ids
            
    # def get_appoinment_time_slot(self, time_id, therapist_id):
    #     print('sdf')
    #     time_id = self.env['time.time'].sudo().browse(time_id)
    #     data = self.get_appoinment_slots(hours, timedelta(minutes=time_id.duration))


class Sale(models.Model):
    _inherit = 'sale.order'
    
    
    def create_invoice_website(self):
        invoice_lines = []
        if self.web_event_id:
            inv_desc = self.web_event_id.event_seq
        if self.web_apt_id:
            inv_desc = self.web_apt_id.sequence
        for line in self.order_line:
            vals = {
                # 'name': line.name,
                'price_unit': line.price_unit,
                'quantity': line.product_uom_qty,
                'product_id': line.product_id.id,
                'name': line.product_id.name + '(' + inv_desc + ')',
                'product_uom_id': line.product_uom.id,
                'tax_ids': [(6, 0, line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [line.id])],
            }
            invoice_lines.append((0, 0, vals))
        account = self.env['account.move'].create({
            'ref': self.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': self.name,
            'invoice_user_id': self.user_id.id,
            'partner_id': self.customer_id.id,
            'sale_id':self.id,
            'currency_id': self.pricelist_id.currency_id.id,
            'invoice_line_ids': invoice_lines,
        })
        account.action_post()
        return True


    def create_invoice_website_paid(self):
        invoice_lines = []
        if self.web_event_id:
            inv_desc = self.web_event_id.event_seq
        if self.web_apt_id:
            inv_desc = self.web_apt_id.sequence
        for line in self.order_line:
            vals = {
                'price_unit': line.price_unit,
                'quantity': line.product_uom_qty,
                'product_id': line.product_id.id,
                'name': line.product_id.name + '(' + inv_desc + ')',
                'product_uom_id': line.product_uom.id,
                'tax_ids': [(6, 0, line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [line.id])],
            }
            invoice_lines.append((0, 0, vals))
        account = self.env['account.move'].create({
            'ref': self.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': self.name,
            'invoice_user_id': self.user_id.id,
            'partner_id': self.customer_id.id,
            'sale_id':self.id,
            'currency_id': self.pricelist_id.currency_id.id,
            'invoice_line_ids': invoice_lines
        })
        account.action_post()
        move_id = self.env['account.move'].sudo().search([('move_type','=','entry'),('ref','=',account.name)],limit=1)
        payment = self.env['account.payment'].create({
            'payment_type':'inbound',
            'partner_type':'customer',
            'destination_account_id':self.partner_id.property_account_receivable_id.id,
            'company_id':self.company_id.id,
            'amount':self.amount_total,
            'ref':account.name,
            'date':account.invoice_date,
            'move_id':move_id.id,
            'partner_id':self.partner_id.id
            # 'journal_id':8
        })
        payment.action_post()
        move_line = payment.move_id.line_ids.filtered(lambda l:l.credit > 0)
        # call base auto reconcile function and pass the values
        account.js_assign_outstanding_line(move_line.id)
        self.payment_type = "credit_card"
        return True
                

    
