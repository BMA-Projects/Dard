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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import ast

class sale_line_split_into_tag(osv.osv_memory):
    _name = "sale.line.split.into.tag"
    _description = "Split into Sale Line"
    _columns = {
        'quantity': fields.float('Quantity',digits_compute=dp.get_precision('Product Unit of Measure')),
    }
    _defaults = {
        'quantity': 0.0,
    }

    def split_line(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        active_id = context.get('active_id', False)
        active_model = context.get('active_model', False)
        quantity = self.browse(cr, uid, data[0], context=context).quantity or 0.0
        if  quantity <= 0:
            raise osv.except_osv(_('Error!'),  _('Quantity can not be Zero or Negative !!!'))

        if quantity > 0.0 and active_id:
            line_obj = self.pool.get(active_model)
            product_uom_qty = line_obj.browse(cr, uid, active_id, context=context).product_uom_qty
            if not product_uom_qty:
                raise osv.except_osv(_('Error!'),  _('Please assign quantity in Sale Line !!!'))
            update_qty = product_uom_qty - quantity
            if update_qty <= 0.0:
                raise osv.except_osv(('Error!'), ('Updated quantity must be less than %s !!!') % (product_uom_qty))
            default_val = {
                        'product_uos_qty': update_qty,
                        'product_uom_qty': update_qty,
                    }
            current_move = line_obj.copy(cr, uid, active_id, default_val, context=context)
            line_obj.write(cr, uid, [active_id], {'product_uom_qty': quantity,'product_uos_qty': quantity}, context=context)
            order_id = line_obj.browse(cr, uid, active_id, context=context).order_id.id
            ir_model_data = self.pool.get('ir.model.data')
            res_id = ir_model_data.get_object_reference(cr, uid, 'sale', 'view_order_form')[1]
            return {
                'name': _('Sale Order'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id],
                'res_model': 'sale.order',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': order_id or False,
            }

        return {'type': 'ir.actions.act_window_close'}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
