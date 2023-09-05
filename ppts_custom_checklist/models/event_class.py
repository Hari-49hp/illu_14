from odoo import api, fields, models, _

class EventClassInherit(models.Model):
    _inherit = 'event.class.master'

    class_room_id = fields.Many2one('roomtype.master', string='Room')
    class_room_incharge_id = fields.Many2one('res.users', string='House Keeping',help='Name of House Keeping Person')
    reception_id = fields.Many2one('res.users', string='Receptionist',help='Name of the Recptionist')
    class_checklist_line_ids = fields.One2many('class.check.list.line','class_check_list_id')

    def class_add_checklists(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'class.checklist.wizard',
            'views': [(False, 'form')],
            'view_id': 'view_checklist_wizard_form',
            'target': 'new',
        }

class ClassCheckListLine(models.Model):
    _name = 'class.check.list.line'
    _description = 'Checklist Line'

    checklist_master_id = fields.Many2one('checklist.master',string='Checklist Name',required=True,help='Checklist Name')
    checklist_description = fields.Text('Description',required=True,help='Internal Description')
    checklist_category_id = fields.Many2one('checklist.category',required=True,string='Checklist Category',help='Category of Checklist')
    checklist_responsible = fields.Many2one('res.users',string='Responsible (Checklist)',required=True,help='Responsible Person of Checklist')
    class_check_list_id = fields.Many2one('event.class.master',help='Checklist Master')

    @api.onchange('checklist_master_id')
    def onchange_checklist_master(self):
        if self.checklist_master_id:
            self.checklist_description = self.checklist_master_id.description
            self.checklist_category_id = self.checklist_master_id.category_id.id
            self.checklist_responsible = self.checklist_master_id.responsible.id
