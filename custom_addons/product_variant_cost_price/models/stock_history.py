# -*- coding: utf-8 -*-
# © 2015 Ainara Galdona - AvanzOSC
# © 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime

import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
    
class stock_history(osv.osv):
    _inherit = 'stock.history'

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        res = super(stock_history, self).read_group(cr, uid, domain, fields, groupby, offset=offset, limit=limit, context=context, orderby=orderby, lazy=lazy)
        if context is None:
            context = {}
        date = context.get('history_date', datetime.now())
        if 'inventory_value' in fields:
            group_lines = {}
            for line in res:
                domain = line.get('__domain', domain)
                group_lines.setdefault(str(domain), self.search(cr, uid, domain, context=context))
            line_ids = set()
            for ids in group_lines.values():
                for product_id in ids:
                    line_ids.add(product_id)
            line_ids = list(line_ids)
            lines_rec = {}
            if line_ids:
                cr.execute('SELECT id, product_id, price_unit_on_quant, company_id, quantity FROM stock_history WHERE id in %s', (tuple(line_ids),))
                lines_rec = cr.dictfetchall()
            lines_dict = dict((line['id'], line) for line in lines_rec)
            product_ids = list(set(line_rec['product_id'] for line_rec in lines_rec))
            products_rec = self.pool['product.product'].read(cr, uid, product_ids, ['cost_method'], context=context)
            products_dict = dict((product['id'], product) for product in products_rec)
            cost_method_product_ids = list(set(product['id'] for product in products_rec if product['cost_method'] != 'real'))
            histories = []
            if cost_method_product_ids:
                cr.execute('SELECT DISTINCT ON (product_id, company_id) product_id, company_id, cost FROM product_price_history_product WHERE product_id in %s AND datetime <= %s ORDER BY product_id, company_id, datetime DESC', (tuple(cost_method_product_ids), date))
                histories = cr.dictfetchall()
            histories_dict = {}
            for history in histories:
                histories_dict[(history['product_id'], history['company_id'])] = history['cost']
            for line in res:
                inv_value = 0.0
                lines = group_lines.get(str(line.get('__domain', domain)))
                for line_id in lines:
                    line_rec = lines_dict[line_id]
                    product = products_dict[line_rec['product_id']]
                    if product['cost_method'] == 'real':
                        price = line_rec['price_unit_on_quant']
                    else:
                        price = histories_dict.get((product['id'], line_rec['company_id']), 0.0)
                    inv_value += price * line_rec['quantity']
                line['inventory_value'] = inv_value
        return res
    
#     def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
#         res = super(stock_history, self).read_group(cr, uid, domain, fields, groupby, offset=offset, limit=limit, context=context, orderby=orderby, lazy=lazy)
#         if context is None:
#             context = {}
#         date = context.get('history_date')
#         prod_dict = {}
#         if 'inventory_value' in fields:
#             for line in res:
#                 if '__domain' in line:
#                     lines = self.search(cr, uid, line['__domain'], context=context)
#                     inv_value = 0.0
#                     product_tmpl_obj = self.pool.get("product.template")
#                     lines_rec = self.browse(cr, uid, lines, context=context)
#                     for line_rec in lines_rec:
#                         if line_rec.product_id.cost_method == 'real':
#                             price = line_rec.price_unit_on_quant
#                         else:
#                             if not line_rec.product_id.id in prod_dict:
#                                 cnt = cozntext.copy()
#                                 cnt.update({'inventory_product_id': line_rec.product_id})
#                                 prod_dict[line_rec.product_id.id] = product_tmpl_obj.get_history_price(cr, uid, line_rec.product_id.product_tmpl_id.id, line_rec.company_id.id, date=date, context=cnt)
#                             price = prod_dict[line_rec.product_id.id]
#                         inv_value += price * line_rec.quantity
#                     line['inventory_value'] = inv_value
#         return res

    def _get_inventory_value(self, cr, uid, ids, name, attr, context=None):
        if context is None:
            context = {}
        date = context.get('history_date')
        product_tmpl_obj = self.pool.get("product.template")
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            
            if line.product_id.cost_method == 'real':
                res[line.id] = line.quantity * line.price_unit_on_quant
            else:
                cnt = context.copy()
                cnt.update({'inventory_product_id': line.product_id})
                res[line.id] = line.quantity * product_tmpl_obj.get_history_price(cr, uid, line.product_id.product_tmpl_id.id, line.company_id.id, date=date, context=cnt)
        return res
    
    
    _columns = {
                'inventory_value': fields.function(_get_inventory_value, string="Inventory Value", type='float', readonly=True),
                }

    
    
