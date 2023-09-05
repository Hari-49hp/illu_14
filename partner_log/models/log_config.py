# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, tools, _


class LogConfig(models.Model):
    _name = 'log.config'
    _description = 'Log Config'
    _rec_name = 'model_id'
    _sql_constraints = [
        ('model_uniq', 'unique(model_id)',
         'There is already a rule defined on this model and this group.\n'
         'You cannot define another: please edit the existing one.'),
    ]

    active = fields.Boolean(default=True)
    model_id = fields.Many2one('ir.model', 'Model', required=True, domain=[('model', '!=', 'log.config')], ondelete='cascade')
    model = fields.Char('Model', related='model_id.model')
    