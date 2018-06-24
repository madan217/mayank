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

class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_type = fields.Selection(selection=[('cgst', 'CGST'), ('sgst', 'SGST'), ('igst', 'IGST')], string="Tax Type")

class PortCode(models.Model):
    _name = 'port.code'

    name = fields.Char('Port Name')
    code = fields.Char('Port Code')


class Partner(models.Model):
    _inherit = 'res.partner'

    def _default_country(self):
        return self.env['res.country'].search([('name', '=', 'India')], limit=1)

    cin_no = fields.Char('CIN', help='Customer Identification Number')
    pan_no = fields.Char('PAN', help='PAN Number')
    #state_code = fields.Char('State Code', help='State Code')
    country_id = fields.Many2one('res.country', default=_default_country)
    gstin_registered = fields.Boolean('GSTIN-Registered')
    gstin = fields.Char('GSTIN')
    e_commerce = fields.Boolean('E-Commerce')
    e_commerce_tin = fields.Char('E-Commerce GSTIN')

    @api.onchange('state_id')
    def onchange_state_id(self):
        obj1 = self.env['account.fiscal.position'].search([('name', '=', 'Intra State')])
        obj2 = self.env['account.fiscal.position'].search([('name', '=', 'Inter State')])
        if self.state_id:
            if self.env.user.company_id.state_id.id == self.state_id.id:
                self.property_account_position_id = obj1
            else:
                self.property_account_position_id = obj2

    @api.onchange('country_id')
    def onchange_country_id(self):
        obj = self.env['account.fiscal.position'].search([('name', '=', 'Export')])
        if self.country_id:
            if self.country_id.name != 'India':
                self.property_account_position_id = obj
            else:
                self.property_account_position_id = ""


class Product(models.Model):
    _inherit = 'product.template'

    hsn_code = fields.Char('HSN/SAC')


class CountryState(models.Model):
    _description = "Country state"
    _inherit = 'res.country.state'

    state_code = fields.Char('Code', help='Numeric State Code ')



######### Customer Invoice Line ###########
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    elec_ref = fields.Char('Electronic Reference')
    gstin=fields.Char(related='partner_id.gstin',store=True)
    invoice_type=fields.Selection([('Regular','Regular'),('SEZ supplies with payment','SEZ supplies with payment'),('SEZ supplies without payment','SEZ supplies without payment'),
                                  ('Deemed Export','Deemed Export')],string="Invoice Type",default='Regular',required=True)
    e_commerce_operator = fields.Many2one('res.partner','E-Commerce Operator')
    ship_bill_date = fields.Date('Shipping Bill Date')
    ship_bill_no = fields.Char('Shipping Bill No.')
    port_code = fields.Many2one('port.code')
    export_invoice = fields.Boolean('Export Invoice')
    export_type = fields.Selection([('WPAY','WPAY'),('WOPAY','WOPAY')])
    flag_field = fields.Boolean('Flag')

    @api.onchange('partner_id')
    @api.multi
    def partner_id_flag(self):
        if self.partner_id.gstin_registered == True:
            self.flag_field= True
        else:
            False

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    cgst = fields.Float(string='CGST', compute='_compute_gst',digits=dp.get_precision('Product Price'),store=True)
    sgst = fields.Float(string='SGST', compute='_compute_gst',digits=dp.get_precision('Product Price'),store=True)
    igst = fields.Float(string='IGST', compute='_compute_gst',digits=dp.get_precision('Product Price'),store=True)
    gst_amount = fields.Float('GST Amt.',compute='_compute_gst',store=True)
    tax_desc = fields.Char('Tax Desc.',compute='_compute_gst',store=True)
    amount = fields.Float(string='Amt. with Taxes',readonly=True, compute='_compute_gst',store=True)
    type_sale = fields.Many2one('invoice.type')

    @api.multi
    @api.depends('price_unit','discount','quantity','invoice_id.type','invoice_line_tax_ids.tax_type','invoice_line_tax_ids.type_tax_use')
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
            gst_amt = 0
            if rec.invoice_id.type == 'out_invoice':
                if not rec.invoice_line_tax_ids:
                    rec.tax_desc = 'none'
                    gst_amt = 0
                for line in rec.invoice_line_tax_ids:
                    if line.tax_type == 'cgst' and line.type_tax_use == 'sale':
                        cgst_total = cgst_total + line.amount
                        gst_amt+=line.amount
                    if line.tax_type == 'sgst' and line.type_tax_use == 'sale':
                        sgst_total = sgst_total + line.amount
                        gst_amt+=line.amount
                    if line.tax_type == 'igst' and line.type_tax_use == 'sale':
                        igst_total = igst_total + line.amount
                        rec.tax_desc = 'igst'
                        gst_amt = line.amount
                    if (line.tax_type == 'cgst' or line.tax_type == 'sgst') and line.type_tax_use == 'sale':
                        rec.tax_desc = 'gst'
                    cgst_rate = cgst_total/100
                    sgst_rate = sgst_total/100
                    igst_rate = igst_total/100

            if rec.invoice_id.type == 'in_invoice':
                for line in rec.invoice_line_tax_ids:
                    if line.tax_type == 'cgst' and line.type_tax_use == 'purchase':
                        cgst_total = cgst_total + line.amount
                    if line.tax_type == 'sgst' and line.type_tax_use == 'purchase':
                        sgst_total = sgst_total + line.amount
                    if line.tax_type == 'igst' and line.type_tax_use == 'purchase':
                        igst_total = igst_total + line.amount
                        rec.tax_desc = 'igst'
                        gst_amt = line.amount
                    if (line.tax_type == 'cgst' or line.tax_type == 'sgst') and line.type_tax_use == 'purchase':
                        rec.tax_desc = 'gst'

                    cgst_rate = cgst_total/100
                    sgst_rate = sgst_total/100
                    igst_rate = igst_total/100

            base = rec.price_unit * (1 - (rec.discount or 0.0) / 100.0)
            rec.cgst = (base * rec.quantity) * cgst_rate
            rec.sgst = (base * rec.quantity) * sgst_rate
            rec.igst = (base * rec.quantity) * igst_rate
            rec.amount = (base * rec.quantity) + rec.cgst + rec.sgst + rec.igst
            rec.gst_amount = gst_amt


