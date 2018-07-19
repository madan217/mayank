# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import time
import itertools
import xlwt
from xlwt import *
import base64
from datetime import datetime
from collections import defaultdict
from io import BytesIO
from collections import OrderedDict


class ReportExcel(models.TransientModel):
    _name= "report.excel"
    excel_file = fields.Binary('Excel Report')
    file_name = fields.Char('Excel File', size=64)


class CompleteProductionWizard(models.TransientModel):
    _name = 'complete.production'
    _description = 'Production Details'

    from_date = fields.Date('From', required=True)
    to_date = fields.Date('To', required=True)


    @api.multi
    def get_lines(self):
        ProductObj = self.env['product.product']

        D = defaultdict(list)
        attribute_ids = []
        # assign Raw template id exm:39 
        raw_variants = ProductObj.search([('product_tmpl_id', '=', 19)])
        #assign Counter template id exm: 40
        counter_variants = ProductObj.search([('product_tmpl_id', '=', 31)])
 
        wireLineObj = self.env['weighted.wire.line']
        wire_ids = wireLineObj.search([
            ('wire_date', '>=', self.from_date),
            ('wire_date', '<=', self.to_date),
            ('state', '=', 'done'),
            ('mo_id.product_id.product_tmpl_id.id', '=', 19)]) # assign for Raw Template exm:39
        for wire_id in wire_ids:
            D[wire_id.wire_date].append((wire_id.mo_id.product_id.id,
                                        wire_id.mo_id.product_id.attribute_value_ids.ids[0],
                                        wire_id.mo_id.product_id.name,
                                        wire_id.qty_produced))
            attribute_ids.append(wire_id.mo_id.product_id.attribute_value_ids.ids[0])

        counterLineObj = self.env['operation.detail.line']
        counter_ids = counterLineObj.search([
            ('operation_date', '>=', self.from_date),
            ('operation_date', '<=', self.to_date),
            ('state', '=', 'done'),
            ('mo_id.product_id.product_tmpl_id.id', '=', 31)]) # assign for Counter Template exm:40
        for counter_id in counter_ids:
            D[counter_id.operation_date].append((counter_id.mo_id.product_id.id,
                                        counter_id.mo_id.product_id.attribute_value_ids.ids[0],
                                        counter_id.mo_id.product_id.name,
                                        counter_id.qty))
            attribute_ids.append(counter_id.mo_id.product_id.attribute_value_ids.ids[0])

        attribute_ids = list(set(attribute_ids))
        pickingObj = self.env['stock.picking']
        max_dict = 0
        print "dict d===============", dict(D).items()
        header_list = []
        for k, v in dict(D).items():

            kdate = k + ' ' + '00:00:00'
            kend = k + ' ' + '23:59:59'
            total = 0.0
            pickings = pickingObj.search([
                ('min_date','>=', kdate),
                ('min_date','<=', kend),
                ('location_id', '=', 15), # assigne source location id
                ('location_dest_id', '=', 23), #assigne destination location id
                ('state', '=', 'done')])
            for pick in pickings:
                total += pick.total_qty
            l = []
            total_raw = 0.0
            total_counter = 0.0
            
            keyfunc = lambda t: (t[0], t[1], t[2])
            v.sort(key=keyfunc)
            for key, rows in itertools.groupby(v, keyfunc):
                total_qty = 0.0
                for r in rows:
                    total_qty += r[3]
                    if key[0] in raw_variants.ids:
                        total_raw += r[3]
                    elif key[0] in counter_variants.ids:
                        total_counter += r[3]
                header_list.append((key[0],key[1],key[2], 0.0))
                l.append((key[0],key[1],key[2], total_qty))
            l.append([total_raw,total_counter,total])
            D[k] = l
        D['1900-01-01'] = list(set(header_list))
        print "dl==================",dict(D)
        O = sorted(D.items(), key = lambda x:datetime.strptime(x[0], '%Y-%m-%d'))
        print "o==================",O
        return O, attribute_ids

    @api.multi
    def print_complete_production_report_xls(self):
        data_dict = []
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        filename = 'Complete Production '+str(datetime.strptime(self.from_date, '%Y-%m-%d')\
            .strftime('%d/%m/%Y')) + '-' + str(datetime.strptime(self.to_date, '%Y-%m-%d')\
            .strftime('%d/%m/%Y'))+'.xls'
        report_id = False
        if self.id:
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
            # worksheet.col(0).width = 10000
            # worksheet.col(1).width = 7000
            # worksheet.col(2).width = 7000
            # worksheet.col(3).width = 7000
            # worksheet.col(4).width = 7000
            # worksheet.col(5).width = 7000
            # worksheet.col(6).width = 7000
            # worksheet.col(7).width = 7000
            # worksheet.col(8).width = 7000
            # worksheet.col(9).width = 7000
            # worksheet.col(10).width = 7000
            # worksheet.col(11).width = 7000
            # worksheet.col(12).width = 7000
            worksheet.row(0).height = 400
            # worksheet.row(5).height = 00
            columns_center_bold_style = xlwt.easyxf('font:height 220; align: wrap on, horiz center; font: bold on; pattern: pattern solid, fore_colour white; border: top thin, right thin, bottom thin, left thin;')
            columns_center_style = xlwt.easyxf('font:height 200; align: horiz center; pattern: pattern solid, fore_colour white; border: top thin, right thin, bottom thin, left thin;')
            columns_right_style = xlwt.easyxf('font:height 200; align: wrap on, horiz right; pattern: pattern solid, fore_colour white; border: top thin, right thin, bottom thin, left thin;')
            columns_left_style = xlwt.easyxf('font:height 200; align: wrap on, horiz left; pattern: pattern solid, fore_colour white; border: top thin, right thin, bottom thin, left thin;')
            columns_left_bold_style = xlwt.easyxf('font:height 200; align: horiz left;font: bold on; pattern: pattern solid, fore_colour white; border: top thin, right thin, bottom thin, left thin;')
            xlwt.add_palette_colour("eunry", 0x21)
            workbook.set_colour_RGB(0x21, 201, 165, 165)
            style = xlwt.easyxf('font:bold on, color 0x28; align: horiz center; align: vert centre; font:height 350; pattern: pattern solid, fore_colour white;border: top thin, right thin, bottom thin, left thin;')
            style_so = xlwt.easyxf('font:bold on; align: horiz left; align: vert centre; font:height 250; pattern: pattern solid, fore_colour white;border: top thin, right thin, bottom thin, left thin;')
            style_qty = xlwt.easyxf('font:bold on, color 0x28; align: horiz left; align: vert centre; font:height 200; pattern: pattern solid, fore_colour white;border: top thin, right thin, bottom thin, left thin;')
            
            worksheet.write_merge(0,1,0,9, 'Complete Production Report From %s to %s'%(datetime.strptime(self.from_date, '%Y-%m-%d').strftime('%d/%m/%Y'), str(datetime.strptime(self.to_date, '%Y-%m-%d').strftime('%d/%m/%Y'))), style_so)
            data_dict, attribute_ids = self.get_lines()
            attObj = self.env['product.attribute.value']
            if attribute_ids:
                worksheet.write(7,0, 'Date', columns_center_bold_style)
                count_check = True
                header_col = 0
                colPid = []
                for data in data_dict:
                    if data[0] == '1900-01-01':
                        print "==========="
                        for at in attribute_ids:
                            merge_count = 0
                            for pdata in sorted(data[1], key=lambda x: x[2],reverse=True):
                                if isinstance(pdata, (tuple)):
                                    if at == pdata[1]:
                                        merge_count += 1
                                        header_col += 1
                                        print "pdata========",pdata
                                        colPid.append((pdata[0],pdata[1],))
                                        worksheet.col(header_col).width = 4000
                                        worksheet.write(7,header_col, pdata[2], columns_center_bold_style)
                            if merge_count == 2:
                                worksheet.write_merge(5,6,header_col-1,header_col,attObj.browse(at).name,columns_center_bold_style)
                            elif merge_count == 1:
                                print "attObj.browse(at).name===",attObj.browse(at).name
                                worksheet.write_merge(5,6,header_col,header_col,attObj.browse(at).name,columns_center_bold_style)
                        print "colpid===========",colPid
                        worksheet.col(header_col+1).width = 4000
                        worksheet.write(7,header_col+1, 'Total Raw', columns_center_bold_style)
                        worksheet.col(header_col+2).width = 4000
                        worksheet.write(7,header_col+2, 'Total Counter', columns_center_bold_style)
                        worksheet.col(header_col+3).width = 4000
                        worksheet.write(7,header_col+3, 'Dispatched', columns_center_bold_style)
                        break
                row = 8
                grand_total_raw = 0.0
                grand_total_counter = 0.0
                grand_total_dispatched = 0.0
                for data2 in data_dict:
                    if data2[0] != '1900-01-01':
                        col = 0
                        match_col = []
                        worksheet.write(row,col, datetime.strptime(data2[0], '%Y-%m-%d')\
                                .strftime('%d/%m/%Y'), columns_center_style)
                        for at2 in attribute_ids:
                            for pdata2 in data2[1]:
                                if isinstance(pdata2, (tuple)):
                                    for colid in colPid:
                                        if colid[0] == pdata2[0] and colid[1] == pdata2[1]:
                                            worksheet.write(row,colPid.index(colid)+1, '{:.5f}'.format(pdata2[3]), columns_center_style)
                                            match_col.append(colPid.index(colid)+1)
                                else:
                                    worksheet.write(row,header_col+1, '{:.5f}'.format(pdata2[0]), columns_center_style)
                                    worksheet.write(row,header_col+2, '{:.5f}'.format(pdata2[1]), columns_center_style)
                                    worksheet.write(row,header_col+3, '{:.5f}'.format(pdata2[2]), columns_center_style)
                        for r in range(1,(header_col+1)):
                            if r not in match_col:
                                worksheet.write(row,r, '{:.5f}'.format(0), columns_center_style)

                        grand_total_raw += pdata2[0]
                        grand_total_counter += pdata2[1]
                        grand_total_dispatched += pdata2[2]
                        row += 1

                worksheet.write(row,header_col+1, '{:.5f}'.format(grand_total_raw), columns_center_bold_style)
                worksheet.write(row,header_col+2, '{:.5f}'.format(grand_total_counter), columns_center_bold_style)
                worksheet.write(row,header_col+3, '{:.5f}'.format(grand_total_dispatched), columns_center_bold_style)
                
            fp = BytesIO()
            workbook.save(fp)
            report_id = self.env['report.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
            fp.close()

            if report_id:
                return {
                        'view_mode': 'form',
                        'res_id': report_id.id,
                        'res_model': 'report.excel',
                        'view_type': 'form',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                    }
            else:
                raise osv.except_osv(_('Data Not Found'),(''))