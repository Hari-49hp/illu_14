# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


TESTIMONIAL_PRIORITY = [
    ('0', 'Very Low'),
    ('1', 'Low'),
    ('2', 'Medium'),
    ('3', 'Better'),
    ('4', 'Good'),
    ('5', 'Best'),
]


class ImLivechatChannel(models.Model):

    _inherit = 'im_livechat.channel'
    
    
    def _get_livechat_mail_channel_vals(self, anonymous_name, operator, user_id=None, country_id=None):
        # partner to add to the mail.channel
        operator_partner_id = operator.partner_id.id
        channel_partner_to_add = [(4, operator_partner_id)]
        visitor_user = False
        if user_id:
            visitor_user = self.env['res.users'].browse(user_id)
            if visitor_user and visitor_user.active:  # valid session user (not public)
                channel_partner_to_add.append((4, visitor_user.partner_id.id))
                
        user_name = [visitor_user.display_name if visitor_user else anonymous_name, operator.livechat_username if operator.livechat_username else operator.name]
        
        if user_name:
            user_name = ' '.join([visitor_user.display_name if visitor_user else anonymous_name, operator.livechat_username if operator.livechat_username else operator.name])
        else:
            user_name = ''
        
            
        return {
            'channel_partner_ids': channel_partner_to_add,
            'livechat_active': True,
            'livechat_operator_id': operator_partner_id,
            'livechat_channel_id': self.id,
            'anonymous_name': False if user_id else anonymous_name,
            'country_id': country_id,
            'channel_type': 'livechat',
            'name': user_name,
            'public': 'private',
            'email_send': False,
        }
        

class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    mega_menu_type = fields.Selection([('event','Event'),('healing','Healing'),('therapy','Therapy'),('about','About')],string='Mega Menu Type')


class Testimonial(models.Model):
    _name = 'testimonial'
    _description = 'Testimonial'

    image_av = fields.Binary('Image')
    video_1920 = fields.Binary('Video')
    video_url = fields.Char('Video URL', help='Accepts url or embed Youtube, Vimeo, Dailymotion and Youku videos')
    name = fields.Char(string='Title')
    description = fields.Text(string='Description')
    website_publish = fields.Boolean(string='Publish', help='Website Publish')
    feature_in_homepage = fields.Boolean(string='Feature', help='Feature in Homepage')
    in_training_individual_page = fields.Boolean(string='Traning Individual', help='View testimonial In Traning Individual Website Page ')
    in_retreats_page = fields.Boolean(string='In Retreats Page', help='View testimonial In Retreats Website Page ')

    priority = fields.Selection(TESTIMONIAL_PRIORITY, string='Priority', default='0')   
    partner_id = fields.Many2one('res.partner', string='Customer')
    service_type = fields.Many2one('appointment.category', string='Service Type')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    employee_type = fields.Many2many('hr.employee.category', string='Employee Type')
    tags_ids = fields.Many2many('testimonial.tags', string='Tags')

    def get_image(self):
        return '/web/image?model=testimonial&id=%s&field=image_av' % (self.id)

class TestimonialTags(models.Model):
    _name = 'testimonial.tags'
    _description = 'Testimonial Tags'
    _order = 'sequence'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Tag')
    website_publish = fields.Boolean('Publish')

class HrJobs(models.Model):
    _inherit = 'hr.job'

    job_type = fields.Selection([('fulltime','FullTime'),('parttime','PartTime')], string='Job Type', default='fulltime')
    website_publish = fields.Boolean('Website Publish')
    image_av = fields.Binary('Image')
    responsibilities = fields.One2many('hr.job.responsibilities', 'job_id', string='Responsibilities')
    qualifications = fields.One2many('hr.job.qualifications', 'job_id', string='Qualifications')
    is_therapist = fields.Boolean('Is Therapist',help="Check The employee Therapist or Not")

    @api.onchange('company_id')
    def _onchange_company_id1(self):
        self.address_id = self.company_id.partner_id.id

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    website_publish = fields.Boolean('Website Publish')
    career_type = fields.Selection([('management', 'Management'), ('therapist', 'Therapist')],
                                    required=True, default='management')

