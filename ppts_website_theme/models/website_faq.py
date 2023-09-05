# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class WebsiteFaq(models.Model):
    _name = 'website.faq'
    _description = 'Website FAQ'


    name = fields.Char(string='Title')
    description = fields.Html(string='Description')
    website_publish = fields.Boolean(string='Publish', help='Website Publish')
    feature_in_homepage = fields.Boolean(string='Feature', help='Feature in Homepage')
    feature_in_training = fields.Boolean(string='Traning Page', help='Feature in Training')


    partner_id = fields.Many2one('res.partner', string='Customer')
    service_type = fields.Many2one('appointment.category', string='Service Type')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    employee_type = fields.Many2many('hr.employee.category', string='Employee Type')
    faq_tag_ids = fields.Many2many('faq.tags',string="Tags")


class FaqTag(models.Model):
    _name = 'faq.tags'
    _description = 'Website Tags'
    _order = 'sequence'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Tag')
    website_publish = fields.Boolean('Publish')