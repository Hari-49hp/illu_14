import logging
from odoo import models, fields, api, tools, release, _
from odoo.exceptions import ValidationError, UserError

logger = logging.getLogger(__name__)

# added below variable for selection fields 09-08-22

CAMPAIGN_TYPES = [
    ('operators', 'Datamined'),
    ('new_upload','New Upload'),
    ('operators_and_upload','Datamined & New Upload'),
    ('voice_message', 'Voice Message')
]


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    campaign_lead_id = fields.Many2one('asterisk_dialer.campaign',index=True,string='Lead campaign')
    campaign_oppor_id = fields.Many2one('asterisk_dialer.campaign',index=True,string='Opportunity campaign')
    campaign_type_id = fields.Many2one('campaign.type',string="Type ",help="Select tye of the campaign",default=lambda self: self.env['campaign.type'].search([('code','=','Gen')]).id)
    campaign_type = fields.Selection(
        CAMPAIGN_TYPES,
        default='operators'
    )
    is_register = fields.Boolean(related='stage_id.is_register', string='Is Register', readonly=False)
    type_partner = fields.Selection([('type_existing', 'Existing'), ('type_new', 'New')], string='Type of Customer?',
                                    default='type_existing', required=True)
    free_register = fields.Boolean(string='Free Register',copy=False)
    paid_register = fields.Boolean(string='Paid Register',copy=False)
    stage_status = fields.Boolean(string='Stage Status',copy=False)

    call_history_line_ids = fields.One2many('call.history','call_history_id',string="History of Calls")
    lead_id = fields.Integer(string="Lead")
    appointment_id = fields.Many2one('appointment.appointment',string="Appointment")
    event_reg_id = fields.Many2one('event.registration',string="Event Registration")

    #Fields for lead score
    # location = fields.Integer('Location',help='Enter the score for Location')
    # country = fields.Integer('Country',help='Enter the score for country')
    # gender = fields.Integer('Gender',help='Enter the score for Gender')
    # source = fields.Integer('Source',help="Enter score for Source")
    # medium = fields.Integer('Medium',help="Enter score for Medium")
    
    # def update_partner_in_opportunity(self)
    #     for each_records in self:

    def action_partner_appts(self):
        if self.partner_id:
            self.partner_id.populate_visit_values()
            return {
                    'type': 'ir.actions.act_window',
                    'name': 'Contact',
                    'view_mode': 'form',
                    'res_model': 'res.partner',
                    'view_id': False,
                    'views': [(self.env.ref('custom_partner.res_partner_history_history_from_view').id, 'form')],
                    'res_id': self.partner_id.id,
                    }
        
    def lead_to_oppor(self):
        action = 'exist'
        lead_val = self.env['crm.lead'].search(
                        [('contact_name', '=',self.contact_name),
                         ('mobile', '=', self.mobile),('email_from','=',self.email_from),('type','=','lead')])
        if lead_val:
            vals = {'partner_id': self._origin.partner_id.id or False,
                    'name': "merge",
                    'lead_id':self._origin.id,
                    'user_id': self._origin.user_id.id,
                    'team_id':self._origin.team_id.id or False,
                    'action' : action,
                    'duplicated_lead_ids':[(6, 0, [self._origin.id,lead_val.id])]
                    }
            wiz_lead_opportunity = self.env['crm.lead2opportunity.partner'].with_context(active_ids=self._origin.id).create(vals)
            if wiz_lead_opportunity:
                wiz_lead_opportunity.action_apply()
            state_id = self.env['crm.stage'].search([('create_contact','=',True)])
            self._origin.stage_id = state_id.id

    def action_register(self):
        # if self.stage_id.create_contact and self.stage_id.is_register:
        #     self.free_register = True
        # if self.stage_id.is_register and not self.stage_id.create_contact:
        #     self.paid_register = False
        # if self.stage_status:
        #     self.stage_status = False


        view = self.env.ref('event.view_event_registration_form')
        return {
            'name': _('Attendees'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'event.registration',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {
                        'default_event_id': self.campaign_lead_id.event_id.id or False, 
                        'default_partner_id':self.partner_id.id or False,
                        'default_sales_person':self.user_id.id or False,
                        'default_utm_campaign_id':self.campaign_id.id or False,
                        'default_utm_source_id':self.source_id.id or False,
                        'default_utm_medium_id':self.medium_id.id or False,
                        'default_crm_id':self.id or False,

                            },
        }


    def action_appointment_register(self):
        if self.stage_id.create_contact and self.stage_id.is_register:
            self.free_register = True
        if self.stage_id.is_register and not self.stage_id.create_contact:
            self.paid_register = False
        if self.stage_status:
            self.stage_status = False

        view = self.env.ref('ppts_custom_apt_mgmt.appointments_appointments_single_from_view')
        return {
            'name': _('Appointments'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'appointment.appointment',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {
                        'default_partner_id':self.partner_id.id or False,
                        'default_crm_id':self.id or False,
                            },
        }

    @api.onchange('stage_id')
    def onchange_stage(self):
        partner_id =False
        if self.stage_id.name == "Book for Free Consultation" or self.stage_id.name == "Book for Paid Session":
            self.stage_status = True 
        else:
            self.stage_status = False 
        for each in self:
            if each.partner_id.lead_customer == True and each.stage_id.create_contact == True:
                each.partner_id.lead_customer =False
                each.partner_id.is_a_customer =True
            # if each.first_name and each.last_name and not each.partner_id and each.stage_id.create_contact == True:
            #     name = each.first_name + each.last_name
            #     vals = {
            #     'name': name or "",
            #     'firstname':each.first_name,
            #     'secondname':each.second_name,
            #     'street': each.street,
            #     'street2':each.street2 or "",
            #     'city':each.city,
            #     'state_id':each.state_id.id or False,
            #     'country_id':each.country_id.id or False,
            #     'zip':each.zip,
            #     'mobile':each.mobile,
            #     'phone':each.phone,
            #     'email':each.email,
            #     'customer_rank':1,
            #     'company_type':'company',
            #     'alternate_mobile':False,
            #     'alternate_email':False,
            #     'type':'contact'
            #     }
            #     partner_id = self.env['res.partner'].create(vals)
            #     each.partner_id = partner_id.id
            #     oppor_id = self.env['crm.lead'].search(
            #         [('contact_name', '=',name),
            #          ('mobile', '=', self.mobile),('email_from','=',self.email_from),('type','=','opportunity')])
            #     if oppor_id:
            #         for each_oppr in oppor_id:
            #             each_oppr.partner_id = partner_id.id
            #     lead_id = self.env['crm.lead'].search(
            #         [('contact_name', '=',name),
            #          ('mobile', '=', self.mobile),('email_from','=',self.email_from),('type','=','lead')])
            #     if lead_id:
            #         for each_lead in lead_id:
            #             each_lead.partner_id = partner_id.id
            # self.lead_to_oppor()
            
    # def action_appointment(self):
    #     return {
    #             'type': 'ir.actions.act_window',
    #             'name': 'Appointment',
    #             'view_mode': 'form',
    #             'res_model': 'appointment.appointment',
    #             'target': 'new',
    #         }
            
    # def action_event(self):
    #     return {
    #             'type': 'ir.actions.act_window',
    #             'name': 'Event Registration',
    #             'view_mode': 'form',
    #             'res_model': 'event.registration',
    #             'target': 'new'
    #         }


class CallHistory(models.Model):
    _name = "call.history"

    remarks = fields.Html(string="Notes",tracking=True)
    call_date = fields.Datetime(string="Date",tracking=True)
    user_id = fields.Many2one('res.users',string="User",tracking=True)
    call_history_id = fields.Many2one('crm.lead')
    quick_remark = fields.Char(string="Quick Remarks")



class CrmStage(models.Model):
    _inherit = 'crm.stage'

    create_contact = fields.Boolean('Create Contact',help='Enable boolean to create a contact and count of free booking')
    paid_booking = fields.Boolean('Paid Booking',help="Enable to get count for paid booking stage")
    # campaign_type_ids = fields.Many2many('campaign.type',string='Campaign Type')
    is_register = fields.Boolean('Is Register',help='Enable boolean is the stage is for register')
    quick_remarks_id = fields.Many2one('appointment.quick.remark',string='Quick Remarks',tracking=True)




