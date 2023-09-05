# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,tools, api, _
from datetime import date, time, datetime
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)
import psycopg2


class res_partner(models.Model):
    _inherit = 'res.partner'

    custom_credit = fields.Float('Credit')

    def action_view_credit_detail(self):
        self.ensure_one()
        partner_credit_ids = self.env['partner.credit'].search([('partner_id','=',self.id)])
        for payment_id in partner_credit_ids:
            self.env['partner.credit'].browse(payment_id)
            payment_id.do_update()       
        return {
            'name': 'Credit Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'partner.credit',
            'domain': [('partner_id', '=', self.id)],
        }

    def CreateCreditPartner(self, partner_id, credit_amount=False):
        print(partner_id,'partner_idpartner_idpartner_id')
        credit_amount = abs(credit_amount)
        try:
            partner_details = self.env['res.partner'].browse(partner_id['id'])
        except:
            partner_details = self.env['res.partner'].browse(int(partner_id))
        if credit_amount != 0 :
            update_partner_credit_obj = self.env['partner.credit']
            credit  = False
            partner_credit_id =False
            partner_search = update_partner_credit_obj.search([('partner_id','=',partner_details.id)])
            if not partner_search:
                val = {
                    'partner_id': partner_details.id,
                }
                partner_credit_id = update_partner_credit_obj.create(val)
            if partner_search:
                credit = partner_search.id
            else:
                credit = partner_credit_id.id
            update_credit_account_obj = self.env['credit.account']
            amount_vals = {
                'credit_amount':credit_amount,
                'journal_id': 7,
                'partner_id':partner_details.id,
                'credit_id':credit
            }
            credit_account_id = update_credit_account_obj.create(amount_vals)
            _logger.info('@ Newly created partner credit record id :%s',credit_account_id)
            credit_account_id.post()

    def UpdateCredit(self,partner_id , company_id , pos_currency_id , custom_credit):
        pos_curr = self.env['res.currency'].browse(pos_currency_id)
        company_details = self.env['res.company'].browse(company_id[0])
        partner_details = self.env['res.partner'].browse(partner_id['id'])
        res = False
        if(pos_curr.id != company_details.currency_id.id):
            currency_rate  = pos_curr.rate/company_details.currency_id.rate
            new_credit = custom_credit /currency_rate
            credit_update = partner_details.custom_credit - new_credit
            res = partner_details.write({'custom_credit':credit_update})
            # Create the partner credit if the partner pays the extra amount
            return res
        else:
            credit_update = partner_details.custom_credit - (custom_credit)
            res = partner_details.write({'custom_credit':credit_update})
            # Create the partner credit if the partner pays the extra amount
            return res

    def CheckCredit(self,partner_id , company_id , pos_currency_id , custom_credit):
        pos_curr = self.env['res.currency'].browse(pos_currency_id)
        company_details = self.env['res.company'].browse(company_id[0])
        partner_details = self.env['res.partner'].browse(partner_id['id'])
        res = False
        if(pos_curr.id != company_details.currency_id.id):
            currency_rate  = pos_curr.rate/company_details.currency_id.rate
            new_credit = custom_credit /currency_rate
            return new_credit
        else:
            return custom_credit

class partner_credit(models.Model):
    _name = 'partner.credit'
    _description ="partner Credit"

    partner_id = fields.Many2one('res.partner',"Customer")
    credit_jr = fields.Float('Credit', readonly=True)
    update = fields.Float('Update')

    def do_update(self):
        update_credit_history_obj = self.env['update.credit.history']       
        if self.update > 0.00:
            self.credit_jr = self.update
            val = {
                'date_update': datetime.now(),
                'update_credit_amount' : self.update,
                'old_credit_bal': self.partner_id.custom_credit,
                'balance': self.partner_id.custom_credit + self.update,
                'partner_id': self.partner_id.id,
            }
            update_credit_history_obj.create(val)
            self.partner_id.custom_credit = self.partner_id.custom_credit + self.credit_jr
        if self.partner_id.custom_credit != 0.00:  
            self.credit_jr = self.partner_id.custom_credit
        self.update = 0.00                
    
    def open_wizard(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'credit.account',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'default_partner_id': self.partner_id.id,'default_credit_id':self.id},
            } 

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            update = self.partner_id.update 
            return {'credit_jr':update}

class UpdateCreditHistory(models.Model):
    _name = 'update.credit.history'
    _description ="Update Credit History"
    
    date_update = fields.Date('Date')
    update_credit_amount = fields.Float('Update Credit amount')
    old_credit_bal = fields.Float('Old Credit Balance')
    balance = fields.Float('Balance')
    partner_id = fields.Many2one('res.partner', 'Customer')


class UpdateCreditHistoryPayment(models.Model):
    _name = 'update.credit.history.payment'
    _description ="Update Credit History Payment"
    
    date_update = fields.Date('Date')
    update_credit_amount = fields.Float('Update Credit amount')
    old_credit_bal = fields.Float('Old Credit Balance')
    payment_refer = fields.Many2one('account.payment', 'Payment Ref.')
    balance = fields.Float('Balance')
    partner_id = fields.Many2one('res.partner', 'Customer')


class UpdateCreditAccount(models.TransientModel):
    _name = 'credit.account'
    _description = "Credit Account"
    
    credit_amount = fields.Float('Credit Amount',required="True")
    journal_id = fields.Many2one('account.journal', 'Payment Journal',
        required=True,domain=[('type','in',['cash','bank']),('credit_jr','=',False)])
    credit_id = fields.Many2one('partner.credit', 'Customer')
    partner_id = fields.Many2one('res.partner', 'Customer')
    
    def post(self):

        account_payment_obj = self.env['account.payment']
        update_credit_payment_history_obj = self.env['update.credit.history.payment']
        
        date_now = datetime.strftime(datetime.now(), '%Y-%m-%d')
        
        vals = {}
        
        vals = {
            'name' : self.env['ir.sequence'].with_context(ir_sequence_date=date_now).next_by_code('account.payment.customer.invoice'),
            'payment_type' : "inbound",
            'amount' : self.credit_amount,
            #'move' : account_payment_obj._create_payment_entry(amount),
            # 'communication' : "Credit Recharge",
            'date' : datetime.now().date(),
            'journal_id' : self.journal_id.id,
            'payment_method_id': 1,
            'partner_type': 'customer',
            'partner_id': self.partner_id.id,
        }
        
        payment_create = account_payment_obj.create(vals)
        payment_create.action_post()
        if self.credit_id.credit_jr >= 0.00:
            self.credit_id.credit_jr = payment_create.amount
            value = {
                'date_update': datetime.now(),
                'update_credit_amount' : self.credit_id.credit_jr,
                'old_credit_bal': self.partner_id.custom_credit,
                'balance': self.partner_id.custom_credit + self.credit_id.credit_jr,
                'partner_id': self.partner_id.id,
                'payment_refer' : payment_create.id,
            }
            update_credit_payment_history_obj.create(value)
            self.partner_id.custom_credit = self.partner_id.custom_credit + self.credit_id.credit_jr
        
        if self.partner_id.custom_credit != 0.00:
            self.credit_id.credit_jr = self.partner_id.custom_credit
            
        return

