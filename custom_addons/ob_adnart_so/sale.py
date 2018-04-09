# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_compare
from lxml import etree


class plating_master(models.Model):
    _name = 'plating.master'
    
    name = fields.Char(string="Plating", required=True)

class sale_line_plating(models.Model):
    _name="sale.line.plating"
    
    _rec_name = 'plating_id'
    
    def onchange_plating_id(self,cr, uid, ids, line_ship_dt, product_qty):
        result={}
        if line_ship_dt:
            result.update({'plating_ship_date':line_ship_dt})
        if product_qty:
            result.update({'plating_qty':product_qty,'plating_ship_qty':product_qty})
        return {'value': result}

    plating_id = fields.Many2one('plating.master', string="Plating", )
    plating_1 = fields.Char(string="Plating@")
    plating_qty = fields.Float(string="Plating Qty")
    plating_ship_qty = fields.Float(string="Ship Qty")
    plating_ship_date = fields.Date(string="Ship Date")
    plaking_pkg_slip = fields.Char(string="Pkg. Slip")
    sale_plating_id = fields.Many2one('sale.order.line', string="Plating")
    mrp_plating_id = fields.Many2one('mrp.production', string="Plating")
    proc_plating_id = fields.Many2one('procurement.order', string="Plating")
    stock_plating_id = fields.Many2one('stock.move', string="Plating")

class metal_master(models.Model):
    _name = 'metal.master'

    name = fields.Char('Metal Name', required=True, translate=True)
    
class line_spacs_master(models.Model):
    _name = 'line.spacs.master'

    name = fields.Char('spacs', required=True, translate=True)

# class sale_color_master(models.Model):
#     _name = 'sale.color.master'
#     
#     name = fields.Char(string="Color", required=True)

class sale_color_type_master(models.Model):
    _name = 'sale.color.type.master'
    
    name = fields.Char(string="Type", required=True)
    
class sale_line_color(models.Model):
    _name = "sale.line.color"
    
    
    def onchange_color_qty(self,cr, uid, ids, qty):
        result={}
        if qty:
            result.update({'sale_color_qty':qty})
        return {'value': result}    

    
#     sale_color_id = fields.Many2one('sale.color.master', string="Color Name")
    sale_color = fields.Char(string="Color Name")
    sale_color_qty = fields.Float(string="Qty")
    sale_color_type_id = fields.Many2one('sale.color.type.master', string="Type")
    sale_color_type = fields.Selection(
        [('print', "P"), ('color', "C")],
        string=u"Type", required=True, default='color')
    sale_line_color_id = fields.Many2one('sale.order.line', string="Color")
    mrp_line_color_id = fields.Many2one('mrp.production', string="Color")
    proc_color_id = fields.Many2one('procurement.order', string="Color")
    stock_color_id = fields.Many2one('stock.move', string="Color")


# class sale_color_print_master(models.Model):
#     _name = 'sale.color.print.master'
#     
#     name = fields.Char(string="Color", required=True)

class sale_color_print_type_master(models.Model):
    _name = 'sale.color.print.type.master'
    
    name = fields.Char(string="Type",required=True)
    
class sale_line_color_print(models.Model):
    _name = "sale.line.color.print"
    
    def onchange_color_print_qty(self,cr, uid, ids, qty):
        result={}
        if qty:
            result.update({'sale_color_print_qty':qty})
        return {'value': result}
    
    
#     sale_color_print_id = fields.Many2one('sale.color.print.master', string="Color Name")
    sale_color_print = fields.Char(string="Color Name")
    sale_color_print_type = fields.Selection(
        [('print', "P"), ('color', "C")],
        string=u"Type", required=True, default='print')
    sale_color_print_qty = fields.Float(string="Qty")
    sale_color_print_type_id = fields.Many2one('sale.color.print.type.master', string="Type")
    sale_line_color_print_id = fields.Many2one('sale.order.line', string="Color")
    mrp_line_color_print_id = fields.Many2one('mrp.production', string="Print")
    proc_color_print_id = fields.Many2one('procurement.order', string="Print")
    stock_color_print_id = fields.Many2one('stock.move', string="Print")


