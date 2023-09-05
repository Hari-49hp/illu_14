from odoo import api, fields, models, _

class ProjectTask(models.Model):
    _inherit = 'project.task'

    checklist_line_id = fields.Many2one('check.list.line')

    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)
        if res.checklist_line_id:
            check_line = self.env['check.list.line'].browse(res.checklist_line_id.id)
            if res.stage_id:
                check_line.status = res.stage_id.id
                check_line.project_task_id =res.id
        return res

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)

        if self.checklist_line_id:
            print(self.checklist_line_id.status.id,self.checklist_line_id.checklist_responsible.id,'before')
            print(vals,'after')
            setup = False
            msg = '<ul class="o_Message_trackingValues">'
            if not self.checklist_line_id.status.id == self.stage_id.id:
                if 'stage_id' in vals:
                    status_id = self.env['project.task.type'].search([('id','=',vals['stage_id'])])
                    msg += _(
                        '<li><div class="o_Message_trackingValue"><div class="o_Message_trackingValueFieldName o_Message_trackingValueItem"> <b>%(name)s</b> (State):</div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(old_status)s</div> <div title="Changed" role="img" class="o_Message_trackingValueSeparator o_Message_trackingValueItem fa fa-long-arrow-right"></div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(new_status)s</div></div></li>',
                        old_status=self.checklist_line_id.status.name,
                        new_status=status_id.name,
                        name= self.name,
                    )
                    self.checklist_line_id.status = self.stage_id.id
                    msg += '</ul>'
                    setup = True

            if not self.checklist_line_id.checklist_responsible.id == self.responsible_id.id:
                if 'responsible_id' in vals:
                    checklist_responsible_id = self.env['res.users'].search([('id','=',vals['responsible_id'])])
                    msg += _(
                        '<li><div class="o_Message_trackingValue"><div class="o_Message_trackingValueFieldName o_Message_trackingValueItem"> <b>%(name)s</b> (Responsible):</div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(old_status)s</div> <div title="Changed" role="img" class="o_Message_trackingValueSeparator o_Message_trackingValueItem fa fa-long-arrow-right"></div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(new_status)s</div></div></li>',
                        old_status=self.checklist_line_id.checklist_responsible.name,
                        new_status=checklist_responsible_id.name,
                        name= self.name,
                    )
                    self.checklist_line_id.checklist_responsible = self.responsible_id.id
                    msg += '</ul>'
                    setup = True

            if not self.checklist_line_id.start_date == self.start_date:
                if 'start_date' in vals:
                    msg += _(
                        '<li><div class="o_Message_trackingValue"><div class="o_Message_trackingValueFieldName o_Message_trackingValueItem"> <b>%(name)s</b> (Start Date):</div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(old_status)s</div> <div title="Changed" role="img" class="o_Message_trackingValueSeparator o_Message_trackingValueItem fa fa-long-arrow-right"></div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(new_status)s</div></div></li>',
                        old_status=self.checklist_line_id.start_date,
                        new_status=self.start_date,
                        name= self.name,
                    )
                    self.checklist_line_id.start_date = self.start_date
                    msg += '</ul>'
                    setup = True

            if not self.checklist_line_id.end_date == self.end_date:
                if 'end_date' in vals:
                    msg += _(
                        '<li><div class="o_Message_trackingValue"><div class="o_Message_trackingValueFieldName o_Message_trackingValueItem"> <b>%(name)s</b> (End Date):</div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(old_status)s</div> <div title="Changed" role="img" class="o_Message_trackingValueSeparator o_Message_trackingValueItem fa fa-long-arrow-right"></div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(new_status)s</div></div></li>',
                        old_status=self.checklist_line_id.end_date,
                        new_status=self.end_date,
                        name= self.name,
                    )
                    self.checklist_line_id.end_date = self.end_date
                    msg += '</ul>'
                    setup = True

            # checklist_id = self.env['check.list'].search([('event_id','=',self.checklist_line_id.event_id.id)],limit=1)
            if setup == True:self.checklist_line_id.check_list_id.message_post(body=msg)

        
        return res

class ProjectTProject(models.Model):
    _inherit = 'project.project'

    event_id = fields.Many2one('event.event')

class ProjectTTaskType(models.Model):
    _inherit = 'project.task.type'

    event_stage = fields.Boolean('Event State')