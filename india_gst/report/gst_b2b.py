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
import datetime
import odoo.addons.decimal_precision as dp
import re
class GstrB2BXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, invoices):

        invoice_obj = self.env['check.date'].search([])[-1]
        invoice_id = self.env['account.invoice'].search([('type','=','out_invoice'),
                                                        ('state', 'in', ['open', 'paid']),
                                                        ('date_invoice','>=',invoice_obj.start_date),
                                                        ('date_invoice','<=',invoice_obj.end_date)])

        worksheet = workbook.add_worksheet('GSTR B2B')
        worksheet.set_column('A:K',15)
        date_format = workbook.add_format({'num_format': 'd-mmm-yyyy'})

        row = 1
        col = 0
        new_row = row + 1
        y = 'Yes'
        n = 'No'

        worksheet.write('A%s' %(row), 'GSTIN/UIN of Recipient')
        worksheet.write('B%s' %(row), 'Invoice Number')
        worksheet.write('C%s' %(row), 'Invoice date')
        worksheet.write('D%s' %(row), 'Invoice Value')
        worksheet.write('E%s' %(row), 'Place Of Supply')
        worksheet.write('F%s' %(row), 'Reverse Charge')
        worksheet.write('G%s' %(row), 'Invoice Type')
        worksheet.write('H%s' %(row), 'E-Commerce GSTIN')
        worksheet.write('I%s' %(row), 'Rate')
        worksheet.write('J%s' %(row), 'Taxable Value')
        worksheet.write('K%s' %(row), 'Cess Amount')

        ls = []
        for obj in invoice_id:
            if obj.flag_field == True and obj.export_invoice == False:

                for rec in obj.invoice_line_ids:
                    if rec.invoice_line_tax_ids:

                        if rec.tax_desc == 'gst' and rec.gst_amount == 5:
                            ls.append([rec.tax_desc,rec.gst_amount])
                        if rec.tax_desc == 'gst' and rec.gst_amount == 12:
                            ls.append([rec.tax_desc,rec.gst_amount])
                        if rec.tax_desc == 'gst' and rec.gst_amount == 18:
                            ls.append([rec.tax_desc,rec.gst_amount])
                        if rec.tax_desc == 'gst' and rec.gst_amount == 28:
                            ls.append([rec.tax_desc,rec.gst_amount])
                        if rec.tax_desc == 'igst' and rec.gst_amount == 5:
                            ls.append([rec.tax_desc,rec.gst_amount])
                        if rec.tax_desc == 'igst' and rec.gst_amount == 12:
                            ls.append([rec.tax_desc,rec.gst_amount])
                        if rec.tax_desc == 'igst' and rec.gst_amount == 18:
                            ls.append([rec.tax_desc,rec.gst_amount])
                        if rec.tax_desc == 'igst' and rec.gst_amount == 28:
                            ls.append([rec.tax_desc,rec.gst_amount])
                        if rec.tax_desc == 'none' and rec.gst_amount == 0:
                            ls.append([rec.tax_desc,rec.gst_amount])

        for obj in invoice_id:
            if obj.flag_field == True and obj.export_invoice == False:
                for row in set(map(tuple, ls)):
                    r = 0
                    for rec in obj.invoice_line_ids:
                        if rec.invoice_line_tax_ids:
                            if rec.tax_desc == row[0] and rec.gst_amount == row[1]:
                                r+=rec.price_subtotal
                        if r == 0:
                            pass
                        else:
                            worksheet.write('A%s' %(new_row), obj.partner_id.gstin)
                            worksheet.write('B%s' %(new_row), obj.number)
                            inv_date = datetime.datetime.strptime(obj.date_invoice, '%Y-%m-%d')
                            worksheet.write('C%s' %(new_row), inv_date, date_format)
                            worksheet.write('D%s' %(new_row), obj.amount_total)
                            if obj.partner_id.state_id:
                                worksheet.write_rich_string('E%s' %(new_row), obj.partner_id.state_id.state_code + "-" + obj.partner_id.state_id.name)
                            else:
                                worksheet.write('E%s' %(new_row), '')
                            worksheet.write('F%s' %(new_row), 'N')
                            worksheet.write('G%s' %(new_row), obj.invoice_type)
                            worksheet.write('I%s' %(new_row), row[1])
                            worksheet.write('J%s' %(new_row), r)
                            worksheet.write('K%s' %(new_row), '')

                            new_row+=1



GstrB2BXlsx('report.account.gstr.b2b.xlsx',
            'account.invoice')




