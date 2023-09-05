from odoo import api, fields, models, _
import re

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _compute_payment_method(self):
        for rec in self:
            cache = ''
            for i in rec.payment_ids:
                cache += '/' + i.payment_method_id.name
            rec.payment_methods = cache[1:]
    
    def _compute_remaining_session(self):
        for rec in self:
            if rec.appt_sale_id:
                if rec.appt_sale_id.session_type == 'type_package':
                    count = 0
                    for line in rec.appt_sale_id.appointment_line_id:
                        if line.state_line == 'draft': count += 1
                    rec.remaining_session = str(count) + '/' + str(len(rec.appt_sale_id.appointment_line_id))
                else:
                    if rec.state == 'new':
                        rec.remaining_session = '1/1'
                    else:
                        rec.remaining_session = '0/1'
            else:
                rec.remaining_session = '0/1'

    payment_methods = fields.Char('Payment Method', compute='_compute_payment_method')
    # descriptions = fields.Char('Description', related="appt_sale_id.descriptions", default='Retail Order')
    descriptions = fields.Char('Description', default='Retail Order' ,compute="_compute_description")
    creation_date = fields.Date('Activation date', related="appt_sale_id.creation_date")
    notes = fields.Text('Notes', related="appt_sale_id.notes")
    remaining_session = fields.Char('Remaining', compute='_compute_remaining_session')


    def _compute_description(self):
        for rec in self:
            if not rec.descriptions:
                if rec.appt_sale_id:
                    rec.descriptions = rec.appt_sale_id.descriptions
                if rec.event_reg_id:
                    rec.descriptions =  rec.event_reg_id.event_id.name
                if not rec.appt_sale_id and not rec.event_reg_id:
                    rec.descriptions = 'Retail Order'
            

    def redirect_to_appointment(self):
        if self.appt_sale_id:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'name': _('Appointment'),
                'res_model': 'appointment.appointment',
                'res_id': self.appt_sale_id.id,
                'target': 'new',
            }
        if self.event_reg_id:
            return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'name': _('Event'),
            'res_model': 'event.registration',
            'res_id': self.event_reg_id.id,
            'target': 'new',
        }
        
    def redirect_to_modification(self):
        if self.account_move:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'name': _('Invoice'),
                'res_model': 'account.move',
                'res_id': self.account_move.id,
                'target': 'new',
            }

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    order_ref_id = fields.Char(related='order_id.name',string="Order Ref ")
    payment_methods = fields.Char('Payment Method', related='order_id.payment_methods')
    date_order = fields.Datetime(related='order_id.date_order')

    def redirect_to_appointment(self):
        if self.appt_sale_id:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'name': _('Appointment'),
                'res_model': 'appointment.appointment',
                'res_id': self.appt_sale_id.id,
                'target': 'new',
            }
        if self.event_reg_id:
            return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'name': _('Event'),
            'res_model': 'event.registration',
            'res_id': self.event_reg_id.id,
            'target': 'new',
        }