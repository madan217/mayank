# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class mrpProductionInh(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, vals):
        res = super(mrpProductionInh, self).create(vals)
        if res:
            res.action_assign()
        return res
        