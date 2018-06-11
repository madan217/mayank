# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class MrpConfigSettings(models.TransientModel):
    _inherit = 'mrp.config.settings'

    past_days = fields.Integer('Past Days Entry', default=0)
    future_days = fields.Integer('Future Days Entry', default=0)

    @api.model
    def get_default_past_days(self, fields):
        return {
            'past_days': self.env['ir.values'].get_default('mrp.config.settings', 'past_days')
        }

    @api.model
    def get_default_future_days(self, fields):
        return {
            'future_days': self.env['ir.values'].get_default('mrp.config.settings', 'future_days')
        }

    @api.multi
    def set_default_past_days(self):
        IrValues = self.env['ir.values']
        IrValues.set_default('mrp.config.settings', 'past_days', self.past_days)

    @api.multi
    def set_default_future_days(self):
        IrValues = self.env['ir.values']
        IrValues.set_default('mrp.config.settings', 'future_days', self.future_days)
    