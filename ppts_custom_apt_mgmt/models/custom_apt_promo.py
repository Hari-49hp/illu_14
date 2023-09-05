from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime,timedelta


class Coupon(models.Model):
    _inherit = 'coupon.coupon'

    appointment_id = fields.Many2one('appointment.appointment', 'appointment Reference', readonly=True,
                               help="The appointment from which coupon is generated")

class CouponProgram(models.Model):
    _inherit = 'coupon.program'

    partner_id = fields.Many2one('res.partner', string='Customer Name',
                                 copy=False)


class CustomAppointmentsLine(models.Model):
    _inherit = ['appointment.line.id']

    amount_promotion = fields.Float(string='Promotion Amount', copy=False)
    apply_coupon_status = fields.Boolean(string='Coupon Applied Status', default=False,
                                         help='This field used to identify coupon is applied or not')

    use_promo_code = fields.Boolean(string='Use Promo Code', default=False)
    promo_code = fields.Char(string='Promo Code')

    #recharge coupon

    use_rc_coupon_code = fields.Boolean(string='Use RC Coupon Code', default=False)
    rc_coupon_code = fields.Char(string='RC Coupon Code')

    amount_rc_coupon = fields.Float(string='RC Coupon Amount', copy=False)
    apply_rc_coupon_status = fields.Boolean(string='Coupon Applied Status', default=False,
                                         help='This field used to identify RC Coupon is applied or not')

    def action_use_promo(self):
        if self.promo_code:
            coupon = self.env['coupon.coupon'].search([('code', '=', self.promo_code)], limit=1)

            if coupon:
                coupon_status = coupon.state
                # print('coupon_status-->>',coupon_status)
                today_date= datetime.today().strftime('%Y-%m-%d')
                if coupon.expiration_date:
                    expiration_date= coupon.expiration_date.strftime('%Y-%m-%d')
                else:
                    expiration_date=''

                # print('coupon_date-->>', today_date)

                if coupon_status == 'used':
                    # self.apply_coupon_status = False
                    raise UserError('This coupon has already been used "' + self.promo_code + '". Please Check.')
                elif coupon_status == 'cancel':
                    # self.apply_coupon_status = False
                    raise UserError('This coupon has been cancelled "' + self.promo_code + '". Please Check.')
                elif coupon_status == 'expired' or coupon.expiration_date and (coupon.expiration_date and expiration_date < today_date):
                    # self.apply_coupon_status = False
                    raise UserError('This coupon is expired "' + self.promo_code + '". Please Check.')
                elif coupon_status == 'new':
                    self.apply_coupon_status = True
                    self.amount_promotion = coupon.program_id.discount_fixed_amount
                    coupon.state='used'
                    # msg = 'valid'
                else:
                    self.apply_coupon_status = True
                    self.amount_promotion=coupon.program_id.discount_fixed_amount
            else:
                self.apply_coupon_status = False
                raise UserError('This coupon is invalid "'+self.promo_code+'". Please Check.')
                # msg ='invalid'

        return True

    def action_use_rc_coupon(self):
        if self.rc_coupon_code:
            coupon = self.env['coupon.program'].search([('promo_code', '=', self.rc_coupon_code)], limit=1)
            # print('program--ID', coupon)

            if coupon:
                self.apply_rc_coupon_status = True
                self.amount_rc_coupon = coupon.discount_fixed_amount

            else:
                self.apply_rc_coupon_status = False
                raise UserError('This coupon is invalid "' + self.rc_coupon_code + '". Please Check.')

        return True



