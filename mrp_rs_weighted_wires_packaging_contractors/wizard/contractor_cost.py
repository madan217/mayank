# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from collections import defaultdict, OrderedDict
from operator import itemgetter
import itertools

class ConstructorWizard(models.TransientModel):
    _name = 'report.mrp_rs_weighted_wires_packaging_contractors.rcc'
    _description = 'Contractor Cost'

    def get_domain_product(self):
        ir_model_data = self.env['ir.model.data']
        pTempId = ir_model_data.get_object_reference(
            'mrp_rs_weighted_wires_packaging_contractors',
            'product_weighted_wire')[1]
        productIds = self.env['contractor.rate'].search([]).mapped('product_id').ids
        return [('id', 'in', productIds)]

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    operation = fields.Selection([
        ('Polish', 'Polish'),
        ('Packed', 'Packed')],
        string='Operation', required=True)
    contractor_id = fields.Many2one('mrp.contractor', 'Contractor',
        required=True)
    product_id = fields.Many2one('product.product', 'Product',
        domain=lambda self : self.get_domain_product())
    polish_type = fields.Selection([
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual')],
        states={'draft': [('readonly', False)]},
        string='Polish Type')

    @api.multi
    def get_report_data(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        domain = [
                ('package_date', '>=', self.start_date),
                ('package_date', '<=', self.end_date),
                ('state', '=', 'done')]
        if self.polish_type == 'Manual':
            domain = domain + [('polish_type', '=', 'Manual')]
        elif self.polish_type == 'Automatic':
            domain = domain + [('polish_type', '=', 'Automatic')]
        if self.product_id and self.product_id.id:
            domain = domain + [('mo_id.product_id.id', '=', self.product_id.id)]
        if self.operation == 'Polish':
            domain = domain + [('polished_by', '=', self.contractor_id.id)]
            plIds = self.env['packaging.line'].search(domain)
        elif self.operation == 'Packed':
            domain = domain + [('packed_by', '=', self.contractor_id.id)]
            plIds = self.env['packaging.line'].search(domain)
        res = []
        grandTotal = 0.00
        grandQty = 0.00
        D = defaultdict(list)
        for pid in plIds:
            contractor_rate = self.env['contractor.rate'].search([
            ('start_date', '<=', pid.package_date),
            ('end_date', '>=', pid.package_date),
            ('product_id', '=', pid.mo_id.product_id.id)])
            print "contractor_rate=====",contractor_rate,pid.package_date
            total = 0.0
            rate = 0.0
            if contractor_rate:
                if self.operation == 'Polish':
                    if self.polish_type == 'Manual' and pid.polish_type == 'Manual':
                        print ("manual==============")
                        rate = contractor_rate[0].polish_rate_manual
                    elif self.polish_type == 'Automatic' and pid.polish_type == 'Automatic':
                        print ("Automatic============")
                        rate = contractor_rate[0].polish_rate
                    if not self.polish_type:
                        if pid.polish_type == 'Manual':
                            rate = contractor_rate[0].polish_rate_manual
                        elif pid.polish_type == 'Automatic':
                            rate = contractor_rate[0].polish_rate
                if self.operation == 'Packed':
                    rate = contractor_rate[0].packaging_rate
            total = rate * pid.qty
            D[pid.package_date].append((
                pid.mo_id.name,
                pid.qty,
                round(total, 2),
                round(rate, 2),
                pid.mo_id.product_id.display_name,
                pid.polish_type))
            res.append({
                'package_date' : pid.package_date, 
                'mo' :  pid.mo_id.name,
                'qty': pid.qty,
                'total': round(total, 2),
                'rate': round(rate, 2),
                'product_id' : pid.mo_id.product_id.display_name,
                'polish_type': pid.polish_type
                })
            grandTotal += total
            grandQty += pid.qty
        for k, v in dict(D).items():
            l = []
            keyfunc = lambda t: (t[5],t[0], t[3], t[4])
            v.sort(key=keyfunc)
            for key, rows in itertools.groupby(v, keyfunc):
                qtySum = 0.0
                totolSum = 0.0
                for r in rows:
                    qtySum += r[1]
                    totolSum += r[2]
                
                l.append((key[0],key[1],key[2],key[3], qtySum, totolSum))
            D[k] = l
        print ('dk===================',dict(D.items()))
        resIds = self.read(
            ['start_date', 'end_date', 'contractor_id', 'product_id', 'operation', 'polish_type'])[0]
        res = sorted(D.items(), key = lambda x:datetime.strptime(x[0], '%Y-%m-%d'))

        print "res================",res
        resIds['pids'] = res
        resIds['grandTotal'] = round(grandTotal, 2)
        resIds['grandQty'] = grandQty
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
            render('mrp_rs_weighted_wires_packaging_contractors.rcc', docargs)
        

    @api.multi
    def print_contractor_cost(self):
        self.ensure_one()
        data = self.get_report_data()
        return self.env['report'].get_action(self, 'mrp_rs_weighted_wires_packaging_contractors.rcc', data=data)
