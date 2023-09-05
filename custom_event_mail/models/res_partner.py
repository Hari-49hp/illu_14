from odoo import api, fields, models

class MailingContact(models.Model):
    _inherit = 'mailing.contact'

    mobile = fields.Char('Mobile')

class CustompartnerLoc(models.Model):
    _inherit = 'res.partner'

    is_existing_customer = fields.Boolean(string='Is Existing Customer?')

    def send_welcome_email(self):
        existing_customer_ids= self.env['res.partner'].search([('is_existing_customer', '=', False),('company_type', '!=', 'company'),('email', '!=', '')])
        for customer in existing_customer_ids:
            customer.is_existing_customer=True
            template_id = self.env.ref('custom_event_mail.custom_user_welcome_mail_template')
            mail_response= template_id.send_mail(customer.id,force_send=True)
