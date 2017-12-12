# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _

class procurement_order(models.Model):
    _inherit = 'procurement.order'
    
    sub_origin = fields.Char('Sub Source Document', size=32)
    proc_plating_ids = fields.One2many('sale.line.plating','proc_plating_id','Plating')
    proc_color_ids = fields.One2many('sale.line.color','proc_color_id','Color')
    proc_color_print_ids = fields.One2many('sale.line.color.print','proc_color_print_id','Print')
    size = fields.Char(string="Size")
    metal_ids = fields.Many2many('metal.master', 'proc_order_metal','proc_order_metal_id', 'proc_metal_id',string='Metal')
    line_specs_ids  = fields.Many2many('line.spacs.master', 'proc_order_spacs','proc_order_spac_id', 'proc_spacs_id',string='Specs')
    decoration_ids  = fields.Many2many('line.decoration', 'proc_order_decoration','proc_order_prdo_decorate_id', 'proc_order_decorate_id',string='Decoration')
    packaging_ids  = fields.Many2many('line.packaging', 'proc_order_packaging','proc_order_prdo_packaging_id', 'proc_order_packaging_id',string='Packaging')
    s_mould = fields.Char(string="S- Mould")
    p_mould = fields.Char(string="P- Mould")
    line_specs = fields.Char("Line Space1")
    prod_del_dt = fields.Date("Production Del. Date")
    line_ship_dt = fields.Date(string='Ship Date')
    overrun_qty = fields.Float("Overrun Quantity", copy=False)
    prod_sample = fields.Boolean('Sample')
    prod_approval = fields.Boolean("Approved")
    prod_del_date = fields.Date("Delivery date")
    prod_approve_date = fields.Date("Approved Date")
    prod_sample_qty = fields.Float(string="Quantity")
   
    
    def _run_move_create(self, cr, uid, procurement, context=None):
        res = super(procurement_order, self)._run_move_create(cr, uid, procurement, context)
        line_specs_ids,decoration_ids,packaging_ids, metal_ids , plating_line_list, color_line_list,color_print_line_list = [],[],[],[],[], [],[]
        
        if procurement.prod_sample:
            res.update({'prod_sample':procurement.prod_sample})
        if procurement.prod_approval:
            res.update({'prod_approval':procurement.prod_approval})
        if procurement.prod_del_date:
            res.update({'prod_del_date':procurement.prod_del_date})
        if procurement.prod_approve_date:
            res.update({'prod_approve_date':procurement.prod_approve_date})
        if procurement.prod_sample_qty:
            res.update({'prod_sample_qty':procurement.prod_sample_qty})
        
        if procurement.size:
            res.update({'size':procurement.size})
        if procurement.metal_ids:
            metal_ids = [x.id for x in procurement.metal_ids]
        if metal_ids:
            res.update({'metal_ids':[(6,0,metal_ids)]})
        if procurement.line_specs_ids:
            line_specs_ids = [x.id for x in procurement.line_specs_ids]
        if line_specs_ids:
            res.update({'line_specs_ids':[(6,0,line_specs_ids)]})

        if procurement.decoration_ids:
            decoration_ids = [x.id for x in procurement.decoration_ids]
        if decoration_ids:
            res.update({'decoration_ids':[(6,0,decoration_ids)]})

        if procurement.packaging_ids:
            packaging_ids = [x.id for x in procurement.packaging_ids]
        if packaging_ids:
            res.update({'packaging_ids':[(6,0,packaging_ids)]})

        if procurement.s_mould:
            res.update({'s_mould' : procurement.s_mould})
        if procurement.p_mould:
            res.update({'p_mould' : procurement.p_mould})
        if procurement.line_specs:
            res.update({'line_specs' : procurement.line_specs})
        if procurement.line_ship_dt:
            res.update({'line_ship_dt' : procurement.line_ship_dt})
        if procurement.prod_del_dt:
            res.update({'prod_del_dt' : procurement.prod_del_dt})
#         if procurement.overrun_qty:
#             res.update({'overrun_qty' : procurement.overrun_qty})
        if procurement.proc_plating_ids:
            for plating_line in procurement.proc_plating_ids:
                plating_line_list.append(plating_line.id)
            if plating_line_list:
                res.update({'stock_plating_ids': [(6,0,plating_line_list)]})
        if procurement.proc_color_ids:
            for color_line in procurement.proc_color_ids:
                color_line_list.append(color_line.id)
            if color_line_list:
                res.update({'stock_color_ids': [(6,0,color_line_list)]})
        if procurement.proc_color_print_ids:
            for color_print_line in procurement.proc_color_print_ids:
                color_print_line_list.append(color_print_line.id)
            if color_print_line_list:
                res.update({'stock_color_print_ids': [(6,0,color_print_line_list)]})
        return res
    
    def _prepare_mo_vals(self, cr, uid, procurement, context=None):
        res = super(procurement_order, self)._prepare_mo_vals(cr, uid, procurement, context)
        
        line_specs_ids,decoration_ids,packaging_ids, metal_ids, plating_line_list ,color_line_list,color_print_line_list = [],[],[],[],[], [], []
        
        if procurement.prod_sample:
            res.update({'prod_sample':procurement.prod_sample})
        if procurement.prod_approval:
            res.update({'prod_approval':procurement.prod_approval})
        if procurement.prod_del_date:
            res.update({'prod_del_date':procurement.prod_del_date})
        if procurement.prod_approve_date:
            res.update({'prod_approve_date':procurement.prod_approve_date})
        if procurement.prod_sample_qty:
            res.update({'prod_sample_qty':procurement.prod_sample_qty})
        
        if procurement.size:
            res.update({'size':procurement.size})
        if procurement.metal_ids:
            metal_ids = [x.id for x in procurement.metal_ids]
        if metal_ids:
            res.update({'metal_ids':[(6,0,metal_ids)]})
        
        if procurement.line_specs_ids:
            line_specs_ids = [x.id for x in procurement.line_specs_ids]
        if line_specs_ids:
            res.update({'line_specs_ids':[(6,0,line_specs_ids)]})    
        
        if procurement.decoration_ids:
            decoration_ids = [x.id for x in procurement.decoration_ids]
        if decoration_ids:
            res.update({'decoration_ids':[(6,0,decoration_ids)]})

        if procurement.packaging_ids:
            packaging_ids = [x.id for x in procurement.packaging_ids]
        if packaging_ids:
            res.update({'packaging_ids':[(6,0,packaging_ids)]})

        if procurement.s_mould:
            res.update({'s_mould' : procurement.s_mould})
        if procurement.p_mould:
            res.update({'p_mould' : procurement.p_mould})
        if procurement.line_specs:
            res.update({'line_specs' : procurement.line_specs})
        if procurement.line_ship_dt:
            res.update({'line_ship_dt' : procurement.line_ship_dt})
        if procurement.prod_del_dt:
            res.update({'prod_del_dt' : procurement.prod_del_dt})
