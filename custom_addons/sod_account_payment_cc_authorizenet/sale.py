
from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp import netsvc

class sale_order(orm.Model):
    _inherit = 'sale.order' 

    def button_register_payment(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        res = {}
        account_object = self.pool.get('account.invoice')
        ctx=context
        ctx['from_sales']=ids[0]
        
        self.write(cr, uid, ids, {'order_policy':'prepaid'}, context)
        for sale in self.browse(cr, uid, ids, context=context):
            if not sale.invoice_exists:
                wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)
                wf_service.trg_validate(uid, 'sale.order', ids[0], 'manual_invoice', cr)
                for new_sale in self.browse(cr, uid, ids, context=context):
                    for invoice in new_sale.invoice_ids:
                        wf_service.trg_validate(uid, 'account.invoice', invoice.id, 'invoice_open', cr)
                        res = account_object.invoice_pay_customer(cr, uid, [invoice.id], context=ctx)
        return res