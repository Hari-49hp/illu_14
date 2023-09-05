from odoo import api, fields, models, _
from datetime import datetime

class ChecklistCategory(models.Model):
    _name = 'checklist.category'
    _description = 'Checklist Category'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    name = fields.Char('Name',required=True)
    code = fields.Char('Code')
    notes = fields.Text('Notes')

class ChecklistSubCategory(models.Model):
    _name = 'checklist.sub.category'
    _description = 'Checklist Sub Category'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    name = fields.Char('Name',required=True)
    code = fields.Char('Code')
    category_id = fields.Many2one('checklist.category',required=True)
    notes = fields.Text('Notes')

class ChecklistMaster(models.Model):
    _name = 'checklist.master'
    _description = 'Checklist Master'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    name = fields.Char('Name',required=True,help='Name of Checklist Master')
    checklist_type = fields.Selection([('application', 'Application'), ('event', 'Event')],string='Type',help='Type of Checklist')
    category_id = fields.Many2one('checklist.category',required=True,string='Category',help='Main Category of Checklist')
    responsible = fields.Many2one('res.users',domain="[('share', '=', False)]",string='Responsible',help='Responsible person of the checklist')
    description = fields.Text(string='Description',required=True,help='Internal Description')
    attachment = fields.Binary('Attachment',help='Attach supporting documents related to Checklist.')
    filename = fields.Char(string="File Name",help='File Name')

