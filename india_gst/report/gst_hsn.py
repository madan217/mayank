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
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import xlsxwriter
from datetime import date
from datetime import datetime, date
import odoo.addons.decimal_precision as dp
import re
class GstrHsnXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, invoices):

        invoice_obj = self.env['check.date'].search([])[-1]
        invoice_id = self.env['account.invoice'].search([('type','=','out_invoice'),
                                                        ('state', 'in', ['open', 'paid']),
                                                        ('date_invoice','>=',invoice_obj.start_date),
                                                        ('date_invoice','<=',invoice_obj.end_date)])

        worksheet = workbook.add_worksheet('GSTR HSN Summary')
        worksheet.set_column('A:J',17)

        row = 1
        col = 0
        new_row = row + 1

        worksheet.write('A%s' %(row), 'HSN')
        worksheet.write('B%s' %(row), 'Description')
        worksheet.write('C%s' %(row), 'UQC')
        worksheet.write('D%s' %(row), 'Total Quantity')
        worksheet.write('E%s' %(row), 'Total Value')
        worksheet.write('F%s' %(row), 'Taxable Value')
        worksheet.write('G%s' %(row), 'Integrated Tax Amount')
        worksheet.write('H%s' %(row), 'Central Tax Amount')
        worksheet.write('I%s' %(row), 'State/UT Tax Amount')
        worksheet.write('J%s' %(row), 'Ces Amount')

        partner_state = self.env.user.company_id.partner_id.state_id.name

        ls = []
        t = []
        for obj in invoice_id:
            for rec in obj.invoice_line_ids:
                if rec.product_id.hsn_code:
                    ls.append(rec.product_id.hsn_code)

        hsn_no = set(ls)
        for hsn in hsn_no:
            qty = 0
            # total = 0
            taxable = 0
            cgst = 0
            sgst = 0
            igst = 0
            uom = ''

            for inv in invoice_id:
                c = 0
                s = 0
                i = 0

                for line in inv.invoice_line_ids:
                    if line.product_id.hsn_code == hsn:
                        qty+=line.quantity
                        # total+=(line.quantity*line.price_unit)
                        taxable+=line.price_subtotal
                        uom = line.uom_id.name
                        cgst+=line.cgst
                        sgst+=line.sgst
                        igst+=line.igst

            t_value = taxable+cgst+sgst+igst
            worksheet.write('A%s' %(new_row), hsn)
            worksheet.write('B%s' %(new_row), '')
            worksheet.write('C%s' %(new_row), uom)
            worksheet.write('D%s' %(new_row), qty)
            worksheet.write('E%s' %(new_row), t_value)
            worksheet.write('F%s' %(new_row), taxable)
            worksheet.write('G%s' %(new_row), igst)
            worksheet.write('H%s' %(new_row), cgst)
            worksheet.write('I%s' %(new_row), sgst)

            new_row+=1

GstrHsnXlsx('report.account.gstr.hsn.xlsx',
            'account.invoice')
