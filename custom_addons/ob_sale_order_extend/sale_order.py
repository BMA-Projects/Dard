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

    _columns = {
        'state': fields.selection([
            ('draft', 'Draft Order'),
            ('sent', 'Draft Order Sent'),
            ('prepared', 'Prepared for Confirm'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange', help="Gives the status of the Draft Order or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).The 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True),
    }


    # def button_confirm(self, cr, uid, ids, context=None):
    #     return self.action_button_confirm(cr, uid, ids, context)
    
    def action_prepare(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            if not o.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot prepare a sales order which has no line.'))
        return self.write(cr, uid, ids, {'state': 'prepared'}, context)

    def action_draft(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        _order_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id','=',ids[0]),
                                                                            ('product_id','=',False),
                                                                            ('product_uom_qty','=',0.0),])
        if len(_order_line_ids) > 0:
            for _line in self.pool.get('sale.order.line').browse(cr, uid, _order_line_ids, context):
                _pos = _line.name.find('] ')
                if _pos != -1:
                    _default_code = _line.name[1:_pos]
                    _product_id = self.pool.get('product.product').search(cr, uid, [('default_code','=',_default_code)])
                    if len(_product_id) > 0:
                        _line.write({'product_id': _product_id[0]})
        self.write(cr, uid, ids, {'state':'draft'})
        for _order_id in ids:
            workflow.trg_delete(uid, 'sale.order', _order_id, cr)
            workflow.trg_create(uid, 'sale.order', _order_id, cr)
        return True

    def notify_sale_order_cancel_reset(self, cr, uid, state, name, context=None):
        res = {}
        group_obj = self.pool.get('res.groups')
        user_obj = self.pool.get('res.users')
        mrp_order_ids = self.pool.get('mrp.production').search(cr, uid, [('origin','ilike',name)])
        if context.get('active_id', False):
            sale_id = context['active_id']
            if mrp_order_ids:
                category_id = self.pool.get('ir.module.category').search(cr, uid, [('name','=','Manufacturing')])
                manager_ids = group_obj.search(cr, uid, [('name','=', 'Manager'),('category_id','in',category_id)])
                user_ids = group_obj.browse(cr, uid, manager_ids, context=context)[0].users
                email = []
                for id in user_ids:
                     email.append(id.email)
                email_to = ''
                for e in email:
                    email_to = email_to and str(email_to) + ',' + str(e) or str(email_to) + str(e)
                tmpl_obj = self.pool.get('email.template')
                if state == 'draft':
                    tmpl_ids = tmpl_obj.search(cr, uid, [('name','=','SO Reset E-mail Template')])
                elif state == 'cancel':
                    tmpl_ids = tmpl_obj.search(cr, uid, [('name','=','SO Cancel E-mail Template')])
                if tmpl_ids:
                    email_to = ''       ####### Making the email id blank so that the Client doesnt recieve the email of SO reset.[FIX ME]###########
                    tmpl_obj.write(cr, uid, tmpl_ids[0], {'email_to':email_to}, context=context)
                    res = self.pool.get('email.template').send_mail(cr, uid, tmpl_ids[0], sale_id, True,)
        return res
    
    def _portal_payment_block(self, cr, uid, ids, fieldname, arg, context=None):
        if not context : context={}
        result = super(sale_order,self)._portal_payment_block(cr, uid, ids, fieldname, arg, context=context)
        for this in self.browse(cr, uid, ids, context=context):
                result[this.id] = False
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