class sale_order(models.Model):
    _inherit = "sale.order"


    def action_ship_create(self, cr, uid, ids, context=None):
        if not context: context = {}
        procurement_obj = self.pool.get('procurement.order')
        for order in self.browse(cr, uid, ids, context=context):
            for line in order.order_line:
                vals = {}
                line_specs_ids ,decoration_ids,packaging_ids, metal_ids,plating_line_list, sale_color_list, sale_color_print_list = [],[],[],[],[],[], []
                
                if line.prod_sample:
                    vals.update({'prod_sample':line.prod_sample})
                if line.prod_approval:
                    vals.update({'prod_approval':line.prod_approval})
                if line.prod_del_date:
                    vals.update({'prod_del_date':line.prod_del_date})
                if line.prod_approve_date:
                    vals.update({'prod_approve_date':line.prod_approve_date})
                if line.prod_sample_qty:
                    vals.update({'prod_sample_qty':line.prod_sample_qty})
                
                if line.size:
                    vals.update({'size':line.size})
                if line.metal_ids:
                    metal_ids = [x.id for x in line.metal_ids]
                if metal_ids:
                    vals.update({'metal_ids':[(6,0,metal_ids)]})
                
                if line.line_specs_ids:
                    line_specs_ids = [x.id for x in line.line_specs_ids]
                if line_specs_ids:
                    vals.update({'line_specs_ids':[(6,0,line_specs_ids)]})    
                
                if line.decoration_ids:
                    decoration_ids = [x.id for x in line.decoration_ids]
                if decoration_ids:
                    vals.update({'decoration_ids':[(6,0,decoration_ids)]})

                if line.packaging_ids:
                    packaging_ids = [x.id for x in line.packaging_ids]
                if packaging_ids:
                    vals.update({'packaging_ids':[(6,0,packaging_ids)]})



                if line.s_mould:
                    vals.update({'s_mould' : line.s_mould})
                if line.p_mould:
                    vals.update({'p_mould' : line.p_mould})
                if line.line_specs:
                    vals.update({'line_specs' : line.line_specs})
                if line.line_ship_dt:
                    vals.update({'line_ship_dt' : line.line_ship_dt})
                if line.prod_del_dt:
                    vals.update({'prod_del_dt' : line.prod_del_dt})
                    
#                 if line.overrun_qty:
#                     vals.update({'overrun_qty' : line.overrun_qty})
                if line.sale_plating_ids:
                    for plating_line in line.sale_plating_ids:
                        plating_line_list.append(plating_line.id)
                if plating_line_list:
                    vals.update({'proc_plating_ids': [(6,0,plating_line_list)]})
                if line.sale_color_ids:
                    for color_line in line.sale_color_ids:
                        sale_color_list.append(color_line.id)
                if sale_color_list:
                    vals.update({'proc_color_ids':[(6,0,sale_color_list)]})
                if line.sale_color_print_ids:
                    for color_print_line in line.sale_color_print_ids:
                        sale_color_print_list.append(color_print_line.id)
                if sale_color_print_list:
                    vals.update({'proc_color_print_ids':[(6,0,sale_color_print_list)]})
                if vals:
                    procure_ids = [p_id.id for p_id in line.procurement_ids]
                    procurement_obj.write(cr, uid, procure_ids, vals, context=context)
        return super(sale_order, self).action_ship_create(cr, uid, ids, context) 

    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
        res = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, group_id, context)
        procurement_obj = self.pool.get('procurement.order')
        
        line_specs_ids,packaging_ids,decoration_ids, metal_ids,plating_line_list,sale_color_list,sale_color_print_list = [],[],[],[],[],[], []
        vals = {}
        
        if line.prod_sample:
            vals.update({'prod_sample':line.prod_sample})
        if line.prod_approval:
            vals.update({'prod_approval':line.prod_approval})
        if line.prod_del_date:
            vals.update({'prod_del_date':line.prod_del_date})
        if line.prod_approve_date:
            vals.update({'prod_approve_date':line.prod_approve_date})
        if line.prod_sample_qty:
            vals.update({'prod_sample_qty':line.prod_sample_qty})
        
        if line.size:
            vals.update({'size':line.size})
        if line.metal_ids:
            metal_ids = [x.id for x in line.metal_ids]
        if metal_ids:
            vals.update({'metal_ids':[(6,0,metal_ids)]})
            
        if line.line_specs_ids:
            line_specs_ids = [x.id for x in line.line_specs_ids]
        if line_specs_ids:
            vals.update({'line_specs_ids':[(6,0,line_specs_ids)]})

        if line.decoration_ids:
            decoration_ids = [x.id for x in line.decoration_ids]
        if decoration_ids:
            vals.update({'decoration_ids':[(6,0,decoration_ids)]})

        if line.packaging_ids:
            packaging_ids = [x.id for x in line.packaging_ids]
        if packaging_ids:
            vals.update({'packaging_ids':[(6,0,packaging_ids)]})

        if line.s_mould:
            vals.update({'s_mould' : line.s_mould})
        if line.p_mould:
            vals.update({'p_mould' : line.p_mould})
        if line.line_specs:
            vals.update({'line_specs' : line.line_specs})
        if line.line_ship_dt:
            vals.update({'line_ship_dt' : line.line_ship_dt})
        if line.prod_del_dt:
            vals.update({'prod_del_dt' : line.prod_del_dt})
