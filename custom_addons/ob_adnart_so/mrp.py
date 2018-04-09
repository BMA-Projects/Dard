# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _
import math

class line_decoration(models.Model):
    _name = 'line.decoration'

    name = fields.Char('Decorate', required=True, translate=True)

class line_packaging(models.Model):
    _name = 'line.packaging'

    name = fields.Char('Packaging', required=True, translate=True)

class mrp_production(models.Model):
    _inherit = 'mrp.production'

    @api.one
    @api.constrains('overrun_qty')
    def _check_overrun_qty(self):
        if self.overrun_qty < self.product_qty:
            raise Warning(_('Overrun Quantity Should be Greater than Product Quantity !!!'))
        
    @api.multi
    def _get_quantity(self):
#         for mo_order in self:
#             if not mo_order.overrun_qty:
#                 overrun = mo_order.product_qty * mo_order.over_run / 100
#                 overrun_qty = mo_order.product_qty + math.ceil(overrun)
#                 mo_order.overrun_qty = overrun_qty
        for mo_order in self:
            if mo_order.product_qty:
                mo_order.overrun_qty = mo_order.product_qty
#         
#         if self.over_run:
#             if not self.overrun_qty:
#                 overrun = self.product_qty * self.over_run / 100
#                 overrun_qty = self.product_qty + math.ceil(overrun)
#                 self.overrun_qty = overrun_qty

    @api.onchange('over_run')
    def _onchange_overrun(self):
        if self.over_run:
            overrun = self.product_qty * self.over_run / 100
            overrun_qty = self.product_qty + math.ceil(overrun)
            self.overrun_qty = overrun_qty

    @api.onchange('overrun_qty')
    def _onchange_overrun_qty(self):
        if self.overrun_qty:
            quantity = self.overrun_qty - self.product_qty
            overrun_quantity = quantity * 100 / self.product_qty
            over_run = math.ceil(overrun_quantity)
            self.over_run = over_run
    
    mrp_plating_ids = fields.One2many('sale.line.plating','mrp_plating_id','Plating')
    mrp_color_ids = fields.One2many('sale.line.color','mrp_line_color_id','Colors')
    mrp_color_print_ids = fields.One2many('sale.line.color.print','mrp_line_color_print_id','Print')
    line_specs = fields.Char("Line Specs1")
    line_specs_ids  = fields.Many2many('line.spacs.master', 'mrp_prod_spacs','mrp_prdo_spac_id', 'mrp_spacs_id',string='Line Specs')
    over_run = fields.Float('Overrun (%)', copy=False)
    overrun_qty = fields.Float("Overrun Quantity", copy=False, compute="_get_quantity")
    prod_del_dt = fields.Date("Production Del. Date")
    line_ship_dt = fields.Date(string='Ship Date')
    line_sc_date = fields.Date(string='Schedule Date')
    size = fields.Char(string="Size")
    metal_ids = fields.Many2many('metal.master', 'mrp_prod_metal','mrp_prod_metal_id', 'mp_metal_id',string='Metal')
    s_mould = fields.Char(string="S- Mould")
    p_mould = fields.Char(string="P- Mould")
    prod_sample = fields.Boolean('Sample')
    prod_approval = fields.Boolean("Approved")
    prod_del_date = fields.Date("Delivery date")
    prod_approve_date = fields.Date("Approved Date")
    prod_sample_qty = fields.Float(string="Quantity")
    decoration_ids  = fields.Many2many('line.decoration', 'mrp_decoration','mrp_prdo_decorate_id', 'mrp_decorate_id',string='Decoration')
    packaging_ids  = fields.Many2many('line.packaging', 'mrp_packaging','mrp_prdo_packaging_id', 'mrp_packaging_id',string='Packaging')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: