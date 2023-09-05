from odoo import api, fields, models, _

class EventPayRate(models.Model):
    _inherit = 'event.event'

    pay_rate_line = fields.One2many('event.pay.rate.line','event_id',string='Pay Rate Lines',tracking=True)

    def write(self, vals):
        rres = super(EventPayRate, self).write(vals)
        for res in self:
            reg_id = self.env['event.registration'].search([('event_id', '=', res.id)])
            inv_amount_total=0.0
            for reg in reg_id:
                inv_amount_total=inv_amount_total+ reg.invoice_id.amount_total
            if res.facilitator_evnt_ids:
                for pay_rate in res.pay_rate_line:
                    pay_rate.unlink()
                for line in res.facilitator_evnt_ids:
                    facilitator_id = self.env['event.pay.rate.line'].create({
                        'event_id': res.id,
                        'therapist_id': line.id,
                    })
        return rres

class EventPayRateLine(models.Model):
    _name = 'event.pay.rate.line'

    event_id=fields.Many2one('event.event')
    therapist_id = fields.Many2one('hr.employee', string='Therapist', copy=False, tracking=True)
    invoice_amount = fields.Float('Invoice Amount')