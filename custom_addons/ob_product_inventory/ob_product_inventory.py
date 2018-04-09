# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement

class stock_quant(osv.osv):
    _inherit = 'stock.quant'

    _columns = {
            'sale_order_line_ids':fields.many2one('sale.order.line','Sale Order Line'),
            'warehouse_location_name': fields.related('location_id', 'location_id', type='many2one', relation="stock.location", string='Warehouse'),
    }

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    
    def _get_product_inventory(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        stock_quant_obj = self.pool.get("stock.quant")
        for record in self.browse(cr, uid, ids, context=context):
            line_ids = stock_quant_obj.search(cr, uid, [('product_id', '=', record.product_id.id)])
            result[record.id] = line_ids
        return result
    
    _columns = {
         'product_inventory': fields.function(_get_product_inventory, type='one2many', relation="stock.quant", string="Product Inventory"),
    }
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        
        stock_quant_obj = self.pool.get("stock.quant")
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
                uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
                lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        if product:
            line_ids = stock_quant_obj.search(cr, uid, [('product_id', '=', product)])
            res['value'].update({'product_inventory': line_ids})
        return res
    