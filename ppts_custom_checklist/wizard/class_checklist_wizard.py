from odoo import fields, models,api,_

class ClassChecklistWizard(models.Model):
    _name = "class.checklist.wizard"
    _description ="ClassChecklistWizard"

    checklist_ids = fields.Many2many('checklist.master', string="checklist")

    def submit_class_checklist(self):
        if self.env.context.get('active_id'):
            checklist_id = self.env['event.class.master'].browse(self.env.context.get('active_id'))
            for lst_ids in self.checklist_ids:
                vals={
                    'checklist_master_id':lst_ids.id,
                    'checklist_description':lst_ids.description,
                    'checklist_category_id':lst_ids.category_id.id,
                    'checklist_responsible':lst_ids.responsible.id,
                    'class_check_list_id':checklist_id.id}
                checklist_id.class_checklist_line_ids.create(vals)
        return True