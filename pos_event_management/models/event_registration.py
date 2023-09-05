# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError

class EventRegistration(models.Model):
    _inherit = 'event.registration'


    def action_view_event_pos(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Order',
            'view_mode': 'tree,form',
            'res_model': 'pos.order',
            'domain': [('id', '=', self.pos_order_id.id)],
        }

    def _get_current_logged_in_user(self):
        return self.env.user.partner_id.id

    pos_order_id = fields.Many2one('pos.order',string='Pos Order')
    pos_order_line_id = fields.Many2one('pos.order.line',string='Ticket')
    sales_person = fields.Many2one(comodel_name="res.users", string="Sales Person",default=lambda self: self.env.uid)
    partner_id = fields.Many2one(
        'res.partner', string='Customer Name',
        states={'done': [('readonly', True)]}, default=_get_current_logged_in_user)     
    attendee_partner_id = fields.Many2one(comodel_name="res.partner",
    string='Attendee Name ', readonly=False, tracking=10)
    email = fields.Char(string='Email', related='attendee_partner_id.email', readonly=False, store=True, tracking=11)
    phone = fields.Char(string='Phone', related='attendee_partner_id.phone', readonly=False, store=True, tracking=12)
    mobile = fields.Char(string='Mobile', related='attendee_partner_id.mobile', readonly=False, store=True, tracking=13)
    event_payment_status = fields.Selection([('no_paid','Not Paid'),('partially_paid','Partially Paid'),('payment_received','Paid'),('paid','Paid'),('refund','Refund')],compute='_compute_payment_from_payment',string="PaymentStatus ")
    event_refund_status = fields.Boolean(string="Refund Status",help="To show the unpaid statement while cancel the event.")
    is_pos_order = fields.Boolean(related='company_id.is_pos_order', string='Create POS Order', readonly=False)
    event_id = fields.Many2one('event.event', string='Event', required=True,readonly=True, states={'draft': [('readonly', False)]},domain=lambda self: [("is_published_event", "=",True)])
    is_send_mail_gift = fields.Boolean(string="Gift",help="Mail send for gifted event")

    # Open the event registration form while click the button in tree view 27-09-22
    def action_open_registration(self):

        return {
                'name': 'Client Registration',
                'view_mode': 'form',
                'res_model': 'event.registration',
                'target': 'current',
                'type': 'ir.actions.act_window',
                'res_id': self.id,
                'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},
                'flags': {'initial_mode': 'edit'},
            }


    def _compute_payment_from_payment(self):
        for rec in self:
            rec.event_payment_status = 'no_paid'
            if rec.pos_order_id: 
                if rec.pos_order_id.amount_paid != 0 and rec.pos_order_id.state == 'draft':
                    rec.event_payment_status = 'partially_paid'         
                elif rec.pos_order_id.state == 'draft': 
                    rec.event_payment_status = 'no_paid'
                elif rec.pos_order_id.state in ('paid','done','invoiced'):
                    rec.event_payment_status = 'paid'
                    if rec.event_payment_status == 'paid':
                        template_id = self.env.ref('pos_event_management.event_gift_mail_template')
                        if template_id and rec.is_send_mail_gift == False and rec.type_booking == 'type_gift':
                            template_id.send_mail(rec.id,force_send=True)
                            is_send_mail_gift = True
                else:
                    rec.event_payment_status = 'no_paid'
            else:
                rec.event_payment_status = 'no_paid'
            # to change the payment status if there is an refund 04-07-22
            if rec.pos_order_id and rec.event_refund_status:
                rec.event_payment_status = 'refund'

    def action_pos_order(self):
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'pos.order',
                'view_mode': 'tree,form',
                'target': 'current',
                'domain': [('id','=',self.pos_order_id.id)]
            }
    
    @api.onchange("event_id")
    def _onchange_event_id(self):
        if self.event_id:
            pass
            if self.event_id.event_ticket_ids:
                self.event_ticket_id = self.event_id.event_ticket_ids[0].id
                self.ticket_price = self.event_ticket_id.full_price
            else:
                self.event_ticket_id = False
                self.ticket_price = 0

    @api.onchange("event_ticket_id")
    def _onchange_event_ticket_id(self):
        for rec in self:
            if rec.event_ticket_id:
                rec.ticket_price = rec.event_ticket_id.full_price 
            else:
                rec.ticket_price = 0

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.attendee_partner_id = self.partner_id.id
            self.gift_name_partner_id = self.partner_id.id
        else:
            self.attendee_partner_id = False
            self.gift_name_partner_id = False
 
    def action_create_pos(self):
        for rec in self:
            pos_session_id = self.env['pos.session'].search([('state', '=', 'opened')], limit=1)
            if not pos_session_id:
                raise UserError(_("Please create a POS session to create POS order and confirm the Appointment"))
            seq = self.env['ir.sequence'].search([('name','=','POS APT'),('code','=','POS APT')])
            if seq:
                pos_seq = seq.next_by_id()
            else:
                seq =  self.env['ir.sequence'].create({'name': 'POS APT','code':'POS APT','active':True,'implementation':'no_gap','prefix':'POS/APT','padding':5,'number_increment':1,'number_next_actual':1})
                pos_seq = seq.next_by_id()

            if pos_session_id:
                pos_id = self.env['pos.order'].sudo().create({
                    'partner_id': rec.partner_id.id,
                    'pricelist_id': 1,
                    'session_id': pos_session_id.id,
                    'amount_tax': 0.0,
                    'amount_paid': 0.0,
                    'amount_return': 0.0,
                    'amount_total': 0.0,
                    'state': 'draft',
                    'sale_type_for': 'event',
                    'apt_booking_date': rec.date_open.date(),
                    'apt_booked_by': rec.sales_person.id,
                    'company_id': rec.company_id.id,
                    'name': pos_seq,
                    'pos_reference': pos_seq,
                    'event_reg_id':rec.id
                })
                rec.pos_order_id = pos_id.id
            else:
                raise UserError(_("Please create a POS session to create POS order and confirm the Appointment"))

            if not rec.event_ticket_id.product_id.available_in_pos:
                rec.event_ticket_id.product_id.available_in_pos = True

            self.env['pos.order.line'].sudo().create({
                    'full_product_name':rec.event_ticket_id.product_id.name,
                    'product_id': rec.event_ticket_id.product_id.id,
                    'qty': 1,
                    'price_subtotal':rec.event_ticket_id.price,
                    'price_subtotal_incl':rec.event_ticket_id.price,
                    'order_id': rec.pos_order_id.id,
                    'discount': 0,
                    'tax_ids_after_fiscal_position': False,
                    'price_unit': rec.event_ticket_id.price,
                    'name': rec.name,
                    'event_reg_id':rec.id

            })
            rec.pos_order_id._onchange_amount_all()
            rec.state='open'

    def open_wizard(self):
        return {
                'type': 'ir.actions.act_window',
                'name': _('Pay Now'),
                'res_model': 'event.payment.confirmation',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                    'default_event_id': self.id,
                },
            }

