# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import fields, osv

class sale_order(osv.osv):
    _inherit = 'sale.order'
# 
    def copy(self, cr, uid, id, default=None, context=None):
        if not context:context = {}
        sale_order_line_obj = self.pool.get("sale.order.line")
        order_line = []
        line_default = {
            'po_ref': False,
            'po_line_ref': False,
        }
#         for line in self.browse(cr, uid, [id], context=context).order_line:
#             line_id = sale_order_line_obj.copy(cr, uid, line.id, line_default, context=context)
#             order_line.append((4, line_id, False))
#         if default:
#             default.update({'order_line': order_line})
#         else:
#             default = {'order_line': order_line}
        return super(sale_order, self).copy(cr, uid, id, default, context=context)

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def _check_po_enable(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            model_obj = self.pool.get('ir.model.data')
            mto_route = model_obj.get_object_reference(cr, uid, 'stock', 'route_warehouse0_mto')[1]
            buy_route = model_obj.get_object_reference(cr, uid, 'purchase', 'route_warehouse0_buy')[1]
            selected_routes = []

            if line.product_id and line.product_id.route_ids and mto_route and buy_route:
                for route in line.product_id.route_ids:
                    selected_routes.append(route.id)
                if mto_route in selected_routes and buy_route in selected_routes:
                    res[line.id] = True
                else:
                    res[line.id] = False
            else:
                res[line.id] = False
        return res

    def create(self, cr, uid, vals, context=None):
        vals.update({
            'po_ref': False,
            'po_line_ref': False,
        })
        res = super(sale_order_line, self).create(cr, uid, vals, context)
        return res

    _columns = {
            #'is_create_po_enable' : fields.boolean('Is Create PO Enable'),
            'is_create_po_enable': fields.function(_check_po_enable, method=True, type='boolean', string='Posted'),
            'po_ref' : fields.char('PO Reference', default=False, copy=False),
            'po_line_ref' : fields.char('PO Line Reference', default=False, copy=False),
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
