# -*- coding: utf-8 -*-
from odoo import models, fields, api

class EventEvent(models.Model):
    _inherit = 'event.event'

    auto_confirm = fields.Boolean('Automatically Confirm Registrations', default=False,help="Events and registrations will automatically be confirmed "
             "upon creation, easing the flow for simple events.")

class EventRegistration(models.Model):
    _inherit = 'event.registration'

    def _get_current_logged_in_user(self):
        return self.env.user.partner_id.id
    
    pos_order_id = fields.Many2one('pos.order',string='Pos Order')
    pos_order_line_id = fields.Many2one('pos.order.line',string='Ticket')
    pos_order_atv = fields.Boolean('Pos Order Active')
    sales_person = fields.Many2one(comodel_name="res.users", string="Sales Person")
    partner_id = fields.Many2one('res.partner', string='Customer Name',states={'done': [('readonly', True)]}, default=_get_current_logged_in_user)     
    attendee_partner_id = fields.Many2one(comodel_name="res.partner",string='Attendee Name ', readonly=False, tracking=10)
    email = fields.Char(string='Email', related='attendee_partner_id.email', readonly=False, store=True, tracking=11)
    phone = fields.Char(string='Phone', related='attendee_partner_id.phone', readonly=False, store=True, tracking=12)
    mobile = fields.Char(string='Mobile', related='attendee_partner_id.mobile', readonly=False, store=True, tracking=13)

    def action_pos_order(self):
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'pos.order',
                'view_mode': 'tree,form',
                'target': 'current',
                'domain': [('id','=',self.pos_order_id.id)]
            }
    
    @api.onchange("event_id")
    def _onchange_event_ticket_id(self):
        if self.event_id:
            pass
            if self.event_id.event_ticket_ids:
                self.event_ticket_id = self.event_id.event_ticket_ids[0].id
                self.ticket_price = self.event_ticket_id.full_price
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.attendee_partner_id = self.partner_id.id
            self.gift_name_partner_id = self.partner_id.id
        else:
            self.attendee_partner_id = False
            self.gift_name_partner_id = False