# To open the event payment wizard in the client form 
    def open_event_payment_wizard(self):
        payrate = self.ticket_price
        def product_tax(product_id, amount):
            if product_id:
                total_included = 0
                for tax in product_id.taxes_id:
                    taxes = tax.compute_all(amount, self.env.company.currency_id, 1, product=product_id.id, partner=False)
                    t2 = taxes['total_included'] - amount
                    total_included += t2
                return total_included

        if self.pos_order_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Dashboard',
                'view_mode': 'kanban,tree,form',
                'res_model': 'pos.config',
            } 
        else:
            lst = []
            if self.event_ticket_id:
                lst.append([0, 0, {
                            # 'full_product_name':self.appointments_id.appointments_type_id.product_id.name,
                            'product_id': self.event_ticket_id.product_id.id,
                            'qty':1,
                            'price_subtotal': self.event_ticket_id.price,
                            'price_subtotal_incl': payrate + product_tax(self.event_ticket_id.product_id, payrate),
                            'discount':self.event_ticket_id.disc_rate,
                            'price_unit': self.event_ticket_id.price,
                            'name': self.event_ticket_id.name,
                        }])
            CONFIRM = self.env['event.registration.confirmation']
            CONFT = CONFIRM.search([('event_id','=',self.id)],limit=1)
            def con_return(ap_id):
                return {
                        'type': 'ir.actions.act_window',
                        'name': _('Pay Now'),
                        'res_model': 'event.registration.confirmation',
                        'res_id': ap_id,
                        'target': 'new',
                        'view_mode': 'form',
                        'view_type': 'form',
                      
                }
            if CONFT:
                CONFT.product_categ_id = CONFT.qty = 1
                CONFT.product_id = False
                CONFT.price_unit = CONFT.discount = 0.0
                CONFT.discount_type = 'percentage'
                return con_return(CONFT.id)
            else:

                conf_id = CONFIRM.create({
                    'event_id': self.id,
                    'partner_id': self.partner_id.id,
                    'product_categ_id': 1,
                    'lines': lst,
                })
                return con_return(conf_id.id)
        
    def event_payment(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Dashboard',
                'view_mode': 'kanban,tree,form',
                'res_model': 'pos.config',
                'domain':"['|',('user_ids', 'in', uid),('user_ids','=',False)]"
                }

    # mail notification send for event registration through website 13-07-22
    def action_send_event_reg(self):
        for rec in self:
            template_id = self.env.ref('pos_event_management.registered_event_mail_template')
            mail_response= template_id.send_mail(rec.id,force_send=True)
