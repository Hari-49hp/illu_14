from odoo import api, fields, models, _
from datetime import datetime
from datetime import date
from werkzeug import urls

    
class EventSource(models.Model):
    _name = "event.source"
    _description = "Source of Event"

    source_id = fields.Many2one('utm.source', "Source", ondelete='cascade', required=True)
    medium_id = fields.Many2one('utm.medium', "Medium", ondelete='cascade', required=True)
    campaign_id = fields.Many2one('utm.campaign', "Campaign", ondelete='cascade', required=True)
    event_id = fields.Many2one('event.event', "Event", ondelete='cascade')
    url = fields.Char(compute='_compute_url', string='Url Parameters')

    @api.depends('source_id', 'source_id.name', 'event_id')
    def _compute_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # website_url = "/jobs/detail/%s" % job.id
        website_url = "/web/login"
        for source in self:
            source.url = urls.url_join(base_url, "%s?%s" % (website_url,
                urls.url_encode({
                    'utm_campaign': source.campaign_id.name,
                    'utm_medium': source.medium_id.name,
                    'utm_source': source.source_id.name
                })
            ))