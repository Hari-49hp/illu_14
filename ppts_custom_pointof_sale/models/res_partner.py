from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_view_partner_pos_invoices(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("point_of_sale.action_pos_payment_form")
        action['domain'] = [
            ('partner_id', '=', self.id),
        ]
        return action

    def _invoice_pos_total(self):
        pos_payment_invoiced = 0.0
        for record in self:
            if not self.ids:
                record.total_pos_payment_invoiced =pos_payment_invoiced
            domain = [
                ('partner_id', '=', record.id),
                ('state', 'in', ['paid', 'done', 'invoiced']),
                ('company_id', '=', self.env.user.company_id.id),
            ]
            for pos_order in self.env['pos.order'].search(domain):
                if pos_order.amount_paid>0.0:
                    pos_payment_invoiced += pos_order.amount_paid
            record.total_pos_payment_invoiced =pos_payment_invoiced

    total_pos_payment_invoiced = fields.Monetary(compute='_invoice_pos_total',groups='account.group_account_invoice,account.group_account_readonly')