#         if line.overrun_qty:
#             vals.update({'overrun_qty' : line.overrun_qty})
        if line.sale_plating_ids:
            for plating_line in line.sale_plating_ids:
                plating_line_list.append(plating_line.id)
        if plating_line_list:
            vals.update({'proc_plating_ids': [(6,0,plating_line_list)]})
        if line.sale_color_ids:
            for color_line in line.sale_color_ids:
                sale_color_list.append(color_line.id)
        if sale_color_list:
            vals.update({'proc_color_ids':[(6,0,sale_color_list)]})
        if line.sale_color_print_ids:
            for color_print_line in line.sale_color_print_ids:
                sale_color_print_list.append(color_print_line.id)
        if sale_color_print_list:
            vals.update({'proc_color_print_ids':[(6,0,sale_color_print_list)]})
        if vals:
            procurement_obj.write(cr, uid, [line.procurement_ids.id], vals, context=context)
            res.update(vals)
        return res
    
class sale_order_line(models.Model):
    _inherit = "sale.order.line"

#     product_id = fields.Many2one('product.product', string='Product', change_default=True, readonly=True, states={'draft': [('readonly', False)]}, ondelete='restrict'),
    sale_plating_ids = fields.One2many('sale.line.plating','sale_plating_id','Plating', copy=True)
    sale_color_ids = fields.One2many('sale.line.color','sale_line_color_id','Colors',copy=True)
    sale_color_print_ids = fields.One2many('sale.line.color.print','sale_line_color_print_id','Print', copy=True)
    line_specs = fields.Char("Line Specs1")
    prod_del_dt = fields.Date("Production Del. Date")
    line_specs_ids  = fields.Many2many('line.spacs.master', 'sale_order_line_spacs','sale_order_line_spacs_id', 'sol_line_spacs_id',string='Line Specs')
    decoration_ids  = fields.Many2many('line.decoration', 'sale_order_line_decoration','sale_order_line_prdo_decorate_id', 'sale_order_line_decorate_id',string='Decoration')
    packaging_ids  = fields.Many2many('line.packaging', 'sale_order_line_packaging','sale_order_line_prdo_packaging_id', 'sale_order_line_packaging_id',string='Packaging')
    size = fields.Char(string="Size")
    metal_ids = fields.Many2many('metal.master', 'sale_order_line_metal','sale_order_line_metal_id', 'sol_metal_id',string='Metal')
    s_mould = fields.Char(string="S- Mould")
    p_mould = fields.Char(string="P- Mould")
    prod_sample = fields.Boolean('Sample')
    prod_approval = fields.Boolean("Approved")
    prod_del_date = fields.Date("Delivery date")
    prod_approve_date = fields.Date("Approved Date")
    prod_sample_qty = fields.Float(string="Quantity")
    

