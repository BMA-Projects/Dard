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

from osv import fields, osv

class generate_shipping_quotes(osv.osv_memory):
    _name = "generate.shipping.quotes"
    _description = "Generate Shipping Quotes"

    def action_get_quotes(self, cr, uid, ids, context=None):
        if context.get('active_ids',False):
            picking_obj = self.pool.get('stock.picking')

            for picking_id in context['active_ids']:
                picking = picking_obj.browse(cr,uid,picking_id)
                carrier_id = picking.carrier_id.id or False
                cust_default = False
                if carrier_id:
                    cust_default = picking_obj._get_cust_default_shipping(cr,uid,carrier_id,context)
                    carrier_obj = self.pool.get('delivery.carrier')
                    carrier_lnk = carrier_obj.browse(cr,uid,carrier_id)
                    service_type_ups = ''
                    service_type_fedex = ''
                    service_type_usps = ''
                    first_class_mail_type_usps = ''
                    container_usps = ''
                    size_usps = ''
                    if carrier_lnk.is_ups:
                        service_type_ups = carrier_lnk.service_code or '03'
                    elif carrier_lnk.is_fedex:
                        service_type_fedex = carrier_lnk.service_code or 'FEDEX_GROUND'
                    elif carrier_lnk.is_usps:
                        service_type_usps = carrier_lnk.service_code or 'All'
                        first_class_mail_type_usps = carrier_lnk.first_class_mail_type_usps or 'Parcel'
                        container_usps = carrier_lnk.container_usps or 'Parcel'
                        size_usps = carrier_lnk.size_usps or 'REGULAR'
                    picking_obj.write(cr,uid,picking_id,{
                        'service_type_ups': service_type_ups,
                        'service_type_fedex': service_type_fedex,
                        'service_type_usps': service_type_usps,
                        'first_class_mail_type_usps': first_class_mail_type_usps,
                        'container_usps': container_usps,
                        'size_usps': size_usps,
                        })

                saleorderline_obj = self.pool.get('sale.order.line')
                saleorderline_ids = saleorderline_obj.search(cr,uid,[('order_id','=',picking.sale_id.id)])
                weight = 0.0
                for saleorderline_id in saleorderline_ids:
                    saleorderline_lnk = saleorderline_obj.browse(cr,uid,saleorderline_id)
                    weight += (saleorderline_lnk.product_id.product_tmpl_id.weight_net * saleorderline_lnk.product_uom_qty)
                sys_default = picking_obj._get_sys_default_shipping(cr, uid, saleorderline_ids,weight, context)

                if not (cust_default or sys_default):
                    continue
                if not (cust_default and cust_default.split("/")[0] == 'USPS') and sys_default and sys_default.split('/')[0] == 'USPS':
                    picking_obj.write(cr,uid,picking_id,{
                        'service_type_usps': sys_default.split('/')[1],
                        'container_usps': sys_default.split('/')[2],
                        'size_usps': sys_default.split('/')[3],
                    })
                    
                context['cust_default'] = cust_default
                context['sys_default'] = sys_default
                context['error'] = False
                try:
                    res = picking_obj.generate_shipping(cr,uid,[picking_id],context)
                except Exception, e:
                    continue

            picking_obj.log(cr, uid, picking_id, 'Shipping quotes generated successfully')
        return {'type': 'ir.actions.act_window_close'}

generate_shipping_quotes()