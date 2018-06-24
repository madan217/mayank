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
from datetime import datetime, date
class InvoiceXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, invoices):

        worksheet = workbook.add_worksheet('GST Invoice')
        worksheet.set_margins(left = 1,right = 0.75,top = 1,bottom = 0.75)
        worksheet.fit_to_pages(1, 1)
        worksheet.set_portrait()
        worksheet.set_paper(9)
        worksheet.center_horizontally()
        worksheet.set_column('A:R',4)
        worksheet.set_row(0,30)
        worksheet.set_row(6,30)

        bold_size_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})


        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})

        merge_format1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})

        merge_format2 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'})

        align_right_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'right',
            'valign': 'vcenter'})

        merge_format_sim = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'})

        align_right_format1 = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})

        align_left_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'})

        merge_format.set_font_size(6)
        merge_format1.set_font_size(8)
        merge_format2.set_font_size(9)
        align_right_format.set_font_size(8)
        merge_format_sim.set_font_size(9)
        align_right_format1.set_font_size(7)
        align_left_format.set_font_size(7)
        bold_size_format.set_font_size(15)
        merge_format1.set_text_wrap()
        merge_format2.set_text_wrap()
        merge_format.set_text_wrap()
        align_right_format.set_text_wrap()
        merge_format_sim.set_text_wrap()
        align_right_format1.set_text_wrap()
        align_left_format.set_text_wrap()
        bold_size_format.set_text_wrap()

        for obj in invoices:
            row = 1
            col = 0
            new_row = row + 1

            worksheet.merge_range('A%s:R%s' %(row,row), 'Invoice', bold_size_format)
            worksheet.merge_range('A%s:D%s' %(new_row, new_row), 'GSTIN', merge_format2)
            worksheet.merge_range('E%s:R%s' %(new_row, new_row), self.env.user.company_id.vat, merge_format_sim)
            worksheet.merge_range('A%s:D%s' %(new_row + 1, new_row + 1), 'Name', merge_format2)
            worksheet.merge_range('E%s:R%s' %(new_row + 1, new_row + 1), self.env.user.company_id.name, merge_format_sim)
            worksheet.merge_range('A%s:D%s' %(new_row + 2, new_row + 2), 'Address', merge_format2)
            worksheet.merge_range('E%s:R%s' %(new_row + 2, new_row + 2), self.env.user.company_id.street, merge_format_sim)
            worksheet.merge_range('A%s:D%s' %(new_row + 3, new_row + 3), 'Invoice No.', merge_format2)
            worksheet.merge_range('E%s:R%s' %(new_row + 3, new_row + 3), obj.number, merge_format_sim)
            worksheet.merge_range('A%s:D%s' %(new_row + 4, new_row + 4), 'Date of invoice', merge_format2)
            worksheet.merge_range('E%s:R%s' %(new_row + 4, new_row + 4), obj.date_invoice, merge_format_sim)

            worksheet.merge_range('A%s:I%s' %(new_row + 5, new_row + 5), 'Details of Receiver', merge_format1)
            worksheet.merge_range('J%s:R%s' %(new_row + 5, new_row + 5), 'Details of Consignee(Shipped to)', merge_format1)

            worksheet.merge_range('A%s:D%s' %(new_row + 6, new_row + 6), 'Name', merge_format2)
            worksheet.merge_range('E%s:I%s' %(new_row + 6, new_row + 6), obj.partner_id.name, merge_format_sim)
            worksheet.merge_range('J%s:M%s' %(new_row + 6, new_row + 6), 'Name', merge_format2)
            worksheet.merge_range('N%s:R%s' %(new_row + 6, new_row + 6), obj.partner_shipping_id.name, merge_format_sim)

            worksheet.merge_range('A%s:D%s' %(new_row + 7, new_row + 7), 'Address', merge_format2)
            worksheet.merge_range('E%s:I%s' %(new_row + 7, new_row + 7), obj.partner_id.street + obj.partner_id.street2 + obj.partner_id.city, merge_format_sim)
            worksheet.merge_range('J%s:M%s' %(new_row + 7, new_row + 7), 'Address', merge_format2)
            worksheet.merge_range('N%s:R%s' %(new_row + 7, new_row + 7), obj.partner_shipping_id.street + obj.partner_shipping_id.street2 + obj.partner_shipping_id.city, merge_format_sim)

            worksheet.merge_range('A%s:D%s' %(new_row + 8, new_row + 8), 'State', merge_format2)
            worksheet.merge_range('E%s:I%s' %(new_row + 8, new_row + 8), obj.partner_id.state_id.name, merge_format_sim)
            worksheet.merge_range('J%s:M%s' %(new_row + 8, new_row + 8), 'State', merge_format2)
            worksheet.merge_range('N%s:R%s' %(new_row + 8, new_row + 8), obj.partner_shipping_id.state_id.name, merge_format_sim)

            worksheet.merge_range('A%s:D%s' %(new_row + 9, new_row + 9), 'State Code', merge_format2)
            worksheet.merge_range('E%s:I%s' %(new_row + 9, new_row + 9), obj.partner_id.state_id.state_code, merge_format_sim)
            worksheet.merge_range('J%s:M%s' %(new_row + 9, new_row + 9), 'State Code', merge_format2)
            worksheet.merge_range('N%s:R%s' %(new_row + 9, new_row + 9), obj.partner_shipping_id.state_id.state_code, merge_format_sim)

            worksheet.merge_range('A%s:D%s' %(new_row + 10, new_row + 10), 'GSTIN', merge_format2)
            worksheet.merge_range('E%s:I%s' %(new_row + 10, new_row + 10), obj.partner_id.vat, merge_format_sim)
            worksheet.merge_range('J%s:M%s' %(new_row + 10, new_row + 10), 'GSTIN', merge_format2)
            worksheet.merge_range('N%s:R%s' %(new_row + 10, new_row + 10), obj.partner_shipping_id.vat, merge_format_sim)
            worksheet.merge_range('A%s:R%s' %(new_row + 10, new_row + 11), '', merge_format2)

            worksheet.merge_range('A%s:A%s' %(new_row + 12, new_row + 13), 'No', merge_format)
            worksheet.merge_range('B%s:C%s' %(new_row + 12, new_row + 13), 'Description of Goods', merge_format)
            worksheet.merge_range('D%s:D%s' %(new_row + 12, new_row + 13), 'HSN code', merge_format)
            worksheet.merge_range('E%s:E%s' %(new_row + 12, new_row + 13), 'Qty', merge_format)
            worksheet.merge_range('F%s:F%s' %(new_row + 12, new_row + 13), 'UOM', merge_format)
            worksheet.merge_range('G%s:H%s' %(new_row + 12, new_row + 13), 'Rate', merge_format)
            worksheet.merge_range('I%s:J%s' %(new_row + 12, new_row + 13), 'Total', merge_format)
            worksheet.merge_range('K%s:K%s' %(new_row + 12, new_row + 13), 'Discount', merge_format)
            worksheet.merge_range('L%s:L%s' %(new_row + 12, new_row + 13), 'Taxable values', merge_format)

            worksheet.merge_range('M%s:N%s' %(new_row + 12, new_row + 12), 'CGST', merge_format)
            worksheet.merge_range('O%s:P%s' %(new_row + 12, new_row + 12), 'SGST', merge_format)
            worksheet.merge_range('Q%s:R%s' %(new_row + 12, new_row + 12), 'IGST', merge_format)

            worksheet.write('M%s' %(new_row + 13), 'Rate', merge_format)
            worksheet.write('N%s' %(new_row + 13), 'Amount', merge_format)

            worksheet.write('O%s' %(new_row + 13), 'Rate', merge_format)
            worksheet.write('P%s' %(new_row + 13), 'Amount', merge_format)

            worksheet.write('Q%s' %(new_row + 13), 'Rate', merge_format)
            worksheet.write('R%s' %(new_row + 13), 'Amount', merge_format)

            count = 0
            tax_igst = 0
            tax_cgst = 0
            tax_sgst = 0

            for line in obj.invoice_line_ids:

                t = line.quantity * line.price_unit
                count += 1

                worksheet.write('A%s' %(new_row + 14), count, align_right_format1)
                worksheet.merge_range('B%s:C%s' %(new_row + 14, new_row + 14), line.product_id.name, align_left_format)
                worksheet.write('D%s' %(new_row + 14), line.product_id.hsn_code, align_right_format1)
                worksheet.write('E%s' %(new_row + 14), line.quantity, align_right_format1)
                worksheet.write('F%s' %(new_row + 14), line.uom_id.name, align_right_format1)
                worksheet.merge_range('G%s:H%s' %(new_row + 14, new_row + 14), line.price_unit, align_right_format1)
                worksheet.merge_range('I%s:J%s' %(new_row + 14, new_row + 14), t, align_right_format1)
                worksheet.write('K%s' %(new_row + 14), line.discount, align_right_format1)
                worksheet.write('L%s' %(new_row + 14), line.price_subtotal, align_right_format1)
                worksheet.write('N%s' %(new_row + 14), line.cgst, align_right_format1)
                worksheet.write('P%s' %(new_row + 14), line.sgst, align_right_format1)
                worksheet.write('R%s' %(new_row + 14), line.igst, align_right_format1)


