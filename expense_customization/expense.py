# -*- coding: utf-8 -*-


from odoo import api, fields, models, _

class HrExpense(models.Model):

    _inherit = "hr.expense"

    contractor_id = fields.Many2one('mrp.contractor', string='Contractor Name')
    date = fields.Date(readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, default=False, string="Date")
    payment_mode = fields.Selection([("own_account", "Employee (to reimburse)"), ("company_account", "Company")], default='company_account', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, string="Payment By")
