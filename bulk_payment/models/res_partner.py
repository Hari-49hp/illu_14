# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def bulk_payment_partner(self):
        invoice_ids = self.env['account.move'].search([('partner_id','=',self.id),('amount_residual','>',0),\
            ('payment_state','in',['not_paid','in_payment','partial']),('state','=','posted'),('journal_id','=',1),\
            ('move_type','=','out_invoice')])

        invoice_ref_ids = self.env['account.move'].search([('partner_id','=',self.id),('amount_residual','>',0),\
            ('payment_state','in',['not_paid','in_payment','partial']),('state','=','posted'),('journal_id','=',1),\
            ('move_type','=','out_invoice')],limit=1)

        payment_move = []; customer_balance = 0.0
        if invoice_ref_ids:
            for move in invoice_ref_ids:
                move.invoice_outstanding_credits_debits_widget = json.dumps(False)
                move.invoice_has_outstanding = False

                if move.state != 'posted' \
                        or move.payment_state not in ('not_paid', 'partial') \
                        or not move.is_invoice(include_receipts=True):
                    continue

                pay_term_lines = move.line_ids\
                    .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

                domain = [
                    ('account_id', 'in', pay_term_lines.account_id.ids),
                    ('move_id.state', '=', 'posted'),
                    ('partner_id', '=', move.commercial_partner_id.id),
                    ('reconciled', '=', False),
                    '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
                ]

                payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

                if move.is_inbound():
                    domain.append(('balance', '<', 0.0))
                    payments_widget_vals['title'] = _('Outstanding credits')
                else:
                    domain.append(('balance', '>', 0.0))
                    payments_widget_vals['title'] = _('Outstanding debits')

                for line in self.env['account.move.line'].search(domain):

                    if line.currency_id == move.currency_id:
                        # Same foreign currency.
                        amount = abs(line.amount_residual_currency)
                    else:
                        # Different foreign currencies.
                        amount = move.company_currency_id._convert(
                            abs(line.amount_residual),
                            move.currency_id,
                            move.company_id,
                            line.date,
                        )

                    if move.currency_id.is_zero(amount):
                        continue

                    payments_widget_vals['content'].append({
                        'journal_name': line.ref or line.move_id.name,
                        'amount': amount,
                        'currency': move.currency_id.symbol,
                        'id': line.id,
                        'move_id': line.move_id.id,
                        'position': move.currency_id.position,
                        'digits': [69, move.currency_id.decimal_places],
                        'payment_date': fields.Date.to_string(line.date),
                    })

                if payments_widget_vals['content']:
                    for i in payments_widget_vals['content']:
                        payment_move.append(int(i['move_id']))
                        
                else:
                    continue
        for i in invoice_ids:
            customer_balance += i.amount_residual

        return {
                'type': 'ir.actions.act_window',
                'name': _('Bulk Payment'),
                'res_model': 'bulk.payment',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                            'default_partner_id': self.id,
                            'default_invoice_type_id': 1,
                            'default_invoice_ids': invoice_ids.ids,
                            'default_partner_outstanding_ids': payment_move,
                            'default_partner_outstanding_amt': customer_balance,
                            'default_remaining_amt': customer_balance,
                            },
                }
