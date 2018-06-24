# -*- coding: utf-8 -*-
##############################################################################
#
#    India-GST
#
#    Merlin Tecsol Pvt. Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    @api.depends('price_unit', 'product_qty','taxes_id.tax_type','taxes_id.type_tax_use')
    def _compute_gst(self):
        cgst_total = 0
        sgst_total = 0
        igst_total = 0
        cgst_rate = 0
        sgst_rate = 0
        igst_rate = 0
        for rec in self:
            cgst_total = 0
            sgst_total = 0
            igst_total = 0
            for line in rec.taxes_id:
                if line.tax_type == 'cgst' and line.type_tax_use == 'sale':
                    cgst_total = cgst_total + line.amount
                if line.tax_type == 'sgst' and line.type_tax_use == 'sale':
                    sgst_total = sgst_total + line.amount
                if line.tax_type == 'igst' and line.type_tax_use == 'sale':
                    igst_total = igst_total + line.amount
                if line.tax_type == 'cgst' and line.type_tax_use == 'purchase':
                    cgst_total = cgst_total + line.amount
                if line.tax_type == 'sgst' and line.type_tax_use == 'purchase':
                    sgst_total = sgst_total + line.amount
                if line.tax_type == 'igst' and line.type_tax_use == 'purchase':
                    igst_total = igst_total + line.amount
                cgst_rate = cgst_total/100
                sgst_rate = sgst_total/100
                igst_rate = igst_total/100

            rec.cgst = (rec.price_unit * rec.product_qty) * cgst_rate
            rec.sgst = (rec.price_unit * rec.product_qty) * sgst_rate
            rec.igst = (rec.price_unit * rec.product_qty) * igst_rate
            rec.amount = (rec.price_unit * rec.product_qty) + rec.cgst + rec.sgst + rec.igst

    cgst = fields.Float(string='CGST', compute='_compute_gst')
    sgst = fields.Float(string='SGST', compute='_compute_gst')
    igst = fields.Float(string='IGST', compute='_compute_gst')
    amount = fields.Float(string='Amt. with Taxes', readonly=True, compute='_compute_gst')
