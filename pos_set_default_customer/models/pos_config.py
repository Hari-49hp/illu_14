# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    default_partner_id = fields.Many2one('res.partner', string="Select Customer")
    new_order_disable = fields.Boolean("Disable New Order")

    def open_ui(self):
        """Open the pos interface with config_id as an extra argument.
        In vanilla PoS each user can only have one active session, therefore it was not needed to pass the config_id
        on opening a session. It is also possible to login to sessions created by other users.
        :returns: dict
        """
        self.ensure_one()
        self.default_partner_id = False
        self.new_order_disable = False
        # check all constraints, raises if any is not met
        self._validate_fields(set(self._fields) - {"cash_control"})
        return {
            'type': 'ir.actions.act_url',
            'url': self._get_pos_base_url() + '?config_id=%d' % self.id,
            'target': 'self',
        }

    def open_existing_session_cb(self):
        """ close session button
        access session form to validate entries
        """
        self.ensure_one()
        self.default_partner_id = False
        self.new_order_disable = False
        return self._open_session(self.current_session_id.id)