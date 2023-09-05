from odoo import api, fields, models, _

class EventPaymentOption(models.TransientModel):
    _name = "event.payment.option"
    _description = "EventPaymentOption"
    _rec_name="payment_option"

    payment_option = fields.Selection([('pay_now','Would you like to process the payment now?'),('pay_later', 'Process the Payment later')],string="Payment Option")
    event_register_id = fields.Many2one('event.registration','Event Registration')

    def action_pay(self):
        if self.payment_option == "pay_now":
            val = self.env.company.is_pos_order
            if val:
                self.event_register_id.action_create_pos()
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Dashboard',
                    'view_mode': 'kanban,tree,form',
                    'res_model': 'pos.config',
                    'domain':"['|',('user_ids', 'in', uid),('user_ids','=',False)]"
                }
            else:
                self.event_register_id.action_confirm()
    