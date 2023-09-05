from odoo import api, fields, models, _
from odoo import http
from odoo.exceptions import ValidationError,UserError
from odoo.http import request
from datetime import date, timedelta, datetime

class PosOrder(models.Model):
    _inherit = "pos.order"


    pos_ref = fields.Char('POS Ref')
    return_order_reason_ids = fields.One2many('return.order.reason','reason_id',string="Return Remarks")
    return_inv = fields.Boolean(string="Return",help="To hide the return remarks tab.")
    pos_discount = fields.Float(string="Discount",compute="_compute_discount_amount")
    
    # used to calculate the discount amount for pos lines 28-07-22
    def _compute_discount_amount(self):
        for rec in self:
            rec.pos_discount = sum(dis.amount_discount for dis in rec.lines if dis.amount_discount > 0)

    def return_all_credit_note(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Refund Invoice'),
            'res_model': 'account.move.reversal',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {
                'default_move_ids': self.account_move.ids,
                'default_move_type': 'out_invoice',
                'default_refund_method': 'refund',
                'default_residual': self.amount_paid,
                'active_ids': self.account_move.ids,
                'active_model': 'account.move',
            },
        }

    def return_products(self):
        return {
                'name': 'Return All',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'pos.return',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {
                            'default_pos_id': self.id,
                             },
                }

    def edit_appointment(self):
        if self.appt_sale_id:
            return {
                'name': _('Orders'),
                'res_model': 'appointment.appointment',
                'view_mode': 'form',
                'res_id': self.appt_sale_id.id,
                'type': 'ir.actions.act_window',
            }


