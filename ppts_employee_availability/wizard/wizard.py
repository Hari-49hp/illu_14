from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime


class UnlinkWizardAvailability(models.Model):
	_name = 'availability.unlink'
	_description = 'Availability Unlink'

	av_id = fields.Many2one('availability.availability',string="Availability")

	def set_av_unconfirmed(self):
		print(self.av_id,'aaaaaaaaaaaa')

class SetToDraft(models.Model):
	_name = 'availability.setdraft'
	_description = 'Availability Set To Draft'

	availability_id = fields.Many2one('availability.availability',string="Availability")