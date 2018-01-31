# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
import logging
from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import workflow


class sale_order(osv.Model):
    _inherit = 'sale.order'
    
    def allow_reopen(self, cr, uid, ids, context=None):
        _logger = logging.getLogger(__name__)
        _logger.debug('FGF sale_order reopen %s' % (ids))
        stock_picking_obj = self.pool.get('stock.picking')
        for order in self.browse(cr, uid, ids, context):
            if order.picking_ids:
                for pick in order.picking_ids:
                    stock_picking_obj.allow_reopen(cr, uid, [pick.id])
        return True
            
    def action_reopen(self, cr, uid, ids, context=None):
        """ Changes SO state to draft.
        @return: True
        """
        _logger = logging.getLogger(__name__)
        _logger.debug('FGF sale_order action reopen %s' % (ids))
        self.allow_reopen(cr, uid, ids, context=None)
        order_line_obj = self.pool.get('sale.order.line')
        po_line_obj = self.pool.get('purchase.order.line')
        move_obj = self.pool.get('stock.move')
        invoice_obj = self.pool.get('account.invoice')
        context.update({'cancel_procurement': True})
        for order in self.browse(cr, uid, ids, context=context):
            proc_group_id = order.procurement_group_id
            if proc_group_id:
                #Raise warning if PO/MO is confirmed
                for proc in proc_group_id.procurement_ids:
                    if proc.purchase_id and proc.purchase_id.state not in ['draft', 'cancel']:
                        raise osv.except_osv(_('Warning'), _('You can not reset sales order %s as related Purchase order %s is confirmed.' % (order.name, proc.purchase_id.name)))
                    if proc.production_id and proc.production_id.state not in ['new','cancel','confirmed','ready']:
                        raise osv.except_osv(_('Warning'), _('You can not reset sales order %s as production started for related Manufacturing order %s.' % (order.name, proc.production_id.name)))
                for proc in proc_group_id.procurement_ids:
                    for move in proc.move_ids:
                        move_obj.action_cancel(cr, uid, move.id, context=context)
                    proc.cancel()
            for oline in order.order_line:
                oline.procurement_ids = False

            if order.invoice_ids:
                flag = False
                for invoice in order.invoice_ids:
                    if invoice.state in ['paid', 'open', 'proforma', 'proforma2']:
                        raise osv.except_osv(_('Warning'), _('You can not reset this Sale Order as it\'s invoice not in draft'))
                    if invoice.state in ['draft']:
                        invoice_obj.unlink(cr, uid, [invoice.id], context=context)
            self.write(cr, uid, order.id, {'state': 'draft'})
            line_ids = []
            for line in order.order_line:
                line_ids.append(line.id)
            order_line_obj.write(cr, uid, line_ids, {'state': 'draft', 'invoiced': False})
            _logger.debug('FGF sale_order trg del %s' % (order.id))
            workflow.trg_delete(uid, 'sale.order', order.id, cr)
            _logger.debug('FGF sale_order trg create %s' % (order.id))
            workflow.trg_create(uid, 'sale.order', order.id, cr)

            pol_fields = po_line_obj.fields_get(cr, uid, context=context)
            sol_fields = order_line_obj.fields_get(cr, uid, context=context)
            
            so_fields = self.fields_get(cr, uid, context=context)
            if so_fields.has_key('has_limit') and so_fields.has_key('by_pass'):
                self.write(cr, uid, ids, {'has_limit': order.partner_id.allow_credit,'by_pass':False})
            
            if so_fields.has_key('ticket_button_visible'):
                self.write(cr, uid, ids, {'ticket_button_visible': False})
            
            if so_fields.has_key('ticket_generated'):
                self.write(cr, uid, ids, {'ticket_generated':False})
            
            if so_fields.has_key('generated_by_admin'):
                self.write(cr, uid, ids, {'generated_by_admin': False})
                
            if so_fields.has_key('generated_by_oem'):
                self.write(cr, uid, ids, {'generated_by_oem': False})
                
            if so_fields.has_key('generated_by_admin'):
                self.write(cr, uid, ids, {'generated_by_admin': False})
                
            if so_fields.has_key('is_mo_created'):
                self.write(cr, uid, ids, {'is_mo_created': False})
            
            if so_fields.has_key('carrier') and so_fields.has_key('method') and so_fields.has_key('ship_ids'):
                self.write(cr, uid, ids, {'carrier': '','method':'','ship_ids':[]})
            
            #Remove SO ref from PO line if ob_sol_to_po installed
            if pol_fields.has_key('so_ref') and pol_fields.has_key('so_line_ref'):
                po_line_ids = po_line_obj.search(cr, uid, [('so_ref','=', order.name)], context=context)
                po_line_obj.write(cr, uid, po_line_ids, {'so_ref': False, 'so_line_ref': False}, context=context)
            #Remove PO ref from SO line if ob_sol_to_po installed
            if sol_fields.has_key('po_ref') and sol_fields.has_key('po_line_ref'):
                for oline in order.order_line:
                    order_line_obj.write(cr, uid, oline.id, {'po_ref': False, 'po_line_ref': False}, context=context)
        return True
        
        
class stock_picking(osv.Model):
    _inherit = 'stock.picking'

    def allow_reopen(self, cr, uid, ids, context=None):
        _logger = logging.getLogger(__name__)
        _logger.debug('FGF picking allow open ids %s ' %(ids))
        for pick in self.browse(cr, uid, ids, context):
            if pick.picking_type_id and pick.picking_type_id.code == 'outgoing' and pick.state == 'done':
                raise osv.except_osv(_('Error'), _('Deliver pickings %s is on state done, you cannot reset to draft ! '  %(pick.name)) )
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:            
