from odoo import api, fields, models, _
from datetime import datetime
from datetime import date

class CustomAppointments(models.Model):
    _inherit = 'appointment.appointment'

    due_adjustment = fields.Float('Due Adjustment')

    def action_adjust_credit(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Adjustment',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_model': 'adv.payment',
            'view_id': 'ppts_custom_apt_mgmt.adv_payment_wizard_form',
            'target': 'new',
            'context': {
                        'default_partner_id': self.partner_id.id,
                        'default_appointment_id':self.id,
                        'default_amount':self.amount_due,
                        'default_company_id':self.company_id.id,
                        'default_is_adjust_balance':True,
                        }
        }

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    appointment_ids = fields.Many2many('appointment.appointment', string="Appointment")

class AccountMove(models.Model):
    _inherit = 'account.move'

    appointment_ids = fields.Many2many('appointment.appointment', string="Appointment")