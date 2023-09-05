from odoo import api, fields, models, _

class TagByHealing(models.Model):
    _name = 'tag.by.healing'
    _description = 'Tag By Healing'

    name = fields.Char('Name',required=True)

class TagBySubHealing(models.Model):
    _name = 'tag.by.sub.healing'
    _description = 'Tag By Sub Healing'

    name = fields.Char('Name',required=True)
    parent_id = fields.Many2one('tag.by.healing',string='Parent')

class TagByTherapy(models.Model):
    _name = 'tag.by.therapy'
    _description = 'Tag By Therapy'

    name = fields.Char('Name',required=True)
    parent_id = fields.Many2one('tag.by.healing',string='Parent')