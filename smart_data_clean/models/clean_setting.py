# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.exceptions import Warning
_logger = logging.getLogger(__name__)

class CleanSetting(models.Model):
    _name = 'clean.setting'
    _description = 'Data Clean Setting'

    model_id = fields.Many2one('ir.model', 'Model ID')
    model = fields.Char('Model Name', related='model_id.model')
    name = fields.Char('Name')

    def apply_clean(self):
        model = str(self.model).replace('.','_')
        if model:
            records_id = self.env[self.model].search([])
            for i in records_id:
                query = """DELETE FROM """ + model + """ WHERE id = """ + str(i.id) +""";"""            
                self._cr.execute(query)