#         if procurement.overrun_qty:
#             res.update({'overrun_qty' : procurement.overrun_qty})
        if procurement.proc_plating_ids:
            for plating_line in procurement.proc_plating_ids:
                plating_line_list.append(plating_line.id)
            if plating_line_list:
                res.update({'mrp_plating_ids': [(6,0,plating_line_list)]})
        if procurement.proc_color_ids:
            for color_line in procurement.proc_color_ids:
                color_line_list.append(color_line.id)
            if color_line_list:
                res.update({'mrp_color_ids': [(6,0,color_line_list)]})
        if procurement.proc_color_print_ids:
            for color_print_line in procurement.proc_color_print_ids:
                color_print_line_list.append(color_print_line.id)
            if color_print_line_list:
                res.update({'mrp_color_print_ids': [(6,0,color_print_line_list)]})
        return res
  
    def make_mo(self, cr, uid, ids, context=None):
        res = super(procurement_order, self).make_mo(cr, uid, ids, context=context)
        mrp_production_obj = self.pool.get('mrp.production')
        vals = {}
        for proc in self.browse(cr, uid, res.keys(),context):
            line_specs_ids,packaging_ids,decoration_ids , metal_ids , plating_line_list, color_line_list, color_print_line_list = [],[],[],[],[],[] ,[]
            
            if proc.prod_sample:
                res.update({'prod_sample':proc.prod_sample})
            if proc.prod_approval:
                res.update({'prod_approval':proc.prod_approval})
            if proc.prod_del_date:
                res.update({'prod_del_date':proc.prod_del_date})
            if proc.prod_approve_date:
                res.update({'prod_approve_date':proc.prod_approve_date})
            if proc.prod_sample_qty:
                res.update({'prod_sample_qty':proc.prod_sample_qty})
            if proc.size:
                res.update({'size':proc.size})
            if proc.metal_ids:
                metal_ids = [x.id for x in proc.metal_ids]
            if metal_ids:
                res.update({'metal_ids':[(6,0,metal_ids)]})
            
            if proc.line_specs_ids:
                line_specs_ids = [x.id for x in proc.line_specs_ids]
            if line_specs_ids:
                res.update({'line_specs_ids':[(6,0,line_specs_ids)]})
            
            if proc.decoration_ids:
                decoration_ids = [x.id for x in proc.decoration_ids]
            if decoration_ids:
                res.update({'decoration_ids':[(6,0,decoration_ids)]})

            if proc.packaging_ids:
                packaging_ids = [x.id for x in proc.packaging_ids]
            if packaging_ids:
                res.update({'packaging_ids':[(6,0,packaging_ids)]})


            if proc.s_mould:
                res.update({'s_mould' : proc.s_mould})
            if proc.p_mould:
                res.update({'p_mould' : proc.p_mould})
            if proc.line_specs:
                res.update({'line_specs' : proc.line_specs})
            if proc.line_ship_dt:
                res.update({'line_ship_dt' : proc.line_ship_dt})
            if proc.prod_del_dt:
                res.update({'prod_del_dt' : proc.prod_del_dt})
            if proc.overrun_qty:
                res.update({'overrun_qty' : proc.overrun_qty})
            if proc.proc_plating_ids:
                for plating_line in proc.proc_plating_ids:
                    plating_line_list.append(plating_line.id)
                if plating_line_list:
                    vals.update({'mrp_plating_ids': [(6,0,plating_line_list)]})
            if proc.proc_color_ids:
                for color_line in proc.proc_color_ids:
                    color_line_list.append(color_line.id)
                if color_line_list:
                    res.update({'mrp_color_ids': [(6,0,color_line_list)]})
            if proc.proc_color_print_ids:
                for color_print_line in proc.proc_color_print_ids:
                    color_print_line_list.append(color_print_line.id)
                if color_print_line_list:
                    res.update({'mrp_color_print_ids': [(6,0,color_print_line_list)]})
            mrp_production_obj.write(cr, uid, [res.get(proc.id)], vals, context=context)
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: