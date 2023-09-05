from odoo import api, fields, models, _


class CustompartnerApt(models.Model):
    _inherit = 'hr.employee'

    def action_partner_appt(self):
        self.ensure_one()
        return {
                'type': 'ir.actions.act_window',
                'name': 'Appointment',
                'view_mode': 'tree,form',
                'res_model': 'appointment.appointment',
                # 'res_id': self.id,
                'domain': [('partner_id','=',self.id)],
                }

    def savee_and_close(self):
        if self.env.context.get('active_model')=='appointment.appointment':
            event_id = self.env['appointment.appointment'].browse(self.env.context.get('active_id'))
            event_id.write({'partner_id': self.id,'name': "Appointment for : "+self.name})
        return {'type': 'ir.actions.act_window_close'}