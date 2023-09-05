from odoo import api, fields, models, _

class CustomParkingMST(models.Model):
    _name = 'parking.master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Parking Master for Event'
    _rec_name = 'parking_type'

    parking_type = fields.Char('Name',tracking=True)
    parking_date = fields.Date('Date',tracking=True)
    parking_guidelines = fields.Html(string='Guidelines',tracking=True)

    def write(self, vals):
        before_val = self.parking_guidelines
        res = super(CustomParkingMST, self).write(vals)
        if self.parking_guidelines:
            for parking in self:
                parking_lines = parking.parking_guidelines
                old_qtyz = parking_lines
                msg = "<b>" + _("The Parking Guidelines has been updated.") + "</b><ul>"
                msg += _(
                    "%(before_valz)s --> %(old_qtyz)s ",
                    before_valz=before_val,old_qtyz=parking_lines

                ) + "<br/>"
                msg += "</ul>"
                parking.message_post(body=msg)
        return res

class CustomEventParking(models.Model):
    _inherit = 'event.event'

    parking_type = fields.Many2one('parking.master',string='Parking Type',default=1,tracking=True)
    events_parking = fields.Html(string='Event Parking', store=True,tracking=True)

    @api.onchange('parking_type')
    def _compute_parking(self):
        self.events_parking = self.parking_type.parking_guidelines