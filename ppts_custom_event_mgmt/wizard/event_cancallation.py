from datetime import date, datetime, timedelta, time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class EventCancellation(models.TransientModel):
    _name = "event.cancellation"
    _description = 'Event Cancellation'

    eve_cancellation_type = fields.Selection([('early', 'Early Cancel'), ('late', 'Late Cancel')], string='Method')
    # cancel_reason_id = fields.Many2one('appointment.cancel.reason',string="Reason")
    event_cancel_charge = fields.Float(string="Cancellation Charge")
    event_id = fields.Many2one('event.registration',string="Event ID")
    cancel_options = fields.Selection([('now', 'Apply Now'), ('ignore', 'Ignore Charges')], string='Cancellation Policy')
    note = fields.Text("Note")

    #to calculate cancellation due
    @api.onchange('eve_cancellation_type')
    def _onchange_cancel_types(self):
        if self.eve_cancellation_type=='early':
            self.event_cancel_charge = 0.0
        else:
            self.event_cancel_charge = self.event_id.event_id.eve_cancel_charge

    # create the invoice for while cancel the event without payment 13-06-22
    def confirm_event_cancel(self):
        active_id = self._context.get('active_id')
        rec = self.env["event.registration"].browse(active_id)
        if self.eve_cancellation_type == 'late' and self.cancel_options == 'now':
            get_service_product = self.env['product.product'].search([('name','=','Cancellation Charges')],limit=1)
            line_vals=[]
            if rec.event_payment_status == 'no_paid':
                    vals = [0,0, {

                    'product_id':get_service_product.id,
                    'quantity':1,
                    'product_uom_id':get_service_product.uom_id.id,
                    'price_unit':self.event_cancel_charge,

                    }]
                    line_vals.append(vals)
            if line_vals:
                create_customer_invoice = self.env['account.move'].create({
                    'move_type':'out_invoice',
                    'state':'draft',
                    'partner_id':rec.partner_id.id,
                    'payment_reference':rec.event_id.event_seq,
                    'invoice_line_ids':line_vals
                    })
        # change state to cancel
        # rec.write({
        #     'state':'cancel',
        #     })
        can_id = self.env['event.registration'].search([('event_id','=',self.event_id.id),('state','=','draft'),('expire','=',False)],order="id asc")
        for i in can_id:
            i.write({
                'total_expire_can': True
            })
        rec.expiry_mail_cron_end()
        rec.action_cancel()
        rec.cancel_notes = self.note

        # create the credit note for remaining customer balance
        jour_vals=[]
        if rec.event_payment_status == 'paid' and self.cancel_options == 'now':
            cancel_amount = rec.ticket_price - self.event_cancel_charge
            rec.partner_id.CreateCreditPartner(rec.partner_id.id, cancel_amount)

            # create the journal entries for cancellation
            bal_amount = rec.pos_order_id.amount_paid - cancel_amount
            get_account_cancel_id = self.env['account.account'].search([('name','=','Cancellation Charges')],limit=1)
            get_bank_id = self.env['account.journal'].search([('type','=','bank')],limit=1)
            debit_vals = {

            'account_id':get_account_cancel_id.id,
            'partner_id':rec.partner_id.id,
            'debit':bal_amount,
            'credit':0.00

            }
            jour_vals.append(debit_vals)
            credit_vals = {

            'account_id':rec.partner_id.property_account_receivable_id.id,
            'partner_id':rec.partner_id.id,
            'credit':bal_amount,
            'debit':0.00
            }

            jour_vals.append(credit_vals)
            if jour_vals:
                create_journal_entries = self.env['account.move'].create({
                    'move_type':'entry',
                    'journal_id':get_bank_id.id,
                    'line_ids':[(0, 0, debit_vals), (0, 0, credit_vals)]
                    })
                create_journal_entries.action_post()





        