class PosReturn(models.TransientModel):
    _name = "pos.return"
    _rec_name = "pos_id"
    _description = 'POS Return'

    pos_id = fields.Many2one('pos.order', string='PoS')
    po_return_lines = fields.One2many('pos.return.line', 'pos_return_id', string='Order Details')
    return_reason = fields.Text(string="Return Reason")
    view_returned_qty = fields.Boolean(string="View Returned Info")
    payment_method_id = fields.Many2one('pos.payment.method',string="Payment Method")
    payment_inv = fields.Boolean(string="Payment ",help="Used to invisible and required the payment method")
    return_qty_inv = fields.Boolean(string="Return Qty",help="help to invisible the return qty in lines")
    # used to invisible the payment method 28-07-22
    @api.onchange('po_return_lines')
    def action_update_payment(self):
        if self.po_return_lines.filtered(lambda x: x.selections == True):
            self.payment_inv = True
        else:
            self.payment_inv = False

    def action_return_confirm(self):
              
        invoice_lines = []
        # used to filter the selected item products 14-7-22
        return_products = self.po_return_lines.filtered(lambda x: x.selections == True)
        stock_update_lines = self.po_return_lines.filtered(lambda x: x.selections == True and x.pos_line_id.product_id.type == 'product')
        amount_total = sum(amt.price_subtotal_incl for amt in self.po_return_lines if amt.selections == True)
        if return_products:
        # create the credit for the customer 15-07-22
            if self.payment_method_id:
                if self.payment_method_id.credit_jr:   
                    self.pos_id.partner_id.CreateCreditPartner(self.pos_id.partner_id, amount_total)
                else:
                    self.action_payment_entries()
            # elif self.payment_method_id.credit_jr
            for line in self.po_return_lines:
                # raise warning if qty exceed reserved qty 15-07-22
                if line.return_qty >= line.reserved_qty and line.selections == True:
                    raise UserError(_('Returning more than or equal to reserved quantity is prohibited. \n Product Name - %s' % (line.pos_line_id.product_id.name)))

                qty_count = line.reserved_qty - line.return_qty
                if line.qty > qty_count  and line.selections == True:
                    raise UserError(_('Returning more than or equal to reserved quantity is prohibited. \n Product Name - %s' % (line.pos_line_id.product_id.name)))

        for stock_prod in stock_update_lines:
            """This function transfers stock to storable product"""            
            stock_move_lines_updates = []
            # used to get the location in picking type master 14-07-22
            get_picking_type_id = self.env['stock.picking.type'].search([('pos_return','=',True),('company_id', '=', self.pos_id.company_id.id)],limit=1)
            # used to get the source location in stock location master 14-07-22
            get_src_location_id = self.env['stock.location'].search([('usage','=','customer'),('company_id','=',self.pos_id.company_id.id)],limit=1)
            # used to get the destination location in stock location master 14-7-22
            get_dest_location_id = self.env['stock.location'].search([('usage','=','internal'),('company_id','=',self.pos_id.company_id.id)],limit=1)            

            quantity = stock_prod.qty
            # update the line item values 15-07-22
            stock_move_lines_updates.append((0, 0, {
                'name': stock_prod.pos_line_id.product_id.name,
                'product_id': stock_prod.pos_line_id.product_id.id,
                'product_uom': stock_prod.pos_line_id.product_id.uom_id.id,
                'product_uom_qty': quantity,
                'location_id':  get_picking_type_id.default_location_src_id.id or get_src_location_id.id,
                'location_dest_id': get_picking_type_id.default_location_dest_id.id or get_dest_location_id.id,
            }))
            # create the stock 15-07-22
            stock_picking_update = self.env['stock.picking'].create({
                'partner_id': self.pos_id.partner_id.id,
                'picking_type_id': get_picking_type_id.id,
                'origin': self.pos_id.name,
                'location_id': get_picking_type_id.default_location_src_id.id or get_src_location_id.id,
                'scheduled_date': fields.Datetime.now(),
                'date_done': fields.Datetime.now(),
                'location_dest_id': get_picking_type_id.default_location_dest_id.id or get_dest_location_id.id,
                'move_lines': stock_move_lines_updates,
                'return_order':True
            })
            # update the done qty values 15-07-22
            for move in stock_picking_update.move_lines:
                move.quantity_done = move.product_uom_qty
            # call the base validate function14-7-22
            stock_picking_update.button_validate()
        self.action_update_rtn_qty()
        # to Unhide the return remarks tab 26-07-22
        self.pos_id.return_inv = True

        # used for captured the return remarks in pos 26-07-22
        product_name = []
        for pos_line in self.po_return_lines.filtered(lambda x: x.selections == True):
            product_name.append(pos_line.full_product_name + ' - '+ str(pos_line.qty))
        create_return_remarks = self.env['return.order.reason'].create({
            'name':self.return_reason,
            'reason_date':datetime.today(),
            'reason_id':self.pos_id.id,
            'return_product_info':product_name
            })
        
            # stock_picking_update.button_validate()
          
        # for line in self.po_return_lines:
        #     if line.selections:

        #         price_subtotal_incl = price_subtotal_incl + line.pos_line_id.price_subtotal_incl
        #         invoice_lines.append([0, 0, {
        #             'product_id': line.pos_line_id.product_id.id,
        #             'quantity': line.pos_line_id.qty,
        #             'price_unit': line.pos_line_id.price_unit,
        #             'price_subtotal': line.pos_line_id.price_subtotal_incl,
        #             'tax_ids': line.pos_line_id.tax_ids_after_fiscal_position.ids,
        #         }])

        # journal_id = self.env['account.journal'].search([('type', '=', "sale"),('company_id','=',self.env.company.id)],limit=1)
        # credit_note = self.env['account.move'].create({
        #         'partner_id': self.pos_id.partner_id.id,
        #         # 'pricelist_id': self.pos_id.pricelist_id.id,
        #         'invoice_date': self.pos_id.pos_order_date,
        #         'journal_id': journal_id.id,
        #         'move_type': 'out_refund',
        #         'invoice_line_ids': invoice_lines,
        # })


            # lines.append([0, 0, {
                #                     'apt_service_category': line.pos_line_id.apt_service_category.id,
                #                     'full_product_name': line.pos_line_id.full_product_name,
                #                     'product_id': line.pos_line_id.product_id.id,
                #                     'price_subtotal': line.pos_line_id.price_subtotal,
                #                     'price_subtotal_incl':line.pos_line_id.price_subtotal_incl,
                #                     'commission_recipient':line.pos_line_id.commission_recipient,
                #                     'discount': line.pos_line_id.discount,
                #                     'absolute_discount': line.pos_line_id.absolute_discount,
                #                     'tax_ids': line.pos_line_id.tax_ids.ids,
                #                     'tax_ids_after_fiscal_position': line.pos_line_id.tax_ids_after_fiscal_position.ids,
                #                     'name': line.pos_line_id.product_id.name,
                #                     'appt_line_id': line.pos_line_id.appt_line_id.id,
                #                     'appointment_set_id': line.pos_line_id.appointment_set_id.id,
                #                     'qty': line.qty * -1,
                #                     'price_unit': line.pos_line_id.price_unit,
                #                     'session_remaining': line.pos_line_id.session_remaining,
                #                     'amount_discount': line.pos_line_id.amount_discount,
                #                     'amount_tax': line.pos_line_id.amount_tax * -1,
                #                     'price_subtotal_incl': line.pos_line_id.price_subtotal_incl * -1,
                #                 }])

        # print('pos_lines',pos_lines)
        # print('self.pos_id,',self.pos_id)
        # sale_id = self.env['pos.order'].create({
        #             'partner_id': self.pos_id.partner_id.id,
        #             'pricelist_id': self.pos_id.pricelist_id.id,
        #             'appt_sale_id': self.pos_id.appt_sale_id.id,
        #             'session_id': self.pos_id.session_id.id,
        #             'session_type': self.pos_id.session_type,
        #             'amount_tax': self.pos_id.amount_tax * -1,
        #             'amount_paid': price_subtotal_incl * -1,
        #             'amount_return': 0.0,
        #             'amount_total': price_subtotal_incl * -1,
        #             'state': 'draft',
        #             'booking_type': self.pos_id.booking_type,
        #             'sale_type_for': self.pos_id.sale_type_for,
        #             'apt_booking_date': self.pos_id.apt_booking_date,
        #             'apt_booked_by': self.pos_id.apt_booked_by.id,
        #             'company_id': self.pos_id.company_id.id,
        #             'pos_ref': self.pos_id.name,
        #             'pos_reference': self.pos_id.payment_method_id.name,
        #             'cheque':self.pos_id.payment_method_id,
        #             'payment_method_id': self.pos_id.payment_method_id,
        #             'lines': pos_lines,
        #         })
    # update the return qty value 18-07-22   
    def action_update_rtn_qty(self):
        get_pos = self.env['pos.order'].search([('name','=',self.pos_id.name)])
        for line in get_pos.lines:
            for rec in self.po_return_lines.filtered(lambda x: x.selections == True):
                if line.product_id.id == rec.pos_line_id.product_id.id and line.id == rec.pos_line_id.id:
                    update_qty = line.return_qty + rec.qty
                    line.update({
                        'return_qty':update_qty
                        })

    @api.onchange('pos_id')
    def onchange_project(self):
        if self.pos_id.lines:
            lines = [(5, 0, 0)]
            for line in self.pos_id.lines:
                if line.return_qty > 0:
                    self.return_qty_inv = True
                # update the quantity if partial return 15-07-22
                get_return_stock_order = self.env['stock.picking'].search([('origin','=',self.pos_id.name),('return_order','=',True)])
            
                if get_return_stock_order:
                    get_quantity = sum(stock.quantity_done for stock in get_return_stock_order.move_lines if stock.product_id == line.product_id)

                    if  get_quantity:
                        quantity = get_quantity
                    else:
                        quantity = line.qty
            
                else:
                    quantity = 0.0
                val = {
                    'pos_line_id': line.id,
                    'full_product_name': line.full_product_name,
                    'appointment_set_id': line.appointment_set_id.id,
                    'qty': line.qty,
                    'price_unit': line.price_unit,
                    'session_remaining': line.session_remaining,
                    'amount_discount': line.amount_discount,
                    'rtn_discount_amount': line.amount_discount,
                    'amount_tax': line.amount_tax,
                    'price_subtotal_incl': line.price_subtotal_incl,
                    'reserved_qty':line.qty,
                    'return_qty':line.return_qty
                }
                lines.append((0, 0, val))
            self.po_return_lines = lines