class HrJobResponsibilities(models.Model):
    _name = 'hr.job.responsibilities'
    _description = 'Responsibilities'

    name = fields.Char('Responsibilities')
    job_id = fields.Many2one('hr.job', string=' Job ')

class HrJobQualifications(models.Model):
    _name = 'hr.job.qualifications'
    _description = 'Qualifications'

    name = fields.Char('Qualifications')
    job_id = fields.Many2one('hr.job', string='Job ')


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    designation = fields.Char('Designation')
    work_experience = fields.Char('Relevant Work Experience')
    notice_period = fields.Char('Notice Period')
    # resume = fields.Many2many('ir.attachment', string='Resume')

    healer = fields.Char(string='Healers Name')
    dob = fields.Char(string='Date of Birth')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender', help='Gender')
    facilitator = fields.Selection([('local', 'Local'), ('guest', ' Guest/Visiting')], string='Facilitator', help='Facilitator')
    country_id = fields.Many2one('res.country', string='Nationality')
    url = fields.Char(string='URL')
    city_id = fields.Many2one('res.country.state', string='City')
    relocate = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Willing To Relocate ', help='willing to relocate ')
    type = fields.Selection([('type_online', 'Online'),('type_onsite', 'Onsite'),
                             ('type_hybrid', 'Hybrid')], string='Type', help='Type specify Online/ Offline/ Hybrid')
    others = fields.Text(string="Others")

    approaches_ids = fields.One2many('approaches.applicant', 'applicant_id', string="Approaches")
    question_answer_ids = fields.One2many('question.answer.applicant', 'applicant_id', string="Question & Answer")

    def unlink(self):
        for i in self.approaches_ids:
            i.unlink()
        for each in self.question_answer_ids:
            each.unlink()
        return super(HrApplicant, self).unlink()


class ApproachesApplicant(models.Model):
    _name = 'approaches.applicant'
    _description ="ApproachesApplicant"

    applicant_id = fields.Many2one('hr.applicant', string="Approaches", required=True)
    service_category_id = fields.Many2one('appointment.category', string="Service Category", required=True)
    sub_category_id = fields.Many2many('calendar.appointment.type', string="Sub Category", required=True)


class QuestionAnswerApplicant(models.Model):
    _name = 'question.answer.applicant'
    _description = "Question Answer Applicant"

    applicant_id = fields.Many2one('hr.applicant', string="Approaches", required=True)
    question_id = fields.Many2one('initial.application.question', string="Question", required=True)
    answer_id = fields.Many2many('initial.application.answer', string="Answer", required=True)

class ResCompany(models.Model):
    _inherit = 'res.company'

    def get_company_address(self):
        address = ''
        address += self.street+',' if self.street else ''
        address += self.street2+',' if self.street2 else ''
        address += self.city+',' if self.city else ''
        address += self.state_id.name+',' if self.state_id else ''
        address += self.zip+',' if self.zip else ''
        address += self.country_id.name+',' if self.country_id else ''
        return address

class BlogPost(models.Model):
    _inherit = 'blog.post'

    image_av = fields.Binary('Image') 
    feature_post = fields.Boolean(string='Feature Post In Homepage', help='Feature post in Homepage')


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    lang_ids = fields.Many2many('res.lang', string='Languages Known')
    is_student = fields.Boolean(string="Student")
    certification_ids = fields.One2many('certification', 'employee_id', string="Certification")

    def get_language_website(self):
        lang = ''
        for i in self.lang_ids:
            lang += i.name+','
        return lang[:-1]

    def get_job_position_website(self):
        position = ''
        for i in self.employee_type:
            position += i.name+','
        return position[:-1]

    def get_by_support_website(self):
        support = ''
        for i in self.by_support:
            support += i.name+','
        return support[:-1]

    def get_name_with_s(self):
        return self.name+"'s"


