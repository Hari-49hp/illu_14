import base64
from email.policy import default

import requests 

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from dateutil import rrule
import re
import pytz
import babel.dates
from odoo import tools
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from odoo.tools.misc import get_lang

from datetime import date, timedelta, datetime
from dateutil.relativedelta import *
import time
from odoo.addons.http_routing.models.ir_http import slug
from bs4 import BeautifulSoup


# Appointments & Booking
class HrEmployees(models.Model):
    _inherit = 'hr.employee'

    calendar_appointment_type_id = fields.Many2many('calendar.appointment.type',string='Aalendar Appointment Type')

class CustomCalAppointments(models.Model):
    _name = 'calendar.appointment.type'
    _inherit = ['calendar.appointment.type', 'website.published.mixin']


    assignation_method = fields.Selection([('random', 'Random'),('chosen', 'Chosen by the Customer')], string='Assignment Method', default='chosen' ,required=True, help="How employees will be assigned to meetings customers book on your website.")
    type_code = fields.Char(string='Sub Category Code')
    is_published = fields.Boolean('Is Published', copy=False)
    website_url = fields.Char('Website URL')
    training_website_url = fields.Char('Training Website URL')

    type_appointment = fields.Selection([('type_online', 'Online'),('type_onsite', 'Onsite')],string='Mode of Appointment?',default='type_onsite')
    domain_filter = fields.Char(string='Domain',help='domain for event/ Appointment',default=lambda self: self._get_default_domain(),store=True)
    service_categ_id = fields.Many2one('appointment.category', string='Service Category', copy=False,help='Under which service category does this service fall?')
    service_code = fields.Char(string='Service Code',related='service_categ_id.maincateg_code')
    appointment_categ_id = fields.Many2one('appointment.type.category', string='Appointment Category', copy=False,help='Under which service category does this service fall?')
    
    sub_categ_id = fields.Many2one('appointment.sub.category', string='Sub Category', copy=False)

    allow_online = fields.Boolean(string='Publish to Website', default=False,help='Allow Clients to book appointment type Online')
    show_additional = fields.Boolean(string='Additional Options', default=False,help='Show Additional Options')
    cpt_code = fields.Char(string='CPT Code')

    allow_addon = fields.Boolean(string='Add-On', default=False, help='Can be added to an existing appointment without Increasing its Length')
    early_cancel_charge = fields.Integer(string='Color',tracking=True)
    color_code = fields.Integer(string='Color', default=1,tracking=True)
    capacity = fields.Integer(string='Capacity', default=1)
    deducted = fields.Integer(string='# Deducted', default=1)
    sort_order = fields.Integer(string='Sort Order')
    product_id = fields.Many2one('product.product', string='Related Product', copy=False)
    company_id = fields.Many2many('res.company', string='Branch',default=lambda self: self.env.company, copy=False)
    comp_id = fields.Many2one('res.company', string='Branch',index=True, default=lambda self: self.env.company)
    company_currency_id = fields.Many2one('res.currency', related="comp_id.currency_id")

    apt_price_list_ids=fields.One2many('price.list.line','appointment_id',string='Price List Lines')
    time_id = fields.Many2one('time.time',string="Appointment Duration")

    #other duration are not used anymore
    duration_ids = fields.Many2many('time.time',string="Appointment Duration")
    revenue_category_id = fields.Many2one('appointment.revenue',string="Revenue Category")
    product_price = fields.Float('Related Product Price')

    interval_number = fields.Integer('Expiry on',default=1)
    interval_range = fields.Selection([('months','Month'),('day','Day')],string="range",default="months")

    cancel_interval_number = fields.Integer('Early Cancel',default=1)
    cancel_interval_range = fields.Selection([('hour','Hour'),('day','Day')],string="range",default="day")
    cancel_interval_price = fields.Float('Early Price', default="150")
    website_publish = fields.Boolean(string='Publish In MegaMenu', help='Website Publish')
    feature_in_homepage = fields.Boolean(string='Feature', help='Feature in Homepage')
    tag_ids = fields.Many2many('tag.by.therapy', string='Tags')
    image = fields.Binary('Image')
    description = fields.Html(string='Description')
    certifications = fields.Html(string="Certification")
    about_training = fields.Html(string="About")
    qualifications = fields.Html(string="Qualifications")
    healing_content_ids = fields.One2many('calendar.appointment.type.content', 'apt_type_id', string='Content')
    duration_price_ids = fields.One2many('duration.price','apt_type_id',string='Duration Price')
    is_training = fields.Boolean(string='Is Traning', related='service_categ_id.is_training' , help='Is Traning')
    is_corporate = fields.Boolean(string='Is Corporate', related='service_categ_id.is_corporate' , help='Is Corporate')
    is_retreats = fields.Boolean(string='Is Retreats', related='service_categ_id.is_retreats' , help='Is Retreats')
    feature_in_header = fields.Boolean(string='Feature In Header' , help='In header this survice will be featured and the users can direct place appointment from there')
    category_type = fields.Selection(string='Type', related="service_categ_id.category_type")
    therapy_did_you_know = fields.Html('Did You Know?!')
    therapy_learn_more = fields.Html('Learn More')
    therapy_full_description_list = fields.Html('List Description')
    is_appointment = fields.Boolean(string='Is Appointment', help='Is Appointment')
    is_event = fields.Boolean(string='Is Event', help='Is Event')
    training_line_id = fields.One2many('traning.level.line', 'service_sub_categ_id', string="Traning Line")
    training_question_line_id = fields.One2many('training.question', 'service_sub_categ_id', string="Traning Question")
    short_description = fields.Text(string="Featured Event Description",help="Display in header")


 
    @api.constrains('description')
    def _check_len_html(self):
        soup = BeautifulSoup(self.description)
        description = soup.get_text()
        if len(description)>1000:
            raise ValidationError("Description is too long, max of 1000 characters only allowed")

    # Validation for description
    @api.constrains('short_description')
    def _check_desc_len_html(self):
        soup = BeautifulSoup(self.short_description)
        short_description = soup.get_text()
        if len(short_description)>150:
            raise ValidationError("Featured Event Description is too long, max of 150 characters only allowed")


    @api.onchange('domain_filter','is_event','is_appointment','name','service_categ_id')
    def _onchange_channel_type(self):
        domain =[]
        if self.env.context.get('default_is_appointment', False):
            domain = [('is_appointment','=', True)]
        if self.env.context.get('default_is_event', False):
            domain = [('is_event', '=', True)]
        return {'domain': {'service_categ_id': domain}}



    def _get_default_domain(self):
        domain = []
        if self.env.context.get('default_is_appointment', False):
            domain = [('is_appointment','=', True)]
        if self.env.context.get('default_is_event', False):
            domain = [('is_event', '=', True)]
        return domain



    def _default_therapy_healing_therapy_header(self):
        return """ 
            <div class=" col-xs-6 col-lg-6 col-md-6 col-sm-12 col-xs-12 ">
                <p style=" max-width: 600px;margin: 0 !important; " class=" desc mt-3 mb-4 "> Our qualified relationship
                therapists, guide you to make the necessary mental, emotional and behavioral changes to take
                charge of your relationship issues. </p>
                </div>
                <div class=" col-xs-6 col-lg-6 col-md-6 col-sm-12 col-xs-12 ">
                    <h4 class=" bigpragraph ">Relationship Healing &amp; Therapy Solutions focuses on counseling for the
                following individuals:</h4>
                    <div>
                        <ul class=" awardlists listwithdots font16 ">
                            <li>
                        Couples in Crisis: People looking to manage and bring alive their current relationship.
                            </li>
                            <li>
                        People who have decided to end a relationship.
                            </li>
                            <li>
                        People who are struggling to find a potential suitable partner.
                            </li>
                        </ul>
                    </div>
			</div>
        """

    def _default_therapy_healing_therapy_learn_more(self):
        return """ 
            <div class=" card-body " style="background-color: #ffff !important;">
                <div class=" certification-section ">
                    <div class=" row " style="background-color: #ffff;">
                        <div class=" col-xl-6 col-lg-6 col-md-6 col-sm-12 col-xs-12 ">
                            <ul class=" normalblt-list ">
                                <li> Identify &amp; Release Subconscious Belief Systems </li>
                                <li> Identifying &amp; Releasing Limiting &amp; Toxic Emotions: anger, hurt,
                            fear of loneliness, guilt and rejection. </li>
                                <li> Reprogramming thought &amp; Behavior Patterns &amp; Positive Based
                            Suggestion Work </li>
                                <li> Age Regression &amp; Inner Child Integration. </li>
                                <li> Cognitive Coaching to Identify Goals &amp; Values. </li>
                                <li> *Optional: Spiritual Healing: Forgiveness, Understanding Karmic
                            Contracts, Cord Cutting) </li>
                                <li>
                            Energy Healing Energetic Processes to address &amp; Heal On the
                            Cellular Memory, Soul &amp; Metaphysical (Karmic Contracts,
                            Forgiveness &amp; Energy Exchange, Cord Cutting &amp; Past Life)
                                </li>
                            </ul>
                        </div>
                        <div class=" col-xl-6 col-lg-6 col-md-6 col-sm-12 col-xs-12 ">
                            <div>
                                <h4>Approaches Include:</h4>
                                <p>
                            Hypnosis &amp; Hypnotherapy, NLP, Cognitive Behavioral Therapy,
                            Emotional Intelligence, Life Coaching, Energy Healing &amp;
                            Cleansing, Spiritual Healing, Psychotherapy &amp; Counseling.
                                </p>
                                <p> Clients Would Require 3 – 5 Sessions To Resolve The Above Issue.
                            Clients Can Avail Single Sessions Or Avail The Benefits Of Our
                            Discount Packages!</p>
                                <p> Discounts Include: Package Of 3 (5% Discount) Package Of 5 (10%
                            Discount) Package Of 10 (15% Discount) </p>
                            </div>
                            <div class=" mt-4 ">
                                <h4>Our Packages Include:</h4>
                                <div>
                                    <ul class=" normalblt-list ">
                                        <li>
                                    1 Free 30 Minute Consultation
                                        </li>
                                        <li>
                                    Treatment Packages of 3, 5 or 10 sessions recommended by
                                    the practitioner with special discounts and offers
                                        </li>
                                        <li>
                                    MP3 Audio or Hand Outs offering tools and techniques for
                                    daily practice and lifestyle changes
                                        </li>
                                    </ul>
                                    <span class=" disclaim ">**Disclaimer: The mentioned above
                                benefits are based on each individual’s experience and
                                results vary for every individual.</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        """

    therapy_healing_therapy_header = fields.Html('Header', default=_default_therapy_healing_therapy_header) 
    therapy_healing_therapy_learn_more = fields.Html('Footer', default=_default_therapy_healing_therapy_learn_more) 


    @api.depends('name')
    def _compute_website_url(self):
        for event in self:
            event.website_url= ""
            event.training_website_url=" "
            if event.id:  # avoid to perform a slug on a not yet saved record in case of an onchange.
                if event.service_categ_id and event.service_categ_id.category_type == 'healing': event.website_url = '/healing/%s/register' % slug(event)
                elif event.service_categ_id and event.service_categ_id.category_type == 'therapy': event.website_url = '/therapy/%s/register' % slug(event)
                if event.is_training: 
                    event.training_website_url = '/training/%s/individual/page' % slug(event)

    @api.onchange('time_id')
    def _onchange_time_id(self):
        if self.time_id:
            time_val = str(timedelta(minutes=int(self.time_id.duration)))[:-3]
            time_val = time_val.replace(':','.')
            self.write({'appointment_duration':float(time_val)})
        else:
            self.write({'appointment_duration':0})

    @api.model
    def create(self, vals):
        program = super(CustomCalAppointments, self).create(vals)
        pr_categ_id = self.env['product.category'].search([('name', '=', program.service_categ_id.name)], limit=1)

        if not pr_categ_id:
            pr_categ_id = self.env['product.category'].search([('name', '=', 'Appointment')], limit=1)

        product_id = self.env['product.product'].create({
            'name': program.name,
            'categ_id': pr_categ_id.id,
            'appointment_id': program.id,
            'type': 'service',
            'invoice_policy': 'order',
            'supplier_taxes_id': False,
            'sale_ok': True,
            'purchase_ok': False,
            'list_price': 0.0,
            'product_used': 'appointments',
            'company_id': False,
            'available_in_pos' : True,
            'is_commission_product' : True
        })
        program.product_id = product_id

        self.env['price.list.line'].create({
            'appointment_id': program.id,
            'product_id': product_id.id,
            'unit_price': program.product_price,
            })

        program.product_id.write({'list_price':program.product_price,
            'lst_price':program.product_price,
            'revenue_category_id': program.revenue_category_id.id
            })

        for i in program.apt_staff_list_ids:
            i.employee_id.write({
                'calendar_appointment_type_id':[(4,program.id)],
                })

        product_id.write({
            'duration_ids': [(6, 0, program.duration_price_ids.ids)],
            })

        return program

    def write(self, vals):
        res = super(CustomCalAppointments, self).write(vals)
        self.product_id.write({'list_price':self.product_price,
            'lst_price':self.product_price,
            'revenue_category_id': self.revenue_category_id.id
            })
        
        return res


