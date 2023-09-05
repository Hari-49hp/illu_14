from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
# from datetime import date

class CrmLead(models.Model):
    _inherit = 'crm.lead'
 
    @api.model
    def _default_about(self):
        return self.env['master.aboutus'].search([('name','=','Social Media')])
    
    sequence = fields.Char('Sequence',readonly=True, copy=False, default='New')
    master_category = fields.Many2many('master.category',string='Event Type')
    event_id = fields.Many2one('event.event', string='Event')
    event_type_id = fields.Many2one('event.type', related='event_id.event_type_id',string='Event')

    first_name = fields.Char('First name')
    last_name = fields.Char('Last name')
    address1 = fields.Char('Address1') #related='partner_id.name'
    email = fields.Char('Email')
    gender = fields.Selection([('male','Male'),('female','Female'),('other','Others')],string='Gender')
    dob = fields.Date('Date of Birth')
    
    master_aboutus = fields.Many2one('master.aboutus',string="How Did You Hear About Us?",default=_default_about)
    master_intrestedin = fields.Many2one('master.intrestedin',string="What Services Are you Interested In?")
    master_struggling = fields.Many2one('master.struggling',string="Which Areas are you struggling with?")
    master_holistic = fields.Many2one('master.holistic',string="Which Holistic Approaches are you interested in?")
    master_membership = fields.Many2one('master.membership',string="Membership Status?")
    phone = fields.Char('Phone')
    email = fields.Char('Email')
    branch_id = fields.Many2one('master.branch',string="Branch")
    partner_id = fields.Many2one('res.partner','Contacts')
    
    visited_by = fields.Selection([('person','In Person'),('online','Online')],string='Visit')
    online_id = fields.Many2one('master.online',string="Online")
    membership_expires = fields.Date('Membership Expires')

    event_ticket_id = fields.Many2one('event.event.ticket',string='Event Ticket')
    attendee_name = fields.Char(string='Attendee Name')
    
    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New' and vals['master_aboutus']:
            sequence_id = self.env['ir.sequence'].next_by_code('crm.lead') or 'New'
            about_val = self.env['master.aboutus'].search([('id','=',vals['master_aboutus'])])
            vals['sequence'] = "Illu" + '/' + str(about_val.sequence) + '/' + str(sequence_id)
        result = super(CrmLead, self).create(vals)
        return result
    
    @api.onchange("dob")
    def _compute_dob(self):
        if self.dob:
            if datetime.strptime(str(self.dob), '%Y-%m-%d').date() >= datetime.now().date():
                self.dob = ''
    
    @api.onchange("partner_id")
    def _compute_fname_lname(self):
        if self.partner_id.phone:
            self.phone = self.partner_id.phone
        else:
            self.phone = ''
        if self.partner_id.email:
            self.email = self.partner_id.email
        else:
            self.email = ''
        if self.partner_id:
            self.first_name = self.partner_id.firstname
            self.last_name = self.partner_id.lastname
            self.branch_id =  self.partner_id.branch_id
            self.dob = self.partner_id.dob
            self.gender = self.partner_id.gender
            
    def _create_lead_partner_data(self, name, is_company, parent_id=False):
        result = super(CrmLead, self)._create_lead_partner_data(name, is_company, parent_id)
        result.update({
            'branch_id':self.branch_id.id,
            'master_aboutus':self.master_aboutus.id,
            'gender':self.gender,
            'dob':self.dob,
            'master_intrestedin':self.master_intrestedin.id,
            'master_struggling':self.master_struggling.id,
            'master_holistic':self.master_holistic.id,
            'master_membership':self.master_membership.id,
            'visited_by':self.visited_by,
            'membership_expires':self.membership_expires,
            'online_id':self.online_id.id
            })
        return result

    # mail notification send for event registration 12-07-22
    # def action_send_event_reg(self):

    #     template_id = self.env.ref('custom_crm.web_event_reg_lead_create_template')
    #     mail_response= template_id.send_mail(self.id,force_send=True)
