import base64
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CustomClassMST(models.Model):
    _name = 'event.class.master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Event Class'
    _rec_name = 'class_name'

    class_name = fields.Char('Name',tracking=True)
    class_code = fields.Char(string='Template ID',tracking=True,help='Template ID for Event')
    eve_class_type = fields.Many2one('event.type',string='Event Category',tracking=True,help='Type of Event. Event comes under wihch category')
    class_type = fields.Many2one('event.class.type',string='Type',tracking=True)
    class_level = fields.Many2one('event.class.level',string='Event Format',tracking=True,help='Level of Events')
    class_main_catg = fields.Many2one('event.maincateg.master',string='Main Category',tracking=True,help='Main Category of Event')
    class_sub_catg = fields.Many2one('event.subcateg.master',string='Event Sub Category',tracking=True,help='Sub Category of Event')
    class_image_url = fields.Char(string='Image URL',store=True,tracking=True,help='URL of Event Image')
    class_image = fields.Binary(string='Image',tracking=True,store=True)
    class_description = fields.Text(string='Description',tracking=True,help='User Description for Event')
    class_prereq_note = fields.Text('Prerequisite Notes',tracking=True,help='Prerequisite Notes of Events')
    class_prereq_client = fields.Many2many('event.class.pre.client',string='Prerequisite Client Type',tracking=True,help='Prerequisite Client Type of Events')
    class_auto_client = fields.Many2many('event.class.auto.client',string='Auto-assigned Client Type',tracking=True,help='Auto-assigned Client Type of Events')
    class_regstration_note = fields.Text(string='Registration Note', tracking=True,help='Special Registration Note for Events')
    class_internal_note = fields.Text(string='Internal Note', tracking=True,help='Internal Note about Events')
    class_archive = fields.Boolean(string='Inactive', default=False, tracking=True,help='Instead of Deleting Event Template can be Archived')
    type_event = fields.Selection([
        ('type_online', 'Online'),
        ('type_onsite', 'On-site'),
        ('type_hybrid', 'Hybrid')], string='Event Platform', default='type_onsite', help='Type of event to specify Online / Offline / Hybrid')
    type_online = fields.Selection([
        ('type_live', 'Online Live'),
        ('type_record', 'Online- Recorded videos')],default='type_live', string='Online Category',
        help='Sub categroy of Online Type Events')

    address_id = fields.Many2one('venue.venue', string='Venue', tracking=True,help='Location of Event')
    sales_incharge_id = fields.Many2one('res.users', string='Sales Incharge', tracking=True, domain="[('share','=',True)]")

    class_sub_image = fields.Image(string='Sub attachment', tracking=True,
                                     help='Sub Category of Event')

    def onchange_image_url(self):
        image = False
        if self.class_image_url:
            image = base64.b64encode(requests.get(self.class_image_url).content)
        self.class_image = image

    def unlink(self):
        for expense in self:
            event_ids=self.env['event.event'].search([('class_type','=',expense.id)])
            if event_ids:
                raise UserError(_('You cannot delete Template. It is Linked with Events '))
        return super(CustomClassMST, self).unlink()

class EventClassPreClient(models.Model):
    _name = 'event.class.pre.client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Event Class Prerequisite Client Type'
    _rec_name = 'class_pre_client'

    class_pre_client = fields.Char('Name',tracking=True)
    class_pre_client_note= fields.Char('Notes',tracking=True)

class EventClassAutoClient(models.Model):
    _name = 'event.class.auto.client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Event Class Auto-assigned Client Type'
    _rec_name = 'class_auto_clinet'

    class_auto_clinet = fields.Char('Name',tracking=True)
    class_auto_clinet_note = fields.Char('Notes',tracking=True)


class EventClassType(models.Model):
    _name = 'event.class.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Event Class Type'
    _rec_name = 'class_type'

    class_type = fields.Char('Name',tracking=True)
    class_type_note= fields.Char('Notes',tracking=True)

class EventClassLevel(models.Model):
    _name = 'event.class.level'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Event Format'
    _rec_name = 'class_level'
    #class level renamed as Event Format

    class_level = fields.Char('Name',tracking=True)
    event_categ_id = fields.Many2one('event.type', string='Event Category', tracking=True)
    class_level_note= fields.Char('Notes',tracking=True)
    is_prerequisite = fields.Boolean(string="prerequisite")

#
class CustomEventClass(models.Model):
    _inherit = 'event.event'

    class_type = fields.Many2one('event.class.master',string='Class',tracking=True,store=True)
    class_code = fields.Char(string='Class ID',related='class_type.class_code',tracking=True)

    def temp_warning(self):
        if self.class_type.id == False:
            raise UserError(_('You should need to create Checklist'))

    #event class fetch

    @api.onchange('class_type')
    def _compute_from_event_type(self):
        for evnt in self:
            if evnt.class_type:
                if not evnt.name:
                    evnt.name = evnt.class_type.class_name
                if not evnt.evnt_maincateg:
                    evnt.evnt_maincateg = evnt.class_type.class_main_catg
                if not evnt.evnt_subcateg:
                    evnt.evnt_subcateg = evnt.class_type.class_sub_catg
                if not evnt.event_img_url:
                    evnt.event_img_url = evnt.class_type.class_image_url
                if not evnt.event_img:
                    evnt.event_img = evnt.class_type.class_image
                # if not evnt.event_desc:
                #     evnt.event_desc = evnt.class_type.class_name
                if not evnt.description:
                    evnt.description = evnt.class_type.class_description
                if not evnt.type_event:
                    evnt.type_event = evnt.class_type.type_event
                if not evnt.type_online:
                    evnt.type_online = evnt.class_type.type_online
                if not evnt.address_id:
                    evnt.address_id = evnt.class_type.address_id
                if not evnt.event_survey_id:
                    evnt.event_survey_id = evnt.class_type.event_survey_id
                if not evnt.class_level_id:
                    evnt.class_level_id = evnt.class_type.class_level
                if not evnt.event_type_id:
                    evnt.event_type_id = evnt.class_type.eve_class_type
