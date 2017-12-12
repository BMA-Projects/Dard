from openerp.osv import fields, osv

class procurement_order(osv.osv):
    _inherit = 'procurement.order'

    _columns = {
            'supplier_id' : fields.many2one('res.partner', 'Supplier'),
            'shipping_id' : fields.many2one('res.partner', 'Shipping Address'),
            }

    #Set Destination and Customer Address on Procurement
    def make_po(self, cr, uid, ids, context=None):
        vals = {}
        sale_line_obj = self.pool.get('sale.order.line')
        purchase_line_obj = self.pool.get('purchase.order.line')
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.shipping_id:
                vals['partner_dest_id'] = procurement.shipping_id.id
                # if procurement.shipping_id.supplier == True and procurement.shipping_id.customer == False and procurement.shipping_id.property_stock_supplier:
                #     vals['location_id'] = procurement.shipping_id.property_stock_supplier.id
                # else:
                vals['location_id'] = procurement.shipping_id.property_stock_customer.id
                self.write(cr, uid, [procurement.id], vals, context=context)
        ctx = context.copy()
        ctx.update({'is_make_po': True})
        res = super(procurement_order, self).make_po(cr, uid, ids, context=ctx)
        #To set PO/POL ref on SOL
        for procurement in self.browse(cr, uid, ids, context=context):
            if res.has_key(procurement.id) and res.get(procurement.id, False):
                po_line = purchase_line_obj.browse(cr, uid, res.get(procurement.id, False), context=context)
                sale_line_obj.write(cr, uid, procurement.sale_line_id.id, {'po_ref': po_line.order_id.name, 'po_line_ref': po_line.name}, context=context)

        return res


    def _run(self, cr, uid, procurement, context=None):
        if not context: context = {}
        context.update({'pro_id': procurement.id})
        return super(procurement_order, self)._run(cr, uid, procurement, context=context)

    def _get_product_supplier(self, cr, uid, procurement, context=None):
        res = super(procurement_order, self)._get_product_supplier(cr, uid, procurement, context=context)
        if procurement.supplier_id:
            res = procurement.supplier_id
        return res

    #To set SO/SOL ref on POL
    def _get_po_line_values_from_proc(self, cr, uid, procurement, partner, company, schedule_date, context=None):
        if context is None:
            context = {}
        vals = super(procurement_order, self)._get_po_line_values_from_proc(cr, uid, procurement, partner, company, schedule_date, context=context)
        if procurement.sale_line_id:
            vals.update({'so_ref':procurement.sale_line_id.order_id.name, 'so_line_ref':procurement.sale_line_id.name, 'sale_line_ref_id': procurement.sale_line_id.id})
        return vals


    def _run_move_create(self, cr, uid, procurement, context=None):
        ''' Returns a dictionary of values that will be used to create a stock move from a procurement.
        This function assumes that the given procurement has a rule (action == 'move') set on it.

        :param procurement: browse record
        :rtype: dictionary
        '''
        vals = super(procurement_order, self)._run_move_create(cr, uid, procurement, context=context)
        if procurement.sale_line_id:
            vals.update({'sol_id': procurement.sale_line_id.id})
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: