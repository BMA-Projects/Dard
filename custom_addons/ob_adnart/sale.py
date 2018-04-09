# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    mould = fields.Char('Mould', size=50)
    size = fields.Char('Size', size=50)

class stock_picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def _get_quantity(self):
        res = {}
        qty = 0
        for lines in self.move_lines:
            qty = qty + lines.product_qty
            self.total_qty = qty

    sale_id = fields.Many2one('sale.order', 'Sale order', copy=False)
    total_qty = fields.Integer(string="Picking Quantity", compute="_get_quantity")

    def create(self, cr, uid, vals, context=None):
        res = super(stock_picking, self).create(cr, uid, vals, context=context)
        sale_obj = self.pool.get('sale.order')
        origin = vals.get('origin','')
        sale_id = sale_obj.search(cr, uid, [('name','=',origin)])
        if sale_id:
            vals.update({'sale_id': sale_id[0]})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: