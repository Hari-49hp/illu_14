from odoo import api, fields, models, _

class RoomTypeMST(models.Model):
    _name = 'roomtype.master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Room Type Master'
    _rec_name = 'room_type'

    room_type = fields.Char('Room',tracking=True)
    type_code = fields.Char(string='Code',tracking=True)
    room_maincateg_id = fields.Many2one('room.maincateg.master', string='Room Category',required=True,tracking=True)
    company_id = fields.Many2one('res.company','Company',change_default=True,default=lambda self: self.env.company)
    room_notes = fields.Text(string='Internal Note',tracking=True)

class RoomMainCateg(models.Model):
    _name = 'room.maincateg.master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Room Categ'
    _rec_name = 'room_maincateg'

    room_maincateg = fields.Char(string='Name',tracking=True)
    roomcateg_code = fields.Char(string='Code',tracking=True)
    roomcateg_notes = fields.Text(string='Internal Note',tracking=True)
