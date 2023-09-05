from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = 'project.task'

    responsible_id = fields.Many2one('res.users','Responsible')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

class EventStage(models.Model):
    _inherit = 'event.stage'

    is_published = fields.Boolean('Is Published')
    is_waiting = fields.Boolean('Is Waiting')
    is_reject = fields.Boolean(string="Is Reject",help="Help to reject the Event.")

class Event(models.Model):
    _inherit = 'event.event'

    create_checklist_active = fields.Boolean('Checklist Active')
    project_id = fields.Many2one('project.task',string="Checklist Project")
    project_d_id = fields.Many2one('project.project',string="Project",store=True)
    is_published_event = fields.Boolean(related='stage_id.is_published', string='Is Published Event', readonly=False)
    is_waiting = fields.Boolean(related='stage_id.is_waiting', string='Is Waiting', readonly=False)

    def checklist(self):
        action = self.env.ref('ppts_custom_checklist.check_list_action').read()[0]
        action['context'] = {
            'default_event_id': self.id,
            'default_event_dt_time': self.date_begin,
            'default_event_category_id': self.event_type_id.id,
        }
        action['domain'] = [('event_id', '=', self.id)]
        checklist = self.env['check.list'].search([('event_id', '=', self.id)])
        if len(checklist) == 1:
            action['views'] = [(self.env.ref('ppts_custom_checklist.check_list_from_view').id, 'form')]
            action['res_id'] = checklist.id
        return action

    def project_task(self):
        project = self.env['project.project'].search([('id', '=', self.project_d_id.id)])
        if self.project_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Project',
                'view_mode': 'kanban',
                'res_model': 'project.project',
                # 'res_id': self.project_id.id,
                'domain': [('id', '=', project.id)],
                }

    def create_task(self):
        checklist = self.env['check.list'].search([('event_id', '=', self.id)])
        self.create_checklist_active = True
        if checklist:
            project = self.env['project.project'].search([('event_id', '=', self.id)])
            if not project:
                pro_vals = {
                'name':self.name,
                'event_id':self.id
                }
                project = self.env['project.project'].create(pro_vals)
                self.project_d_id = project.id
                project_stage = self.env['project.task.type'].search([('event_stage','=',True)])
                if project_stage and project:
                    for pro_stg in project_stage:
                        pro_stg.write({'project_ids': [(4, project.id)]})
            if project:
                for c_list in checklist:
                    for lines in c_list.checklist_line_id:
                        task = self.env['project.task'].search([('checklist_line_id','=',lines.id)])
                        if not task:
                            vals = {
                                'name':lines.checklist_master_id.name,
                                'user_id':lines.checklist_master_id.responsible.id,
                                'checklist_line_id':lines.id,
                                'project_id':project.id,
                                'date_deadline':lines.end_date,
                                'start_date':lines.start_date,
                                'end_date':lines.end_date,
                                'stage_id':1
                            }
                            self.project_id = self.env['project.task'].create(vals)