class StockMove(models.Model):
    
    _inherit = 'stock.move'
    
    stock_plating_ids = fields.One2many('sale.line.plating','stock_plating_id','Plating')
    stock_color_ids = fields.One2many('sale.line.color','stock_color_id','Color')
    stock_color_print_ids = fields.One2many('sale.line.color.print','stock_color_print_id','Print')
    size = fields.Char(string="Size")
    metal_ids = fields.Many2many('metal.master', 'stock_move_metal','stock_move_metal_id', 'stock_metal_id',string='Metal')
    s_mould = fields.Char(string="S- Mould")
    p_mould = fields.Char(string="P- Mould")
    line_specs = fields.Char("Line Space1")
    line_specs_ids  = fields.Many2many('line.spacs.master', 'stock_move_spacs','stock_move_spacs_id', 'stock_spacs_id',string='Specs')
    decoration_ids  = fields.Many2many('line.decoration', 'stock_move_decoration','stock_move_prdo_decorate_id', 'stock_move_decorate_id',string='Decoration')
    packaging_ids  = fields.Many2many('line.packaging', 'stock_move_packaging','stock_move_prdo_packaging_id', 'stock_move_packaging_id',string='Packaging')
    line_ship_dt = fields.Date(string='Ship Date')
    prod_del_dt = fields.Date("Production Del. Date")
    overrun_qty = fields.Float("Overrun Quantity", copy=False)
    prod_sample = fields.Boolean('Sample')
    prod_approval = fields.Boolean("Approved")
    prod_del_date = fields.Date("Delivery date")
    prod_approve_date = fields.Date("Approved Date")
    prod_sample_qty = fields.Float(string="Quantity")

    
    def _prepare_procurement_from_move(self, cr, uid, move, context=None):
        vals = super(StockMove, self)._prepare_procurement_from_move(cr, uid, move, context)
        metal_ids,plating_line_list, color_line_list , color_print_line_list, line_specs_ids,decoration_ids,packaging_ids = [],[],[],[],[],[],[]
        
        if move.prod_sample:
            vals.update({'prod_sample':move.prod_sample})
        if move.prod_approval:
            vals.update({'prod_approval':move.prod_approval})
        if move.prod_del_date:
            vals.update({'prod_del_date':move.prod_del_date})
        if move.prod_approve_date:
            vals.update({'prod_approve_date':move.prod_approve_date})
        if move.prod_sample_qty:
            vals.update({'prod_sample_qty':move.prod_sample_qty})
        
        if move.size:
            vals.update({'size':move.size})
        if move.metal_ids:
            metal_ids = [x.id for x in move.metal_ids]
        if metal_ids:
            vals.update({'metal_ids':[(6,0,metal_ids)]})
        if move.line_specs_ids:
            line_specs_ids = [x.id for x in move.line_specs_ids]
        if line_specs_ids:
            vals.update({'line_specs_ids':[(6,0,line_specs_ids)]})

        if move.decoration_ids:
            decoration_ids = [x.id for x in move.decoration_ids]
        if decoration_ids:
            vals.update({'decoration_ids':[(6,0,decoration_ids)]})

        if move.packaging_ids:
            packaging_ids = [x.id for x in move.packaging_ids]
        if packaging_ids:
            vals.update({'packaging_ids':[(6,0,packaging_ids)]})

        if move.s_mould:
            vals.update({'s_mould' : move.s_mould})
        if move.p_mould:
            vals.update({'p_mould' : move.p_mould})
        if move.line_specs:
            vals.update({'line_specs' : move.line_specs})
        if move.line_ship_dt:
            vals.update({'line_ship_dt' : move.line_ship_dt})

        if move.prod_del_dt:
            vals.update({'prod_del_dt' : move.prod_del_dt})
#         if move.overrun_qty:
#             vals.update({'overrun_qty' : move.overrun_qty})
        if move.stock_plating_ids:
            for plating_line in move.stock_plating_ids:
                plating_line_list.append(plating_line.id)
            if plating_line_list:
                vals.update({'proc_plating_ids': [(6,0,plating_line_list)]})
        if move.stock_color_ids:
            for color_line in move.stock_color_ids:
                color_line_list.append(color_line.id)
            if color_line_list:
                vals.update({'proc_color_ids': [(6,0,color_line_list)]})
        if move.stock_color_print_ids:
            for color_print_line in move.stock_color_print_ids:
                color_print_line_list.append(color_print_line.id)
            if color_print_line_list:
                vals.update({'proc_color_print_ids': [(6,0,color_print_line_list)]})
        return vals
