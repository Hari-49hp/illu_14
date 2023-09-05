# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    working_hours_start = fields.Char(string='Working Hours ',help="8am - 6pm Daily")
    display_name = fields.Char(string="Display Name",help="JLT,Dubai")
    press_media_attachment = fields.Binary(string="Attachment")
    parking_guidelines = fields.Html(string="Parking Details")
    terms_condition = fields.Html(string="Terms & Condition")
    privacy_policy = fields.Html(string="Privacy Policy")
    website_show_location = fields.Boolean(string="Website Show Location")
    mobile = fields.Char(string='Mobile',help="Mobile Number/ Whatsapp Number")

    

class ResPartner(models.Model):
    _inherit = "res.partner"

    blog_quote = fields.Char('Blog Quote',help='Blog Quote to display in Website')
    tag_ids = fields.Many2many('blog.tag', string='Blog Tags')
    is_columnists = fields.Boolean("Is Columnists",help="Enable to view Blog Details")
    is_employee = fields.Boolean("Is Employee",help="Enable if contact created from user",default=False)
    hr_id = fields.Many2one('hr.employee',' Employee ',readonly=True)