class CheckList(models.Model):
    _name = 'check.list'
    _rec_name = 'event_id'
    _description = 'Checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    event_id = fields.Many2one('event.event',string='Event Name',required=True,help='Name of the Event')
    event_dt_time = fields.Datetime('Event Date & Time',related='event_id.date_begin',readonly=True,help='Event Starting Time')
    event_categ_id = fields.Many2one('event.type',string='Event Category', related = 'event_id.event_type_id',help='Main Category of Event')
    event_sub_categ_ids =fields.Many2one('event.subcateg.master',string='Event Sub Category', related = 'event_id.evnt_subcateg',help='Sub Category of Event')
    event_sub_categ_id = fields.Many2one('calendar.appointment.type','Sub Category',copy=False, related = 'event_id.event_sub_categ_id',tracking=True,help='Event Sub Category')
    checklist_date = fields.Datetime('Checklist Date', default=datetime.today(),required=True,help='Date of Checklist Creation')
    # eve_therapist_id Many2one is not used

    facilitator_id = fields.Many2one('res.partner',string="Facilitator",required=True,related = 'event_id.organizer_id',help='')

    therapist_ids = fields.Many2many('hr.employee', string='Facilitator', related='event_id.facilitator_evnt_ids',
                                     tracking=True,help='Facilitator of Event')
    responsible_id = fields.Many2one('res.users','Responsible',required=True,related = 'event_id.user_id',help='Responsible Person of the Checklist')
    event_mode = fields.Boolean('Online Event',readonly=True,help='Mode of Event Checklist')
    checklist_line_id = fields.One2many('check.list.line','check_list_id')

    def write(self, values):
        ct = 0
        if 'checklist_line_id' in values:
            msg = '<ul class="o_Message_trackingValues">'
            for i in self.checklist_line_id:
                if values['checklist_line_id'][ct][2] and 'status' in values['checklist_line_id'][ct][2]:
                    status_id = self.env['project.task.type'].search([('id','=',values['checklist_line_id'][ct][2]['status'])])
                    msg += _(
                        '<li><div class="o_Message_trackingValue"><div class="o_Message_trackingValueFieldName o_Message_trackingValueItem"> <b>%(name)s</b> (State):</div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(old_status)s</div> <div title="Changed" role="img" class="o_Message_trackingValueSeparator o_Message_trackingValueItem fa fa-long-arrow-right"></div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(new_status)s</div></div></li>',
                        old_status=i.status.name,
                        new_status=status_id.name,
                        name= i.checklist_master_id.name,
                    )

                if values['checklist_line_id'][ct][2] and 'start_date' in values['checklist_line_id'][ct][2]:
                    msg += _(
                        '<li><div class="o_Message_trackingValue"><div class="o_Message_trackingValueFieldName o_Message_trackingValueItem"> <b>%(name)s</b> (Start Date):</div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(old_status)s</div> <div title="Changed" role="img" class="o_Message_trackingValueSeparator o_Message_trackingValueItem fa fa-long-arrow-right"></div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(new_status)s</div></div></li>',
                        old_status=i.start_date,
                        new_status=values['checklist_line_id'][ct][2]['start_date'],
                        name= i.checklist_master_id.name,
                    )

                if values['checklist_line_id'][ct][2] and 'end_date' in values['checklist_line_id'][ct][2]:
                    msg += _(
                        '<li><div class="o_Message_trackingValue"><div class="o_Message_trackingValueFieldName o_Message_trackingValueItem"> <b>%(name)s</b> (End Date):</div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(old_status)s</div> <div title="Changed" role="img" class="o_Message_trackingValueSeparator o_Message_trackingValueItem fa fa-long-arrow-right"></div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(new_status)s</div></div></li>',
                        old_status=i.end_date,
                        new_status=values['checklist_line_id'][ct][2]['end_date'],
                        name= i.checklist_master_id.name,
                    )

                if values['checklist_line_id'][ct][2] and 'checklist_responsible' in values['checklist_line_id'][ct][2]:
                    checklist_responsible_id = self.env['res.users'].search([('id','=',values['checklist_line_id'][ct][2]['checklist_responsible'])])
                    msg += _(
                        '<li><div class="o_Message_trackingValue"><div class="o_Message_trackingValueFieldName o_Message_trackingValueItem"> <b>%(name)s</b> (Checklist Responsible):</div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(old_status)s</div> <div title="Changed" role="img" class="o_Message_trackingValueSeparator o_Message_trackingValueItem fa fa-long-arrow-right"></div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%(new_status)s</div></div></li>',
                        old_status=i.checklist_responsible.name,
                        new_status=checklist_responsible_id.name,
                        name= i.checklist_master_id.name,
                    )

                ct += 1
            msg += '</ul>'

            self.message_post(body=msg)

        result = super(CheckList, self).write(values)
        return result

    def update_checklist(self):
        ProjectTask = self.env['project.task']
        for i in self.checklist_line_id:
            project_task = ProjectTask.search([('checklist_line_id', '=', i.id)])
            if project_task:
                project_task.update({
                    'stage_id':i.status.id,
                    'date_deadline':i.end_date,
                    'start_date':i.start_date,
                    'end_date':i.end_date,
                    'responsible_id':i.checklist_responsible.id,
                    })
            else:
                ProjectTask.create({
                    'name':i.checklist_master_id.name,
                    'stage_id':i.status.id,
                    'responsible_id':i.checklist_responsible.id,
                    'date_deadline':i.end_date,
                    'start_date':i.start_date,
                    'end_date':i.end_date,
                    'project_id':self.event_id.project_d_id.id,
                    'checklist_line_id':i.id,
                    })

    def add_checklists(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'checklist.wizard',
            'views': [(False, 'form')],
            'view_id': 'view_checklist_wizard_form',
            'target': 'new',
        }

    @api.onchange('event_id')
    def onchange_event_id(self):
        if self.event_id:
            self.event_dt_time = self.event_id.date_begin
            
class CheckListLine(models.Model):
    _name = 'check.list.line'
    _description = 'Checklist Line'

    checklist_master_id = fields.Many2one('checklist.master',string='Checklist Name',required=True)
    checklist_description = fields.Text('Description',required=True)
    checklist_category_id = fields.Many2one('checklist.category',required=True,string='Checklist Category')
    checklist_responsible = fields.Many2one('res.users',string='Responsible (Checklist)')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    status = fields.Many2one('project.task.type','State',store='True')
    check_list_id = fields.Many2one('check.list')
    project_task_id = fields.Many2one('project.task',string="Project Task")

    @api.onchange('checklist_master_id')
    def compute_checklist_date(self):
        self.start_date=self.check_list_id.event_id.date_begin
        self.end_date=self.check_list_id.event_id.date_end


    @api.onchange('checklist_master_id')
    def onchange_checklist_master(self):
        if self.checklist_master_id:
            self.checklist_description = self.checklist_master_id.description
            self.checklist_category_id = self.checklist_master_id.category_id.id
            self.checklist_responsible = self.checklist_master_id.responsible.id

