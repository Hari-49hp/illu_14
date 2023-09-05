from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import time

class TagByTherapy(models.Model):
    _inherit = 'tag.by.therapy'

    service_categ_ids = fields.Many2many('appointment.category', 'tag_by_therapy_service_categ_ids', string='Service Category')
    service_sub_categ_ids = fields.Many2many('appointment.sub.category', 'tag_by_therapy_service_sub_categ_ids', string='Service Sub Category')
