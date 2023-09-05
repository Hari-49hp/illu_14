# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PartnerCreditTransfer(models.TransientModel):
    _name = 'partner.credit.transfer'
    _description = 'Partner Credit Transfer'

    # @api.depends('from_partner_id')
    # def _compute_set_credit(self):
    #   self.total_due = 0
    #   account_types = []
    #   receivable_type = self.env.ref('account.data_account_type_receivable').id
    #   payable_type = self.env.ref('account.data_account_type_payable').id
    #   account_types.extend([receivable_type, payable_type])
    #   domain = [('partner_id', '=', self.from_partner_id.id), ('amount_residual', '!=', 0),
    #             ('account_id.user_type_id', 'in', account_types)]
    #   domain += [('move_id.state', '=', 'posted')]
    #   customer_balance = sum([x.amount_residual for x in self.env['account.move.line'].search(domain)])
    #   self.total_due = abs(customer_balance) if customer_balance < 0 else 0
    #   return self.total_due

    @api.depends('from_partner_id')
    def _compute_set_credit(self):
        if self.from_partner_id:
            self.total_due = self.from_partner_id.customer_balance

    from_partner_id = fields.Many2one('res.partner',string="From Client")
    from_partner_account = fields.Many2one('account.account',string="From Account",related="from_partner_id.property_account_receivable_id")

    to_partner_id = fields.Many2one('res.partner',string="To Client",required=True)
    to_partner_account = fields.Many2one('account.account',string="To Account",related="to_partner_id.property_account_receivable_id")

    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env.user.company_id.currency_id)
    total_due = fields.Monetary('Available Amount',compute="_compute_set_credit",store=True) #,related="from_partner_id.total_due"
    transfer_amount = fields.Monetary('Enter Amount',required=True)
    count_seq = fields.Integer()
    tax_ids = fields.Many2many('account.account.tag',string='Taxes')

    def transfer(self):
        if self.transfer_amount > self.total_due:
            raise UserError(_("Transfer amount should not be greater than Available Amount"))
        if self.transfer_amount > 0 and self.total_due > 0:
            debit_vals = {
                'debit': abs(self.transfer_amount),
                'credit': 0.0,
                'partner_id':self.from_partner_id.id,
                'account_id': self.from_partner_account.id,
                'tax_tag_ids': self.tax_ids.ids,
            }
            credit_vals = {
                'debit': 0.0,
                'credit': abs(self.transfer_amount),
                'account_id': self.to_partner_account.id,
                'partner_id':self.to_partner_id.id,
                'tax_tag_ids': self.tax_ids.ids,
            }
            transfer_journal_id = self.env['account.journal'].search([('code', '=', "PT")])
            vals = {
                'journal_id': transfer_journal_id.id,
                'state': 'draft',
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)],
                "ref":"Credit Partner Transfer"
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
            self.from_partner_id.custom_credit = self.from_partner_id.custom_credit - self.transfer_amount
            if self.to_partner_id.customer_balance >= 0:
                update_partner_credit_obj = self.env['partner.credit']
            
                partner_search = update_partner_credit_obj.search([('partner_id','=',self.to_partner_id.id)])
                if not partner_search:
                    val = {
                        'partner_id': self.to_partner_id.id,
                    }
                else:
                    val = {
                        'partner_id': self.to_partner_id.id,
                    }
                partner_credit_id = update_partner_credit_obj.create(val)
                if partner_search:
                    credit = partner_search.id
                else:
                    credit = partner_credit_id.id
                update_credit_account_obj = self.env['credit.account']
                # amount_vals = {
                #     'credit_amount':self.transfer_amount,
                #     'journal_id': 7,
                #     'partner_id':self.to_partner_id.id,
                #     'credit_id':credit
                # }
                # credit_account_id = update_credit_account_obj.create(amount_vals)
                # credit_account_id.post()
        else: 
            raise UserError(_("Outstanding and Transfer amount should not be zero or less than zero"))


        
