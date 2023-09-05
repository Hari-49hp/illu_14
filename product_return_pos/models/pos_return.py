# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Anusha P P (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import models, api, fields


class PosOrderReturn(models.Model):
    _inherit = 'pos.order'

    return_ref = fields.Char(string='Return Ref', readonly=True, copy=False)
    return_status = fields.Selection([
        ('nothing_return', 'Nothing Returned'),
        ('partialy_return', 'Partialy Returned'),
        ('fully_return', 'Fully Returned')
    ], string="Return Status", default='nothing_return',
        readonly=True, copy=False, help="Return status of Order")
    reference_no = fields.Char('Reference No',readonly=True, copy=False)
    cheque = fields.Char('Cheque #')
    payment_method_id = fields.Many2many('pos.payment.method', string='Payment Method ')

    @api.model
    def get_lines(self, ref):
        result = []
        order_id = self.search([('pos_reference', '=', ref)], limit=1)
        # print (order_id,'orddddd')
        if order_id:
            lines = self.env['pos.order.line'].search([('order_id', '=', order_id.id)])
            for line in lines:
                prod = ''
                # added cancellation charge in pos 29-06-22
                get_product_id = self.env['product.product'].search([('name','=','Cancellation Charges')],limit=1)
                if line.full_product_name == get_product_id.name:
                    prod = line.product_id.name + '-'+get_product_id.name
                else:
                    prod = line.product_id.name

                if line.qty - line.returned_qty > 0:
                    new_vals = {
                        'product_id': line.product_id.id,
                        'product': prod ,
                        'qty': line.qty - line.returned_qty,
                        'price_unit': line.price_unit,
                        'discount': line.discount,
                        'line_id': line.id,
                        'commission_recipient': line.commission_recipient,
                        'sub_total':"%.2f" % float(line.price_subtotal),
                    }
                    result.append(new_vals)

        return [result]
    
    @api.model
    def get_payment_info(self, ref, return_ref):
        result = []
        order_id = False
        if ref and return_ref:
            order_id = self.search(['|',('pos_reference', '=', return_ref),('pos_reference', '=', ref)], limit=1)
        elif ref or return_ref:
            order_id = self.search([('pos_reference', '=', ref or return_ref)], limit=1)
            
        if order_id:
            if order_id.cheque or order_id.payment_method_id:
                new_vals = {
                    'cheque': order_id.cheque or ' ',
                    'payment_method': order_id.payment_method_id and order_id.payment_method_id.mapped('name') or ' ',
                }
                result.append(new_vals)
            
        return result

    def create(self, vals):
        res = super(PosOrderReturn, self).create(vals)
        if res.company_id.id == 1:
            if vals.get('reference_no', ' ') == ' ':
                print('JLT')
                res.reference_no = self.env['ir.sequence'].next_by_code('pos.order.jlt') or ' '
        elif res.company_id.id == 2:
            if vals.get('reference_no', ' ') == ' ':
                print('MIE')
                res.reference_no = self.env['ir.sequence'].next_by_code('pos.order.mie') or ' '
        elif res.company_id.id == 3:
            if vals.get('reference_no', ' ') == ' ':
                print('ABU')
                res.reference_no = self.env['ir.sequence'].next_by_code('pos.order.abu') or ' '
        elif res.company_id.id == 4:
            if vals.get('reference_no', ' ') == ' ':
                print('HQ')
                res.reference_no = self.env['ir.sequence'].next_by_code('pos.order.hq') or ' '
        elif res.company_id.id == 5:
            if vals.get('reference_no', ' ') == ' ':
                print('ILU')
                res.reference_no = self.env['ir.sequence'].next_by_code('pos.order.ill') or ' '

        return res

    def write(self, vals):
        # for order in self:
        # res = super(PosOrderReturn, self).write(vals)
        for order in self:
            if vals.get('return_ref') or order.return_ref:
                if vals.get('return_ref'):
                    orders = self.env['pos.order'].search([('pos_reference','=',vals.get('return_ref'))],limit=1,order="id desc")
                    if orders and orders.event_reg_id:
                        vals['event_reg_id'] = orders.event_reg_id
                        vals['sale_type_for'] ='event'
                        orders.event_reg_id.pos_order_id = order.id
                    # for orders in orders_ids:
                    if orders:
                        if vals.get('state') and vals['state'] == 'paid' and self.name == '/': vals['name'] = orders.name
                        vals['appt_sale_id'] = orders.appt_sale_id.id
                        # orders.appt_sale_id.state = 'paid'
                        for i in orders.lines:
                            line_id = self.env['pos.order.line'].search([('product_id','=',i.product_id.id)],limit=1)
                            line_id.commission_recipient = i.commission_recipient
                            line_id.commission_type = i.commission_type
                            line_id.therapist_commission_type = i.therapist_commission_type
                            line_id.therapist_commission = i.therapist_commission

                        orders.appt_sale_id.amount_due = 0.00
                        #orders.appt_sale_id.apt_payment_received = True
                        orders.appt_sale_id.payment_status_apt = 'payment_received'
                        apt_ids = self.env['appointment.appointment'].search([('pos_order_id','=',orders.appt_sale_id.pos_order_id.id)])
                        if apt_ids:
                            for apt_rec in apt_ids:
                                apt_rec.pos_order_id = order.id
                        orders.appt_sale_id.pos_order_id = order.id
                        orders.unlink()
                    self.env.cr.commit()
                elif order.return_ref:
                    orders = self.env['pos.order'].search([('pos_reference','=',order.return_ref)],limit=1,order="id desc")
                    if orders and orders.event_reg_id:
                        vals['event_reg_id'] = orders.event_reg_id
                        vals['sale_type_for'] ='event'
                        orders.event_reg_id.pos_order_id = order.id
                    if orders:
                        if vals.get('state') and vals['state'] == 'paid' and self.name == '/': vals['name'] = orders.name
                        vals['appt_sale_id'] = orders.appt_sale_id.id
                        for i in orders.lines:
                            line_id = self.env['pos.order.line'].search([('order_id','=',order.id),('product_id','=',i.product_id.id)],limit=1)
                            line_id.commission_recipient = i.commission_recipient
                            line_id.commission_type = i.commission_type
                            line_id.therapist_commission_type = i.therapist_commission_type
                            line_id.therapist_commission = i.therapist_commission
                        # orders.appt_sale_id.state = 'paid'
                        orders.appt_sale_id.amount_due = 0.00
                        #orders.appt_sale_id.apt_payment_received = True
                        orders.appt_sale_id.payment_status_apt = 'payment_received'
                        apt_ids = self.env['appointment.appointment'].search([('pos_order_id','=',orders.appt_sale_id.pos_order_id.id)])
                        if apt_ids:
                            for apt_rec in apt_ids:
                                apt_rec.pos_order_id = order.id
                        orders.appt_sale_id.pos_order_id = order.id
                        orders.unlink()
                    order.env.cr.commit()
        
        res = super(PosOrderReturn, self).write(vals)
        return res

    def _order_fields(self, ui_order):
        order = super(PosOrderReturn, self)._order_fields(ui_order)
        # print(ui_order['return_ref'],'ui_order[')
        if 'return_ref' in ui_order.keys() and ui_order['return_ref']:
            order['return_ref'] = ui_order['return_ref']
        #     parent_order = self.search([('pos_reference', '=', ui_order['return_ref'])], limit=1)

        #     updated_lines = ui_order['lines']
        #     ret = 0
        #     qty = 0
        #     for uptd in updated_lines:
        #         line = self.env['pos.order.line'].search([('order_id', '=', parent_order.id),
        #                                                    ('id', '=', uptd[2]['line_id'])], limit=1)
        #         if line:
        #             line.returned_qty += -(uptd[2]['qty'])
        #     for line in parent_order.lines:
        #         qty += line.qty
        #         ret += line.returned_qty
        #     if qty-ret == 0:
        #         if parent_order:
        #             parent_order.return_status = 'fully_return'
        #             print(parent_order.return_status)
        #     elif ret:
        #         if qty > ret:
        #             if parent_order:
        #                 parent_order.return_status = 'partialy_return'

        return order
    def send_mail(self):
        '''
        This function opens a window to compose an email, with the edi MOM template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']   
        template_id = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'account.move',
            'default_res_id': self.account_move.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id or False,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

class PosOrderLineReturn(models.Model):
    _inherit = 'pos.order.line'

    returned_qty = fields.Float(string='Returned Qty', digits='Returned Qty', readonly=True)
    reference_no = fields.Char('Reference No',readonly=True, copy=False,related="order_id.reference_no")

    
