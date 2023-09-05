import werkzeug
from odoo import api, fields, models, _

ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')


class EventTypeMST(models.Model):
    _name = 'eventtype.master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Event Type Master'
    _rec_name = 'event_type'
    
    event_type = fields.Char('Event Type', tracking=True)
    type_code = fields.Char('Code', tracking=True)
    event_notes = fields.Text('Internal Note', tracking=True)
    event_color = fields.Char(string="Color Code" ,help="Choose your color",size=9, tracking=True)

class EventMainCateg(models.Model):
    _name = 'event.maincateg.master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Event Main Categ'
    _rec_name = 'event_maincateg'

    event_maincateg = fields.Char('Name', tracking=True)
    maincateg_code = fields.Char('Code', tracking=True)
    maincateg_notes = fields.Text('Internal Note', tracking=True)

class EventTypeMST(models.Model):
    _name = 'event.subcateg.master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Event Sub Categ'

    _rec_name = 'event_subcateg'

    event_subcateg = fields.Char('Name', tracking=True)
    subcateg_code = fields.Char('Code', tracking=True)
    event_categ_id = fields.Many2one('event.type',string='Event Category', required=True, tracking=True)
    #event main category is moved to event.type as requested by client..
    maincateg_id = fields.Many2one('event.maincateg.master',string='Main Category', tracking=True)
    subcateg_notes = fields.Text('Internal Note', tracking=True)
    

class EventVenue(models.Model):
    _name = 'venue.venue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Event Venue'
    _rec_name = 'name'

    name = fields.Char('Name', tracking=True)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    city_id = fields.Many2one('city.master',string='City')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company.id, index=True)
    contact_address = fields.Char(string='Complete Address',related='street')
    phone = fields.Char(string='phone')
    mobile = fields.Char(string='mobile')
    website = fields.Char(string='website')
    email = fields.Char(string='email')
    vat = fields.Char(string='vat')
    about_venue = fields.Char(string="About", help="Display in website about Venue")

    @api.onchange('country_id')
    def get_contact_address(self):
        for rec in self:
            street = self.street or ''
            street2 = self.street2 or ''
            zip = self.zip or ''
            city = self.city or ''
            state_id = self.state_id.name or ''
            c_address = street+' '+street2+' '+zip+' '+city+' '+state_id
            self.contact_address=c_address

    def google_map_link(self, zoom=10):
        params = {
            'q': '%s,%s,%s %s, %s' % (self.street or '', self.street2 or '', self.city or '', self.zip or '', self.country_id and self.country_id.display_name or ''),
            'z': zoom,
        }
        return 'https://maps.google.com/maps?' + werkzeug.urls.url_encode(params)

    def open_google_map(self):
        params = {
            'q': '%s,%s, %s %s, %s' % (
            self.street or '', self.street2 or '', self.city or '', self.zip or '', self.country_id and self.country_id.display_name or ''),
            'z': 10,
        }
        return {'name': 'Go to website',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': 'https://maps.google.com/maps?'+ werkzeug.urls.url_encode(params)
                }