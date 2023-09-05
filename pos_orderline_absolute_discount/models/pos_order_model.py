import logging
from datetime import timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv.expression import AND

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    absolute_discount = fields.Float(string=_('Discount amount'), default=0.0, digits=(12, 2))
    amount_discount = fields.Float(string=_('Discount amount'), default=0.0, digits=(12, 2))

class PosOrder(models.Model):
    _inherit = "pos.order"

    amount_discount = fields.Float(string="Discounted Value", default=0.0, store=True)

    @api.depends("lines")
    def _compute_amount_discount_val(self):
        up_sum=0.0
        for rec in self:
            up_sum = sum(line.amount_discount for line in rec.lines)

            rec.amount_discount=up_sum

    @api.model
    def _amount_line_tax(self, line, fiscal_position_id):
        if line.absolute_discount:
            taxes = line.tax_ids.filtered(
                lambda t: t.company_id.id == line.order_id.company_id.id
            )
            if fiscal_position_id:
                taxes = fiscal_position_id.map_tax(
                    taxes, line.product_id, line.order_id.partner_id
                )
            price = line.price_unit - line.absolute_discount
            taxes = taxes.compute_all(
                price,
                line.order_id.pricelist_id.currency_id,
                line.qty,
                product=line.product_id,
                partner=line.order_id.partner_id or False,
            )["taxes"]
            return sum(tax.get("amount", 0.0) for tax in taxes)
        else:
            return super(PosOrder, self)._amount_line_tax(line, fiscal_position_id)


    def _prepare_invoice_line(self, order_line):
        disc_per = 0
        if order_line.price_unit or order_line.absolute_discount:
            disc_per = (order_line.absolute_discount/order_line.price_unit)*100
        return {
            'product_id': order_line.product_id.id,
            'quantity': order_line.qty if self.amount_total >= 0 else -order_line.qty,
            'discount': order_line.discount or disc_per,
            'absolute_discount': order_line.absolute_discount,
            'amount_discount': order_line.amount_discount,
            'price_unit': order_line.price_unit,
            'name': order_line.product_id.display_name,
            'tax_ids': [(6, 0, order_line.tax_ids_after_fiscal_position.ids)],
            'product_uom_id': order_line.product_uom_id.id,
        }

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    absolute_discount = fields.Float(string="Discount per Unit (abs)", default=0.0)

    @api.depends(
        "price_unit", "tax_ids", "qty", "discount", "product_id", "absolute_discount"
    )
    def _compute_amount_discount(self):
        for line in self:
            line.amount_discount = (line.price_unit*line.qty) - line.price_subtotal
            line.amount_tax = line.price_subtotal_incl - line.price_subtotal

    amount_discount = fields.Float(string="Discount Value", default=0.0,compute='_compute_amount_discount',store=True)
    amount_tax = fields.Float(string="Tax Value", default=0.0,compute='_compute_amount_discount',store=True)

    @api.depends("price_unit", "tax_ids", "qty", "discount", "product_id", "absolute_discount")
    def _compute_amount_line_all(self):
        self.ensure_one()
        for line in self:
            fpos = self.order_id.fiscal_position_id
            tax_ids_after_fiscal_position = (fpos.map_tax(self.tax_ids, self.product_id, self.order_id.partner_id)if fpos
                    else self.tax_ids)
            if line.absolute_discount:
                    price = line.price_unit - line.absolute_discount
                    taxes = tax_ids_after_fiscal_position.compute_all(
                        price,
                        line.order_id.pricelist_id.currency_id,
                        line.qty,
                        product=line.product_id,
                        partner=line.order_id.partner_id,
                    )
            else:
                price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
                taxes = tax_ids_after_fiscal_position.compute_all(price, self.order_id.pricelist_id.currency_id, self.qty, product=self.product_id, partner=self.order_id.partner_id)
            return {
                'price_subtotal_incl': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            }



    # @api.depends(
    #     "price_unit", "tax_ids", "qty", "discount", "product_id", "absolute_discount"
    # )
    # def _compute_amount_line_all(self):
    #     super(PosOrderLine, self)._compute_amount_line_all()
    #     for line in self:
    #         fpos = line.order_id.fiscal_position_id
    #         tax_ids_after_fiscal_position = (
    #             fpos.map_tax(line.tax_ids, line.product_id, line.order_id.partner_id)
    #             if fpos
    #             else line.tax_ids
    #         )
    #         if line.absolute_discount:
    #             price = line.price_unit - line.absolute_discount
    #             taxes = tax_ids_after_fiscal_position.compute_all(
    #                 price,
    #                 line.order_id.pricelist_id.currency_id,
    #                 line.qty,
    #                 product=line.product_id,
    #                 partner=line.order_id.partner_id,
    #             )
    #             line.update(
    #                 {
    #                     "price_subtotal_incl": taxes["total_included"],
    #                     "price_subtotal": taxes["total_excluded"],
    #                 }
    #             )



    @api.onchange("qty", "discount", "price_unit", "tax_ids", "absolute_discount")
    def _onchange_qty(self):
        if self.product_id and self.absolute_discount:
            if not self.order_id.pricelist_id:
                raise UserError(_("You have to select a pricelist in the sale form !"))
            price = self.price_unit - self.absolute_discount
            self.price_subtotal = self.price_subtotal_incl = price * self.qty
            if self.product_id.taxes_id:
                taxes = self.product_id.taxes_id.compute_all(
                    price,
                    self.order_id.pricelist_id.currency_id,
                    self.qty,
                    product=self.product_id,
                    partner=False,
                )
                self.price_subtotal = taxes["total_excluded"]
                self.price_subtotal_incl = taxes["total_included"]
        else:
            super(PosOrderLine, self)._onchange_qty()


