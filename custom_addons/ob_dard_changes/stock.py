# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning


import openerp.addons.decimal_precision as dp

class stock_move(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_from_move(self, cr, uid, move, context=None):
        vals = super(stock_move, self)._prepare_procurement_from_move(cr, uid, move, context)
        if move.over_run:
            vals.update({'product_qty': move.product_qty, 'over_run': move.over_run, 'product_uos_qty': move.product_qty})
        return vals


    def action_scrap(self, cr, uid, ids, quantity, location_id, restrict_lot_id=False, restrict_partner_id=False, context=None):
        res = super(stock_move, self).action_scrap(cr, uid, ids, quantity, location_id, restrict_lot_id, restrict_partner_id, context=context)
        if context.get('scrap', False):
            return res
        sale_obj = self.pool.get('sale.order')
        quant_obj = self.pool.get('stock.quant')
        order_line_obj = self.pool.get('sale.order.line')
        pack_obj = self.pool.get('stock.pack.operation')
        if res and isinstance(res[0], list):
            res = res[0]
        for move in self.browse(cr, uid, res, context=context):
            order_line_id = order_line_obj.search(cr, uid, [('sol_seq', 'like',move.production_id.sub_origin)], context=context)
            if not order_line_id:
                continue
            sale_id = sale_obj.search(cr, uid, [('procurement_group_id', '=',  move.group_id.id)], context=context)
            for sale in sale_obj.browse(cr, uid, sale_id, context=context):
                total_qty = 0.0
                remaining_qty = 0.0 
                for picking in sale.picking_ids:
                    if picking.state == 'done':
                        for moveline in picking.move_lines:
                            if moveline.product_id.id == move.product_id.id and order_line_id[0] == moveline.sol_id.id:
                                if not moveline.scrapped:
                                    total_qty += moveline.product_uom_qty
                        continue
                if total_qty:
                    remaining_qty = remaining_qty - total_qty
                for picking in sale.picking_ids:
                    if picking.state == 'done':
                        continue
                    for moveline in move.production_id.move_created_ids2:
                        if not moveline.scrapped:
                            remaining_qty += moveline.product_uom_qty
                        if moveline.scrapped:
                            remaining_qty -= moveline.product_uom_qty
                    if remaining_qty < 0.0:
                        raise Warning(_('You can not scrap more than produced quantity'))
                    move_dict = {}
                    new_quantity = quantity
                    for moveline in picking.move_lines:
                        if moveline.product_id.id == move.product_id.id and order_line_id[0] == moveline.sol_id.id:
                            if moveline.sol_id.id in move_dict.keys():
                                 new_quantity = move_dict.get(moveline.sol_id.id)
                            if moveline.product_uom_qty < new_quantity:
                                move_qty = new_quantity - moveline.product_uom_qty
                                move_dict.update({moveline.sol_id.id: move_qty})
                                self.write(cr, uid, [moveline.id], {'product_uom_qty': 0.0, 'product_uos_qty': 0.0}, context=context)
                                continue
                            else:
                                if new_quantity:
                                    qty = moveline.product_uom_qty - new_quantity
                                else:
                                    qty = moveline.product_uom_qty - quantity
                                self.write(cr, uid, [moveline.id], {'product_uom_qty': qty, 'product_uos_qty': qty}, context=context)
                                break
                for picking in sale.picking_ids:
                    for pack_id in picking.pack_operation_ids:
                        if pack_id.product_id.id == move.product_id.id:
                            qty = pack_id.product_qty - quantity
                            if qty < 0.0:
                                qty = 0.0
                            pack_obj.write(cr, uid, [pack_id.id], {'product_qty': qty}, context=context)
        return res


class stock_picking(models.Model):
    _inherit='stock.picking'
    
    @api.model
    def create(self, vals):
        if vals.has_key('origin') and vals.get('origin'):
            vals['note'] = self.env['sale.order'].search([('name', '=', vals.get('origin'))]).note
        return super(stock_picking, self).create(vals)
    
    @api.one
    @api.depends('partner_id')
    def _get_supplier(self):
        
        if self.picking_type_id.code == 'incoming':
            po_id = self.env['purchase.order'].search([('name','=',self.origin)])
            self.supplier_id = po_id.partner_id.id
    
    supplier_id = fields.Many2one('res.partner', compute=_get_supplier, readonly=True, string="Supplier")
    
    @api.model
    def _create_invoice_from_picking(self,picking, vals):
        if 'partner_id' in vals and vals.get('partner_id', False):
            partner_id = vals.get('partner_id')
            partner = self.env['res.partner'].browse(partner_id)
            zorch_id = self.env['ir.model.data'].get_object_reference('ob_dard_changes', 'zorch_categ_id')[1]
            if picking.sale_id:
                vals.update({
                    'client_po_ref': picking.sale_id.client_po_ref,
                    'picking_id': picking.id,
                    'comment': picking.sale_id.note
                })
                if partner.category_id and zorch_id in partner.category_id.ids:
                    vals.update({
                        'zorch_visible': picking.sale_id.zorch_visible,
                        'zorch_sale_order': picking.sale_id.zorch_sale_order,
                        'zorch_po_number': picking.sale_id.zorch_po_number
                    })
        return super(stock_picking,self)._create_invoice_from_picking(picking,vals)


from openerp.osv import fields, osv
class stock_quant(osv.osv):
    """
    Quants are the smallest unit of stock physical instances
    """
    _inherit = "stock.quant"
    
    def _calc_inventory_value(self, cr, uid, ids, name, attr, context=None):
        context = dict(context or {})
        res = {}
        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        for quant in self.browse(cr, uid, ids, context=context):
            context.pop('force_company', None)
            if quant.company_id.id != uid_company_id:
                #if the company of the quant is different than the current user company, force the company in the context
                #then re-do a browse to read the property fields for the good company.
                context['force_company'] = quant.company_id.id
                quant = self.browse(cr, uid, quant.id, context=context)
            res[quant.id] = self._get_inventory_value(cr, uid, quant, context=context)
        return res
    
    _columns = {
    
        'inventory_value': fields.function(_calc_inventory_value, string="Inventory Value", type='float', readonly=True, digits_compute=dp.get_precision('Product Price')),
    
    }