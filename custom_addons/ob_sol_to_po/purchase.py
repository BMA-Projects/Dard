from openerp.osv import fields, osv
from IN import SOL_AAL
from openerp import SUPERUSER_ID

class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    def copy(self, cr, uid, id, default=None, context=None):
        if not context:
            context = {}
        purchase_order_line_obj = self.pool.get("purchase.order.line")
        if not default:
            default = {}
        currunt_order = self.browse(cr, uid, [id], context=context)
        order_line = []
        line_default = {
            'so_ref': False,
            'so_line_ref': False,
        }
        for line in self.browse(cr, uid, [id], context=context).order_line:
            line_id = purchase_order_line_obj.copy(cr, uid, line.id, line_default, context=context)
            order_line.append((4, line_id, False))
        if default:
            default.update({'order_line': order_line})
        else:
            default = {'order_line': order_line}
        if currunt_order:
            default.update({
                'minimum_planned_date': currunt_order.minimum_planned_date,
            })
        return super(purchase_order, self).copy(cr, uid, id, default, context=context)

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        sale_config_obj = self.pool.get('sale.config.settings')
        fields = sale_config_obj.fields_get(cr, SUPERUSER_ID, context=context)
        config_res = sale_config_obj.default_get(cr, SUPERUSER_ID, fields, context=context)
        if (config_res.has_key('create_po_or_poline') and config_res.get('create_po_or_poline') == 'new_po_with_new_line') or (config_res.has_key('create_po_or_poline') and config_res.get('create_po_or_poline') == 'create_new_po'):
            if context is None:
                context = {}
            search_args = []
            for arg in args:
                if args[0]:
                    search_args.append(arg[0])
            #Return empty list to prevent line merge while creating PO from SOL - available_po_line_ids = []
            if context.get('is_make_po', False) and 'partner_id' in search_args and 'picking_type_id' in search_args and 'location_id' in search_args and 'company_id' in search_args and 'dest_address_id' in search_args:
                context.update({'is_make_po': False})
                available_po_ids = self.search(cr, uid, args, context=context)
                if available_po_ids:
                    po_id = available_po_ids[0]
                    po_rec = self.browse(cr, uid, po_id, context=context)
                    if 'pro_id' in context:
                        procurement_order = self.pool.get('procurement.order').browse(cr, uid, context.get('pro_id'))
                        old_sale_id = po_rec.origin and po_rec.origin.split(':') and po_rec.origin.split(':')[0]
                        if procurement_order and procurement_order.group_id and procurement_order.group_id.name and old_sale_id:
                            if procurement_order.group_id.name != old_sale_id:
                                return []
                            else:
                                return super(purchase_order, self).search(cr, uid, args=args, offset=offset, limit=limit, order=order, context=context, count=count)                    
                else:
                    return []
        return super(purchase_order, self).search(cr, uid, args=args, offset=offset, limit=limit, order=order, context=context, count=count)
    
class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'

    _columns = {
        'so_ref' : fields.char('SO Reference', default=False),
        'so_line_ref' : fields.char('SO Line Reference', default=False),
        'sale_line_ref_id': fields.many2one('sale.order.line','Sale order line ref.')
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        ctx = context.copy()
        search_args = []
        sale_config_obj = self.pool.get('sale.config.settings')
        fields = sale_config_obj.fields_get(cr, SUPERUSER_ID, context=ctx)
        config_res = sale_config_obj.default_get(cr, SUPERUSER_ID, fields, context=ctx)
        if (config_res.has_key('create_po_or_poline') and config_res.get('create_po_or_poline') == 'create_new_line') or (config_res.has_key('create_po_or_poline') and config_res.get('create_po_or_poline') == 'new_po_with_new_line'):
            for arg in args:
                if args[0]:
                    search_args.append(arg[0])
            #Return empty list to prevent line merge while creating PO from SOL - available_po_line_ids = []
            if config_res.has_key('create_po_or_poline') and config_res.get('create_po_or_poline') == 'new_po_with_new_line':
                ctx.update({'is_make_po': True})
            if ctx.get('is_make_po', False) and 'order_id' in search_args and 'product_id' in search_args and 'product_uom' in search_args:
                ctx.update({'is_make_po': False})
                return []
        return super(purchase_order_line, self).search(cr, uid, args=args, offset=offset, limit=limit, order=order, context=ctx, count=count) 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
