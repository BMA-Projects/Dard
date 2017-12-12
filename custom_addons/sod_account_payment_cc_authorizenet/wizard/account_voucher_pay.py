# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _

class account_voucher_pay_view(orm.Model):
    _name = "account.voucher.pay"
    _description = "Account Voucher Pay successful"
    _columns = {
        'name': fields.char('Name', size=220),
    }

    def send_status(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', [])
        mod_obj = self.pool.get('ir.model.data')
        reference_id=False
        if context.get('from_sales'):
            res = mod_obj.get_object_reference(cr, uid, 'sale', 'view_order_form')
            reference_id = context.get('from_sales')
            res_id = res and res[1] or False
            return {
                'name': _('Sales Order'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id],
                'res_model': 'sale.order',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': reference_id,
            }
        elif context.get('invoice_type') == "in_invoice":
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            reference_id = context.get('record_id')
            res_id = res and res[1] or False,
            return {
                'name': _('Supplier Invoices'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.invoice',
                'context': "{'type':'in_invoice'}",
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': reference_id,
            }
        else:
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            reference_id = context.get('record_id')
            res_id = res and res[1] or False,
            return {
                'name': _('Customer Invoices'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id],
                'res_model': 'account.invoice',
                'context': "{'type':'out_invoice'}",
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': reference_id,
            }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
