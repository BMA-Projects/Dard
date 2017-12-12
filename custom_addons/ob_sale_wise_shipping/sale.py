# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp import models, fields, api, _


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    shipping_address_id = fields.Many2one('res.partner',string="Shipping Address")
    carrier_id_by_line = fields.Many2one('delivery.carrier',string="Delivery Method")
    
class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def name_get(self):
        result = super(res_partner,self).name_get()
        context = self._context
        for record in self:
            if record.parent_id:
                result.append((record.id, '%s - %s' % (record.parent_id.name, record.name)))
            else:
                result.append((record.id,'%s' % (record.name)))
        return result

    @api.model
    def create(self, vals):
        context = self._context
        if context.get('from_so_line'):
            vals.update({'customer': False, 'is_company': True})
        result = super(res_partner, self).create(vals)
        return result

    @api.v7
    def _set_default_customer(self, cr, uid, context):
        if context.get('from_so_line'):
            return False
        return True 

    @api.v7
    def _set_default_is_company(self, cr, uid, context):
        if context.get('from_so_line'):
            return True
        return False

    _defaults = {
        'customer': _set_default_customer,
        'is_company': _set_default_is_company,
    }

class sale_order(models.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
        res = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, group_id, context)
        if line.shipping_address_id.id:
            res.update({'partner_dest_id':line.shipping_address_id.id})
        return res

class stock_move(models.Model):
    _inherit = 'stock.move'

    def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):
        partner_dict = {}
        dummy_dict = {}
        vals = super(stock_move, self)._picking_assign(cr, uid, move_ids, procurement_group, location_from, location_to, context)
        pick_obj = self.pool.get("stock.picking")
        move_rec = self.browse(cr, uid, move_ids, context=context)
        for move in move_rec:
            picks = pick_obj.search(cr, uid, [
                       ('group_id', '=', procurement_group),
                       ('location_id', '=', location_from),
                       ('location_dest_id', '=', location_to),
                       ('partner_id', '=', move.partner_id.id),
                       ('state', 'in', ['draft', 'confirmed', 'waiting'])], context=context)
            if not picks:
                values = {
                    'origin': move.origin,
                    'company_id': move.company_id and move.company_id.id or False,
                    'move_type': move.group_id and move.group_id.move_type or 'direct',
                    'partner_id': move.partner_id.id or False,
                    'picking_type_id': move.picking_type_id and move.picking_type_id.id or False,
                }
                pick = pick_obj.create(cr, uid, values, context=context)
                self.write(cr, uid, move.id, {'picking_id': pick}, context=context)
            else:
                pick = picks[0]
                self.write(cr, uid, move.id, {'picking_id': pick}, context=context)
        return vals

class procurement_order(models.Model):
    _inherit = 'procurement.order'

    def _run_move_create(self, cr, uid, procurement, context=None):
        res = super(procurement_order, self)._run_move_create(cr, uid, procurement, context)
        if procurement.partner_dest_id.id:
            res.update({'partner_id': procurement.partner_dest_id.id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
