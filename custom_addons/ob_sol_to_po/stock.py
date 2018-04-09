from openerp.osv import fields, osv


class stock_move(osv.osv):
    _inherit = "stock.move"

    _columns = {
               'sol_id' : fields.many2one('sale.order.line', 'Sale Order Line'),
            }

    def _prepare_procurement_from_move(self, cr, uid, move, context=None):
        if context is None:
            context = {}
        sale_obj = self.pool.get('sale.order')
        sale_line_obj = self.pool.get('sale.order.line')
        vals = super(stock_move, self)._prepare_procurement_from_move(cr, uid, move, context=context)
        if move.sol_id:
            vals.update({'sale_line_id': move.sol_id.id})
        #Add sale_order_line reference in procurement order(PO)
        if move.origin:
            so = sale_obj.search(cr ,uid , [('name','=',move.origin)], context=context)
        if context.get('supplier_id', False):
            vals.update({'supplier_id': context.get('supplier_id')})
        if context.get('supplier_id', False):
            vals.update({'shipping_id': context.get('shipping_id')})
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: