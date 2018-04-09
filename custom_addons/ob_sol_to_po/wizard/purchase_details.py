# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import fields, osv
from lxml import etree
from openerp import models, api, _
import openerp.addons.decimal_precision as dp


class purchase_details(osv.osv_memory):
    _name = 'purchase.details'
    _rec_name = 'quantity'

    _columns = {
            'supplier_id' : fields.many2one('res.partner', 'Supplier'),
            'quantity': fields.float('Quantity',digits_compute=dp.get_precision('Product Unit of Measure')),
            'shipping_id' : fields.many2one('res.partner', 'Shipping Address'),
            'street': fields.char('Street', size=128),
            'street2': fields.char('Street2', size=128),
            'zip': fields.char('Zip', change_default=True, size=24),
            'city': fields.char('City', size=128),
            'state_id': fields.many2one("res.country.state", 'State'),
            'country_id': fields.many2one('res.country', 'Country'),
            'email': fields.char('Email', size=240),
            'phone': fields.char('Phone', size=64),
            'mobile': fields.char('Mobile', size=64),
            'fax': fields.char('Fax', size=64),
            'website': fields.char('Website', size=64, help="Website of Partner or Company"),
            }

    _defaults = {
        'quantity': 0.0,
    }

    def onchange_shipping_id(self, cr, uid, ids, shipping_id, context=None):
        res = {'value': {}}
        partner_obj = self.pool.get('res.partner')
        if shipping_id:
            partner = partner_obj.browse(cr, uid, shipping_id, context=context)
            res['value'].update({'street': partner.street, 'street2': partner.street2, 'zip': partner.zip, 'city': partner.city, \
                'state_id': partner.state_id, 'country_id': partner.country_id, 'email': partner.email, 'phone': partner.phone, \
                'mobile': partner.mobile, 'fax': partner.fax, 'website': partner.website})
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        context = self._context
        res = super(purchase_details, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        active_suppliers = []
        model_obj = self.env['ir.model.data']
        #Set active suppliers from product
        if context.get('active_model') == 'sale.order.line' and context.get('active_ids') and view_type == 'form':
            order_line = self.env['sale.order.line'].browse(context['active_ids'])[0]
            if order_line and order_line[0].product_id:
                product = order_line[0].product_id
                domain = [('supplier_id', 'in', product.seller_ids)]
                for supplier in product.seller_ids:
                    if supplier.name and supplier.name.active:
                        active_suppliers.append(supplier.name.id)
                if active_suppliers:
                    nodes = doc.xpath("//field[@name='supplier_id']")
                    for node in nodes:
                        node.set('domain', "[('id', 'in', "+ str(active_suppliers) + ")]")
        res['arch'] = etree.tostring(doc)

        return res


    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('sale.order.line')
        res = super(purchase_details, self).default_get(cr, uid, fields, context)
        if context.get('active_model') == 'sale.order.line' and context.get('active_ids'):
            #Set default quantity in wizard from order line
            for line in line_obj.browse(cr, uid, context['active_ids'], context=context):
                res['quantity'] = line.product_uom_qty
        return res

    def create_po(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_id = context.get('active_id', False)

        procurement_obj = self.pool.get('procurement.order')
        sale_obj = self.pool.get('sale.order')
        sale_line_obj = self.pool.get('sale.order.line')

        #Split order lines according to new quantity provided in wizard
        for wizard in self.browse(cr, uid, ids, context=context):
            quantity = wizard.quantity or 0.0
            supplier_id = wizard.supplier_id.id
            if  quantity <= 0:
                raise osv.except_osv(_('Error!'),  _('Quantity can not be Zero or Negative !!!'))

            if active_id:
                line = sale_line_obj.browse(cr, uid, active_id, context=context)
                order = line.order_id
                if not line.product_uom_qty:
                    raise osv.except_osv(_('Error!'),  _('Please assign quantity in Sale Line !!!'))
                if line.product_uom_qty < quantity:
                    raise osv.except_osv(_('Error!'),  _("Please Don't enter quantity more than Sale Line!!!"))
                update_qty = line.product_uom_qty - quantity
                if update_qty > 0.0:
                    default_val = {
                                'product_uos_qty': update_qty,
                                'product_uom_qty': update_qty,
                            }
                    current_move = sale_line_obj.copy(cr, uid, active_id, default_val, context=context)
                    sale_line_obj.write(cr, uid, active_id, {'product_uom_qty': quantity,'product_uos_qty': quantity}, context=context)

                #Create Procurement and PO
                proc_ids = []
                vals = sale_obj._prepare_procurement_group(cr, uid, order, context=context)
                context.update({'supplier_id': supplier_id, 'shipping_id': wizard.shipping_id.id})
                if not order.procurement_group_id:
                    group_id = self.pool.get("procurement.group").create(cr, uid, vals, context=context)
                    order.write({'procurement_group_id': group_id})

                #Try to fix exception procurement (possible when after a shipping exception the user choose to recreate)
                if line.procurement_ids:
                    #first check them to see if they are in exception or not (one of the related moves is cancelled)
                    procurement_obj.check(cr, uid, [x.id for x in line.procurement_ids if x.state not in ['cancel', 'done']])
                    line.refresh()
                    #run again procurement that are in exception in order to trigger another move
                    proc_ids += [x.id for x in line.procurement_ids if x.state in ('exception', 'cancel')]
                    procurement_obj.reset_to_confirmed(cr, uid, proc_ids, context=context)
                elif sale_line_obj.need_procurement(cr, uid, [line.id], context=context):
                    vals = sale_obj._prepare_order_line_procurement(cr, uid, order, line, group_id=order.procurement_group_id.id, context=context)
                    vals.update({'supplier_id': wizard.supplier_id.id, 'shipping_id': wizard.shipping_id.id})
                    proc_id = procurement_obj.create(cr, uid, vals, context=context)
                    proc_ids.append(proc_id)
                sale_line_obj.write(cr, uid, active_id, {'state': 'done'}, context=context)
                #Confirm procurement order such that rules will be applied on it
                #note that the workflow normally ensure proc_ids isn't an empty list
                procurement_obj.run(cr, uid, proc_ids, context=context)

        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: