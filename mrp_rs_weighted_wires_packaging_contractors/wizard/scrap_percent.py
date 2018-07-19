# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from collections import defaultdict, OrderedDict
from operator import itemgetter
import itertools

class ScrapPercentWizard(models.TransientModel):
    _name = 'report.mrp_rs_weighted_wires_packaging_contractors.scrap'
    _description = 'Scrap %'


    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    scrap_so_date = fields.Date('Scrap SO Date', required=True)

    @api.multi
    def get_report_data(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        moveObj = self.env['stock.move']
        # assign production location id Here i have given 7
        domain = [
                ('date', '>=', self.start_date + ' ' + '00:00:00'),
                ('date', '<=', self.end_date + ' ' + '23:59:59'),
                ('location_dest_id', '=', 7),
                ('product_id.product_tmpl_id.id', 'in', [10,25]),
                ('state', '=', 'done')]
        moveIds = moveObj.search(domain)
        total_consumed = 0.0
        total_scrap = 0.0
        for mv in moveIds:
            total_consumed += mv.quantity_done
        print "scrap_so_date========",self.scrap_so_date
        soIds = self.env['sale.order'].search([
            ('confirmation_date', '>=', self.scrap_so_date + ' ' + '00:00:00'),
            ('confirmation_date', '<=', self.scrap_so_date + ' ' + '23:59:59'),
            ('scrap_order', '=', 'Yes'),
            ('state', 'in', ['sale','done'])])
        print "scrap_so_date========",self.scrap_so_date
        for so in soIds:
            for line in so.order_line:
                # assign product template ids here i have given 10,25
                total_scrap += line.product_uom_qty
        scrap_percent = round(((total_scrap / total_consumed) * 100),2)
        resIds = self.read(
            ['start_date', 'end_date'])[0]
        resIds['total_consumed'] = total_consumed
        resIds['total_scrap'] = total_scrap
        resIds['scrap_percent'] = scrap_percent
        data['form'] = resIds
        return data

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.browse(self.env.context.get('active_ids'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
        }
        return self.env['report'].\
            render('mrp_rs_weighted_wires_packaging_contractors.scrap', docargs)
        

    @api.multi
    def print_scrap_percent(self):
        self.ensure_one()
        data = self.get_report_data()
        return self.env['report'].get_action(self, 'mrp_rs_weighted_wires_packaging_contractors.scrap', data=data)