class HrCertification(models.Model):
    _name = "hr.certification"
    _description = "Certification"

    name = fields.Char(string="Name", required=True)


class Certification(models.Model):
    _name = "certification"
    _description = "Certification"

    employee_id = fields.Many2one('hr.employee', string="Employee")
    certificate_id = fields.Many2one('hr.certification', string="Name of Certificate", required=True)
    event_id = fields.Many2one('event.event', string="Event")


class MailingList(models.Model):
    _inherit = 'mailing.list'

    is_newsletter = fields.Boolean('Is a Newsletter')


class EventEvent(models.Model):
    _inherit = 'event.event'

    def get_facilitator_name(self):
        return self.facilitator_evnt_ids[0].name

    def get_event_price(self):
        return self.event_ticket_ids[0].full_price if len(self.event_ticket_ids.ids) > 0 else 0.0

    def get_start_end_time(self):
        d1_hr = str(self.hour_time_begin) if self.hour_time_begin else '00'
        d1_min = str(self.min_time_begin) if self.min_time_begin else '00'
        d2_hr = str(self.hour_time_end) if self.hour_time_end else '00'
        d2_min = str(self.min_time_end) if self.min_time_end else '00'
        data = d1_hr + ':' + d1_min + ' To ' + d2_hr + ':' + d2_min
        return str(data)
    
    def create_event_SO_from_Website(self, data={}):
        
        partner_id = type_partner = email = phone = name = city_id  = country_id = receiver_id = ''; type_booking = 'type_self';
        partner_vals = {}; receiver_vals = {}
        
        
        
        if data.get('receiver_email',False) or data.get('receiver_mobile',False):
        
            if data.get('receiver_email',False):
                receiver_id = self.env['res.partner'].sudo().search([('email', '=', data.get('receiver_email',False))], limit=1)
        
            elif data.get('receiver_mobile',False):
                receiver_id = self.env['res.partner'].sudo().search([('phone', '=', data.get('receiver_mobile',False))], limit=1)
        
            receiver_vals.update({
                'mobile': data.get('receiver_mobile',False),
                'email':  data.get('receiver_email',False),
                'name': data.get('receiver_name',False),
                })
        if not receiver_id and (data.get('receiver_email',False) or data.get('receiver_mobile',False)):
        
            receiver_id = self.env['res.partner'].sudo().create(receiver_vals)
            
        if receiver_id:
            type_booking = 'type_gift'
        
        if data.get('email',False) or data.get('phone',False):
        
            if data.get('email',False):
                partner_id = self.env['res.partner'].sudo().search([('email', '=', data.get('email',False))], limit=1)
                if partner_id:
                    type_partner = "type_existing"
        
            elif data.get('phone',False):
                partner_id = self.env['res.partner'].sudo().search([('phone', '=', data.get('phone',False))], limit=1)
                if partner_id:
                    type_partner = "type_existing"
        
        partner_vals.update({
            'mobile': data.get('phone',False),
            'email':  data.get('email',False),
            'name': data.get('customer_name',False),
            'city_id':  data.get('city_id',False),
            'country_id': data.get('country_id',False),
            'country_id': data.get('country_id',False),
            'street':data.get('street',False),
            })
        
        if not partner_id:
        
            type_partner = "type_new"
            
            lead_source_id = self.env['master.refferal'].sudo().search([('name', '=', 'Website')], limit=1)
            
            if not lead_source_id:
                lead_source_id = self.env['master.refferal'].sudo().create({'name':'Website'})
            
            if lead_source_id:
                partner_vals.update({'reffer_type_id':lead_source_id.id})
            
        
            partner_id = self.env['res.partner'].sudo().create(partner_vals)
        else:
            try:
                partner_id.write(partner_vals)
            except Exception as e:
                partner_vals = {}
                partner_vals.update({
                    'city_id': data.get('city_id',False),
                    'country_id':data.get('country_id',False),
                    'street':data.get('street',False),
                    })
                partner_id.write(partner_vals)
                
        lst = []
        registration_ids = self.env['event.registration']
        for ticket_id in self.event_ticket_ids:
            ticket_vals = {}
            len = int(data.get('ticket_id_'+str(ticket_id.id), 0))
            
            ticket_vals = {
                'type_partner':type_partner,
                'name':partner_id.name,
                'extras_partner_id':partner_id.id,
                'email':partner_id.email,
                'mobile':partner_id.mobile,
                'partner_id':partner_id.id,
                'country_id':data.get('country_id',False),
                'event_id': self.id,
                'event_ticket_id': ticket_id.id,
                'booking_mode':'online',
                'gift_name_partner_id': receiver_id and receiver_id.id or False,
                'gift_email': data.get('receiver_email',False),
                'gift_mobile': data.get('receiver_mobile',False),
                'type_booking': type_booking,
                }
            
            for i in range(0, len):
                registration_ids = registration_ids + self.env['event.registration'].sudo().create(ticket_vals)
                # call the event ticket price on change method 13-07-22
                registration_ids._onchange_event_ticket_id()
                # call the mail send function 13-07-22
                if registration_ids:
                    registration_ids.action_send_event_reg()
                
                lst.append([0, 0, {
                                'product_id': ticket_id.product_id.id,
                                'name': ticket_id.product_id.name + '('+ self.event_seq + ')',
                                'product_uom_qty': 1,
                                'product_uom': ticket_id.product_id.uom_id.id,
                                'price_unit': ticket_id.full_price,
                                'web_event':self.name
                            }])
                
        if lst:
            sale_id = self.env['sale.order'].sudo().create({
                        'partner_id': partner_id.id,
                        'customer_id':partner_id.id,
                        'partner_inv_id':partner_id.id,
                        'partner_ship_id':partner_id.id,
                        'pricelist_id': partner_id.property_product_pricelist.id,
                        'company_id': self.company_id.id,
                        'order_line': lst,
                        'web_event_id':self.id,
                        'descriptions':self.name,
                        'type':'event'
                    })
            sale_id.action_confirm()
            registration_ids.write({"sale_order_id": sale_id.id})
            
            return sale_id.id


