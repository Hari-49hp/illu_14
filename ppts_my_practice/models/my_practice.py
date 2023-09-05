from odoo import api, fields, models, _
from datetime import date, timedelta, datetime

class MyPractice(models.Model):
    _name = 'my.practice'
    _description ="MyPractice"

    name = fields.Char('Name')
