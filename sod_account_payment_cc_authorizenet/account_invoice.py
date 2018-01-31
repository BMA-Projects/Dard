from openerp.osv import orm, fields
from lxml import etree

class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def _check_dates(self, cr, uid, ids, context=None):
        # will never fire constraint
        return True
    
    _columns = {
        'refund_invoice_id': fields.many2one('account.invoice', 'Refund Reference')
    }

    #over writed to remove effect
    _constraints = [
        (_check_dates, 'Due date must be greater then Invoice Date', ['date_due','date_invoice'])
    ]
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        journal_obj = self.pool.get('account.journal')
        if context is None:
            context = {}

        res = super(account_invoice,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            method_nodes = doc.xpath("//field[@name='payment_method']")
            term_nodes = doc.xpath("//field[@name='payment_term']")
            if (context.get('type','') not in ('out_invoice')):
                for node in method_nodes:
                    node.set('domain', "[('type','in',['bank', 'cash']),'|',('cc_processing','=',False),('cc_refunds','=',False)]") 
                    node.set('widget', '')
                for node in term_nodes:
                    node.set('domain', "[('is_cc_term','=',False)]")
                    node.set('widget', '')
            else:
                for node in method_nodes:
                    node.set('domain', "[('type','in',['bank', 'cash'])]")
                    node.set('widget', '')
            res['arch'] = etree.tostring(doc)
        return res    
        
