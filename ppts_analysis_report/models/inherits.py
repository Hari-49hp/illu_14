from odoo import api, fields, models, _
from datetime import date, timedelta, datetime


class CustomAppointments(models.Model):
    _inherit = 'appointment.appointment'

    @api.model
    def create(self, vals):
        res = super(CustomAppointments, self).create(vals)
        att_service = self.env['attendance.service.category'].search([])
        att_service.create({
            'apt_id': res.id,
            'name': res.partner_id.id,
            'visit_type_id': res.du_service_categ_id.id,
            'expiry_date': res.expiry_date,
            'visit_rem': 1,
            'staff': res.sales_rep_id.id,
            'visit_location': res.company_id.id,
            'booking_mode': res.booking_mode,
        })

        return res


class PosOrder(models.Model):
    _inherit = "pos.order"

    sales_rep_id = fields.Many2one('res.users', string="Sale ID")

    @api.model
    def create(self, vals):
        rec = super(PosOrder, self).create(vals)
        report_summary = self.env['sales.report.summary'].search([])
        report_summary.create({
            'pos_id': rec.id,
            'sale_date': rec.date_order,           
            })
        if rec.appt_sale_id:
            service = self.env['sales.service.detail'].search([])
            service.create({'apt_id': rec.appt_sale_id.id,
                            'location_id': rec.company_id.id,
                            'sub_category_id': rec.appt_sale_id.appointments_type_id.id,
                            'client': rec.partner_id.id,
                            'mobile': rec.partner_id.mobile,
                            'detail_sale_date': rec.appt_sale_id.booking_date,
                            'activation_date': rec.appt_sale_id.creation_date,
                            'exp_date': rec.appt_sale_id.booking_date,
                            'service_id': rec.appt_sale_id.du_service_categ_id.id,
                            'cash_equal': rec.amount_paid,
                            'total_amount': rec.amount_total,
                            'non_cash_equal': rec.amount_total - rec.amount_paid,
                            'quantity': len(rec.lines),
                            })
        if rec.user_id:
            rep_summary = self.env['sales.rep.summary'].search([])
            rep_summary.create({
                'sales_rep_id': rec.user_id.id,
                'date': rec.date_order,
                'company_id': rec.company_id.id,
                'sub_total': rec.amount_total,
                'vat': rec.amount_tax,
                'total': rec.amount_paid,
            })
            for obj in rec.lines:
                if obj.price_subtotal_incl:
                    rep_detail = self.env['sales.rep.detail'].search([])
                    rep_detail.create({
                        'pos_id': rec.id,
                        'client': rec.partner_id.id,
                        'sale_date': rec.date_order,
                        'location_id': rec.company_id.id,
                        'sales_rep_id': rec.user_id.id,
                        'date': rec.date_order,
                        'company_id': rec.company_id.id,
                        'item_name': obj.product_id.name,
                        'item_price': obj.price_unit,
                        'category_id': obj.product_id.pos_categ_id.id,
                        'quantity': obj.qty,
                        'sub_total': obj.price_unit,
                        'vat': obj.amount_tax,
                        'total': obj.price_subtotal_incl,
                        'discount': obj.discount,
                        'discount_amount': obj.amount_discount,
                    })

        if rec.appt_sale_id and rec.appt_sale_id.session_type == 'type_single':
            for obj in rec.lines:
                if obj.price_subtotal_incl:
                    detail = self.env['sales.report.detail'].search([])
                    detail.create({'pos_id': rec.id,
                                   'apt_id': rec.appt_sale_id.id,
                                   'detail_sale_date': rec.date_order,
                                   'location': rec.company_id.id,
                                   'client': rec.partner_id.id,
                                   'sale_id': rec.appt_sale_id.sequence,
                                   'item_id': obj.product_id.name,
                                   'item_price': obj.price_unit,
                                   'quantity': obj.qty,
                                   'sub_total': obj.price_subtotal_incl,
                                   'vat': obj.amount_tax,
                                   'item_total': obj.price_subtotal,
                                   'discount': obj.discount,
                                   'total_paid': rec.amount_paid,
                                   })
        elif rec.appt_sale_id and rec.appt_sale_id.session_type == 'type_package':
            detail = self.env['sales.report.detail'].search([])
            detail.create({'pos_id': rec.id,
                           'apt_id': rec.appt_sale_id.id,
                           'detail_sale_date': rec.date_order,
                           'location': rec.company_id.id,
                           'client': rec.partner_id.id,
                           'sale_id': rec.appt_sale_id.sequence,
                           'item_total': rec.amount_total,
                           'total_paid': rec.amount_paid,
                           })

        elif rec.event_reg_id:
            for obj in rec.lines:
                if obj.price_subtotal_incl:
                    detail = self.env['sales.report.detail'].search([])
                    detail.create({'pos_id': rec.id,
                                   'detail_sale_date': rec.date_order,
                                   'location': rec.company_id.id,
                                   'client': rec.partner_id.id,
                                   'sale_id': rec.event_reg_id.event_id.name,
                                   'item_id': obj.product_id.name,
                                   'item_price': obj.price_unit,
                                   'quantity': obj.qty,
                                   'sub_total': obj.price_subtotal_incl,
                                   'vat': obj.amount_tax,
                                   'discount': obj.discount,
                                   'item_total': rec.amount_total,
                                   'total_paid': rec.amount_paid,
                                   })
        else:
            for obj in rec.lines:
                if obj.price_subtotal_incl:
                    detail = self.env['sales.report.detail'].search([])
                    detail.create({
                        'pos_id': rec.id,
                        'detail_sale_date': rec.date_order,
                        'location': rec.company_id.id,
                        'client': rec.partner_id.id,
                        'sale_id': rec.name,
                        'item_id': obj.product_id.name,
                        'item_price': obj.price_unit,
                        'quantity': obj.qty,
                        'sub_total': obj.price_subtotal_incl,
                        'vat': obj.amount_tax,
                        'discount': obj.discount,
                        'item_total': obj.price_subtotal,
                        'total_paid': rec.amount_paid,
                    })
        for obj in rec.lines:
            service_summary = self.env['sales.service.summary'].search([])
            service_summary.create({'pos_id': rec.id,
                                    'apt_id': rec.appt_sale_id.id,
                                    'sub_category_id': rec.appt_sale_id.appointments_type_id.id,
                                    'quantity': obj.qty,
                                    'date': rec.appt_sale_id.booking_date,
                                    'service_id': rec.appt_sale_id.du_service_categ_id.id,
                                    'total_amount': obj.price_subtotal,
                                    'cash_equal': rec.amount_paid,
                                    'non_cash_equal': rec.amount_total - rec.amount_paid,
                                    })

            # voided_summary = self.env['voided.sales.summary'].search([])
            # voided_summary.create({'pos_id': rec.id,
            #                        'apt_id': rec.appt_sale_id.id,
            #                        'sale_date': rec.appt_sale_id.booking_date,
            #                        'total': rec.amount_total})

            seller_detail = self.env['best.sellers.detail'].search([])
            seller_detail.create({'sale_id': rec.id,
                                  'client': rec.partner_id.id,
                                  'date': rec.date_order,
                                  'location_id': rec.company_id.id,
                                  'qty': obj.qty,
                                  'total': rec.amount_total,
                                  'product_id': obj.product_id.id,
                                  'pos_categ_id': obj.product_id.pos_categ_id.id,
                                  })

            client_view = self.env['client.view'].search([])
            client_view.create({'pos_id': rec.id,
                                'apt_id': rec.appt_sale_id.id,
                                'name': rec.appt_sale_id.partner_id.id,
                                'date': rec.date_order,
                                'time': rec.appt_sale_id.time_slot_id.start_time,
                                'visit_serv_categ_id': rec.appt_sale_id.du_service_categ_id.id,
                                'visit_type_id': rec.appt_sale_id.du_service_categ_id.id,
                                'type_id': rec.appt_sale_id.appointments_type_id.id,
                                'expiry_date': rec.appt_sale_id.expiry_date,
                                'visit_rem': 1,
                                'staff': rec.appt_sale_id.sales_rep_id.id,
                                'visit_location': rec.appt_sale_id.company_id.id,
                                'booking_mode': rec.appt_sale_id.booking_mode,
                                })

            tax = self.env['sales.tax.detail'].search([])
            tax.create({
                'pos_id': rec.id,
                # 'sale_id': rec.order_id.id,
                'item_id': obj.product_id.id,
                'client': rec.partner_id.id,
                'date': rec.date_order,
                'location_id': rec.company_id.id,
                'qty': obj.qty,
                'vat': obj.amount_tax,
                'total': obj.amount_tax,
            })

            taxes = self.env['sales.tax.summary'].search([])
            taxes.create({'pos_id': rec.id,
                          'apt_id': rec.appt_sale_id.id,
                          'location_id': rec.appt_sale_id.company_id.id,
                          'date': rec.date_order,
                          'vat': obj.amount_tax,
                          'total': obj.amount_tax,
                          })

            seller_summary = self.env['best.sellers.summary'].search([])
            seller_summary.create({'pos_id': rec.id,
                                   'product_id': obj.product_id.id,
                                   'qty': obj.qty,
                                   'total': obj.price_subtotal_incl,
                                   'date': rec.date_order,
                                   'cogs': 0.00,
                                   'margin': 100,
                                   'pos_categ_id': obj.product_id.pos_categ_id.id,
                                   'type': obj.product_id.type,
                                   'product_service': obj.product_id.type,
                                   })
            if rec.appt_sale_id:
                att_summary = self.env['attendance.summary'].search([])
                att_summary.create({
                    'pos_id':rec.id,
                    'sale_id':rec.appt_sale_id.id,
                    'date':rec.date_order,
                    'time':rec.appt_sale_id.time_slot_id.start_time,
                    'visit_serv_categ_id':rec.appt_sale_id.du_service_categ_id.name,
                    'staff_id':rec.appt_sale_id.sales_rep_id.id,
                    'type_id':rec.appt_sale_id.appointments_type_id.name,
                    'visit_type_id':rec.appt_sale_id.du_service_categ_id.name,
                    'visit_location':rec.appt_sale_id.company_id.id,
                    'members_revenue':0.00,
                    'total_revenue':rec.amount_total,
                })
                att_staff = self.env['attendance.staff'].search([])
                att_staff.create({
                    'pos_id': rec.id,
                    'apt_id': rec.appt_sale_id.id,
                    'date': rec.date_order,
                    'time': rec.appt_sale_id.time_slot_id.start_time,
                    'client': rec.partner_id.id,
                    'visit_serv_categ_id': rec.appt_sale_id.du_service_categ_id.name,
                    'staff_id': rec.appt_sale_id.sales_rep_id.id,
                    'pricing_option_id': rec.appt_sale_id.appointments_type_id.name,
                    'visit_type_id': rec.appt_sale_id.du_service_categ_id.name,
                    'visit_location': rec.appt_sale_id.company_id.id,
                    'expiry_date': rec.appt_sale_id.expiry_date,
                    'visit_rem': 1,
                    'booking_mode': rec.appt_sale_id.booking_mode,
                })
                att_date = self.env['attendance.date'].search([])
                att_date.create({
                    'pos_id': rec.id,
                    'apt_id': rec.appt_sale_id.id,
                    'date': rec.date_order,
                    'time': rec.appt_sale_id.time_slot_id.start_time,
                    'client': rec.partner_id.id,
                    'visit_serv_categ_id': rec.appt_sale_id.du_service_categ_id.name,
                    'staff_id': rec.appt_sale_id.sales_rep_id.id,
                    'pricing_option_id': rec.appt_sale_id.appointments_type_id.name,
                    'visit_type_id': rec.appt_sale_id.du_service_categ_id.name,
                    'visit_location': rec.appt_sale_id.company_id.id,
                    'expiry_date': rec.appt_sale_id.expiry_date,
                    'visit_rem': 1,
                    'booking_mode': rec.appt_sale_id.booking_mode,
                })
                att_visit_type = self.env['attendance.visit.type'].search([])
                att_visit_type.create({
                    'pos_id': rec.id,
                    'apt_id': rec.appt_sale_id.id,
                    'date': rec.date_order,
                    'time': rec.appt_sale_id.time_slot_id.start_time,
                    'client': rec.partner_id.id,
                    'visit_serv_categ_id': rec.appt_sale_id.du_service_categ_id.name,
                    'staff_id': rec.appt_sale_id.sales_rep_id.id,
                    'pricing_option_id': rec.appt_sale_id.appointments_type_id.name,
                    'visit_type_id': rec.appt_sale_id.du_service_categ_id.name,
                    'visit_location': rec.appt_sale_id.company_id.id,
                    'expiry_date': rec.appt_sale_id.expiry_date,
                    'visit_rem': 1,
                    'booking_mode': rec.appt_sale_id.booking_mode,
                })
                att_noshow = self.env['attendance.noshow.cancels'].search([])
                att_noshow.create({
                    'pos_id': rec.id,
                    'apt_id': rec.appt_sale_id.id,
                    'date': rec.date_order,
                    'time': rec.appt_sale_id.time_slot_id.start_time,
                    'client': rec.partner_id.id,
                    'visit_serv_categ_id': rec.appt_sale_id.du_service_categ_id.name,
                    'staff_id': rec.appt_sale_id.sales_rep_id.id,
                    'pricing_option_id': rec.appt_sale_id.appointments_type_id.name,
                    'visit_type_id': rec.appt_sale_id.du_service_categ_id.name,
                    'visit_location': rec.appt_sale_id.company_id.id,
                    'expiry_date': rec.appt_sale_id.expiry_date,
                    'visit_rem': 1,
                    'booking_mode': rec.appt_sale_id.booking_mode,
                })

        return rec


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.model
    def create(self, vals):
        record = super(PosOrderLine, self).create(vals)
        for rec in record:
            if rec.price_subtotal_incl:
                report = self.env['sales.product.detail'].search([])
                report.create({'pos_id': rec.id,
                               'product_id': rec.product_id.id,
                               'client': rec.order_id.partner_id.id,
                               'sale_date': rec.order_id.date_order,
                               'location_id': rec.order_id.company_id.id,
                               'unit_price': rec.price_unit,
                               'qty': rec.qty,
                               'total': rec.price_subtotal_incl,
                               'cash_equal': rec.price_subtotal_incl,
                               })
                product_summary = self.env['sales.product.summary'].search([])
                if not rec.product_id == product_summary.product_id.ids:
                    product_summary.create({
                        'product_id': rec.product_id.id,
                        'size': rec.product_id.volume,
                        'barcode': rec.product_id.barcode,
                        'location_id': rec.order_id.company_id.id,
                        'date': rec.order_id.date_order,
                        'qty': rec.qty,
                        'pos_categ_id': rec.product_id.pos_categ_id.id,
                        'total': rec.price_subtotal_incl,
                        'cash_equal': rec.price_subtotal_incl,
                        'non_cash_equal': rec.order_id.amount_total - rec.order_id.amount_paid,
                    })
                # if rec.product_id.appointment_id:
                #     sales_category = self.env['sales.category'].search([])
                #     sales_category.create({
                #         'sub_category_id': rec.product_id.appointment_id.id,
                #         'pos_category_id': rec.product_id.pos_categ_id.id,
                #         'date': rec.order_id.date_order,
                #         # 'sub_total': rec.product_id.price_subtotal,
                #         # 'total': rec.product_id.price_subtotal_incl,
                #     })
                if rec.product_id:
                    sales_category = self.env['sales.category'].search([])
                    sales_category.create({
                        'category_id': rec.product_id.categ_id.id,
                        'pos_category_id': rec.product_id.pos_categ_id.id,
                        'sub_total': rec.price_subtotal,
                        'vat': rec.amount_tax,
                        'total': rec.price_subtotal_incl,
                        'date': rec.order_id.date_order,
                        'user_id': rec.order_id.user_id.id,
                    })

        return record

    # order_ref_id = fields.Char(related='order_id.name')
    # payment_methods = fields.Char('Payment Method', related='order_id.payment_methods')
    # date_order = fields.Datetime(related='order_id.date_order')


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        invoice = super(AccountMove, self).create(vals)
        if invoice.move_type == 'out_invoice':
            inv = self.env['invoice.report'].search([])
            inv.create({'tax_id': invoice.id,
                        'sale_date': invoice.invoice_date,
                        'client': invoice.partner_id.id,
                        'location_id': invoice.company_id.id,
                        'status': invoice.payment_state,
                        'inv_total': invoice.amount_total,
                        })
        return invoice


class AppointmentOrderLine(models.Model):
    _inherit = 'appointment.line.id'

    def action_void_line(self):
        void = super(AppointmentOrderLine, self).action_void_line()
        dic = {'appointment_id': self.id,
               'date': self.void_date,
               'client': self.appointment_id.partner_id.id,
               'sold_by': self.appointment_id.sales_rep_id.id,
               'voided_by': self.appointment_id.sales_rep_id.id,
               'price': self.unit_price,
               'qty': self.unit_qty,
               'sub_total': self.price_subtotal,
               'discount': self.percentage_discount,
               'vat': self.tax_amount,
               }
        approve = self.env['voided.sales.detail'].create(dic)
        voided_summary = self.env['voided.sales.summary'].search([])
        voided_summary.create({
            'appointment_id': self.id,
            'apt_id': self.appointment_id.id,
            'sale_date': self.void_date,
            })
        return void
