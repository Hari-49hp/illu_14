# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FeedbackCategory(models.Model):
    _name = 'feedback.category'
    _description = 'feedback category'


    name = fields.Char(string='Name')
    code = fields.Text(string='Code')
    website_publish = fields.Boolean(string='Publish', help='Website Publish')

class FeaturedIn(models.Model):
    _name = 'featured.in'
    _description = 'FeaturedIn'


    name = fields.Char(string='Name')
    code = fields.Text(string='Code')
    featured_image = fields.Binary('Image')
    website_publish = fields.Boolean(string='Publish', help='Website Publish')

    def get_featured_image(self):

        return '/web/image?model=featured.in&id=%s&field=featured_image' % (self.id)


class OurTraining(models.Model):
    _name = 'our.training'
    _description = 'OurTraining'


    name = fields.Char(string='Name')
    code = fields.Text(string='Code')
    image = fields.Binary('Image')
    website_publish = fields.Boolean(string='Publish', help='Website Publish')        