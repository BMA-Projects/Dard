# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
###############################################################################

from openerp.osv import fields, osv
from openerp import models, fields, api, _
import math
from openerp.exceptions import Warning

#----------------------------------------------------------
# Products
#----------------------------------------------------------
    
class product_template(models.Model):
    _inherit = 'product.template'

    over_run = fields.Float('Overrun (%)', copy=False)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_ship_create(self, cr, uid, ids, context=None):
        if not context: context = {}
        procurement_obj = self.pool.get('procurement.order')
        for order in self.browse(cr, uid, ids, context=context):
            for line in order.order_line:
                procure_ids = [p_id.id for p_id in line.procurement_ids]
                procurement_obj.write(cr, uid, procure_ids, {'over_run': line.over_run}, context=context)
        return super(SaleOrder, self).action_ship_create(cr, uid, ids, context)

    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
        res = super(SaleOrder, self)._prepare_order_line_procurement(cr, uid, order, line, group_id, context)
        if line.over_run:
            res.update({'over_run':line.over_run})
        return res


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _get_quantity(self):
        for rec in self:
            if rec.over_run:
                if not rec.overrun_qty:
                    overrun = rec.product_uom_qty * rec.over_run / 100
                    overrun_qty = rec.product_uom_qty + math.ceil(overrun)
                    rec.overrun_qty = overrun_qty
        
    over_run = fields.Float("Overrun (%)", copy=False)
    overrun_qty = fields.Float("Overrun Quantity", copy=False, compute="_get_quantity")

    @api.onchange('over_run')
    def _onchange_overrun(self):
        if self.over_run:
            overrun = self.product_uom_qty * self.over_run / 100
            overrun_qty = self.product_uom_qty + math.ceil(overrun)
            qty_double = overrun_qty * 2
            if overrun_qty <= 0:
                raise Warning(_('Overrun Quantity Should be always Positive !!!'))
            self.overrun_qty = overrun_qty

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        value = {}
        overrun_qty = 0.0
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        if product:
            over_run = self.pool.get("product.product").browse(cr, uid, product, context=context).over_run
            product_uos_qty = res.get('value',False).get('product_uos_qty',False)
            if product_uos_qty:
                overrun = product_uos_qty * over_run / 100
                overrun_qty = product_uos_qty + math.ceil(overrun)
            if res.get('value',False):
                res.get('value').update({'over_run': over_run, 'overrun_qty': overrun_qty})
            else:
                res = {'value': {'over_run': over_run, 'overrun_qty': overrun_qty}}
        return res

class StockMove(models.Model):
    
    _inherit = 'stock.move'
    
    over_run = fields.Float("Overrun (%)", copy=False, readonly=True)
    
    def _prepare_procurement_from_move(self, cr, uid, move, context=None):
        vals = super(StockMove, self)._prepare_procurement_from_move(cr, uid, move, context)
        if move.over_run:
            qty = (move.product_qty * move.over_run) / 100
            qty = move.product_qty + math.ceil(qty)
            vals.update({'product_qty': qty, 'over_run': move.over_run, 'product_uos_qty': qty})
        return vals

class procurement_order(models.Model):
    _inherit = 'procurement.order'

    over_run = fields.Float("Overrun (%)", copy=False, readonly=True)

    def _run_move_create(self, cr, uid, procurement, context=None):
        res = super(procurement_order, self)._run_move_create(cr, uid, procurement, context)
        res.update({'over_run': procurement.over_run})
        return res
    
    def _prepare_mo_vals(self, cr, uid, procurement, context=None):
        res = super(procurement_order, self)._prepare_mo_vals(cr, uid, procurement, context)
        if procurement.over_run:
            res.update({'over_run':procurement.over_run})
        return res

    @api.v7
    def make_po(self, cr, uid, ids, context=None):
        """ Resolve the purchase from procurement, which may result in a new PO creation, a new PO line creation or a quantity of product will be as overrun calculation
        @return: dictionary giving for each procurement its related resolving PO line.
        """
        if context is None:
            context = {}
        po_line_obj = self.pool.get('purchase.order.line')
        product_obj = self.pool.get('product.product')
        res = super(procurement_order, self).make_po(cr, uid, ids, context=context)
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.purchase_id:
                for po_line in procurement.purchase_id.order_line:
                     if po_line.product_id == procurement.product_id:
                         po_line_obj.write(cr, uid, [po_line.id], {'over_run':procurement.over_run})
        return res
    
    def make_mo(self, cr, uid, ids, context=None):
        if not context: context = {}
        res = super(procurement_order, self).make_mo(cr, uid, ids, context=context)
        mrp_production_obj = self.pool.get('mrp.production')
        for proc in self.browse(cr, uid, res.keys(),context):
            mrp_production_obj.write(cr, uid, [res.get(proc.id)], {'over_run': proc.over_run}, context=context)
        return res
    
class mrp_production(models.Model):
    _inherit = 'mrp.production'

    over_run = fields.Float("Overrun (%)", copy=False, readonly=True)

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    over_run = fields.Float("Overrun (%)", copy=False, readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
