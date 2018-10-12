# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class MrpDaysSettings(models.Model):
    _name = 'mrp.days'
    _description = 'Days'

    past_days = fields.Integer('Past Days Entry', default=0)
    future_days = fields.Integer('Future Days Entry', default=0)