# rate
                for line1 in line.invoice_line_tax_ids:
                    if line1.tax_type == 'cgst':
                        tax_cgst = line1.amount
                    elif line1.tax_type == 'sgst':
                        tax_sgst = line1.amount
                    elif line1.tax_type == 'igst':
                        tax_igst = line1.amount

                worksheet.write('M%s' %(new_row + 14), tax_cgst, align_right_format1)
                worksheet.write('O%s' %(new_row + 14), tax_sgst, align_right_format1)
                worksheet.write('Q%s' %(new_row + 14), tax_igst, align_right_format1)
                new_row += 1
# amount
            # row = 16
            #for line2 in obj.gst_invoice_line:
             #   worksheet.write('N%s' %(row), line2.cgst, align_right_format1)
              #  worksheet.write('P%s' %(row), line2.sgst, align_right_format1)
               # worksheet.write('R%s' %(row), line2.igst, align_right_format1)
                #row += 1

            worksheet.merge_range('A%s:F%s' %(new_row + 14, new_row + 14), 'Tax Description', merge_format1)
            worksheet.merge_range('G%s:J%s' %(new_row + 14, new_row + 14), 'Amount', merge_format1)


            worksheet.merge_range('K%s:O%s' %(new_row + 14, new_row + 14), 'Total', align_right_format)
            worksheet.merge_range('P%s:R%s' %(new_row + 14, new_row + 14), obj.amount_untaxed, merge_format_sim)

            worksheet.merge_range('K%s:O%s' %(new_row + 15, new_row + 15), 'Tax Amount:GST', align_right_format)
            worksheet.merge_range('P%s:R%s' %(new_row + 15, new_row + 15), obj.amount_tax, merge_format_sim)

            worksheet.merge_range('K%s:O%s' %(new_row + 16, new_row + 16), 'Grand Total', align_right_format)
            worksheet.merge_range('P%s:R%s' %(new_row + 16, new_row + 16), obj.amount_total, merge_format_sim)

            worksheet.merge_range('A%s:J%s' %(new_row + 17, new_row + 17), 'Certified that the Particulars given above are true and correct', merge_format)
            worksheet.merge_range('K%s:R%s' %(new_row + 17, new_row + 17), 'Electronic Reference Number', merge_format)

            worksheet.merge_range('A%s:J%s' %(new_row + 18, new_row + 18), '', merge_format)
            worksheet.merge_range('K%s:R%s' %(new_row + 18, new_row + 18), obj.elec_ref, merge_format)

            worksheet.merge_range('A%s:J%s' %(new_row + 19, new_row + 23), 'Terms and Conditions\n\n\n\n\n\n\n', merge_format)

            worksheet.merge_range('K%s:R%s' %(new_row + 19, new_row + 23), 'For, ' + self.env.user.company_id.name + '\n\n\n\n\n\n\nAuthorised Signatory ' , merge_format)



            for line3 in obj.tax_line_ids:
                worksheet.merge_range('A%s:F%s' %(new_row + 15, new_row + 15), line3.name, merge_format)
                worksheet.merge_range('G%s:J%s' %(new_row + 15, new_row + 15), line3.amount, merge_format)
                new_row += 1



InvoiceXlsx('report.account.invoice.gst1.xlsx',
            'account.invoice')