# create the journal entries based on the payment type 27-07-22

    def action_payment_entries(self):
        for rec in self:
            amount_total = sum(amt.price_subtotal_incl for amt in self.po_return_lines if amt.selections == True) 
            debit_vals = {
                'debit': abs(amount_total),
                'credit': 0.0,
                'partner_id':self.pos_id.partner_id.id,
                'account_id': self.pos_id.partner_id.property_account_receivable_id.id,
            }
            credit_vals = {
                'debit': 0.0,
                'credit': abs(amount_total),
                'account_id': self.payment_method_id.receivable_account_id.id,
                'partner_id':self.pos_id.partner_id.id,
            }
            payment_name = rec.payment_method_id.name
            vals = {
                'state': 'draft',
                'move_type':'entry',
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)],
                "ref":'Refund Transfer'+'-'+ payment_name
            }
            move = self.env['account.move'].create(vals)
            move.action_post()

class PosReturnLine(models.TransientModel):
    _name = "pos.return.line"
    _description = 'POS Return Line'

    pos_return_id = fields.Many2one('pos.return', string='PoS Return ID')
    pos_line_id = fields.Many2one('pos.order.line', string='PoS Line')
    selections = fields.Boolean(string='Select')
    full_product_name = fields.Char("FULL PRODUCT NAME")
    appointment_set_id = fields.Many2one('appointment.appointment','APPOINTMENT')
    qty = fields.Float('QUANTITY')
    price_unit = fields.Float('UNIT PRICE')
    session_remaining = fields.Char('SESSION REMAINING')
    amount_discount = fields.Float('DISCOUNT VALUE')
    rtn_discount_amount = fields.Float(string="Discount")
    amount_tax = fields.Float('TAX VALUE')
    price_subtotal_incl = fields.Float('SUBTOTAL',compute="call_subtoal")
    return_qty = fields.Float(string="Return Qty")
    reserved_qty = fields.Float(string="Reserved Qty")
    return_amt = fields.Float(string="Return Amount",compute="_compute_call_return_amount")
    returnd_amount = fields.Float(string="Returned Amount",compute="_compute_returned_amt")

    @api.depends('qty')
    def _compute_call_return_amount(self):
        for rec in self:
            amt = (rec.qty * rec.price_unit) - rec.amount_discount
            rec.return_amt = amt + rec.amount_tax 
    
    # calculate the return quantity amount based on the discount 27-09-22
    @api.depends('return_qty')
    def _compute_returned_amt(self):
        self.returnd_amount = 0.0
        for rec in self:
            if rec.return_qty:
                disc = rec.rtn_discount_amount/rec.reserved_qty
                ret_qty = (rec.return_qty * rec.price_unit) - disc* rec.return_qty
                tax_amt = (rec.price_unit * rec.return_qty)*5/100
                rec.returnd_amount = ret_qty + tax_amt
   
    @api.onchange('qty')
    def pass_qty(self):
        for rec in self:
            # calculate the discount amount value 27-09-22
            disc = rec.rtn_discount_amount/rec.reserved_qty
            rec.amount_discount = rec.qty * disc
            if rec.qty > rec.reserved_qty:
                raise UserError(_('A quantity greater than the reserved quantity is prohibited.'))
    @api.depends('qty')
    def call_subtoal(self):
        for rec in self:
            if rec.qty < 0:
                raise UserError(_('Quantity values must be positive....'))

            price = rec.price_unit * rec.qty
            rec.amount_tax =price * 5 /100
            amount_overall = price - rec.amount_discount
            rec.price_subtotal_incl = amount_overall + rec.amount_tax