class InitialApplicationQuestion(models.Model):
    _name = 'initial.application.question'
    _description = 'Initial Application Question'

    name = fields.Char(string="Question", required=True)
    options = fields.One2many('initial.application.answer', 'parent_id', string='Options')

    def unlink(self):
        for each in self:
            for i in each.options:
                i.unlink()
        return super(InitialApplicationQuestion, self).unlink()


class InitialApplicationAnswer(models.Model):
    _name = 'initial.application.answer'
    _rec_name = 'name'
    _description = 'Initial Application Answer'

    parent_id = fields.Many2one('initial.application.question', string="Question", required=True)
    name = fields.Char(string="Answer", required=True)


class EventEvent(models.Model):
    _inherit = 'event.event'
    
    certification_ids = fields.One2many('certification', 'event_id', string="Certification")
    retreat_activity_ids = fields.Many2many('retreat.activity', string="Retreat Activity")
    is_retreat = fields.Boolean(related="event_service_categ_id.is_retreats")
    retreat_activity_desc = fields.Html('Activity Description')
    retreat_locations_ids = fields.Many2many('retreat.locations', string="Retreat Locations")
    retreat_location_desc = fields.Html('Location Description')
    retreat_tips_ids = fields.Many2many('retreat.tips', string="Retreat Tips")
    retreat_tips_desc = fields.Html('Tips Description')
    retreat_accomadatiens_desc = fields.Html('Accommodation Description')
    retreat_accomadatiens_image = fields.Many2many('ir.attachment', string='Accommodation Image')

    about_desc = fields.Html('About Facilitator')
    employe_quote = fields.Html('Quotes')
    certification = fields.Html('Certifications')
    qualification = fields.Html('Qualifications')
    prerequisite_note = fields.Html('Prerequisite Note')
    prerequisite_client_types = fields.Many2many('event.class.level',string='Prerequisite Client Types',domain=[('is_prerequisite','=',True)])
    auto_assigned_client_types = fields.Many2one('event.class.level',string="Auto Assigned Client Types",domain=[('is_prerequisite','=',True)])
    minimum_age = fields.Integer(string="Minimum Age")
    maximum_age = fields.Integer(string="Maximum Age")

    def get_event_dates(self):
        if self.event_multiple_date == 'oneday':
            return self.s_start_date.strftime("%d %B")
        if self.event_multiple_date == 'multiday':
            start = self.env['multi.date.line'].sudo().browse(self.multi_date_line_ids.ids[0])
            end = self.env['multi.date.line'].sudo().browse(self.multi_date_line_ids.ids[-1])
            return start.date_begin.strftime("%d %B")+ ' To ' + end.date_begin.strftime("%d %B")


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    country_id = fields.Many2one('res.country', string="Country",compute='_compute_country_id',store=True,readonly=False,tracking=14)
    city_id = fields.Many2one('city.master', string="City",compute='_compute_city_id',store=True,readonly=False,tracking=15)
    website_payment_status = fields.Selection([('no_paid','Not Paid'),('partially_paid','Partially Paid'),('payment_received','Paid'),('paid','Paid')],default='no_paid')
    booking_mode = fields.Selection([('online', 'Website'),('direct', 'Backend')],
                                    string='Booking Method',default='direct')
    
    @api.depends('partner_id')
    def _compute_country_id(self):
        for registration in self:
            registration.country_id =False
            if not registration.country_id and registration.partner_id:
                registration.country_id = registration._synchronize_partner_values(
                    registration.partner_id,
                    fnames=['country_id']
                ).get('country_id') or False


    @api.depends('partner_id')
    def _compute_city_id(self):
        for registration in self:
            registration.city_id=False
            if not registration.city_id and registration.partner_id:
                registration.city_id = registration._synchronize_partner_values(
                    registration.partner_id,
                    fnames=['city_id']
                ).get('city_id') or False

    def _compute_payment_from_payment(self):
        
        response = super(EventRegistration, self)._compute_payment_from_payment()
        
        for rec in self:
            if rec.sale_order_id and rec.booking_mode == "online":
                if rec.website_payment_status == "paid" or rec.pos_order_id.state in ('paid','done','invoiced'):
                    rec.event_payment_status = 'paid'
                else:
                    rec.event_payment_status = 'no_paid'

            if rec.event_payment_status == 'paid' and rec.booking_mode == "online":
                get_source_id = self.env['utm.source'].sudo().search([('name','ilike','Website')],limit=1)
                get_lead_id = self.env['crm.lead'].sudo().search([('event_reg_id','=',rec.id),('source_id','=',get_source_id.id)])
                if get_lead_id:
                    crm_stage = self.env['crm.stage'].search([('is_won','=',True)],limit=1)
                    get_lead_id.stage_id = crm_stage 
    
class EventType(models.Model):
    _inherit = 'event.type'

    description = fields.Text("Description")

class RetreatLocations(models.Model):
    _name = 'retreat.locations'
    _rec_name = 'name'
    _description = 'Retreat Locations'

    name = fields.Char(string="Activity", required=True)
    image_1920 = fields.Binary(string="Image", required=True)
    event_id = fields.Many2one('event.event',string='Event')
    
class RetreatActivity(models.Model):
    _name = 'retreat.activity'
    _rec_name = 'name'
    _description = 'Retreat Activity'

    name = fields.Char(string="Activity", required=True)
    image_1920 = fields.Binary(string="Image", required=True)
    event_id = fields.Many2one('event.event',string='Event')

class RetreatTips(models.Model):
    _name = 'retreat.tips'
    _rec_name = 'name'
    _description = 'Retreat Tips'

    name = fields.Char(string="Activity", required=True)
    event_id = fields.Many2one('event.event',string='Event')
