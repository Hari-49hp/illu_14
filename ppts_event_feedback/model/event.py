from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Survey(models.Model):
    _inherit = "survey.survey"

    event_id = fields.Many2one('event.event',string="Event",tracking=True,help='Name of Event.')
    event_active = fields.Boolean('Event Survey',tracking=True,help='Set this Survey Used for Events.')
    is_template = fields.Boolean('Is Survey Template',tracking=True,help='Set this Survey is Template.')

    @api.onchange("event_id")
    def _onchange_event_id(self):
        if self.event_id:self.title = self.event_id.name+ ' ('+str(self.event_id.date_begin)+\
        ' - '+str(self.event_id.date_end)+') '

    @api.model
    def create(self, vals):
        res = super(Survey, self).create(vals)
        if res.event_id:
            query ="UPDATE event_event SET survey_id = "+str(res.id)+" WHERE id="+str(res.event_id.id)+";"
            self.env.cr.execute(query) 
        return res

    def write(self, vals):
        res = super(Survey, self).write(vals)
        if self.event_id:
            query ="UPDATE event_event SET survey_id = "+str(self.id)+" WHERE id="+str(self.event_id.id)+";"
            self.env.cr.execute(query) 
        return res

class Event(models.Model):
    _inherit = "event.event"
    
    survey_id=fields.Many2one('survey.survey',string="Survey",tracking=True)
    event_survey_id = fields.Many2one('survey.survey', string="Survey Template", tracking=True,
                                      help='Survey Template to be used for Events.')
    survery_count = fields.Integer(string='Survey Count', compute='_compute_survey_count',tracking=True)
    event_approver_id = fields.Many2one('res.users',string="Approver",tracking=True)
    reject_value = fields.Boolean(string="Reject")
    reject_reason_id = fields.Many2one('event.reject.master',string="Reject Reason" ,readonly=True)
    reject_desc = fields.Text(string="Reject Description",readonly=True)
    reject_id = fields.Many2one('res.users',string="Rejected By")
    reject_on = fields.Datetime(string="Rejected On")
    eve_approved_by = fields.Many2one('res.users',string="Approved By")
    eve_approved_on = fields.Datetime(string="Approved On")
    approve_value = fields.Boolean(string="Approved")
    
    def event_survey(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Survey',
                'view_mode': 'tree,form',
                'res_model': 'survey.survey',
                'res_id': self.survey_id.id,
                'domain': [('id','=',self.survey_id.id)],
                }

    def action_send_email(self):
        if self.survey_id.state == 'closed':
            raise UserError(_("You cannot send invitations for closed surveys."))
        if not self.survey_id:
            raise UserError(_("You cannot send invitations without survey attachment"))
        template = self.env.ref('survey.mail_template_user_input_invite', raise_if_not_found=False)
        participants=self.env['event.registration'].search([('event_id','=',self.id)])
        if not participants:
            raise UserError(_("No Participants to Send Email"))
        if template:
            for obj in participants:
                template.email_to = obj.email
                template.sudo().send_mail(self.survey_id.id, force_send=True)

    # use this function to set the domain for event field

    @api.onchange('event_service_categ_id','event_approver_id')
    def _set_user_group_domain(self):
        group_manager = self.env.ref('ppts_custom_event_mgmt.group_manager')
        vals = []
        for user in group_manager.users:
            vals.append(user.id)

        return {'domain': {'event_approver_id': [('id', 'in', vals),('employee_id.company_id.id','=',self.company_id.id)]}}

        
    def _compute_survey_count(self):
        for rec in self:
            survey = self.env['survey.user_input'].search([('survey_id', '=', rec.survey_id.id)])
            if survey:
                rec.survery_count = len(survey)
            else:
                rec.survery_count=0
                
    def action_survey_response_list_view(self):
        survey_view = self.env.ref('ppts_event_feedback.survey_view_action').read()[0]
        if self.survey_id.id:
            survey = self.env['survey.user_input'].search([('survey_id', '=', self.survey_id.id)])
            if len(survey) > 1:
                survey_view['domain'] = [('id', 'in', survey.ids)]
            elif survey:
                survey_view['views'] = [(self.env.ref('survey.survey_user_input_view_form').id, 'form')]
                survey_view['res_id'] = survey.id
            return survey_view
        else:
            raise UserError(_("Please add Survey for this event"))

class EventClass(models.Model):
    _inherit = "event.class.master"

    event_survey_id=fields.Many2one('survey.survey',string="Survey Template",tracking=True,help='Survey Template to be used for Events.')
