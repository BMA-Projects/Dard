# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _
from datetime import date
import datetime

class product_product(models.Model):
    _inherit = "product.product"

    @api.one
    def _get_purchased_qty(self):
        stock_picking_ref = self.env['stock.picking']
        purchase_orders = self.env['purchase.order'].search([('order_line.product_id','=',self.id),('state','in',['confirmed','approved'])])
        qty = 0.0
        for order in purchase_orders:
            pickings = stock_picking_ref.search([('origin','=', order.name),('state','not in',['done','cancel'])])
            for picking in pickings:
                qty = sum([line.product_uom_qty for line in picking.move_lines if line.product_id.id == self.id])
                #for pl in lines:
                #    qty += pl.product_uom_qty
        self.purchased_quantity = qty


    @api.one
    def _get_allocated_qty(self):
        stock_picking_ref = self.env['stock.picking']
        sale_orders = self.env['sale.order'].search([('order_line.product_id','=',self.id),('state','in',['manual', 'progress'])])
        qty = 0.0
        for order in sale_orders:
            pickings = stock_picking_ref.search([('origin','=', order.name),('state','not in',['done','cancel'])])
            for picking in pickings:
                qty = sum([line.product_uom_qty for line in picking.move_lines if line.product_id.id == self.id])
                #for pl in lines:
                #    qty += pl.product_uom_qty
        self.allocated_quantity = qty
        
    @api.one
    def _get_consumed_qty(self):
        stock_move_ref = self.env['stock.move']
        stock_move_recs = stock_move_ref.search([('product_id', '=', self.id), ('state', '=', 'done'), ('origin', 'ilike', 'MO%')])
        qty = 0.0
        qty = sum([order.product_uom_qty for order in stock_move_recs if order.product_id.id == self.id])
        self.consumed_quantity = qty


    def _get_minqty(self):
        for rec in self:
            reorder_rule = self.env['stock.warehouse.orderpoint'].search([('product_id','=',rec.id)],limit=1)
            rec.min_qty_ror = reorder_rule.product_min_qty or ''

    default_code = fields.Char(string='Item Number', select=True) #overridden to change string
    allocated_quantity = fields.Float("Allocated Quantity", compute='_get_allocated_qty', store=True)
    purchased_quantity = fields.Float("Purchased Quantity", compute='_get_purchased_qty', store=True)
    consumed_quantity = fields.Float("Consumed Quantity", compute='_get_consumed_qty', store=True)
    old_sku = fields.Char(string='Old SKU', select=True)
    min_qty_ror = fields.Char(string="Minimum Quantity",compute='_get_minqty', store=True)
    qty_write_date = fields.Date(string="Product QTY Write Date", default=fields.Date.today())
    
    # Override this function for use of auto set product template and product variant in bom while the creation of bom from product variant.
    def action_view_bom(self, cr, uid, ids, context=None):
        tmpl_obj = self.pool.get("product.template")
        products = set()
        for product in self.browse(cr, uid, ids, context=context):
            products.add(product.product_tmpl_id.id)
        result = tmpl_obj._get_act_window_dict(cr, uid, 'mrp.product_open_bom', context=context)
        # bom specific to this variant or global to template
        domain = [
            '|',
                ('product_id', 'in', ids),
                '&',
                    ('product_id', '=', False),
                    ('product_tmpl_id', 'in', list(products)),
        ]
        result['context'] = "{'default_product_id': active_id, 'search_default_product_id': active_id, 'default_product_tmpl_id': %s}" % (len(products) and products.pop() or 'False')
        result['domain'] = str(domain)
        return result

    # Do Transfer confirm
    @api.multi
    def get_this_year_qty(self):
        company_id = self.env.ref('base.main_company')
        warehouse_id = self.env['stock.warehouse'].search([('company_id','=',company_id and company_id.id)])[0]
        in_type_id = warehouse_id and warehouse_id.in_type_id and warehouse_id.in_type_id.id or False
        out_type_id = warehouse_id and warehouse_id.out_type_id and warehouse_id.out_type_id.id or False
        start_year_date = date(date.today().year, 1, 1)
        end_year_date = date(date.today().year, 12, 31)
        start_date = datetime.datetime.strftime(start_year_date, "%Y-%m-%d")
        end_date = datetime.datetime.strftime(end_year_date, "%Y-%m-%d")
        if warehouse_id and in_type_id and out_type_id:
            for product in self:
                total_out_qty_this_year = 0
                total_in_qty_this_year = 0
                out_move_line_ids = self.env['stock.move'].search([('product_id','=', product.id), ('state','in', ['done']), ('picking_id.picking_type_id','=', out_type_id), ('picking_id.state','in', ['done'])])
                in_move_line_ids = self.env['stock.move'].search([('product_id','=', product.id), ('state','in', ['done']), ('picking_id.picking_type_id','=', in_type_id), ('picking_id.state','in', ['done'])])
                for line in out_move_line_ids:
                    if line.picking_id.date_done >= start_date and line.picking_id.date_done <= end_date:
                        if line.picking_id.group_id and line.picking_id.group_id.name:
                            group_name = line.picking_id.group_id.name
                            if not group_name.startswith('PO'):
                                total_out_qty_this_year += line.product_uom_qty
                for line in in_move_line_ids:
                    if line.picking_id.date_done >= start_date and line.picking_id.date_done <= end_date:
                        if line.picking_id.group_id and line.picking_id.group_id.name:
                            group_name = line.picking_id.group_id.name
                            if not group_name.startswith('PO'):
                                total_in_qty_this_year += line.product_uom_qty
                product.total_sold_qty_this_year = total_out_qty_this_year - total_in_qty_this_year

    @api.multi
    def write(self, vals):
        res = super(product_product, self).write(vals)
        if vals.get('total_sold_qty_last_year', False):
            self.qty_write_date = datetime.datetime.now().strftime ("%Y-%m-%d")
        return res

    # DO base
    @api.model
    def get_last_year_qty(self, data={}):
        company_id = self.env.ref('base.main_company')
        warehouse_id = self.env['stock.warehouse'].search([('company_id','=',company_id and company_id.id)])[0]
        in_type_id = warehouse_id and warehouse_id.in_type_id and warehouse_id.in_type_id.id or False
        out_type_id = warehouse_id and warehouse_id.out_type_id and warehouse_id.out_type_id.id or False
        start_year_date = date(date.today().year-1, 1, 1)
        end_year_date = date(date.today().year-1, 12, 31)
        start_date = datetime.datetime.strftime(start_year_date, "%Y-%m-%d")
        end_date = datetime.datetime.strftime(end_year_date, "%Y-%m-%d")
        if warehouse_id and in_type_id and out_type_id:
            for product in self.search([]):
                total_in_qty_this_year = 0
                total_out_qty_this_year = 0
                qty_write_date = datetime.datetime.strptime(product.qty_write_date, "%Y-%m-%d")
                current_year =  date.today().year
                out_move_line_ids = self.env['stock.move'].search([('product_id','=', product.id), ('state','in', ['done']), ('picking_type_id','=', out_type_id), ('picking_id.state','in', ['done'])])
                in_move_line_ids = self.env['stock.move'].search([('product_id','=', product.id), ('state','in', ['done']), ('picking_type_id','=', in_type_id), ('picking_id.state','in', ['done'])])
                for line in out_move_line_ids:
                    if line.picking_id.date_done >= start_date and line.picking_id.date_done <= end_date:
                        if line.picking_id.group_id and line.picking_id.group_id.name:
                            group_name = line.picking_id.group_id.name
                            if not group_name.startswith('PO'):
                                total_out_qty_this_year += line.product_uom_qty
                for line in in_move_line_ids:
                    if line.picking_id.date_done >= start_date and line.picking_id.date_done <= end_date:
                        if line.picking_id.group_id and line.picking_id.group_id.name:
                            group_name = line.picking_id.group_id.name
                            if not group_name.startswith('PO'):
                                total_in_qty_this_year += line.product_uom_qty
                if current_year != qty_write_date.year:
                    product.total_sold_qty_last_year = total_out_qty_this_year - total_in_qty_this_year
                    product.qty_write_date = datetime.datetime.now().strftime ("%Y-%m-%d")
    

    total_sold_qty_this_year = fields.Float('Qty sold this year', compute=get_this_year_qty, store=True)
    total_sold_qty_last_year = fields.Float('Qty sold last year', readonly=True)


class product_template(models.Model):
    _inherit = "product.template"

    loc_rack = fields.Char('Rack', size=80)
    loc_row = fields.Char('Row', size=80)
    loc_case = fields.Char('Case', size=80)	
    default_code = fields.Char(related='product_variant_ids.default_code', string='Item Number') #overridden to change string
    sale_delay = fields.Float('Customer Lead Time', help="The average delay in days between the confirmation of the customer order and the delivery of the finished products. It's the time you promise to your customers.", default=5)
