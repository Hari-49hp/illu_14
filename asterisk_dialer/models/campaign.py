# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
# -*- encoding: utf-8 -*-
from ast import literal_eval
import base64
import pytz
from datetime import datetime,date, timedelta
from jinja2.sandbox import SandboxedEnvironment
import json
import logging
from urllib.parse import unquote
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import mute_logger, ustr
from psycopg2 import IntegrityError

from .campaign_log import LOG_LEVELS

logger = logging.getLogger(__name__)

CAMPAIGN_STATES = [
    ('new', 'New'),
    ('running', 'Ongoing'),
    ('done', 'Finished')
]

CAMPAIGN_TYPES = [
    ('operators', 'Datamined'),
    ('new_upload','New Upload'),
    ('operators_and_upload','Datamined & New Upload')
]

MESSAGE_TYPES = [
    ('sound_file', 'Sound File'),
    ('google_tts', 'Google TTS')
]


def convert_agi_env(env):
    # Function to unquote AGI Env
    res = dict()
    res.update([k.split(': ') for k in unquote(env).split('\n') if k])
    return res


class Campaign(models.Model):
    _name = 'asterisk_dialer.campaign'
    _description = _('Dialer Campaign')
    _order ='id desc'

    name = fields.Char(required=True, help=_("A descriptive name."))
    number = fields.Char(help=_("An extension number to dial to begin outbound calling."
                                "\nAsterisk must execute AGI(agi:async) when dialed."))
    campaign_type = fields.Selection(
        CAMPAIGN_TYPES,
        required=True,
        default='operators',
        help=_("Operators: an operator dials the number to begin outbound calling.\n"
               "Voice Message: play a voice message to all contacts."),
    )
    start_type = fields.Selection(
        [('manual', 'Manual'), ('scheduled', 'Scheduled'),
         ('periodic', 'Periodic')], default='manual', required=True,
        help=_('Manual: run manually'
               '\nScheduled: specify start and end time'
               '\nPeriodic: run periodically in a given time')
    )
    # Periodic settings
    period_type = fields.Selection(
        [('hours', 'Hours'), ('days', 'Days'),
         ('weeks', 'Weeks')], default='days',
    )
    period_number = fields.Integer(
        default='1',
    )
    next_run = fields.Datetime(help=_("Select the starting point for the campaign."))
    channel_provider = fields.Char(
        required=False,
        default=lambda self: self.env['asterisk_common.settings'].get_param('default_provider'),
        help=_("Asterisk dialstring in Technology/Resource format."
               "\nString {NUMBER} is replaced with contact's phone number. Examples:"
               "\nSIP/{NUMBER}@sip.example.com"
               "\nPJSIP/{NUMBER}@sip.example.com"
               "\nIAX2/iax.examle.com/{NUMBER}"
               "\nLocal/{NUMBER}@example-context/n")
    )
    contacts = fields.One2many(
        'asterisk_dialer.contact',
        inverse_name='campaign',
        help=_("The list of contacts belonging to the campaign.")
    )
    contact_count = fields.Integer(
        compute='_get_contact_count', string='Contacts ',
        help=_("Number of contacts in the campaign.")
    )
    total_crm = fields.Integer(compute='_compute_total',string='Total CRM',help=_("Number of CRM Total."))
    total_free_booking = fields.Integer(compute='_compute_free_booking',string='Total Free booking',help=_("Number of Free bookings."))
    total_paid_booking = fields.Integer(compute='_compute_paid_booking',string='Total Paid booking',help=_("Number of Paid bookings."))

    lead_count = fields.Integer(compute='_get_lead_count',
        string='Lead',
        help=_("Number of Lead in the campaign.")
    )
    opportunity_count = fields.Integer(compute='_get_opportunity_count',
            string='Opportunity',
            help=_("Number of Opportunity in the campaign.")
        )
    lead_to_opportunity_count = fields.Integer(compute='_get_lead_to_opportunity_count',
            string='Opportunity ',
            help=_("Number of Opportunity converted from Lead in the campaign.")
        )
    call_count = fields.Integer(
        compute='_get_call_count', string='Calls ',
        help=_("Number of calls in the campaign.")
    )
    log_count = fields.Integer(
        compute='_get_log_count', string='Logs ',
        help=_("Number of campaign log entries.")
    )
    state = fields.Selection(CAMPAIGN_STATES, default='new',group_expand='_group_expand_states')
    start_date = fields.Datetime()
    end_date = fields.Datetime()
    dial_attempts = fields.Integer(
        default=lambda self: self.env['asterisk_common.settings'].get_param('dial_attempts'),
        help=_("Total dial attempts. Set more than one to re-dial if not answered.")
    )
    originate_timeout = fields.Integer(
        default=lambda self: self.env['asterisk_common.settings'].get_param('originate_timeout'),
        help=_("How many seconds to wait for an answer before considering noanswer.")
    )
    max_parallel_calls = fields.Integer(default=1)
    msg_type = fields.Selection(MESSAGE_TYPES, string='Message Type')
    msg_file = fields.Binary(string='Message File')
    playback_widget = fields.Char(compute='_get_playback_widget',
                                  string='Playback')
    msg_filename = fields.Char()
    # Google TTS fields
    tts_text = fields.Text(string='Message Text')
    tts_language = fields.Char('Language', default='en-US')
    tts_voice = fields.Char('Voice', default='en-US-Wavenet-A')
    tts_pitch = fields.Float('Pitch', default=0.0)
    tts_speaking_rate = fields.Float('Speaking Rate', default=1.0)
    # Special field to easily get if we should render message for each contact
    # or one message for all is fine. Depends on using variable substitutions.
    tts_is_common = fields.Boolean(compute='_compute_tts_is_common')
    #
    log_level = fields.Selection(
        LOG_LEVELS, default='i', required=True,
        help=_("Default is info. Use debug log level if more information is needed ")
    )
    logs = fields.One2many('asterisk_dialer.campaign_log', 'campaign')
    calls = fields.One2many('asterisk_dialer.channel', 'campaign', context={'active_test': False})
    domain = fields.Char(default="['|',('mobile,'!=',False),('phone', '!=', False)]")
    model = fields.Char(default='res.partner')
    active = fields.Boolean(default=True, index=True)
    #new Field
    responsible_id = fields.Many2one('res.users',string="Assigned To" ,help='The user responsible for campaign')
    campaign_type_id = fields.Many2one('campaign.type',string="Type",help="Select tye of the campaign")
    event_id = fields.Many2one('event.event', string='Event')
    progress = fields.Float("Progress", store=True, help="Display progress .")
    login_detail = fields.Text(string="Login Details",compute="compute_get_create_details",store=True)
    data_mine_line_ids = fields.One2many('datamine.skipped.records','campaign_id',string="Datamine Skipped Records")
    duplicate_contact = fields.Boolean(string="Duplicate Contacts",help="Help to invisible the duplicate records page")
    new_progress = fields.Float(string="Progress",compute="_compute_remark_progress")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company.id, index=True)


    # get login details for campaign creator 28-00-22
    @api.depends('state','name','campaign_type_id','channel_provider')
    def compute_get_create_details(self):
        for rec in self:
            if rec.create_date and rec.create_uid:
                rec.login_detail = str(rec.create_date.strftime('%Y-%m-%d %H:%M:%S')) + ' , '+ rec.create_uid.name


    # open the upload wizard for use below function 06/07/22
    def action_import_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Choose Your File',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'import.partner'
        }
    #Onchnage for Number
    @api.onchange('responsible_id')
    def _onchange_user(self):
        if self.responsible_id:
            self.number = self.responsible_id.sip_external_phone
        else:
            self.number = False

    #group Expand
    def _group_expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]
            
    # create UTM Campaign
    def _create_campaign(self):
        campaign_utm_id = self.env['utm.campaign']
        campaign_id = False
        for rec in self:
            campaign_utm_search = campaign_utm_id.search([('name','=', rec.name)],limit=1)
            if campaign_utm_search:
               campaign_id = campaign_utm_search
            else:
                create_vals = {
                    'name': rec.name,
                    'user_id': rec.responsible_id.id,          
                    }
                campaign_id = campaign_utm_id.create(create_vals)
            return campaign_id
    def action_data_miner(self):
        vals = ({'default_campaign_id': self.id})
        custom_timezone = pytz.timezone(self.env.user.tz or 'UTC')
        custom_crnt_date = datetime.now().replace(tzinfo=pytz.timezone('UTC')).astimezone(custom_timezone)
        # custom_ven_current_date = custom_crnt_date.strftime('%Y-%m-%d')
        
       
       
        return {
            'name': custom_crnt_date,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'data.miner',
            'target': 'new',
            'context': vals,
        }

    # create UTM Campaign
    def _create_source(self):
        campaign_source_id = self.env['utm.source']
        source = False
        for rec in self:
            contact_id = self.env['asterisk_dialer.contact'].search([('campaign', '=', rec.id)])
            for each_contact in contact_id:
                if each_contact.model_object.reffer_type_id:
                    source_id = self.env['utm.source'].search([('name','=',each_contact.model_object.reffer_type_id.name)])
                    if not source_id:
                        source_vals = {
                        'name': each_contact.model_object.reffer_type_id.name
                        }
                        source = self.env['utm.source'].create(source_vals)
                    if source_id:
                        source = source_id

            return source_id


    def _create_oppportunity(self,campaign=None):
        crm_lead = self.env['crm.lead']
        master_aboutus_id = self.env['master.aboutus'].search([('name','=','Social Media')])
        medium_id = self.env['utm.medium'].search([('name','=','Telecalling')])
        for rec in self:
            contact_id = self.env['asterisk_dialer.contact'].search([('campaign', '=', rec.id)])
            for each_contact in contact_id:
                source =False
                if not each_contact.model_object.reffer_type_id:
                    source = False
                if each_contact.model_object.reffer_type_id:
                    source_id = self.env['utm.source'].search([('name','=',each_contact.model_object.reffer_type_id.name)])
                    if not source_id:
                        source_vals = {
                        'name': each_contact.model_object.reffer_type_id.name
                        }
                        source_val_id = self.env['utm.source'].create(source_vals)
                        source =source_val_id.id
                    if source_id:
                        source = source_id.id
                create_vals = {
                    'name': rec.name,
                    'first_name':each_contact.model_object.firstname,
                    'last_name':each_contact.model_object.lastname,
                    'partner_id': each_contact.model_object.id,
                    'mobile':each_contact.model_object.mobile,
                    'email_from':each_contact.model_object.email,
                    'phone':each_contact.model_object.phone,
                    'user_id': rec.responsible_id.id,
                    'type':'opportunity',
                    'master_aboutus':master_aboutus_id.id,
                    'campaign_oppor_id':rec.id,
                    'campaign_lead_id':rec.id,
                    'campaign_id':campaign.id,
                    'medium_id':medium_id.id,
                    'source_id': source,
                    'campaign_type_id':rec.campaign_type_id.id or False,
                    'campaign_type':rec.campaign_type
                    }
                crm_lead_id = crm_lead.create(create_vals)

    # create Lead as opporturnity
    def _create_lead_as_oppportunity(self,campaign=None):
        master_aboutus_id = self.env['master.aboutus'].search([('name','=','Social Media')])
        medium_id = self.env['utm.medium'].search([('name','=','Telecalling')])
        for rec in self:
            crm_lead = self.env['crm.lead'].search([('type', '=','lead'),('campaign_lead_id','=',rec.id)])
            for each_lead in crm_lead:
                create_vals = {
                    'name': rec.name,
                    'partner_id': False,
                    'contact_name':each_lead.contact_name,
                    'mobile':each_lead.mobile,
                    'email_from':each_lead.email_from,
                    'phone':each_lead.phone,
                    'user_id': rec.responsible_id.id,
                    'type':'opportunity',
                    'master_aboutus':master_aboutus_id.id,
                    'campaign_oppor_id':rec.id,
                    'campaign_lead_id':rec.id,
                    'campaign_id':campaign.id,
                    'medium_id': medium_id.id or False,
                    'source_id':each_lead.source_id.id or False,
                    'campaign_type_id':rec.campaign_type_id.id or False,
                    'campaign_type':rec.campaign_type
   
                    }
                oppportunity_id = self.env['crm.lead'].create(create_vals)



    def write(self, vals):
        self.log(content=[self, vals, ['state']])
        res = super(Campaign, self).write(vals)
        return res

    def _get_playback_widget(self):
        file_source = 'msg_file'
        for rec in self:
            rec.playback_widget = '<audio id="sound_file" preload="auto" ' \
                                  'controls="controls"> ' \
                                  '<source src="/web/content?model=asterisk_dialer.campaign&' \
                                  'id={recording_id}&filename={filename}&field={source}&' \
                                  'filename_field=msg_filename&download=True" />' \
                                  '</audio>'.format(
                                                    recording_id=rec.id,
                                                    filename=rec.msg_filename,
                                                    source=file_source)

    @api.constrains('start_date', 'end_date')
    def _check_start_date(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Campaign end date must be greater then start date")

    @api.onchange('period_type', 'period_number')
    def _reset_next_run(self):
        self.next_run = datetime.now() + timedelta(
            **{self.period_type: self.period_number})

    @api.onchange('campaign_type')
    def _set_msg_type(self):
        if not self.msg_type:
            self.msg_type = 'sound_file'

    def _get_contact_count(self):
        for rec in self:
            rec.contact_count = self.env['asterisk_dialer.contact'].search_count(
                [('campaign', '=', rec.id)])

    def _get_lead_count(self):
        for rec in self:
            rec.lead_count = self.env['crm.lead'].search_count(
                [('campaign_lead_id', '=', rec.id),('type','=','lead')])

    def _get_opportunity_count(self):
        for rec in self:
            rec.opportunity_count = self.env['crm.lead'].search_count(
                ['|',('campaign_oppor_id', '=', rec.id),('campaign_lead_id', '=', rec.id),('type','=','opportunity')])

    def _get_lead_to_opportunity_count(self):
        for rec in self:
            rec.lead_to_opportunity_count = self.env['crm.lead'].search_count(
                [('campaign_lead_id', '=', rec.id),('type','=','opportunity')])                             

    def _get_call_count(self):
        for rec in self:
            rec.call_count = self.env['asterisk_dialer.channel'].search_count(
                [('campaign', '=', rec.id), ('active', 'in', [True, False])])

    def _get_log_count(self):
        for rec in self:
            rec.log_count = self.env['asterisk_dialer.campaign_log'].search_count(
                [('campaign', '=', rec.id)])

    @api.depends('state')
    def _compute_total(self):
        for each in self:
            each.total_crm = self.env['crm.lead'].search_count(
                [('campaign_lead_id', '=', each.id),('type','=','opportunity')])
 
    @api.depends('state')
    def _compute_free_booking(self):
        for each in self:
            each.total_free_booking = self.env['crm.lead'].search_count(
                [('campaign_lead_id', '=', each.id),('stage_id.create_contact','=',True)])

    @api.depends('state')
    def _compute_paid_booking(self):
        for each in self:
            each.total_paid_booking = self.env['crm.lead'].search_count(
                [('campaign_lead_id', '=', each.id),('stage_id.paid_booking','=',True)])
        

    def _compute_tts_is_common(self):
        for rec in self:
            if isinstance(rec.tts_text, str) and '{' in rec.tts_text:
                rec.tts_is_common = False
            else:
                rec.tts_is_common = True

    def render_voice_message(self, contact):
        # Helper function to render the message from template.
        try:
            template_env = SandboxedEnvironment(
                lstrip_blocks=True,
                trim_blocks=False,
                keep_trailing_newline=True,
                autoescape=False,
            )
            template = template_env.from_string(ustr(self.tts_text))
            text = template.render({
                'campaign': self,
                'contact': contact,
                'object': contact.model_object,
            })
        except Exception as e:
            raise ValidationError('Render error: {}'.format(e))
        # One message for all
        if self.tts_is_common:
            filename = 'odoo/dialer_campaign_{}'.format(self.id)
        else:
            filename = 'odoo/dialer_campaign_{}_contact_{}'.format(
                self.id, contact.id)
        # Generate sound file
        self.env.user.asterisk_agent.request(
            'asterisk.tts_create_sound',
            filename,
            text,
            self.tts_language,
            self.tts_voice,
            self.tts_pitch,
            self.tts_speaking_rate
        )

    def originate_to_contact(self, contact):
        # Is it voice message campaign?
        if contact.campaign.campaign_type == 'voice_message':
            # Render individual messages
            if not self.tts_is_common:
                self.render_voice_message(contact)
        self.log('Originate to contact ID {} number {}'.format(
            contact.id, contact.phone), level='debug')
        # Originate to contact
        self.env['asterisk_dialer.channel'].originate(
            channel=contact.campaign.channel_provider.replace(
                '{NUMBER}', contact.phone),
            app='AGI',
            data='agi:async',
            campaign=self,
            contact=contact,
        )

    def check_campaign(self):
        # Check campaign status and dates
        if self.state != 'running':
            return False
        if self.end_date and (fields.Datetime.now() >= self.end_date):
            # Change campaign status to done
            self.state = 'done'
            return False
        return True

    def wakeup(self):
        self.ensure_one()
        self.log('CAMPAIN {} WAKEUP'.format(self.name), level='debug')
        if not self.check_campaign():
            return False
        # Get available operators
        operators_available = self.campaign_type == 'operators' and \
            self.get_available_operators() or []
        # Do we have a free operator?
        if self.campaign_type != 'operators' or operators_available:
            # Get current active calls
            current_calls = self.env['asterisk_dialer.channel'].search_count(
                [('campaign', '=', self.id),
                 ('active', '=', True),
                 ('contact', '!=', False)])
            # Check if we have available channels to originate.
            if self.max_parallel_calls <= current_calls:
                self.log('Max parallel calls reached.', level='debug')
                return False
            # Originate as much calls as is possible
            for i in range(0, self.max_parallel_calls - current_calls):
                contact = self.get_next_contact()
                if contact:
                    self.originate_to_contact(contact)
                else:
                    self.log('No more contacts to dial.', level='info')
                    # FIXME: Does not work.
                    # Remove non-working code.
        else:
            self.log('No available operators.', level='debug')
    #Generate Lead from Campaign
    def generate_lead(self,model,domain,lead_ids):
        if lead_ids:
            for each_lead in lead_ids:
                each_lead.campaign_lead_id =  self.id

    def get_next_contact(self):
        contact = self.env['asterisk_dialer.contact'].search([
            '&', ('campaign', '=', self.id),
            '|', ('state', '=', 'q'),
            '&', ('state', '=', 'f'), ('dial_attempt', '<', self.dial_attempts)
        ], limit=1)
        if contact:
            contact.campaign.log('Got next contact to dial: {} - {}'.format(
                                 contact.name, contact.phone), level='debug')
            contact.write({
                'state': 'p',
                'dial_attempt': contact.dial_attempt + 1
            })
            self.env.cr.commit()
        return contact

    def get_available_operators(self):
        self.ensure_one()
        # Get campaign operators
        operators = self.env['asterisk_dialer.operator'].search(
            [('campaign', '=', self.id),
             ('state', '=', 'available')])
        logger.info('GET AVAILABLE OPERATORS: %s', ','.join(
            [k.name for k in operators]))
        return operators

    def connect_to_operator(self, channel):
        operators = self.get_available_operators()
        logger.info('CONNECT TO AVAILABLE OPERATORS: %s', ','.join(
            [k.name for k in operators]))
        # Connect to the operator
        if operators:
            operators[0].notify_operator({'contact': channel.contact.id})
            self.env.user.asterisk_agent.action({
                'Action': 'AGI',
                'Channel': channel.channel,
                'Command': 'EXEC ConfBridge {}'.format(operators[0].accountcode),
            }, notify=True, no_wait=True, as_list=False)
        else:
            self.log('NO AVAILABLE OPERATORS.', level='debug')

    def connect_to_voice_message(self, channel):
        # Originate a call to playback it
        if self.msg_type == 'sound_file' or self.tts_is_common:
            filename = 'odoo/dialer_campaign_{}'.format(self.id)
        else:
            filename = 'odoo/dialer_campaign_{}_contact_{}'.format(
                self.id, channel.contact.id)
        channel_name = channel.channel
        self.env.user.asterisk_agent.action({
            'Action': 'AGI',
            'Channel': channel_name,
            'Command': 'EXEC Wait 0.5'.format(filename),
        }, notify=True, no_wait=True, as_list=False)
        self.env.user.asterisk_agent.action({
            'Action': 'AGI',
            'Channel': channel_name,
            'Command': 'EXEC Playback {}'.format(filename),
        }, notify=True, no_wait=True, as_list=False)
        self.env.user.asterisk_agent.action({
            'Action': 'AGI',
            'Channel': channel_name,
            'Command': 'HANGUP {}'.format(channel_name),
        }, notify=True, no_wait=True, as_list=False)
        logger.info('-------------------------- 1F')

    @api.model
    def async_agi_start(self, event):
        logger.info('AGI start: %s', json.dumps(event, indent=2))
        # Get the campaign by exten called by operator
        channel = self.env['asterisk_dialer.channel'].search(
            [('uniqueid', '=', event['Uniqueid'])])
        if not channel:
            # Now check if it is dialer app channel so that other apps channels
            # don't come here. Contact channels are pre-created so are found.
            # Operator channels are matched by accountcode.
            operator = self.env['asterisk_dialer.operator'].search(
                [('accountcode', '=', event['AccountCode'])])
            if not operator:
                logger.warning('OPERATOR NOT FOUND BY ACCOUNTCODE %s!',
                               event['AccountCode'])
                self.env.user.asterisk_agent.action({
                    'Action': 'Hangup',
                    'Channel': event['Channel']
                }, no_wait=True, notify=True)
                return False
            campaign = self.search([('number', '=', event['Exten'])])
            if not campaign:
                logger.warning(
                    'OPERATOR CAMPAIGN NOT FOUND BY NUMBER %s', event['Exten'])
                self.env.user.asterisk_agent.action({
                    'Action': 'Hangup',
                    'Channel': event['Channel']
                }, no_wait=True, notify=True)
                return False
            # Operator & campaign found, log a message and create the channel.
            campaign.log('OPERATOR {} FOUND.'.format(operator.name),
                         level='debug')
            # Create the channel for operator
            self.env['asterisk_dialer.channel'].create({
                'operator': operator.id,
                'campaign': campaign.id,
                'system_name': event.get('SystemName', ''),
                'channel': event.get('Channel', ''),
                'callerid_num': event.get('CallerIDNum', ''),
                'callerid_name': event.get('CallerIDName', ''),
                'connected_line_num': event.get('ConnectedLineNum', ''),
                'connected_line_name': event.get('ConnectedLineName', ''),
                'state': event.get('ChannelState', ''),
                'state_desc': event.get('ChannelStateDesc', ''),
                'uniqueid': event.get('Uniqueid', ''),
                'linkedid': event.get('Linkedid', ''),
                'context': event.get('Context', ''),
                'exten': event.get('Exten', ''),
                'accountcode': event.get('AccountCode', ''),
                'priority': event.get('Priority', ''),
            })
            # Update operator's state.
            operator.write({
                'state': 'available',
                'channel': event['Channel'],
                'campaign': campaign.id
            })
            self.env.cr.commit()
            # Answer the channel
            self.env.user.asterisk_agent.action({
                'Action': 'AGI',
                "Command": "Answer",
                'Channel': event.get('Channel')},
                notify=True, no_wait=True, as_list=False)
            # Add to the operator's confbridge.
            self.env.user.asterisk_agent.action({
                'Action': 'AGI',
                'Channel': event.get('Channel'),
                'Command': 'EXEC ConfBridge {}'.format(
                    operator.accountcode),
            }, notify=True, no_wait=True, as_list=False)
            return True
        # Check if this is a contact call.
        elif channel and channel.contact:
            channel.write({
                'channel': event.get('Channel', ''),
                'callerid_num': event.get('CallerIDNum', ''),
                'callerid_name': event.get('CallerIDName', ''),
                'connected_line_num': event.get('ConnectedLineNum', ''),
                'connected_line_name': event.get('ConnectedLineName', ''),
                'state': event.get('ChannelState', ''),
                'state_desc': event.get('ChannelStateDesc', ''),
                'uniqueid': event.get('Uniqueid', ''),
                'linkedid': event.get('Linkedid', ''),
                'context': event.get('Context', ''),
                'exten': event.get('Exten', ''),
                'accountcode': event.get('AccountCode', ''),
                'priority': event.get('Priority', ''),
            })
            camp = channel.campaign
            if camp.campaign_type == 'operators':
                camp.connect_to_operator(channel)
            elif camp.campaign_type == 'voice_message':
                camp.connect_to_voice_message(channel)
            return True
        else:
            logger.warning('AGI START NOT HANDLED.')
            return False

    def run_campaign(self):
        # self.wakeup()
        campaign = self._create_campaign()
        self._create_oppportunity(campaign)
        self._create_lead_as_oppportunity(campaign)
        self.state = 'running'


    def pause_campaign(self):
        print('test')
        # self.state = 'paused'

    def done_campaign(self):
        self.state = 'done'

    def generate_contacts(self, model, domain):
        # get the currect record active id 09-08-22
        active_id = self._context.get('active_id')
        asterisk_dialer_id = self.env["asterisk_dialer.campaign"].browse(active_id)

        if isinstance(domain, str):
            domain = literal_eval(domain)
        contacts = self.env[model].search(domain)
        # Save current domain and model for campaign
        self.write({'domain': domain, 'model': model})
        # Get origination settings
        originate_format = self.env['asterisk_common.settings'].sudo(
            ).get_param('originate_format')
        originate_prefix = self.env['asterisk_common.settings'].sudo(
            ).get_param('originate_prefix')
        strip_plus = self.env['asterisk_common.settings'].sudo(
            ).get_param('originate_strip_plus')
        # Iterate over contacts.
        for contact in contacts:
            # Check if the contact object has phone_normalized field.
            src_number = number = contact.mobile or contact.phone
            if number:
                # Now transform the number according to outgoing dial rules.
                if originate_format != 'no_format' and getattr(
                        contact, '_format_number', False):
                    number = contact._format_number(
                        number, format_type=originate_format)
                # Strip formatting if present.
                number = number.replace(' ', '')
                number = number.replace('(', '')
                number = number.replace(')', '')
                number = number.replace('-', '')
                if number[0] == '+' and strip_plus:
                    # Remove + from the beginning.
                    number = number[1:]
                if originate_prefix:
                    number = '{}{}'.format(originate_prefix, number)
                # create the skipped record if contact is not exist 02-08-22
                get_contact = self.env['asterisk_dialer.contact'].search([('phone','ilike',number),('campaign','=',self.id)])
                if get_contact:
                    data_skipped_record = self.env['datamine.skipped.records'].create({
                        'name':contact.name,
                        'campaign_id':self.id,
                        'mobile':number,
                        'create_date':datetime.today(),
                        'source':'Datamined'
                        })
                    # used for invisible the duplicate contact page 09-08-22
                    if data_skipped_record:
                        asterisk_dialer_id.duplicate_contact = True
                    else:
                        asterisk_dialer_id.duplicate_contact = False



                try:
                    with mute_logger('odoo.sql_db'), self.env.cr.savepoint():
                        self.env['asterisk_dialer.contact'].create({
                            'phone': number,
                            'campaign': self.id,
                            'model_object': '{},{}'.format(
                                model, contact.id),
                            'source':'Datamined'
                        })
                        self.log(
                            'Import {} {} src number {} dst number {}'.format(
                                model, contact.name, src_number, number),
                            level='debug')
                except IntegrityError:
                    self.log('Phone {} already exists in campaign.'.format(
                        number))

    @api.model
    def manage_campaign(self):
        now = fields.Datetime.now()
        campaign_obj = self.env['asterisk_dialer.campaign']
        # Find scheduled campaigns
        campaigns_to_start = campaign_obj.search([
            ('start_type', '=', 'scheduled'),
            ('start_date', '<=', fields.Datetime.to_string(now)),
            ('state', '=', 'ready')
        ])
        if campaigns_to_start:
            campaigns_to_start.write({
                'state': 'running',
            })
            for campaign in campaigns_to_start:
                campaign.wakeup()
        campaigns_to_stop = campaign_obj.search([
            ('end_date', '<=', fields.Datetime.to_string(now)),
            ('state', '!=', 'done')
        ])
        if campaigns_to_stop:
            campaigns_to_stop.write({
                'state': 'done'
            })
        # Find periodic campaigns in done state.
        periodic_campaigns = campaign_obj.search([
            ('start_type', '=', 'periodic'),
            ('state', '=', 'done'),
            ('next_run', '<=', datetime.now())])
        for per_camp in periodic_campaigns:
            per_camp.state = 'running'
            self.env['asterisk_dialer.contact'].search(
                [('campaign', '=', per_camp.id)]).unlink()
            # TODO: Re-run filter to re-generate contacts ???
            per_camp.generate_contacts(per_camp.model, per_camp.domain)
            per_camp.wakeup()

    def log(self, content, level='info'):
        self.ensure_one()
        # contact can be either message string or tupple(record, vals, fields).
        messages = []
        if type(content) is list:
            rec, vals, track_fields = content
            for field in track_fields:
                if vals.get(field):
                    # Get selection values
                    if isinstance(rec._fields[field], fields.Selection):
                        old_value = dict(rec._fields[field].selection).get(rec[field])
                        new_value = dict(rec._fields[field].selection).get(vals.get(field))
                    else:
                        old_value = rec[field]
                        new_value = vals.get(field)
                    if old_value != new_value:
                        messages.append('{} - {}: {} => {}'.format(
                            rec.name, field, old_value, new_value))
        else:
            messages.append(content)
        # Add log message to campaign
        if (self.log_level == 'i' and level[0] == 'i') or (
                self.log_level == 'd'):
            for msg in messages:
                self.env['asterisk_dialer.campaign_log'].create({
                    'campaign': self.id,
                    'content': msg,
                    'level': level[0],
                })
        # Log to console
        if level == 'info':
            logger.info('\n'.join(messages))
        if level == 'debug':
            logger.debug('\n'.join(messages))

    def msg_test(self):
        # Upload voice file to Asterisk and test it using Originate
        if self.msg_type == 'sound_file':
            if not self.msg_file:
                raise ValidationError('File not set!')
            # Copy file to Asterisk
            self.env.user.asterisk_agent.request(
                'asterisk.put_prompt',
                'dialer_campaign_{}.wav'.format(self.id),
                self.msg_file.decode('latin-1'))
        else:
            if not self.tts_text:
                raise ValidationError('Message text not set!')
            if not self.contacts:
                raise ValidationError('Please add a test contact!')
            self.render_voice_message(self.contacts[0])
        # Originate a call to playback it
        self.env['asterisk_dialer.channel'].originate(
            channel=self.env.user.asterisk_user.channels[0].channel,
            app='AGI',
            data='agi:async',
            campaign=self,
            contact=self.contacts[0],
        )

    def action_archive(self):
        # Archive campaigns logs and contacts when campaign is archived
        for rec in self:
            self.env['asterisk_dialer.campaign_log'].search([('campaign', '=', rec.id)]).toggle_active()
            self.env['asterisk_dialer.contact'].search([('campaign', '=', rec.id)]).toggle_active()
            rec.filtered(lambda record: record[rec._active_name]).toggle_active()

    def action_unarchive(self):
        # Unarchive campaigns logs and contacts when campaign is unarchived
        for rec in self:
            self.env['asterisk_dialer.campaign_log'].with_context(active_test=False).search([
                ('campaign', '=', rec.id)]).toggle_active()
            self.env['asterisk_dialer.contact'].with_context(active_test=False).search([
                ('campaign', '=', rec.id)]).toggle_active()
            rec.filtered(lambda record: not record[rec._active_name]).toggle_active()

    def redirect_to_contact(self):
        contact_list =[]
        contact_id = self.env['asterisk_dialer.contact'].search([('campaign', '=', self.id)])
        for each_contact in contact_id:
            contact_list.append(each_contact.model_object.id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contact',
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'view_id': False,
            'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},
            'views': [(self.env.ref('custom_partner.view_partner_summary_tree_view').id, 'tree'),(self.env.ref('custom_partner.res_partner_history_history_from_view').id,'form')],
            'domain':[('id','in',contact_list)],
            'flags': {'initial_mode': 'edit'},
        }


    # @api.depends('state')
    # def _compute_progress(self):
    #     for each in self:
    #         if each.state=="new":
    #             each.progress = 20
    #         elif each.state=="running":
    #             each.progress = 50
    #         else:
    #             each.progress = 100

    # calculate the campaign progess percentage 20-10-22
    def _compute_remark_progress(self):
        for rec in self:
            rec.new_progress = 0.0
            cnt = 0.0
            campaign_contract = self.env['asterisk_dialer.contact'].search([('campaign','=',rec.id)])
            for contract in campaign_contract:
                # partner_remarks = self.env['res.partner'].search_count([('id','=',contract.model_object.id),('latest_quick_remarks','!=',False)])
                partner_remarks = self.env['campaign.partner.remarks'].search_count([('partner_id','=',contract.model_object.id),('remarks','!=',False),('campaign_id','=',rec.id)])
                cnt +=partner_remarks
                rec.new_progress = round((cnt / len(campaign_contract) )*100)

class DataMineSkippedRecords(models.Model):
    _name = "datamine.skipped.records"
    _description = 'Datamine Skipped Records'

    name = fields.Char(string="Name")
    datamine_id = fields.Many2one('asterisk_dialer.contact')
    mobile = fields.Char(string="Mobile")
    campaign_id = fields.Many2one('asterisk_dialer.campaign',string="Campaign")
    create_date = fields.Datetime(string="Create Date")
    source = fields.Text(string="Source")
