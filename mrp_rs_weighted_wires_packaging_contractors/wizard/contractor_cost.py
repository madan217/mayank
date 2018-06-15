# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

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
        for pid in plIds:
            contractor_rate = self.env['contractor.rate'].search([
            ('start_date', '>=', self.start_date),
            ('end_date', '<=', self.end_date),
            ('product_id', '=', pid.mo_id.product_id.id)])

            total = 0.0
            rate = 0.0
            if contractor_rate:
                if self.operation == 'Polish':
                    rate = contractor_rate[0].polish_rate
                if self.operation == 'Packed':
                    rate = contractor_rate[0].packaging_rate
            total = rate * pid.qty
            res.append({
                'package_date' : pid.package_date, 
                'mo' :  pid.mo_id.name,
                'qty': pid.qty,
                'total': total,
                'rate': rate,
                'product_id' : pid.mo_id.product_id.display_name
                })
            grandTotal += total
            grandQty += pid.qty
        resIds = self.read(
            ['start_date', 'end_date', 'contractor_id', 'product_id', 'operation'])[0]
        resIds['pids'] = res
        resIds['grandTotal'] = grandTotal
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
