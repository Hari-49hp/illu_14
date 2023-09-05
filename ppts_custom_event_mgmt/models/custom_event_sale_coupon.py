
from datetime import date, datetime,timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AttendeeEventCoupon(models.Model):
    _inherit = 'event.registration'

    apply_coupon_flag = fields.Boolean(string='Use Coupon', default=False)
    apply_coupon_status = fields.Boolean(string='Coupon Applied Status' , default=False,help='This field used to identify coupon is applied or not')
    apply_coupon_code = fields.Char(string='Coupon Code')
    ticket_price = fields.Float(string="Ticket Price",store=True, help='Price of Ticket without Discount.')
    gift_name_partner_id = fields.Many2one(comodel_name="res.partner")
    gift_name = fields.Char(related="gift_name_partner_id.name", readonly=False, store=True, tracking=14)
    gift_email = fields.Char(related="gift_name_partner_id.email", readonly=False, store=True, tracking=15 ,string="Mobile E-mail ")
    gift_mobile = fields.Char(related="gift_name_partner_id.mobile", readonly=False, store=True, tracking=16,string="Mobile Gift ")
    type_booking = fields.Selection([
        ('type_self', 'for Self'),
        ('type_gift', 'Gift This Event')], string='Type of Booking?',default='type_self', help='Type of Booking to specify Gift this Event or for self.')
    #added to know the client who atten the event
    client_id = fields.Many2one("res.partner",string='Client Name ',compute="_compute_gift_client_name")

    @api.depends('partner_id','gift_name_partner_id')
    def _compute_gift_client_name(self):
        if self.partner_id and not self.gift_name_partner_id:
            self.client_id = self.partner_id
        if self.partner_id and self.gift_name_partner_id:
            self.client_id = self.gift_name_partner_id
        else:
            self.client_id = False



    @api.depends('event_ticket_id')
    def _compute_update_price(self):
        for rec in self:
            price = 0
            product_price = self.env['event.event.ticket'].search([('event_id','=',rec.event_id.id),('id', '=', rec.event_ticket_id.id)], limit=1)
            price=product_price.full_price
            if price:
                rec.ticket_price=price

    @api.onchange('gift_name_partner_id','gift_name','gift_mobile','gift_email')
    def _onchange_update_name(self):
        if self.gift_name_partner_id:
            self.attendee_partner_id = self.gift_name_partner_id.id
        if self.gift_name:
            self.name=self.gift_name
        if self.gift_email:
            self.email=self.gift_email
        if self.gift_mobile:
            self.mobile = self.gift_mobile

    @api.onchange('apply_coupon_flag')
    def use_coupon_on_sale(self):
        if not self.apply_coupon_flag:
            if not self.sale_order_id:
                self.apply_coupon_status=False
                self.apply_coupon_code=''
            else:
                raise UserError('This coupon is applied & Order Has been Placed. You are not allowed to modify!')

    def apply_coupon_on_sale(self):
        if self.apply_coupon_code:
            coupon = self.env['coupon.coupon'].search([('code', '=', self.apply_coupon_code)], limit=1)
            if coupon:
                coupon_status = coupon.state
                if coupon.expiration_date:
                    expiration_date= coupon.expiration_date.strftime('%Y-%m-%d')
                else:
                    expiration_date=''
                if coupon_status == 'used':
                    raise UserError('This coupon has already been used "' + self.apply_coupon_code + '". Please Check.')
                elif coupon_status == 'cancel':
                    raise UserError('This coupon has been cancelled "' + self.apply_coupon_code + '". Please Check.')
                elif coupon_status == 'expired' or coupon.expiration_date and (coupon.expiration_date and expiration_date < today_date):
                    raise UserError('This coupon is expired "' + self.apply_coupon_code + '". Please Check.')
                elif coupon_status == 'new':
                    self.apply_coupon_status = True
                else:
                    self.apply_coupon_status = True
            else:
                self.apply_coupon_status = False
                raise UserError('This coupon is invalid "'+self.apply_coupon_code+'". Please Check.')

