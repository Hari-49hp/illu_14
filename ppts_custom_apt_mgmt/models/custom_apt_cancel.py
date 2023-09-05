from odoo import api, fields, models, _
from datetime import date, timedelta, datetime

class CustomAppointments(models.Model):
    _inherit = 'appointment.appointment'

    use_partial_cancel = fields.Boolean(string='Apply Partial Cancel', default=False, tracking=True)
    apt_invoice_amt=fields.Float(string='Invoice Total', copy=False, tracking=True)
    apt_payment_amt=fields.Float(string='Payment Total',  copy=False, tracking=True)
    apt_used_pack=fields.Integer(string='Utilized Items',  copy=False, tracking=True)
    apt_not_used_pack=fields.Integer(string='Not Used Items',  copy=False, tracking=True)
    apt_refund_amt = fields.Float(string='Refund Total', copy=False, tracking=True)

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    appointment_id = fields.Many2one('appointment.appointment','Appointment')

    def action_create_payments(self):
        payments = self._create_payments()
        if self._context.get('dont_redirect_to_payments'):
            return True
        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False,
                        'appointments_id': self.appointment_id.id,
                        },
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        return action