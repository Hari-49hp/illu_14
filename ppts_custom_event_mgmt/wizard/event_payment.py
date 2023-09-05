from datetime import date, datetime, timedelta, time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class EventPaymentConfirmation(models.TransientModel):
    _name = "event.payment.confirmation"
    _description = 'Event Payment Confirmation'

    event_id = fields.Many2one('event.registration', string='Event Registration')
    company_id = fields.Many2one('res.company', string='Venue', change_default=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")

    
    # if click pay later button it will redirect to respective customers 01-08-22
    def pay_later(self):
        get_partner_id = self.env['res.partner'].search([('id', '=', self.event_id.partner_id.id)])
        form_view_id = self.env.ref('custom_partner.res_partner_history_history_from_view').id
        if get_partner_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Client'),
                'res_model': 'res.partner',
                'res_id': get_partner_id.id,
                'view_mode': 'form',
                'views': [[form_view_id, 'form']],
                
                    }

    def pay_now(self):
        payrate = self.event_id.ticket_price

        # return {
        #         'type': 'ir.actions.act_window',
        #         'name': _('Pay Now'),
        #         'res_model': 'event.registration.confirmation',
        #         'target': 'new',
        #         'view_mode': 'form',
        #         'view_type': 'form',
        #         'context': {
        #                     'default_event_id':self.event_id.id,
        #                     'default_partner_id':self.event_id.partner_id.id
        #                 },
        #     }
        
        def product_tax(product_id, amount):
            if product_id:
                total_included = 0
                for tax in product_id.taxes_id:
                    taxes = tax.compute_all(amount, self.currency_id, 1, product=product_id.id, partner=False)
                    t2 = taxes['total_included'] - amount
                    total_included += t2
                return total_included

        if self.event_id.pos_order_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Dashboard',
                'view_mode': 'kanban,tree,form',
                'res_model': 'pos.config',
            } 
        else:
            lst = []
            if self.event_id.event_ticket_id:
                lst.append([0, 0, {
                            # 'full_product_name':self.appointments_id.appointments_type_id.product_id.name,
                            'product_id': self.event_id.event_ticket_id.product_id.id,
                            'qty':1,
                            'price_subtotal': self.event_id.event_ticket_id.price,
                            'price_subtotal_incl': payrate + product_tax(self.event_id.event_ticket_id.product_id, payrate),
                            'discount':self.event_id.event_ticket_id.disc_rate,
                            'price_unit': self.event_id.event_ticket_id.price,
                            'name': self.event_id.event_ticket_id.name,
                        }])
       

        #     if self.appointments_id.topay_cancellation_charge > 0 and self.appointments_id.cancel_options == 'now':
        #         product_id = self.env['product.product'].search([('name','=','Cancellation Charges')],limit=1)
        #         lst.append([0, 0,{
        #             'full_product_name': product_id.name,
        #             'product_id': product_id.id,
        #             'qty': 1,
        #             'price_subtotal': self.appointments_id.topay_cancellation_charge,
        #             'price_subtotal_incl': self.appointments_id.topay_cancellation_charge + product_tax(product_id, self.appointments_id.topay_cancellation_charge),
        #             'discount': 0,
        #             'price_unit': self.appointments_id.topay_cancellation_charge,
        #             'name': self.appointments_id.note_cancellation_charge,
        #             'default_product': True,
        #         }])

        #     if self.appointments_id.topay_no_show_charges > 0 and self.appointments_id.noshow_options == 'now':
        #             product_id = self.env['product.product'].search([('name','=','No Show Charges')],limit=1)
        #             lst.append([0, 0,{
        #                 'full_product_name': product_id.name,
        #                 'product_id': product_id.id,
        #                 'qty': 1,
        #                 'price_subtotal': self.appointments_id.topay_no_show_charges,
        #                 'price_subtotal_incl': self.appointments_id.topay_no_show_charges + product_tax(product_id, self.appointments_id.topay_no_show_charges),
        #                 'discount': self.appointments_id.single_discount,
        #                 'price_unit': self.appointments_id.topay_no_show_charges,
        #                 'name': self.appointments_id.note_no_show,
        #                 'default_product': True,
        #             }])
            CONFIRM = self.env['event.registration.confirmation']
            CONFT = CONFIRM.search([('event_id','=',self.event_id.id)],limit=1)
            def con_return(ap_id):
                return {
                        'type': 'ir.actions.act_window',
                        'name': _('Pay Now'),
                        'res_model': 'event.registration.confirmation',
                        'res_id': ap_id,
                        'target': 'new',
                        'view_mode': 'form',
                        'view_type': 'form',
                       # 'context': {
                       #      'default_event_id':self.event_id.id,
                       #      'default_partner_id':self.event_id.partner_id.id
                       #  },
                }
            if CONFT:
                CONFT.product_categ_id = CONFT.qty = 1
                CONFT.product_id = False
                CONFT.price_unit = CONFT.discount = 0.0
                CONFT.discount_type = 'percentage'
                # CONFT.quick_invoice_sms = 'Please pay your %s invoice bill of %s %s/appointment/ccavenue/request/%s' % (self.appointments_id.name, str(payrate.unit_price + product_tax(self.appointments_id.appointments_type_id.product_id, payrate.unit_price)) ,base_url, str(self.appointments_id.id))
                return con_return(CONFT.id)
            else:

                conf_id = CONFIRM.create({
                    'event_id': self.event_id.id,
                    'partner_id': self.event_id.partner_id.id,
                    'product_categ_id': 1,
                    # 'quick_invoice_sms': 'Please pay your %s invoice bill of %s %sappointment/ccavenue/request/%s' % (self.appointments_id.name, str(payrate.unit_price + product_tax(self.appointments_id.appointments_type_id.product_id, payrate.unit_price)) ,base_url, str(self.appointments_id.id)),
                    'lines': lst,
                })
                return con_return(conf_id.id)
        #     # base_url=self.env ['ir.config_parameter'].sudo ().get_param ('web.base.url')
        #     if CONFT:
        #         CONFT.product_categ_id = CONFT.qty = 1
        #         CONFT.product_id = False
        #         CONFT.price_unit = CONFT.discount = 0.0
        #         CONFT.discount_type = 'percentage'
        #         # CONFT.quick_invoice_sms = 'Please pay your %s invoice bill of %s %s/appointment/ccavenue/request/%s' % (self.appointments_id.name, str(payrate.unit_price + product_tax(self.appointments_id.appointments_type_id.product_id, payrate.unit_price)) ,base_url, str(self.appointments_id.id))
        #         return con_return(CONFT.id)

        #     else:
        #         conf_id = CONFIRM.create({
        #             'appointments_id': self.appointments_id.id,
        #             'partner_id': self.appointments_id.partner_id.id,
        #             'product_categ_id': 1,
        #             # 'quick_invoice_sms': 'Please pay your %s invoice bill of %s %sappointment/ccavenue/request/%s' % (self.appointments_id.name, str(payrate.unit_price + product_tax(self.appointments_id.appointments_type_id.product_id, payrate.unit_price)) ,base_url, str(self.appointments_id.id)),
        #             'lines': lst,
        #         })
        #         return con_return(conf_id.id)
