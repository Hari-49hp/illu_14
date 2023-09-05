from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = "pos.order"

    pos_payment_ref = fields.Char('Payment Reference ID')

    def write(self, vals):
        # res = super(PosOrderRef, self).write(vals)
        for rec in self:
            if rec.state == 'paid':
                sequence = rec.env['ir.sequence'].next_by_code('pos.order.payment.reference')
                vals['pos_payment_ref'] = sequence
                # res.pos_payment_ref = self.env['ir.sequence'].next_by_code('pos.order.payment.reference')
        return super(PosOrder, self).write(vals)


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    pos_payment_ref = fields.Char('Payment Reference ID', related="order_id.pos_payment_ref")