class PosConfig(models.Model):
    _inherit = "pos.config"

    pos_auto_invoice = fields.Boolean('POS auto invoice', help='POS auto to checked to invoice button', default=1)
    user_ids = fields.Many2many('res.users', string='Users')

    @api.model
    def generate_crm_pipeline_link(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url').rstrip('/')
        action_id = self.env['ir.actions.act_window'].search([('name', '=', 'Pipeline')], order='id asc', limit=1)
        menu_id = self.env['ir.ui.menu'].search([('name', '=', 'My Center')], order='id asc', limit=1)
        url = base_url + '/web?#action=' + str(action_id.id) + '&model=crm.lead&view_type=kanban&cids=1&menu_id=' + str(menu_id.id)
        return url
        
class PosSession(models.Model):
    _inherit = 'pos.session'

    def action_view_order(self):
        return {
            'name': _('Orders'),
            'res_model': 'pos.order',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('point_of_sale.view_pos_order_tree_no_session_id').id, 'tree'),
                (self.env.ref('point_of_sale.view_pos_pos_form').id, 'form'),
            ],
            'type': 'ir.actions.act_window',
            'domain': [('session_id', 'in', self.ids)],
            'context': {'search_default_order_today': 1},
        }

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    pos_return = fields.Boolean(string="Pos Return",help="Used to get the source and destination location while return in appointment.")

    # Raise waring if pos return true in two same company records 14-7-22
    @api.constrains('pos_return')
    def pos_return_validation(self):
        get_pos_return = self.env['stock.picking.type'].search([('pos_return','=',True)])
        if len(get_pos_return) > 1 and  get_pos_return.company_id == self.company_id:
            raise UserError(_('The Pos Return has already been marked as true.'))

class StockPicking(models.Model):
    _inherit = "stock.picking"

    return_order = fields.Boolean(string="Return Order",help="used for return order")

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"
    return_qty = fields.Float(string="Return Qty")

class ReturnOrderReason(models.Model):
    _name = "return.order.reason"

    name = fields.Text(string="Reason")
    reason_id = fields.Many2one('pos.order',string="Reason ID")
    reason_date = fields.Datetime(string="Date")
    return_product_info = fields.Text(string="Return Product Info")
