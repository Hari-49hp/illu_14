from odoo import models, api, fields, _

class BulkPayment(models.TransientModel):
    _name = 'bulk.payment'
    _description = 'Bulk Payment'

    partner_id = fields.Many2one('res.partner',string='Partner')
    invoice_type_id = fields.Many2one('account.journal',string='Invoice Type')

    move_type = fields.Selection(selection=[('entry', 'Journal Entry'),('out_invoice', 'Customer Invoice'),\
            ('in_invoice', 'Vendor Bill'),('out_receipt', 'Sales Receipt'),('in_receipt', 'Purchase Receipt'),],\
            string='Invoice Type', default="out_invoice")

    invoice_ids = fields.Many2many('account.move', 'bulk_payment_invoice_ids', string='Invoices')
    auto_reconcile = fields.Boolean('Auto Reconcile',default='True')
    deduct_outstanding = fields.Boolean('Deduce From Outstanding credit')
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id)
    company_currency_id = fields.Many2one('res.currency', readonly=True, string='Currency', related="company_id.currency_id")
    partner_outstanding_amt = fields.Monetary('Amount Due',currency_field='company_currency_id', readonly=True)
    partner_outstanding_ids = fields.Many2many('account.move', 'bulk_payment_partner_outstanding_ids', string='Outstanding Credit')

    remaining_amt = fields.Monetary('Remaining Amount',currency_field='company_currency_id')
    outstand_remaining_amt = fields.Monetary('Remaining Amount',currency_field='company_currency_id')

    @api.onchange('move_type')
    def _onchange_invoice_type_id(self):
        invoice_ids = self.env['account.move'].search([('partner_id','=',self.partner_id.id),\
            ('amount_residual','>',0),('state','=','posted'),('move_type','=',self.move_type)])
        self.write({'invoice_ids':[(6, 0, invoice_ids.ids)]})

    @api.onchange('invoice_ids','deduct_outstanding','partner_outstanding_ids')
    def _onchange_invoice_ids(self):
        self.remaining_amt = 0.0; check_amt = 0.0
        self.outstand_remaining_amt = 0.0
        if self.invoice_ids:
            for i in self.invoice_ids:
                self.remaining_amt += i.amount_residual

        if self.partner_outstanding_ids:
            for i in self.partner_outstanding_ids:
                for j in i.line_ids:
                    check_amt += abs(j.credit)

        if check_amt < self.remaining_amt:
           self.outstand_remaining_amt = self.remaining_amt - check_amt
        else: self.outstand_remaining_amt = 0.0

    def transfer_payment(self):
        from datetime import datetime
        def amt_check():
            amt = 0.0
            for i in self.invoice_ids:
                amt += i.amount_residual
            return amt

        if self.deduct_outstanding == True:
            for line in self.invoice_ids:
                move_line_invoice_id = self.env['account.move.line'].search([('move_id', '=', line.id), ('reconciled', '=', False), ('debit', '>', 0)])
                for i in self.partner_outstanding_ids:
                    move_line_id = self.env['account.move.line'].search([('move_id', '=', i.id), ('reconciled', '=', False), ('credit', '>', 0)])
                    for move_line in move_line_id:
                        if line.amount_residual > 0.0: (move_line + move_line_invoice_id).reconcile()

            if self.outstand_remaining_amt > 0.0:
                payment_id = self.env['account.payment'].create({
                        'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'partner_id': self.partner_id.id,
                        'amount': self.outstand_remaining_amt,
                        'date': datetime.today(),
                        'journal_id': 6,
                        'auto_reconcile': self.auto_reconcile,
                        'deduct_outstanding': False,
                        'invoice_ids': [(6, 0, self.invoice_ids.ids)],
                        'partner_outstanding_ids': [(6, 0, self.partner_outstanding_ids.ids)],
                    })
                payment_id.action_post()
        else:
            if amt_check() > 0:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Payment',
                    'view_mode': 'form',
                    'views': [(False, 'form')],
                    'res_model': 'account.payment',
                    'view_id': 'account.view_account_payment_form',
                    'target': 'new',
                    'context': {
                                'default_partner_id': self.partner_id.id,
                                'default_amount': amt_check(),
                                'default_auto_reconcile': self.auto_reconcile,
                                'default_deduct_outstanding': self.deduct_outstanding,
                                'default_invoice_ids': [(6, 0, self.invoice_ids.ids)],
                                'default_partner_outstanding_ids': [(6, 0, self.partner_outstanding_ids.ids)],
                                }
                }
            

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    auto_reconcile = fields.Boolean('Auto Reconcile')
    deduct_outstanding = fields.Boolean('Deduce From Outstanding credit')
    invoice_ids = fields.Many2many('account.move', 'account_payment_invoice_ids', string='Bulk Payment Invoices')
    partner_outstanding_ids = fields.Many2many('account.move', 'account_payment_partner_outstanding_ids', string='Bulk Payment Outstanding Credit')

    def action_post(self):
        res = super(AccountPayment, self).action_post()

        if self.auto_reconcile == True:
            if self.deduct_outstanding == True:    
                for line in self.invoice_ids:
                    move_line_invoice_id = self.env['account.move.line'].search([('move_id', '=', line.id), ('reconciled', '=', False), ('debit', '>', 0)])
                    for i in self.partner_outstanding_ids:
                        move_line_id = self.env['account.move.line'].search([('move_id', '=', i.id), ('reconciled', '=', False), ('credit', '>', 0)])
                        for move_line in move_line_id:
                            if line.amount_residual > 0.0: self.trans_rec_reconcile_payment(move_line,move_line_invoice_id)
            else:
                payment_id = self.env['account.move.line'].search([('payment_id','=',self.id)],limit=1)
                for line in self.invoice_ids:
                    move_line_invoice_id = self.env['account.move.line'].search([('move_id', '=', line.id), ('reconciled', '=', False), ('debit', '>', 0)])
                    # for i in payment_id:
                    move_line_id = self.env['account.move.line'].search([('move_id', '=', payment_id.move_id.id), ('reconciled', '=', False), ('credit', '>', 0)])
                    for move_line in move_line_id:
                        if line.amount_residual > 0.0: self.trans_rec_reconcile_payment(move_line,move_line_invoice_id)

        return res

    def trans_rec_reconcile_payment(self,line_to_reconcile,payment_line):
        return (line_to_reconcile + payment_line).reconcile()