class TraningLevelLine(models.Model):
    _name = 'traning.level.line'
    _description = 'Traning Level Line'
    _rec_name = 'name'

    name = fields.Char('Level Name')
    notes = fields.Html('Internal Note')
    sequence = fields.Integer(string='Sequence', default=1)
    service_sub_categ_id = fields.Many2one('calendar.appointment.type','Service Sub Category')



class ApptTypePriceList(models.Model):
    _name = 'price.list.line'
    _description = 'Price List Line'

    appointment_id=fields.Many2one('calendar.appointment.type',string="Assign Staff")
    product_id = fields.Many2one('product.product',string='Name')
    price_list_id = fields.Char(string='Price List')
    unit_price = fields.Float(string='Price', copy=False)

    @api.onchange('product_id')
    def _onchange_unit_price(self):
        self.write({'unit_price':self.product_id.list_price})


class EmployeeCommission(models.Model):
    _name = 'employee.commission'
    _description = 'Employee Commission'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee',string='Therapist')
    sale_id = fields.Many2one('pos.order', string='Sale Ref')
    appointment_id = fields.Many2one('appointment.appointment',string='Appointment')
    commission = fields.Float('Commission')


class CalendarAppointmentTypeContent(models.Model):
    _name = 'calendar.appointment.type.content'
    _description = 'Calendar Appointment Type Content'

    apt_type_id = fields.Many2one('calendar.appointment.type', string='Sub Category')
    healing_id = fields.Many2one('healing.question', string='Healing Question', required=True)
    html = fields.Html(string="Content", required=True)

    @api.onchange('healing_id')
    def _onchange_healing_id(self):
        self.html = self.healing_id.html


class HealingQuestion(models.Model):
    _name = 'healing.question'
    _description = 'Healing Question'

    name = fields.Char(string="Name", required=True)
    html = fields.Html(string="Content", required=True)


class TrainingQuestion(models.Model):
    _name = 'training.question'
    _description = 'Training Question'

    name = fields.Char(string="Name", required=True)
    html = fields.Html(string="Content", required=True)
    service_sub_categ_id = fields.Many2one('calendar.appointment.type','Service Sub Category')
