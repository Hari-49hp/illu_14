from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    appointment_ref_id = fields.Many2one('appointment.appointment',string='appointments')
    manual_entries = fields.Boolean(string='Manual Entries')
    payment_method = fields.Char(string="Payment Method",help="mode of payment",compute='_compute_payment_method',store=True)
    package_status = fields.Text(string="Package Status",compute="_compute_get_appointment")
    apt_color = fields.Boolean(string="Apt",help="Help to show the color based on appointment packages")
    return_all_inv = fields.Boolean(string="Return All",compute="_compute_get_appointment",help="Help to invisible the return all button")
    return_status = fields.Selection([('none','None'),('partial','Partially Returned'),('returned','Fully Returned')],default='none',string="Return Status",compute="action_calculate_return_status")
    pos_payment_ref = fields.Char(string='POS Payment Ref.')
    sale_id = fields.Many2one('sale.order',string="Sale Order")
    desc_update = fields.Char(string="Descriptions",compute="_compute_update_description")

    def _compute_update_description(self):
        self.desc_update = ''
        if self.sale_id:
            desc = self.sale_id.order_line.mapped('name')[0]
            # update the name in customer account
            for rec in self.line_ids:
                rec.name = desc   
            # customer account end
            # update the name in journal entries         
            account_id = self.env['account.move'].search([('move_type','=','entry'),('ref','=',self.name)])
            for lines in account_id.line_ids:
                lines.name = str(desc)
            self.desc_update =desc

    def action_return_all(self):
        get_pos_id = self.env['pos.order'].search([('name','=',self.ref)],limit=1)
        if get_pos_id.state == "invoiced":
            return {
                    'name': 'Return All',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'pos.return',
                    'target': 'new',
                    'type': 'ir.actions.act_window',
                    'context': {
                                'default_pos_id': get_pos_id.id,
                                 },
                    }
      
    @api.depends('state','payment_id','pos_order_ids')
    def _compute_payment_method(self):
        method = []
        for each_invoice in self:
            # each_invoice.payment_method = ''
            # pass the pos order payment status 08-07-22
            if self.pos_order_ids:
                each_invoice.payment_method = self.pos_order_ids[0].payment_methods
            else:
                each_invoice.payment_method = ""
    # get the appointment package status using compute 11-08-22
    def _compute_get_appointment(self):
        for rec in self:
            rec.package_status = ''
            rec.return_all_inv = False
            get_pos_id = self.env['pos.order'].search([('name','=',rec.ref)],limit=1)
            if get_pos_id.state == "invoiced":
                rec.return_all_inv = True

            if get_pos_id.appt_sale_id:
                get_used_count = get_pos_id.appt_sale_id.appointment_line_id.filtered(lambda x: x.state_line == 'confirm')
                if get_used_count:
                    rec.apt_color = True 
                    rec.package_status = str(len(get_used_count)) +' '+'Used'       
                else:
                    rec.package_status = 'Not Used'

    def action_calculate_return_status(self):
         for rec in self:
            rec.return_status = "none"
            get_pos_id = self.env['pos.order'].search([('name','=',rec.ref)],limit=1)
            return_qty = sum(pos.return_qty for pos in get_pos_id.lines)
            quantity = sum(line.qty for line in get_pos_id.lines)
            if get_pos_id:
                if quantity == return_qty:
                    rec.return_status = 'returned'
                elif return_qty == 0:
                    rec.return_status = 'none'
                else:
                    rec.return_status = "partial"



    
    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.appointment_ref_id:
            self.appointment_ref_id.invoice_id = self.id
        return res

    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
                'default_appointment_id': self.appointment_ref_id.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    manual_entries = fields.Boolean(string='Manual Entries',related='move_id.manual_entries')


class AccountMoveLine(models.Model):
    _inherit="account.move.line"

    tax_amt = fields.Float(string="VAT",compute="_compute_call_tax_amount")
    # calculate the tax amount 11-08-22
    @api.depends('quantity','price_unit','amount_discount','tax_ids')
    def _compute_call_tax_amount(self):
        for rec in self:
            if rec.tax_ids:
                amount = (rec.price_unit * rec.quantity) - rec.amount_discount
                rec.tax_amt = rec.price_total - amount
            else:
                rec.tax_amt = 0.0
