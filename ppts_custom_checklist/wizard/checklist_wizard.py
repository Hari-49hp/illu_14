from odoo import fields, models,api,_

class ChecklistWizard(models.Model):
    _name = "checklist.wizard"
    _description ="ChecklistWizard"

    checklist_ids = fields.Many2many('checklist.master', string="checklist")

    def submit_checklist(self):
        print (self.env.context.get('active_id'))
        if self.env.context.get('active_id'):
            checklist_id = self.env['check.list'].browse(self.env.context.get('active_id'))
            for lst_ids in self.checklist_ids:
                vals={
                    'checklist_master_id':lst_ids.id,
                    'checklist_description':lst_ids.description,
                    'checklist_category_id':lst_ids.category_id.id,
                    'checklist_responsible':lst_ids.responsible.id,
                    'check_list_id':checklist_id.id}
                checklist_id.checklist_line_id.create(vals)
        return True
