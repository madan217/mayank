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
{

    'name': 'India-GST',
    'description': "Goods & Service-Tax.",
    'version': '1.0.1',
    'category': 'Accounting',
    'author': 'Merlin Tecsol Pvt. Ltd.',
    'website': 'http://www.merlintecsol.com',
    'summary': 'Indian GST Reports',
    'license': 'AGPL-3',
    'depends': ['sale','purchase','account','report_xlsx'],
    'data': [
        "views/gst_view.xml",
        "views/gst_sale_view.xml",
        "views/gst_purchase_view.xml",
        "data/tax_data.xml",
        "data/res.country.state.csv",
        "data/fiscal_data.xml",
        "report/gst_sales_invoice_pdf.xml",
        "report/gst_invoice_pdf.xml",
        "report/gst_invoice.xml",
        'report/gst_b2b.xml',
        'wizard/gstr_b2b_wizard.xml',
        'wizard/gstr_b2cl_wizard.xml',
        'report/gst_b2cl_report.xml',
        'wizard/gstr_b2cs_wizard.xml',
        'report/gst_b2cs_report.xml',
        'wizard/gstr_hsn_wizard.xml',
        'report/gst_hsn_report.xml',
        'wizard/gstr_export_wizard.xml',
        'report/gst_export_report.xml',
        'views/port_code.xml',

    ],
    'images': ['static/description/banner.png'],
}
