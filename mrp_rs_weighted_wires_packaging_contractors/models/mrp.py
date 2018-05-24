# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math


class mrpProductionInh(models.Model):
    _inherit = 'mrp.production'

    @api.depends('weighted_wire_lines', 'weighted_wire_lines.qty_produced')
    def compute_wire_qty(self):
        for mr in self:
            total = 0.0
            for wr in mr.weighted_wire_lines:
                total += wr.qty_produced
            mr.wire_qty = total

    @api.depends('packaging_lines')
    def compute_packaging_qty(self):
        for mr in self:
            total = 0.0
            for pl in mr.packaging_lines:
                total += pl.qty
            mr.packaging_qty = total

    @api.depends('operation_lines')
    def compute_operation_qty(self):
        for mr in self:
            total = 0.0
            for ol in mr.operation_lines:
                total += ol.qty
            mr.operation_qty = total

    wire_used = fields.Many2one(
    	'product.product', 
    	string='Wire Used',
        readonly=True, states={'confirmed': [('readonly', False)]},
    	)
    package_or_wire = fields.Selection([
        ('weighted_wire', 'Uses Weighted Wire'),
        ('polished', 'Polished/Packed'),
        ('open_counter', 'Open/Counter'),
        ('none', 'None')], related="bom_id.package_or_wire", string='Wire Or Polished',
        default='none')
    weighted_wire_lines = fields.One2many(
        'weighted.wire.line', 'mo_id', string='Weighted Wire Lines')
    packaging_lines = fields.One2many(
        'packaging.line', 'mo_id', string='Packaging Lines')
    operation_lines = fields.One2many('operation.detail.line', 'mo_id', string='Operation Lines')
    wire_qty = fields.Float('Qty Produced', compute="compute_wire_qty", store=True, default=0.00)
    packaging_qty = fields.Float('Qty Produced', compute="compute_packaging_qty", store=True, default=0.00)
    operation_qty = fields.Float('Qty Produced', compute="compute_operation_qty", store=True, default=0.00)

    @api.onchange('bom_id')
    def onchange_bom_id(self):
        if not self.bom_id:
            self.wire_used = False
        else:
            self.wire_used = self.bom_id.wire_used.id


    @api.model
    def _update_product_to_produce_custom(self, production, qty):
        production_move = production.move_finished_ids.filtered(lambda x:x.product_id.id == production.product_id.id and x.state not in ('done', 'cancel'))
        # print "product move======",production_move
        if production_move:
            production_move.write({'product_uom_qty': qty})
        else:
            production_move = production._generate_finished_moves()
            print "inside else 1product move======",production_move
            production_move = production.move_finished_ids.filtered(lambda x : x.state not in ('done', 'cancel') and production.product_id.id == x.product_id.id)
            print "inside else product move======",production_move
            production_move.write({'product_uom_qty': qty})

        Production = self.env['mrp.production']
        UoM = self.env['product.uom']
        for sub_product_line in production.bom_id.sub_products:
            move = production.move_finished_ids.filtered(lambda x: x.subproduct_id == sub_product_line and x.state not in ('done', 'cancel'))
            if move:
                product_uom_factor = production.product_uom_id._compute_quantity(production.product_qty - production.qty_produced, production.bom_id.product_uom_id)
                qty1 = sub_product_line.product_qty
                qty1 *= product_uom_factor / production.bom_id.product_qty
                move[0].write({'product_uom_qty': qty1})
            else:
                production._create_byproduct_move(sub_product_line)

    @api.multi
    def change_prod_qty_custom(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for wizard in self:
            production = wizard
            produced = sum(production.move_finished_ids.filtered(lambda m: m.product_id == production.product_id).mapped('quantity_done'))
            if wizard._context.get('wire_approve', False):
                if wizard.wire_qty < wizard.product_qty:
                    raise UserError(_("Approve quantity must be higher than quantity to produce"))
                if wizard.wire_qty < produced:
                    raise UserError(_("You have already processed %d. Please input a quantity higher than %d ")%(produced, produced))
                production.write({'product_qty': wizard.wire_qty})
                if production.weighted_wire_lines:
                    for wrl in production.weighted_wire_lines:
                        wrl.state = 'done'
            elif wizard._context.get('package_approve', False):
                if wizard.packaging_qty < wizard.product_qty:
                    raise UserError(_("Approve quantity must be higher than quantity to produce"))
                if wizard.packaging_qty < produced:
                    raise UserError(_("You have already processed %d. Please input a quantity higher than %d ")%(produced, produced))
                production.write({'product_qty': wizard.packaging_qty})
                if production.packaging_lines:
                    for pl in production.packaging_lines:
                        pl.state = 'done'
            elif wizard._context.get('operation_approve', False):
                if wizard.operation_qty < wizard.product_qty:
                    raise UserError(_("Approve quantity must be higher than quantity to produce"))
                if wizard.operation_qty < produced:
                    raise UserError(_("You have already processed %d. Please input a quantity higher than %d ")%(produced, produced))
                production.write({'product_qty': wizard.operation_qty})
                if production.operation_lines:
                    for ol in production.operation_lines:
                        ol.state = 'done'
            done_moves = production.move_finished_ids.filtered(lambda x: x.state == 'done' and x.product_id == production.product_id)
            qty_produced = production.product_id.uom_id._compute_quantity(sum(done_moves.mapped('product_qty')), production.product_uom_id)
            factor = production.product_uom_id._compute_quantity(production.product_qty - qty_produced, production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(production.product_id, factor, picking_type=production.bom_id.picking_type_id)
            for line, line_data in lines:
                production._update_raw_move(line, line_data)
            operation_bom_qty = {}
            for bom, bom_data in boms:
                for operation in bom.routing_id.operation_ids:
                    operation_bom_qty[operation.id] = bom_data['qty']
            self._update_product_to_produce_custom(production, production.product_qty - qty_produced)
            moves = production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            moves.do_unreserve()
            moves.action_assign()
            for wo in production.workorder_ids:
                operation = wo.operation_id
                if operation_bom_qty.get(operation.id):
                    cycle_number = math.ceil(operation_bom_qty[operation.id] / operation.workcenter_id.capacity)  # TODO: float_round UP
                    wo.duration_expected = (operation.workcenter_id.time_start +
                                 operation.workcenter_id.time_stop +
                                 cycle_number * operation.time_cycle * 100.0 / operation.workcenter_id.time_efficiency)
                quantity = wo.qty_production - wo.qty_produced
                if production.product_id.tracking == 'serial':
                    quantity = 1.0 if not float_is_zero(quantity, precision_digits=precision) else 0.0
                else:
                    quantity = quantity if (quantity > 0) else 0
                if float_is_zero(quantity, precision_digits=precision):
                    wo.final_lot_id = False
                    wo.active_move_lot_ids.unlink()
                wo.qty_producing = quantity
                if wo.qty_produced < wo.qty_production and wo.state == 'done':
                    wo.state = 'progress'
                # assign moves; last operation receive all unassigned moves
                # TODO: following could be put in a function as it is similar as code in _workorders_create
                # TODO: only needed when creating new moves
                moves_raw = production.move_raw_ids.filtered(lambda move: move.operation_id == operation and move.state not in ('done', 'cancel'))
                if wo == production.workorder_ids[-1]:
                    moves_raw |= production.move_raw_ids.filtered(lambda move: not move.operation_id)
                moves_finished = production.move_finished_ids.filtered(lambda move: move.operation_id == operation) #TODO: code does nothing, unless maybe by_products?
                moves_raw.mapped('move_lot_ids').write({'workorder_id': wo.id})
                (moves_finished + moves_raw).write({'workorder_id': wo.id})
                if quantity > 0 and wo.move_raw_ids.filtered(lambda x: x.product_id.tracking != 'none') and not wo.active_move_lot_ids:
                    wo._generate_lot_ids()
        return {}


class MrpBomInh(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'mrp.bom'

    def get_domain_product(self):
    	ir_model_data = self.env['ir.model.data']
    	pTempId = ir_model_data.get_object_reference(
    		'mrp_rs_weighted_wires_packaging_contractors',
    		'product_weighted_wire')[1]
    	productIds = self.env['product.product'].search([('product_tmpl_id', '=', pTempId)]).mapped('id')
    	return [('id', 'in', productIds)]

    package_or_wire = fields.Selection([
        ('weighted_wire', 'Uses Weighted Wire'),
        ('polished', 'Polished/Packed'),
        ('open_counter', 'Open/Counter'),
        ('none', 'None')], string='BOM Criteria',
        default='none')
    wire_used = fields.Many2one(
    	'product.product', 
    	string='Wire Used',
    	domain=lambda self : self.get_domain_product()
    	)

    @api.multi
    @api.onchange('package_or_wire')
    def onchange_package_or_wire(self):
        print "onchange_package_or_wire========="
        if self.package_or_wire != 'weighted_wire':
            self.wire_used = False

class weightedWireLine(models.Model):
    _name = 'weighted.wire.line'
    _description = 'Weighted Wire Lines'

    @api.multi
    @api.depends('wire_issued')
    def compute_qty_produced(self):
        for wr in self:
            if wr.wire_used and (wr.wire_used.weight > 0):
                wr.qty_produced = wr.wire_issued / (wr.wire_used.weight/1000)

    wire_date = fields.Date('Date', default=fields.Date.context_today,
                readonly=True, states={'draft': [('readonly', False)]})
    wire_used = fields.Many2one(
    	'product.product', 
    	string='Wire Used',
        readonly=True, states={'draft': [('readonly', False)]}
    	)

    issued_to = fields.Many2one('mrp.contractor', 'Issued To', readonly=True, states={'draft': [('readonly', False)]})
    wire_issued = fields.Float(
        'Wire Issued(Kg)', digits=dp.get_precision('Product Unit of Measure'), default=0.000,
        readonly=True, states={'draft': [('readonly', False)]})
    qty_produced = fields.Float('Qty Produced', compute="compute_qty_produced", store=True, default=0.00)
    mo_id = fields.Many2one('mrp.production', string='MO', ondelete='cascade')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Status',
        default='draft',
        readonly=True, states={'draft': [('readonly', False)]})

    @api.multi
    def unlink(self):
        if self.state == 'done':
            raise UserError(_('Cannot delete a record'))
        return super(weightedWireLine, self).unlink()
    # @api.model
    # def create(self, vals):
    #     print "wire line create called=========="
    #     res = super(weightedWireLine, self).create(vals)
    #     if res and res.mo_id:
    #         print "res.mo_id.wire_qty=============",res.mo_id.wire_qty
    #         if res.mo_id.product_qty < res.mo_id.wire_qty:
    #             raise UserError(_('Please Click On Approve Button'))
    #     return res

    # @api.multi
    # def write(self, vals):
    #     res = super(weightedWireLine, self).create(vals)
    #     # if self and self.mo_id:
    #     #     print "res.mo_id.wire_qty=============",self.mo_id.wire_qty
    #     #     if self.mo_id.product_qty < self.mo_id.wire_qty:
    #     #         raise UserError(_('Please Click On Approve Button'))
    #     return res


class mrpContractors(models.Model):
    _name = 'mrp.contractor'
    _description = 'Contractors'

    name = fields.Char('Name', required=True)
    start_date = fields.Date('Start Date', default=fields.Date.context_today)
    end_date = fields.Date('End Date')
    active = fields.Boolean('Active', default=True)

class ContractorsRates(models.Model):
    _name = 'contractor.rate'
    _rec_name = 'product_id'
    _description = 'Contractor Rates'

    product_id = fields.Many2one(
        'product.product', 'Product Variant', required=True)
    polish_rate = fields.Float('Polish Rate', digits=(16,2), default=0.00)
    packaging_rate = fields.Float('Packaging Rate', digits=(16,2), default=0.00)
    start_date = fields.Date('Start Date', default=fields.Date.context_today)
    end_date = fields.Date('End Date')
    active = fields.Boolean('Active', default=True)


class packagingLine(models.Model):
    _name = 'packaging.line'
    _description = 'Packaging Lines'

    mo_id = fields.Many2one('mrp.production', string='MO', ondelete='cascade')
    package_date = fields.Date('Date', default=fields.Date.context_today,
        readonly=True, states={'draft': [('readonly', False)]})
    polished_by = fields.Many2one('mrp.contractor', 'Polished By',
        readonly=True, states={'draft': [('readonly', False)]})
    packed_by = fields.Many2one('mrp.contractor', 'Packed By',
        readonly=True, states={'draft': [('readonly', False)]})
    qty = fields.Float('Quantity', default=0.00,
        readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Status',
        default='draft')

    @api.multi
    def unlink(self):
        if self.state == 'done':
            raise UserError(_('Cannot delete a record'))
        return super(packagingLine, self).unlink()

class OperationDetailLine(models.Model):
    _name = 'operation.detail.line'
    _description = 'Operation Detail'

    mo_id = fields.Many2one('mrp.production', string='MO', ondelete='cascade')
    operation_date = fields.Date('Date', default=fields.Date.context_today,
        readonly=True, states={'draft': [('readonly', False)]})
    performed_by = fields.Many2one('mrp.contractor', 'Performed by',
        readonly=True, states={'draft': [('readonly', False)]})
    qty = fields.Float('Quantity', default=0.00,
        readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Status',
        default='draft')

    @api.multi
    def unlink(self):
        if self.state == 'done':
            raise UserError(_('Cannot delete a record'))
        return super(OperationDetailLine, self).unlink()


# class MrpProductProduceInh(models.TransientModel):
#     _inherit = "mrp.product.produce"
    

#     @api.multi
#     def do_produce(self):
#         res = super(MrpProductProduceInh, self).do_produce()
#         if self.production_id.weighted_wire_lines:
#             for wrl in self.production_id.weighted_wire_lines:
#                 wrl.state = 'done'
#         if self.production_id.packaging_lines:
#             for pl in self.production_id.packaging_lines:
#                 pl.state = 'done'
#         if self.production_id.operation_lines:
#             for ol in self.production_id.operation_lines:
#                 ol.state = 'done'
#         return res