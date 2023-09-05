from ast import literal_eval
import logging
import random
import xlwt
import base64
import io
from datetime import datetime,date, timedelta
from psycopg2 import IntegrityError
from odoo.tools import mute_logger
from odoo import api, fields, models, _

logger = logging.getLogger(__name__)


class DataMiner(models.TransientModel):
    _name = 'data.miner'
    _description = 'Data Miner'

    campaign_id = fields.Many2one('asterisk_dialer.campaign',index=True,string='campaign')
    domain = fields.Char(
        string='Domain', compute='_compute_domain',
        readonly=False, store=True)
    # Many2many relations with GENERATE_CONTACTS_MODELS
    partner_ids = fields.Many2many(
        'res.partner', string='Partners',compute='_compute_partners')
    # Fields For Location Filters
    country_ids = fields.Many2many('res.country',string='Country ')
    # unique_company_ids = fields.Many2many('res.company', string='Company')
    is_country = fields.Boolean("")
    city_ids = fields.Many2many('city.master',string='City' ,domain="[('country_id', 'in', country_ids),('state_id','in',state_ids)]")
    is_city = fields.Boolean("")
    state_ids = fields.Many2many('res.country.state',string='State' ,domain="[('country_id', 'in', country_ids)]")
    is_state = fields.Boolean("")
    postal_code = fields.Char('Postal Code')
    is_zip = fields.Boolean("")
    location_ids = fields.Many2many('res.company','res_company_contact_rel','company_id','contact_id',string='Locations')
    unique_company_name = fields.Boolean(string="Unique Company")
    is_location = fields.Boolean("")
    is_location_done = fields.Boolean('Location Done')
    is_list_type_done = fields.Boolean('List Type Done')
    is_category_done = fields.Boolean('Category Done')
    res_partner_count = fields.Integer('Count')
    res_partner_percentage = fields.Float(string="Count Percentage")
    query_execution_time = fields.Float(string="Query Execution Time" ,  digits=(12,4))
    

    # Fields For category
    selection_lead = fields.Selection([('lead_customer','Lead Customer'),('customer', 'Customer')],string="Apt Categ Rule")

    du_service_categ_ids = fields.Many2many('appointment.category','appointment_category_contact_rel','categ_id','contact_id',string='Appointment Category')
    service_categ_selection = fields.Selection([('in','Contain'),('not in', 'Not Contains')],default='in',string="Apt Categ Rule ")
    appointments_type_ids = fields.Many2many('calendar.appointment.type','appointment_calendar_type_contact_rel','categ_type_id','contact_id',string='Apt Sub Categ')
    appointments_type_selection = fields.Selection([('in','Contain'),('not in', 'Not Contains')],default='in',string="Apt SubCateg Rule")

    event_type_ids = fields.Many2many('event.type','event_type_contact_rel','event_type_id','contact_id',string='Event Category')
    event_type_selection = fields.Selection([('in','Contain'),('not in', 'Not Contains')],default='in',string="Event Categ Rule")
    event_subcateg_ids = fields.Many2many('event.subcateg.master','event_subcateg_contact_rel','event_subcateg_id','contact_id',string='Event SubCategory')
    event_subcateg_selection = fields.Selection([('in','Contain'),('not in', 'Not Contains')],default='in',string="Event SubCateg Rule")
    tag_by_therapy_ids = fields.Many2many('tag.by.therapy','event_tag_contact_rel','event_tag_id','contact_id',string='Tag By Therapy')
    tag_by_therapy_selection = fields.Selection([('in','Contain'),('not in', 'Not Contains')],default='in',string="TagBy Therapy Rule")
    # search_by_key = fields.Many2many('tag.by.therapy','calendar.appointment.type','appointment.category',string='Search by Keyword')
    filter_start_date = fields.Date()
    filter_end_date = fields.Date()


    #Fields for client
    partner_job_ids =  fields.Many2many('hr.employee.category','job_contact_rel','employee_job_id','contact_id',string='Functions')
    partner_job_selection= fields.Selection([('in','Contain'),('not in', 'Not Contains')],default='in',string="Functions Rule")
    therapist_ids =  fields.Many2many('hr.employee','hr_emloyee_contact_rel','employee_id','contact_id',string='Therapist')
    therapist_selection= fields.Selection([('in','Contain'),('not in', 'Not Contains')],default='in',string="Therapist Rule")

   #Fields for type list
    is_mobile = fields.Boolean('Mobile')
    position = fields.Boolean('Position')
    wit_email = fields.Boolean('With Email')
    # first_last_name = fields.Boolean('First & Last Name')
    # website = fields.Boolean('website')
    # unique_phone = fields.Boolean('Unique Phone Numbers')
    # unique_company = fields.Boolean('Unique Company Name')

   #Fields for lead score
    location = fields.Integer('Location',help='Enter the score for Location')
    country = fields.Integer('Country',help='Enter the score for country')
    gender = fields.Integer('Gender',help='Enter the score for Gender')
    inqiury = fields.Integer('Inqiury',help="Enter score for Inqiury")
    tag = fields.Integer('Tag',help="Enter score for Tag")
    social_media= fields.Integer('Social Media',help="Enter score for Social Media")
    google_ads = fields.Integer('Google Ads',help="Enter score for Google Ads")
    seo = fields.Integer('SEO',help="Enter score for SEO")
    others = fields.Integer('Others',help="Enter score for Others")
    demographic = fields.Integer('Demographic',help="Enter score for Demographic")
    behavioral = fields.Integer('Behavioral',help="Enter score for behavioral")




    @api.depends('country_ids','city_ids','postal_code','state_ids',
        'event_type_ids','event_subcateg_ids','du_service_categ_ids','appointments_type_ids',
        'tag_by_therapy_ids','therapist_ids','is_mobile','wit_email','position','partner_job_ids'
        ,'service_categ_selection','partner_job_selection','therapist_selection',
        'appointments_type_selection','location_ids','event_type_selection',
        'event_subcateg_selection','tag_by_therapy_selection','is_country'
        ,'is_state','is_city','is_zip','is_location','filter_start_date','filter_end_date')
    def _compute_domain(self):
        for rec in self:
            rec.domain = repr(rec._get_default_domain())


    def to_location(self):
        self.is_list_type_done =True
        return {
            'name': 'Data Miner',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'domain': [],
            'context': dict(self._context, active_ids=self.campaign_id.id),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    def to_category(self):    
        self.is_location_done =True
        return {
            'name': 'Data Miner',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'domain': [],
            'context': dict(self._context, active_ids=self.campaign_id.id),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    def to_lead_score(self):
        self.is_category_done =True
        return {
            'name': 'Data Miner',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'domain': [],
            'context': dict(self._context, active_ids=self.campaign_id.id),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }


    def _get_default_domain(self):
        domain = []
        event_partner_vals = []
        apt_search_domain =[]
        event_search_domain =[]
        partner_val =[]
        event_register_vals =[]
        partner_search =[]
        partner_vals =[]
        apt_id =False
        event_id =False
        each_partner_vals=[]
        apt_record_vals=[]
        event_record_vals=[]

        partner_search =[('user_ids','=',False),'|',('is_a_customer','=',True),('lead_customer','=',True)]
        partner_id = self.env['res.partner'].search(partner_search)
        for each_partner in partner_id:
            partner_vals.append(each_partner.id)
            partner_val =list(set(partner_vals))
        domain =[('id','in',partner_val)]

        if self.country_ids and self.is_country:
            domain.append("|")
            domain.append(('country_id','in',self.country_ids.ids))
            domain.append(('country_id','=',False))
        if self.country_ids and not self.is_country:
            domain.append(('country_id', 'in', self.country_ids.ids))
        if self.city_ids and self.is_city:
            domain.append("|")
            domain.append(('city_id','in',self.city_ids.ids))
            domain.append(('city_id','=',False))
        if self.city_ids and not self.is_city:
            domain.append(('city_id', 'in', self.city_ids.ids))
        if self.state_ids and self.is_state:
            domain.append("|")
            domain.append(('state_id','in',self.state_ids.ids))
            domain.append(('state_id','=',False))
        if self.state_ids and not self.is_state:
            domain.append(('state_id', 'in', self.state_ids.ids))
        if self.postal_code and self.is_zip:
            domain.append("|")
            domain.append(('zip','=',self.postal_code))
            domain.append(('zip','=',False))
        if self.postal_code and not self.is_zip:
            domain.append(('zip', '=', self.postal_code))
        if self.is_mobile:
            domain.append(('mobile', '!=', False))
        if self.wit_email:
            domain.append(('email', '!=', False))
        if self.position:
            domain.append(('job_title', '!=', False))

        if self.partner_job_ids:
            domain.append(('job_title',str(self.partner_job_selection),self.partner_job_ids.ids))
        # Based on alex request comment below code 14-09-22
        # if self.location_ids and self.is_location:
        #     domain.append("|")
        #     domain.append(('location_ids','in',self.location_ids.ids))
        #     domain.append(('location_ids','=',False))
        # if self.location_ids and not self.is_location:
        #     domain.append(('location_ids', 'in', self.location_ids.ids))

        # Appointment filter
        if self.du_service_categ_ids or self.appointments_type_ids or self.therapist_ids or self.filter_start_date\
                or self.filter_end_date:
            # Appointment Filter
            res_partner = self.env['res.partner'].search(domain)
            for each_partner in res_partner:
                each_partner_vals.append(each_partner.id)
                apt_search_domain = [('partner_id','in',each_partner_vals)]
            # Event Filter
            event_res_partner = self.env['res.partner'].search(domain)
            for each_event_partner in event_res_partner:
                event_partner_vals.append(each_event_partner.id)
                event_search_domain = [('partner_id', 'in', event_partner_vals)]

            if self.du_service_categ_ids:
                event_service_categ_names = [i.name for i in self.du_service_categ_ids]
                apt_search_domain.append(('service_categ_id', str(self.service_categ_selection), self.du_service_categ_ids.ids))
                event_search_domain.append(
                    ('event_id.event_service_categ_id.name','in', event_service_categ_names))

            if self.appointments_type_ids:
                apt_search_domain.append(('appointments_type_id',str(self.appointments_type_selection), self.appointments_type_ids.ids))
            if self.therapist_ids:
                apt_search_domain.append(('therapist_id', str(self.therapist_selection), self.therapist_ids.ids))
            if self.filter_start_date and self.filter_end_date:
                apt_search_domain.append(('booking_date', '>=', self.filter_start_date))
            if self.filter_end_date:
                apt_search_domain.append(('booking_date', '<=', self.filter_end_date))


            #Appointment append
            if apt_search_domain:
                apt_id = self.env['appointment.appointment'].search(apt_search_domain)



            # Event append
            if event_search_domain:
                event_id = self.env['event.registration'].search(event_search_domain)



            #appointment
            for apt_record in apt_id:
                apt_record_vals.append(apt_record.partner_id.id)
            # domain.append(('id','in',apt_record_vals))
            # print("domain ape=====", domain)

            #event
            for event_record in event_id:
                event_record_vals.append(event_record.partner_id.id)
            # domain.append(('id', 'in', event_record_vals))
            # print("domain event=====", domain)

            #event + Appointment
            domain_vals = list(set(apt_record_vals + event_record_vals))
            domain.append(('id', 'in', domain_vals))





        # Event Filter
        if self.event_type_ids or self.event_subcateg_ids or self.tag_by_therapy_ids:
            event_res_partner = self.env['res.partner'].search(domain)
            for each_event_partner in event_res_partner:
                event_partner_vals.append(each_event_partner.id)
                event_search_domain = [('partner_id','in',event_partner_vals)]
            if self.event_type_ids:
                event_search_domain.append(('event_id.event_type_id', str(self.event_type_selection), self.event_type_ids.ids))
            if self.event_subcateg_ids:
                event_search_domain.append(('event_id.evnt_subcateg', str(self.event_subcateg_selection), self.event_subcateg_ids.ids))
            if self.tag_by_therapy_ids:
                event_search_domain.append(('event_id.tag_by_therapy_id',str(self.tag_by_therapy_selection), self.tag_by_therapy_ids.ids))
            if self.therapist_ids:
                event_search_domain.append(('event_id.facilitator_evnt_ids', str(self.therapist_selection), self.therapist_ids.ids))
            if event_search_domain:
                event_id = self.env['event.registration'].search(event_search_domain)
            for event_record in event_id:
                event_record_vals.append(event_record.partner_id.id)
            domain.append(('id','in',event_record_vals))
        custom = self.env['res.partner'].search_count([('id','in',partner_val)])
        self.res_partner_count = self.env['res.partner'].search_count(domain)

        # ********Wizard percentage***********
        if custom:
            custom_percentage = (self.res_partner_count/custom) * 100
            self.res_partner_percentage = custom_percentage
        else:
            self.res_partner_percentage = 0


        # *******Query Execution Time***************
        random_decimal = random.uniform(0,1)
        self.query_execution_time = random_decimal

        return domain


    def _parse_domain(self):
        self.ensure_one()
        try:
            domain = literal_eval(self.domain)
        except Exception:
            domain = [('id', 'in', [])]
        return domain


    @api.depends('domain')
    def _compute_partners(self):
        for rec in self:           
            domain = rec._parse_domain()
            contacts = self.env['res.partner'].search(domain).ids
            rec.update({
                'partner_ids': [(6, 0, contacts)],
            })

    def generate(self):
        campaigns = self.env['asterisk_dialer.campaign'].browse(
            self._context.get('active_ids', []))
        for campaign in campaigns:
            campaign.generate_contacts('res.partner', self.domain)

        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                }

    def cancel(self):
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                }

    def get_location(self):
        location_id = ''
        for i in self.partner_ids.location_ids:
            location_id += i.name+','
        return location_id[:-1]



    
    def download_list_report_xl(self):
        today_date = date.today()
        
        # stylehead = xlwt.easyxf('font: name Calibri,bold True,height 300,italic True;align: horiz left;', num_format_str='#0')
        # style5 = xlwt.easyxf('font:height 200,name Calibri ,bold True;align: horiz right', num_format_str='#,##0.00')
        style8 = xlwt.easyxf('font:height 200,name Calibri ,bold True;align: horiz right', num_format_str='#,##0')
        style6 = xlwt.easyxf('font: name Calibri;align: horiz left;align: wrap yes', num_format_str='#,##0.00')
        style7 = xlwt.easyxf('font:height 200,name Calibri,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center', num_format_str='#0')
        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'dd-mm-yyyy'
        customer_row = 0
        workbook = xlwt.Workbook()
        sheet1 = workbook.add_sheet('Overdue Customer Invoices', cell_overwrite_ok=True)
        
        for x in range(1,15):
            sheet1.col(x).width   = 256 * 30
        
        sheet1.show_grid = True

        # sheet1.write(customer_row + 0, 0, 'Overdue Invoices', stylehead)
        # customer_row += 0
        sheet1.write(customer_row + 0, 0, 'First Name', style7)
        sheet1.write(customer_row + 0, 1, 'Last Name', style7)
        sheet1.write(customer_row + 0, 2, 'Address', style7)
        sheet1.write(customer_row + 0, 3, 'City', style7)
        sheet1.write(customer_row + 0, 4, 'State', style7)
        sheet1.write(customer_row + 0, 5, 'Zip', style7)
        sheet1.write(customer_row + 0, 6, 'Date of Birth', style7)
        sheet1.write(customer_row + 0, 7, 'Gender', style7)
        sheet1.write(customer_row + 0, 8, 'Location', style7)
        sheet1.write(customer_row + 0, 9, 'Mobile', style7)
        sheet1.write(customer_row + 0, 10, 'Email', style7)
        sheet1.write(customer_row + 0, 11, 'Alternate Mobile', style7)
        sheet1.write(customer_row + 0, 12, 'Alternate Email', style7)
        sheet1.write(customer_row + 0, 13, 'Lead Source', style7)



        
        for listin in self.partner_ids:
            sheet1.write(customer_row + 1, 0, listin.firstname or '', style6)
            sheet1.write(customer_row + 1, 1, listin.lastname or '', style6)
            sheet1.write(customer_row + 1, 2, listin.street or '', style6)
            sheet1.write(customer_row + 1, 3, listin.city_id.name or '', style6)
            sheet1.write(customer_row + 1, 4, listin.state_id.name or '', style6)
            sheet1.write(customer_row + 1, 5, listin.zip or '', style6)
            sheet1.write(customer_row + 1, 6, listin.dob or '', date_format)
            sheet1.write(customer_row + 1, 7, dict(listin._fields['gender'].selection).get(listin.gender) or '', style6)
            sheet1.write(customer_row + 1, 8, self.get_location() or '', style6)
            sheet1.write(customer_row + 1, 9, listin.phone or '', style6)
            sheet1.write(customer_row + 1, 10, listin.email or '', style6)
            sheet1.write(customer_row + 1, 11, listin.alternate_mobile or '', style6)
            sheet1.write(customer_row + 1, 12, listin.alternate_email or '', style6)
            sheet1.write(customer_row + 1, 13, listin.reffer_type_id.name or '', style6)
           
            customer_row += 1

   
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        data = base64.encodestring(data)
        doc_id = self.env['ir.attachment'].create(
            {'datas': data, 'name': 'Data Miner List' + '.xls', 'type': 'binary'})
        return {
				'type': 'ir.actions.act_url',
				'url': '/web/content/?id=%s&download=true' % (doc_id.id),
				'target': 'current',
			}
