from ast import literal_eval
import logging
from psycopg2 import IntegrityError
from odoo.tools import mute_logger
from odoo import api, fields, models, _

logger = logging.getLogger(__name__)


class GenerateContacts(models.TransientModel):
    _name = 'asterisk_dialer.generate_contacts'
    _description = 'Generate contacts'

    model = fields.Selection([
        ('res.partner', _('Partners')),('crm.lead', ('Lead')),
    ], default=lambda self: self.env['asterisk_dialer.campaign'].browse(
        self.env.context.get('active_id')).model)
    domain = fields.Char(
        string='Domain', compute='_compute_domain',
        readonly=False, store=True)
    # Many2many relations with GENERATE_CONTACTS_MODELS
    partner_ids = fields.Many2many(
        'res.partner', string='Partners', compute='_compute_partners')
    lead_ids = fields.Many2many(
        'crm.lead', string='Lead', compute='_compute_lead')


    @api.depends('model', 'domain')
    def _compute_partners(self):
        for rec in self:
            if rec.model == 'res.partner':
                domain = rec._parse_domain()
                contacts = self.env[rec.model].search(domain).ids
                rec.update({
                    'partner_ids': [(6, 0, contacts)],
                })
            else:
                rec.update({
                    'partner_ids': [(6, 0, [])],
                })

    @api.depends('model', 'domain')
    def _compute_lead(self):
        for rec in self:
            if rec.model == 'crm.lead':
                domain = rec._parse_domain()
                leads = self.env[rec.model].search(domain).ids
                rec.update({
                    'lead_ids': [(6, 0, leads)],
                })
            else:
                rec.update({
                    'lead_ids': [(6, 0, [])],
                })


    def _get_default_domain(self):
        domain = []
        if self.model == 'res.partner':
            domain = ['|',('mobile', '!=', ''),('phone', '!=', '')]
        if self.model == 'crm.lead':
            domain = [('type', '=', 'lead')]

        return domain

    @api.depends('model')
    def _compute_domain(self):
        for rec in self:
            campaign = self.env['asterisk_dialer.campaign'].browse(rec.env.context.get('active_id'))
            if not rec.model:
                rec.domain = ''
            # if campaign.domain:
            #     rec.domain = campaign.domain
            else:
                rec.domain = repr(rec._get_default_domain())

    def _parse_domain(self):
        self.ensure_one()
        try:
            domain = literal_eval(self.domain)
        except Exception:
            domain = [('id', 'in', [])]
        return domain

    def generate(self):
        campaigns = self.env['asterisk_dialer.campaign'].browse(
            self._context.get('active_ids', []))
        for campaign in campaigns:
            if self.model == 'res.partner':
                campaign.generate_contacts(self.model, self.domain)
            if self.model == 'crm.lead':
                campaign.generate_lead(self.model, self.domain,self.lead_ids)

