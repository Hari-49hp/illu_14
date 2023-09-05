from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime


class BySupport(models.Model):
    _name = 'by.support'
    _description = 'By Support'

    name = fields.Char('Name')

class BySolution(models.Model):
    _name = 'by.solution'
    _description = 'By Solution'

    name = fields.Char('Name')