# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _ , tools
from odoo.exceptions import RedirectWarning, UserError, ValidationError ,Warning
import random
import base64
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from collections import defaultdict
from odoo.tools import float_is_zero


class PosSessionInherit(models.Model):
	_inherit = 'pos.session'

	@api.model
	def create(self, vals):
		res = super(PosSessionInherit, self).create(vals)
		orders = self.env['pos.order'].search([('user_id', '=', self.env.uid),
			('state', '=', 'draft'),('session_id.state', '=', 'closed')])
		orders.write({'session_id': res.id})
		return res

	def action_pos_session_closing_control(self):
		self._check_pos_session_balance()
		for session in self:
			orders = session.order_ids.filtered(lambda order: order.is_partial == False)
			if any(order.state == 'draft' for order in orders):
				raise UserError(_("You cannot close the POS when orders are still in draft"))
			if session.state == 'closed':
				raise UserError(_('This session is already closed.'))
			session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
			if not session.config_id.cash_control:
				session.action_pos_session_close()

	def _check_if_no_draft_orders(self):
		draft_orders = self.order_ids.filtered(lambda order: order.state == 'draft')
		do = []
		for i in draft_orders:
			if not i.is_partial :
				do.append(i.name)
		if do:
			raise UserError(_(
					'There are still orders in draft state in the session. '
					'Pay or cancel the following orders to validate the session:\n%s'
				) % ', '.join(do)
			)
		return True
	
	def _custom_reconcile_pos_orders(self):
		order_ids = self.order_ids.filtered(lambda order: order.is_invoiced)
		for order in order_ids:
			move_line_ids = self.move_id.line_ids.filtered(lambda line: line.credit > 0 and not line.reconciled and line.reconcile_pos_id.id == order.id)
			for move_line in move_line_ids:
				if order.account_move and order.account_move.amount_residual > 0:
					order.account_move.js_assign_outstanding_line(move_line.id)
					
					
	def _create_account_move(self):
		""" Create account.move and account.move.line records for this session.

		Side-effects include:
			- setting self.move_id to the created account.move record
			- creating and validating account.bank.statement for cash payments
			- reconciling cash receivable lines, invoice receivable lines and stock output lines
		"""
		journal = self.config_id.journal_id
		# Passing default_journal_id for the calculation of default currency of account move
		# See _get_default_currency in the account/account_move.py.
		account_move = self.env['account.move'].with_context(default_journal_id=journal.id).create({
			'journal_id': journal.id,
			'date': fields.Date.context_today(self),
			'ref': self.name,
		})
		self.write({'move_id': account_move.id})

		data = {}
		data = self._accumulate_amounts(data)
		data = self._create_non_reconciliable_move_lines(data)
		data = self._create_cash_statement_lines_and_cash_move_lines(data)
		data = self._create_invoice_receivable_lines(data)
		data = self._create_stock_output_lines(data)
		data = self._create_balancing_line(data)

		if account_move.line_ids:
			account_move._post()
			
		self._custom_reconcile_pos_orders()
		
	def _accumulate_amounts(self, data):
		# Accumulate the amounts for each accounting lines group
		# Each dict maps `key` -> `amounts`, where `key` is the group key.
		# E.g. `combine_receivables` is derived from pos.payment records
		# in the self.order_ids with group key of the `payment_method_id`
		# field of the pos.payment record.
		amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0}
		tax_amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0, 'base_amount': 0.0, 'base_amount_converted': 0.0}
		split_receivables = defaultdict(amounts)
		split_receivables_cash = defaultdict(amounts)
		combine_receivables = defaultdict(amounts)
		combine_receivables_cash = defaultdict(amounts)
		invoice_receivables = defaultdict(amounts)
		sales = defaultdict(amounts)
		taxes = defaultdict(tax_amounts)
		stock_expense = defaultdict(amounts)
		stock_return = defaultdict(amounts)
		stock_output = defaultdict(amounts)
		rounding_difference = {'amount': 0.0, 'amount_converted': 0.0}
		# Track the receivable lines of the invoiced orders' account moves for reconciliation
		# These receivable lines are reconciled to the corresponding invoice receivable lines
		# of this session's move_id.
		order_account_move_receivable_lines = defaultdict(lambda: self.env['account.move.line'])
		rounded_globally = self.company_id.tax_calculation_rounding_method == 'round_globally'
		i = 1
		for order in self.order_ids:
			# Combine pos receivable lines
			# Separate cash payments for cash reconciliation later.
			paid_amount_credit = 0
			for payment in order.payment_ids:
					amount, date = payment.amount, payment.payment_date
					if not payment.payment_method_id.credit_jr:
						if payment.payment_method_id.split_transactions:
							if payment.payment_method_id.is_cash_count:
								split_receivables_cash[payment] = self._update_amounts(split_receivables_cash[payment], {'amount': amount}, date)
							else:
								split_receivables[payment] = self._update_amounts(split_receivables[payment], {'amount': amount}, date)
						else:
							key = payment.payment_method_id
							if payment.payment_method_id.is_cash_count:
								combine_receivables_cash[key] = self._update_amounts(combine_receivables_cash[key], {'amount': amount}, date)
							else:
								combine_receivables[key] = self._update_amounts(combine_receivables[key], {'amount': amount}, date)
					else:
						if amount > 0:
							paid_amount_credit = paid_amount_credit + amount
						else:
							if payment.payment_method_id.split_transactions:
								if payment.payment_method_id.is_cash_count:
									split_receivables_cash[payment] = self._update_amounts(split_receivables_cash[payment], {'amount': amount}, date)
								else:
									split_receivables[payment] = self._update_amounts(split_receivables[payment], {'amount': amount}, date)
							else:
								key = payment.payment_method_id
								if payment.payment_method_id.is_cash_count:
									combine_receivables_cash[key] = self._update_amounts(combine_receivables_cash[key], {'amount': amount}, date)
								else:
									combine_receivables[key] = self._update_amounts(combine_receivables[key], {'amount': amount}, date)
							

			if order.is_invoiced:
				# Combine invoice receivable lines
				key = order.partner_id
				order._update_credit_amount_invoice(paid_amount_credit)
				if self.config_id.cash_rounding:
					invoice_receivables[key] = self._update_amounts(invoice_receivables[key], {'amount': order.amount_paid}, order.date_order)
				else:
					update_amounts = self._update_amounts(invoice_receivables[i], {'amount': order.amount_paid-paid_amount_credit}, order.date_order)
					update_amounts.update({'partner':key,'pos_id':order.id})
					invoice_receivables.update({i:update_amounts})
					i=i+1;
				# side loop to gather receivable lines by account for reconciliation
				for move_line in order.account_move.line_ids.filtered(lambda aml: aml.account_id.internal_type == 'receivable' and not aml.reconciled):
					order_account_move_receivable_lines[move_line.account_id.id] |= move_line
			else:
				order_taxes = defaultdict(tax_amounts)
				for order_line in order.lines:
					line = self._prepare_line(order_line)
					# Combine sales/refund lines
					sale_key = (
						# account
						line['income_account_id'],
						# sign
						-1 if line['amount'] < 0 else 1,
						# for taxes
						tuple((tax['id'], tax['account_id'], tax['tax_repartition_line_id']) for tax in line['taxes']),
						line['base_tags'],
					)
					sales[sale_key] = self._update_amounts(sales[sale_key], {'amount': line['amount']}, line['date_order'])
					# Combine tax lines
					for tax in line['taxes']:
						tax_key = (tax['account_id'], tax['tax_repartition_line_id'], tax['id'], tuple(tax['tag_ids']))
						order_taxes[tax_key] = self._update_amounts(
							order_taxes[tax_key],
							{'amount': tax['amount'], 'base_amount': tax['base']},
							tax['date_order'],
							round=not rounded_globally
						)
				for tax_key, amounts in order_taxes.items():
					if rounded_globally:
						amounts = self._round_amounts(amounts)
					for amount_key, amount in amounts.items():
						taxes[tax_key][amount_key] += amount

				if self.company_id.anglo_saxon_accounting and order.picking_ids.ids:
					# Combine stock lines
					stock_moves = self.env['stock.move'].sudo().search([
						('picking_id', 'in', order.picking_ids.ids),
						('company_id.anglo_saxon_accounting', '=', True),
						('product_id.categ_id.property_valuation', '=', 'real_time')
					])
					for move in stock_moves:
						exp_key = move.product_id._get_product_accounts()['expense']
						out_key = move.product_id.categ_id.property_stock_account_output_categ_id
						amount = -sum(move.sudo().stock_valuation_layer_ids.mapped('value'))
						stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
						if move.location_id.usage == 'customer':
							stock_return[out_key] = self._update_amounts(stock_return[out_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
						else:
							stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)

				if self.config_id.cash_rounding:
					diff = order.amount_paid - order.amount_total
					rounding_difference = self._update_amounts(rounding_difference, {'amount': diff}, order.date_order)

				# Increasing current partner's customer_rank
				partners = (order.partner_id | order.partner_id.commercial_partner_id)
				partners._increase_rank('customer_rank')

		if self.company_id.anglo_saxon_accounting:
			global_session_pickings = self.picking_ids.filtered(lambda p: not p.pos_order_id)
			if global_session_pickings:
				stock_moves = self.env['stock.move'].sudo().search([
					('picking_id', 'in', global_session_pickings.ids),
					('company_id.anglo_saxon_accounting', '=', True),
					('product_id.categ_id.property_valuation', '=', 'real_time'),
				])
				for move in stock_moves:
					exp_key = move.product_id._get_product_accounts()['expense']
					out_key = move.product_id.categ_id.property_stock_account_output_categ_id
					amount = -sum(move.stock_valuation_layer_ids.mapped('value'))
					stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount}, move.picking_id.date)
					if move.location_id.usage == 'customer':
						stock_return[out_key] = self._update_amounts(stock_return[out_key], {'amount': amount}, move.picking_id.date)
					else:
						stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount}, move.picking_id.date)
		MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)

		data.update({
			'taxes':							   taxes,
			'sales':							   sales,
			'stock_expense':					   stock_expense,
			'split_receivables':				   split_receivables,
			'combine_receivables':				 combine_receivables,
			'split_receivables_cash':			  split_receivables_cash,
			'combine_receivables_cash':			combine_receivables_cash,
			'invoice_receivables':				 invoice_receivables,
			'stock_return':						stock_return,
			'stock_output':						stock_output,
			'order_account_move_receivable_lines': order_account_move_receivable_lines,
			'rounding_difference':				 rounding_difference,
			'MoveLine':							MoveLine
		})
		return data
	
	
	def _create_invoice_receivable_lines(self, data):
		# Create invoice receivable lines for this session's move_id.
		# Keep reference of the invoice receivable lines because
		# they are reconciled with the lines in order_account_move_receivable_lines
		MoveLine = data.get('MoveLine')
		invoice_receivables = data.get('invoice_receivables')

		invoice_receivable_vals = defaultdict(list)
		invoice_receivable_lines = {}
		for partner, amounts in invoice_receivables.items():
			commercial_partner = amounts['partner'].commercial_partner_id
			account_id = commercial_partner.property_account_receivable_id.id
			move_line = self._get_invoice_receivable_vals(account_id, amounts['amount'], amounts['amount_converted'], partner=commercial_partner)
			move_line.update({'reconcile_pos_id': amounts['pos_id']})
			invoice_receivable_vals[commercial_partner].append(move_line)
		for commercial_partner, vals in invoice_receivable_vals.items():
			account_id = commercial_partner.property_account_receivable_id.id
			receivable_lines = MoveLine.create(vals)
			for receivable_line in receivable_lines:
				if (not receivable_line.reconciled):
					if account_id not in invoice_receivable_lines:
						invoice_receivable_lines[account_id] = receivable_line
					else:
						invoice_receivable_lines[account_id] |= receivable_line

		data.update({'invoice_receivable_lines': invoice_receivable_lines})
		return data