class ReportSaleDetails(models.AbstractModel):
    _inherit = "report.point_of_sale.report_saledetails"

    @api.model
    def get_sale_details(
        self, date_start=False, date_stop=False, config_ids=False, session_ids=False
    ):
        """Serialise the orders of the day information

        params: date_start, date_stop string representing the datetime of order
        """
        domain = [("state", "in", ["paid", "invoiced", "done"])]

        if session_ids:
            domain = AND([domain, [("session_id", "in", session_ids)]])
        else:
            if date_start:
                date_start = fields.Datetime.from_string(date_start)
            else:
                # start by default today 00:00:00
                user_tz = pytz.timezone(
                    self.env.context.get("tz") or self.env.user.tz or "UTC"
                )
                today = user_tz.localize(
                    fields.Datetime.from_string(fields.Date.context_today(self))
                )
                date_start = today.astimezone(pytz.timezone("UTC"))

            if date_stop:
                date_stop = fields.Datetime.from_string(date_stop)
                # avoid a date_stop smaller than date_start
                if date_stop < date_start:
                    date_stop = date_start + timedelta(days=1, seconds=-1)
            else:
                # stop by default today 23:59:59
                date_stop = date_start + timedelta(days=1, seconds=-1)

            domain = AND(
                [
                    domain,
                    [
                        ("date_order", ">=", fields.Datetime.to_string(date_start)),
                        ("date_order", "<=", fields.Datetime.to_string(date_stop)),
                    ],
                ]
            )

            if config_ids:
                domain = AND([domain, [("config_id", "in", config_ids)]])

        orders = self.env["pos.order"].search(domain)

        user_currency = self.env.company.currency_id

        total = 0.0
        products_sold = {}
        taxes = {}
        for order in orders:
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id._convert(
                    order.amount_total,
                    user_currency,
                    order.company_id,
                    order.date_order or fields.Date.today(),
                )
            else:
                total += order.amount_total
            currency = order.session_id.currency_id

            for line in order.lines:
                key = (line.product_id, line.price_unit, line.discount)
                key2 = (line.qty or 0, line.absolute_discount or 0)
                products_sold.setdefault(key, key2)

                if line.tax_ids_after_fiscal_position:
                    if line.absolute_discount:
                        line_taxes = line.tax_ids_after_fiscal_position.compute_all(
                            line.price_unit * (1 - line.absolute_discount),
                            currency,
                            line.qty,
                            product=line.product_id,
                            partner=line.order_id.partner_id or False,
                        )
                    else:
                        line_taxes = line.tax_ids_after_fiscal_position.compute_all(
                            line.price_unit * (1 - (line.discount or 0.0) / 100.0),
                            currency,
                            line.qty,
                            product=line.product_id,
                            partner=line.order_id.partner_id or False,
                        )
                    for tax in line_taxes["taxes"]:
                        taxes.setdefault(
                            tax["id"],
                            {
                                "name": tax["name"],
                                "tax_amount": 0.0,
                                "base_amount": 0.0,
                            },
                        )
                        taxes[tax["id"]]["tax_amount"] += tax["amount"]
                        taxes[tax["id"]]["base_amount"] += tax["base"]
                else:
                    taxes.setdefault(
                        0,
                        {"name": _("No Taxes"), "tax_amount": 0.0, "base_amount": 0.0},
                    )
                    taxes[0]["base_amount"] += line.price_subtotal_incl

        payment_ids = (
            self.env["pos.payment"].search([("pos_order_id", "in", orders.ids)]).ids
        )
        if payment_ids:
            self.env.cr.execute(
                """
                  SELECT method.name, sum(amount) total
                  FROM pos_payment AS payment,
                       pos_payment_method AS method
                  WHERE payment.payment_method_id = method.id
                      AND payment.id IN %s
                  GROUP BY method.name
              """,
                (tuple(payment_ids),),
            )
            payments = self.env.cr.dictfetchall()
        else:
            payments = []

        return {
            "currency_precision": user_currency.decimal_places,
            "total_paid": user_currency.round(total),
            "payments": payments,
            "company_name": self.env.company.name,
            "taxes": list(taxes.values()),
            "products": sorted(
                [
                    {
                        "product_id": product.id,
                        "product_name": product.name,
                        "code": product.default_code,
                        "quantity": qty,
                        "price_unit": price_unit,
                        "discount": discount,
                        "absolute_discount": absolute_discount,
                        "uom": product.uom_id.name,
                    }
                    for (product, price_unit, discount), (
                        qty,
                        absolute_discount,
                    ) in products_sold.items()
                ],
                key=lambda l: l["product_name"],
            ),
        }
