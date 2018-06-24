# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from collections import defaultdict, OrderedDict
from operator import itemgetter
import itertools
from datetime import datetime


moDict = {
    'weighted_wire' : 'weighted_wire_lines',
    'polished' : 'packaging_lines',
    'open_counter' : 'operation_lines',
}

class ProductionDetailWizard(models.TransientModel):
    _name = 'report.mrp_rs_weighted_wires_packaging_contractors.mopd'
    _description = 'Production Details'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    product_id = fields.Many2one('product.product', 'Product',
        domain="[('bom_ids', '!=', False)]")


    @api.multi
    def get_report_data(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        moObj = self.env['mrp.production']
        mainMoIds = moObj.search([
            ('product_id', '=', self.product_id.id)])
        print "moids===============",mainMoIds
        moIds = []
        sequenceDict = {}
        sequence = 0
        if mainMoIds:
            p1 = mainMoIds[0].parent_id

            c1 = self.env['mrp.production']
            c1 += mainMoIds[0]
            sequence += 1  
            sequenceDict[mainMoIds[0].product_id.id] = sequence
            while(p1):
                c1 += p1
                sequence += 1
                sequenceDict[p1.product_id.id] = sequence
                p1 = p1.parent_id
        print ("sequenceDict====",sequenceDict)
            

        mopds = []
          
        for mainMo1 in mainMoIds:
            parent1 = mainMo1.parent_id
            chain1 = self.env['mrp.production']
            chain1 += mainMo1
            while(parent1):
                chain1 += parent1
                parent1 = parent1.parent_id
            # lines = getattr(mo, moDict[mo.package_or_wire])
            print "chain===========",chain1
            mopds = sorted(mopds + chain1.mapped('product_id').ids)

        D = defaultdict(list)
        for mainMo in mainMoIds:
            parent = mainMo.parent_id
            chain = self.env['mrp.production']
            chain += mainMo
            while(parent):
                chain += parent
                parent = parent.parent_id
            # lines = getattr(mo, moDict[mo.package_or_wire])
            print "chain===========",chain
            print ":mopds==============", mopds
            for mo in chain:
                lines = []
                if mo.package_or_wire == 'weighted_wire':
                    lines = mo.weighted_wire_lines
                    for l in lines:
                        if l.wire_date >= self.start_date and l.wire_date <= self.end_date:
                            D[l.wire_date].append((mo.product_id.id,l.qty_produced, mo.product_id.display_name))
                            for mop in mopds:
                                if mo.product_id.id != mop:
                                    P = self.env['product.product'].browse(mop).display_name
                                    D[l.wire_date].append((mop,0.0,P))
                elif mo.package_or_wire == 'polished':
                    lines = mo.packaging_lines
                    for l in lines:
                        if l.package_date >= self.start_date and l.package_date <= self.end_date:
                            D[l.package_date].append((mo.product_id.id, l.qty, mo.product_id.display_name))
                            for mop in mopds:
                                if mo.product_id.id != mop:
                                    P = self.env['product.product'].browse(mop).display_name
                                    D[l.package_date].append((mop,0.0,P))
                elif mo.package_or_wire == 'open_counter':
                    lines = mo.operation_lines
                    for l in lines:
                        if l.operation_date >= self.start_date and l.operation_date <= self.end_date:
                            D[l.operation_date].append((mo.product_id.id,l.qty, mo.product_id.display_name))
                            for mop in mopds:
                                if mo.product_id.id != mop:
                                    P = self.env['product.product'].browse(mop).display_name
                                    D[l.operation_date].append((mop,0.0,P))
        print ("d=============1",dict(D.items()))
        productIds = []
        totalDict = defaultdict(list)
        for k, v in dict(D).items():
            l = []
            keyfunc = lambda t: (t[0],t[2])
            print "v=============",v
            v.sort(key=keyfunc)
            for key, rows in itertools.groupby(v, keyfunc):
                qtySum = sum(r[1] for r in rows)
                totalDict[key[0]].append((qtySum))
                productIds.append((key[0], key[1], qtySum))
                
                l.append((key[0],key[1],sequenceDict.get(key[0], -1), qtySum))
            D[k] = sorted(l,key=itemgetter(2), reverse=True)
        for tk, tv in dict(totalDict).items():
        
            print "rrrrrrrr===========",tv
            totalDict[tk] = sum(tv)
        print "totalDict===========",totalDict
        # sorted(data.items(), key = lambda x:datetime.strptime(x[0], '%d-%m-%Y'), reverse=True)
        O = sorted(D.items(), key = lambda x:datetime.strptime(x[0], '%Y-%m-%d'))
        print ("d=============",O)
        resIds = self.read(
            ['start_date', 'end_date', 'product_id'])[0]
        resIds['pids'] = O
        resIds['productIds'] = sorted(list(set(productIds)),key=itemgetter(0))
        print "productIds============",resIds['productIds']
        resIds['totalDict'] = OrderedDict(sorted(totalDict.items()))
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
            render('mrp_rs_weighted_wires_packaging_contractors.mopd', docargs)
        

    @api.multi
    def print_production_details(self):
        self.ensure_one()
        data = self.get_report_data()
        return self.env['report'].get_action(self, 'mrp_rs_weighted_wires_packaging_contractors.mopd', data=data)
