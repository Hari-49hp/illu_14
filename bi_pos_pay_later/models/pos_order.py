# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _ , tools
from odoo.exceptions import Warning
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import random
import psycopg2
import base64
from odoo.http import request
from functools import partial
from odoo.tools import float_is_zero

from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import logging

_logger = logging.getLogger(__name__)


def float_round(amount_total, precision_rounding, rounding_method):
	pass


class POSPayment(models.Model):
    _inherit = 'pos.payment'

    credit_journal_id = fields.Many2one('account.move', string='Journal')


class PosOrderInherit(models.Model):
	_inherit = 'pos.order'

	def _default_session(self):
		return self.env['pos.session'].search([('state', '=', 'opened'), ('user_id', '=', self.env.uid)], limit=1)


	is_partial = fields.Boolean('Is Partial Payment')
	amount_due = fields.Float("Amount Due",compute="get_amount_due")

	@api.depends('amount_total','amount_paid')
	def get_amount_due(self):
		for order in self :
			order.amount_due = 0
			if order.amount_paid - order.amount_total > 0 and order.amount_paid - order.amount_total == 0:
				order.amount_due = 0
				order.is_partial = False
			else:
				order.amount_due = order.amount_total - order.amount_paid
				
	def write(self, vals):
		for order in self:
			if order.name == '/' and order.is_partial :
				vals['name'] = order.config_id.sequence_id._next()
		return super(PosOrderInherit, self).write(vals)

	def _is_pos_order_paid(self):
		return float_is_zero(self._get_rounded_amount(self.amount_total) - self.amount_paid, precision_rounding=self.currency_id.rounding)

	def action_pos_order_paid(self):
		self.ensure_one()
		if not self.is_partial:
			return super(PosOrderInherit, self).action_pos_order_paid()
		if self.is_partial:
			if not self.config_id.cash_rounding:
				total = self.amount_total
			else:
				total = float_round(self.amount_total, precision_rounding=self.config_id.rounding_method.rounding, rounding_method=self.config_id.rounding_method.rounding_method)

			if  self._is_pos_order_paid():
				self.write({'state': 'paid'})
				if self.picking_ids:
					return True
				else :
					return self._create_order_picking()
			else:
				if not self.picking_ids :
					return self._create_order_picking()
				else:
					return False

	@api.model
	def _order_fields(self, ui_order):
		res = super(PosOrderInherit, self)._order_fields(ui_order)
		process_line = partial(self.env['pos.order.line']._order_line_fields, session_id=ui_order['pos_session_id'])
		if 'is_partial' in ui_order:
			res['is_partial'] = ui_order.get('is_partial',False) 
			res['amount_due'] = ui_order.get('amount_due',0.0) 
		return res
	
	
	def _credit_amounts(self, partial_move_line_vals, amount, amount_converted, force_company_currency=False):
		additional_field = {
			'amount_currency': -amount,
			'currency_id': self.pricelist_id.currency_id.id,
		}
		return {
			'debit': -amount_converted if amount_converted < 0.0 else 0.0,
			'credit': amount_converted if amount_converted > 0.0 else 0.0,
			'reconcile_pos_id':self.id,
			**partial_move_line_vals,
			**additional_field,
		}

	def _debit_amounts(self, partial_move_line_vals, amount, amount_converted, force_company_currency=False):
		""" `partial_move_line_vals` is completed by `debit`ing the given amounts.

		See _credit_amounts docs for more details.
		"""
		additional_field = {
			'amount_currency': amount,
			'currency_id': self.pricelist_id.currency_id.id,
		}
		return {
			'debit': amount_converted if amount_converted > 0.0 else 0.0,
			'credit': -amount_converted if amount_converted < 0.0 else 0.0,
			**partial_move_line_vals,
			**additional_field,
		}
		

	def _get_debit_vals(self, payment_method, move_id, amount, amount_converted):
		partial_vals = {
			'account_id': payment_method.receivable_account_id.id,
			'move_id': move_id.id,
			'name': '%s - %s' % (self.name, payment_method.name)
		}
		return self._debit_amounts(partial_vals, amount, amount_converted)

	def _get_credit_vals(self, move_id, amount, amount_converted):
		partial_vals = {
			'account_id': self.partner_id.commercial_partner_id.property_account_receivable_id.id,
			'move_id': move_id.id,
			'name': 'From invoiced orders',
			'partner_id': self.partner_id.id,
		}
		return self._credit_amounts(partial_vals, amount, amount_converted)
	
	def _update_credit_amount_invoice(self, credit):
		
		
		reconciled_line_ids = []
		
		for partial, amount, counterpart_line in self.account_move._get_reconciled_invoices_partials():
			reconciled_line_ids.append(counterpart_line.id)
			self.account_move.js_remove_outstanding_partial(partial.id)
		
		if self.is_invoiced and credit != 0:
			self.account_move.update({'invoice_line_ids': [(0, 0, {
				'move_id': self.account_move.id,
				'quantity': 1,
				'name': 'Credit',
				'price_unit': - float(credit),
				'account_id': self.env['account.account'].search([('internal_type', '=', 'other')], limit=1).id,
			})]
			})
			
		for reconciled_line_id in reconciled_line_ids:
			self.account_move.js_assign_outstanding_line(reconciled_line_id)
			
		
	def _create_credit_journals(self):
		journal_ids = self.env['account.payment'].search([('partner_id','=', self.partner_id.id), ('state','=','posted'), ('partner_type','=','customer'), ('payment_type','=','inbound')]).mapped("move_id")
		move_line_ids = journal_ids.line_ids.filtered(lambda line: line.credit > 0 and not line.reconciled)
		if move_line_ids:
			payment_ids = self.payment_ids.filtered(lambda rec: rec.payment_method_id.credit_jr and not rec.credit_journal_id and rec.amount > 0)
			if payment_ids:
				journal_account_move = self.env['account.move'].with_context(default_journal_id=payment_ids[0].payment_method_id.cash_journal_id.id).create({
					'journal_id': payment_ids[0].payment_method_id.cash_journal_id.id,
					'date': fields.Date.context_today(self),
					'ref': self.name,
				})
				
				total_amount = sum(payment_ids.mapped('amount'))
				MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)
				to_do_reconciles = []
				for reccon_move_line in move_line_ids:
					if total_amount:
						to_do_reconciles.append(reccon_move_line)
						recon_amount = total_amount if total_amount <= reccon_move_line.credit else reccon_move_line.credit
						total_amount = total_amount - recon_amount
						MoveLine.create({'account_id':reccon_move_line.move_id.journal_id.payment_debit_account_id.id, 'move_id': journal_account_move.id, 'name':self.name, 'amount_currency': -recon_amount, 'currency_id': self.pricelist_id.currency_id.id,
										'partner_id': self.partner_id.id,'name': 'From invoiced orders','debit': -recon_amount if recon_amount < 0.0 else 0.0,'credit': recon_amount if recon_amount > 0.0 else 0.0,})
						MoveLine.create({'account_id':reccon_move_line.account_id.id, 'move_id': journal_account_move.id, 'name':self.name, 'amount_currency': recon_amount, 'currency_id': self.pricelist_id.currency_id.id,
										'partner_id': self.partner_id.id,'name': 'From invoiced orders','debit': recon_amount if recon_amount > 0.0 else 0.0,'credit': -recon_amount if recon_amount < 0.0 else 0.0,})
					else:
						break;
					
				if journal_account_move.state == "draft":
					print(journal_account_move)
					journal_account_move.action_post()
					payment_ids.write({'credit_journal_id':journal_account_move.id})
					
					for to_do_reconcile in to_do_reconciles:
						if not to_do_reconcile.reconciled:
							journal_account_move.js_assign_outstanding_line(to_do_reconcile.id)
							
	
		
		
	
	
	@api.model
	def create_from_ui(self, orders, draft=False):
		""" Create and update Orders from the frontend PoS application.

		Create new orders and update orders that are in draft status. If an order already exists with a status
		diferent from 'draft'it will be discareded, otherwise it will be saved to the database. If saved with
		'draft' status the order can be overwritten later by this function.

		:param orders: dictionary with the orders to be created.
		:type orders: dict.
		:param draft: Indicate if the orders are ment to be finalised or temporarily saved.
		:type draft: bool.
		:Returns: list -- list of db-ids for the created and updated orders.
		"""
		order_ids = super(PosOrderInherit, self).create_from_ui(orders, draft=False)
		for order in orders:
			existing_order = False
			if 'server_id' in order['data']:
				existing_order = self.env['pos.order'].search(['|', ('id', '=', order['data']['server_id']), ('pos_reference', '=', order['data']['name'])], limit=1)
			if (existing_order and existing_order.state != 'draft' and order['data']['statement_ids']) or not existing_order:
				self._process_order(order, draft, existing_order)
			
			if existing_order and existing_order.session_id.state == 'closed' and existing_order.is_invoiced and order['data']['statement_ids']:
    # partial payment after closing session
				prec_acc = existing_order.pricelist_id.currency_id.decimal_places
				journal = existing_order.session_id.config_id.journal_id
				journal_account_move = self.env['account.move'].with_context(default_journal_id=journal.id).create({
			    	'journal_id': journal.id,
			    	'date': fields.Date.context_today(self),
			    	'ref': existing_order.session_id.name,
			    })
				
				paid_amount_credit = 0
				for payments in order['data']['statement_ids']:
					payment_id = self.env['pos.payment.method'].browse(payments[2]['payment_method_id'])
					if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):
						if not payment_id.credit_jr:
							MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)
							MoveLine.create(existing_order._get_debit_vals(payment_id, journal_account_move, payments[2]['amount'], payments[2]['amount']))
							MoveLine.create(existing_order._get_credit_vals(journal_account_move, payments[2]['amount'], payments[2]['amount']))
							if journal_account_move.state == 'draft':
								journal_account_move.action_post()
							move_line_ids = journal_account_move.line_ids.filtered(lambda line: line.credit > 0 and not line.reconciled and line.reconcile_pos_id.id == existing_order.id)
							for move_line in move_line_ids:
								if existing_order.account_move and existing_order.account_move.amount_residual > 0:
									existing_order.account_move.js_assign_outstanding_line(move_line.id)
						else:
							if payments[2]['amount'] > 0:
								paid_amount_credit = paid_amount_credit + payments[2]['amount']
				if paid_amount_credit > 0:
					existing_order._update_credit_amount_invoice(paid_amount_credit)

			if 'server_id' in order['data']:
				existing_order = self.env['pos.order'].search(['|', ('id', '=', order['data']['server_id']), ('pos_reference', '=', order['data']['name'])], limit=1)
			
				if existing_order:
					existing_order._create_credit_journals()
					ref = ""
					if existing_order.is_partial and existing_order.is_invoiced:
						for payment_line in existing_order.payment_ids:
							ref = ref+("/" if ref else "")+payment_line.payment_method_id.name 
					if ref:	
						existing_order.account_move.pos_payment_ref = ref +" : "+str(existing_order.amount_paid)
					
								
      # else:
      #
      # 	journal_ids = self.env['account.payment'].search([('partner_id','=', existing_order.partner_id.id), ('state','=','posted'), ('partner_type','=','customer'), ('payment_type','=','inbound')]).mapped("move_id")
      #
      # 	move_line_ids = journal_ids.line_ids.filtered(lambda line: line.credit > 0 and not line.reconciled)
      #
      # 	for move_line in move_line_ids:
      # 		if existing_order.account_move and existing_order.account_move.amount_residual > 0:
      # 			existing_order.account_move.js_assign_outstanding_line(move_line.id)
							
					

		return order_ids

	@api.model
	def _process_order(self, order, draft, existing_order):
		"""Create or update an pos.order from a given dictionary.

		:param dict order: dictionary representing the order.
		:param bool draft: Indicate that the pos_order is not validated yet.
		:param existing_order: order to be updated or False.
		:type existing_order: pos.order.
		:returns: id of created/updated pos.order
		:rtype: int
		"""
		order = order['data']
		is_partial = order.get('is_partial')
		is_draft_order = order.get('is_draft_order')
		is_paying_partial = order.get('is_paying_partial')

		pos_session = self.env['pos.session'].browse(order['pos_session_id'])
		if pos_session.state == 'closing_control' or pos_session.state == 'closed':
			order['pos_session_id'] = self._get_valid_session(order).id

		pos_order = False
		if is_paying_partial:
			pos_order = self.search([('pos_reference', '=', order.get('name'))])
			for pos in pos_order:
				if order['amount_total'] == pos.amount_total:
					pos_order = pos
		else:
			if not existing_order:
				pos_order = self.create(self._order_fields(order))
			else:
				pos_order = existing_order
				pos_order.lines.unlink()
				order['user_id'] = pos_order.user_id.id
				pos_order.write(self._order_fields(order))

		pos_order = pos_order.with_company(pos_order.company_id)
		self = self.with_company(pos_order.company_id)
		self._process_payment_lines(order, pos_order, pos_session, draft)

		try:
			pos_order.action_pos_order_paid()
		except psycopg2.DatabaseError:
			# do not hide transactional errors, the order(s) won't be saved!
			raise
		except Exception as e:
			_logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

		if pos_order.is_partial == False and is_paying_partial == False:
			pos_order._create_order_picking()
		if order.get('to_invoice') and (pos_order.is_partial or pos_order.state == 'paid') and not pos_order.is_invoiced:
			pos_order.action_pos_order_invoice()
		elif pos_order.is_invoiced and pos_order.state != 'invoiced':
			pos_order.state = 'invoiced'
			
			
		return pos_order.id


	def _process_payment_lines(self, pos_order, order, pos_session, draft):
		"""Create account.bank.statement.lines from the dictionary given to the parent function.

		If the payment_line is an updated version of an existing one, the existing payment_line will first be
		removed before making a new one.
		:param pos_order: dictionary representing the order.
		:type pos_order: dict.
		:param order: Order object the payment lines should belong to.
		:type order: pos.order
		:param pos_session: PoS session the order was created in.
		:type pos_session: pos.session
		:param draft: Indicate that the pos_order is not validated yet.
		:type draft: bool.
		"""
		prec_acc = order.pricelist_id.currency_id.decimal_places

		order_bank_statement_lines= self.env['pos.payment'].search([('pos_order_id', '=', order.id)])
		is_paying_partial = pos_order.get('is_paying_partial')
		if not is_paying_partial:
			order_bank_statement_lines.unlink()
		for payments in pos_order['statement_ids']:
			if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):
				order.add_payment(self._payment_fields(order, payments[2]))

		order.amount_paid = sum(order.payment_ids.mapped('amount'))

		if order.amount_paid >= order.amount_total :
			order.write({
				'is_partial' : False,
			})

		if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
			cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
			if not cash_payment_method:
				raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
			return_payment_vals = {
				'name': _('return'),
				'pos_order_id': order.id,
				'amount': -pos_order['amount_return'],
				'payment_date': fields.Date.context_today(self),
				'payment_method_id': cash_payment_method.id,
				'is_change': True,
			}
			order.add_payment(return_payment_vals)
