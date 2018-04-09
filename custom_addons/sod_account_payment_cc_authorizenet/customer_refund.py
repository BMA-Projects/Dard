from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import workflow
from lxml import etree



class invoice_refund(osv.Model):
    
    _inherit = 'account.invoice.refund'
    
    def invoice_refund(self, cr, uid, ids, context=None):
        if not context: context = {}
        invoice_obj = self.pool.get('account.invoice')
        vals = super(invoice_refund, self).invoice_refund(cr, uid, ids, context=context)
        new_invoice_id = [x[2][0] for x in vals.get('domain') if x[0]=='id']
        invoice_obj.write(cr, uid, new_invoice_id, {'refund_invoice_id': context.get('active_id')}, context=context)
        return vals 
    
invoice_refund()


class refund_customer(osv.osv_memory):

    _name = "refund.customer"
    _columns = {
        'cc_number':fields.char('CC Number',size=64),
        'auth_transaction_id' :fields.char('Transaction ID', size=40),
        'authorization_code': fields.char('Authorization Code',size=64),
        'customer_payment_profile_id': fields.char('Payment Profile ID',size=64)
    }
    
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        act_model = context.get('active_model',False)
        result = super(refund_customer, self).default_get(cr, uid, fields, context=context)
        active_id = context.get('active_id',False)
        if active_id:
            invoice = self.pool.get(act_model).browse(cr,uid,active_id)
            transaction_id = invoice.auth_transaction_id
            authorize_code = invoice.authorization_code
            payment_profile_id = invoice.customer_payment_profile_id
            cc_number = invoice.cc_number
            if transaction_id :
                result['auth_transaction_id'] = transaction_id
            if authorize_code:
                result['authorization_code'] = authorize_code
            if payment_profile_id:
                result['customer_payment_profile_id'] = payment_profile_id
            if cc_number:
                result['cc_number'] = cc_number
        return result
    

    def refund_customer(self,cr,uid,ids,context={}):
        if context is None:
            context={}
        authorize_obj = self.pool.get('authorize.net.config')
        active_id = context.get('active_id')
        active_model = context.get('active_model')
        current_object = self.pool.get(active_model)
        credit_object = current_object.browse(cr, uid, active_id)
        config_ids = authorize_obj.search(cr,uid,[])
        total_amount = credit_object.amount_total
        auth_transaction_id = credit_object.auth_transaction_id
        cust_payment_profile_id = credit_object.customer_payment_profile_id
        cc_number = credit_object.cc_number_inv
        cust_profile_id = credit_object.partner_id.customer_profile_id
        if cc_number and len(cc_number) == 4:
            cc_number='XXXX'+''+str(cc_number)
        config_obj = authorize_obj.browse(cr,uid,config_ids[0])
        api_call = False
        try:
            transaction_status = authorize_obj.call(cr,uid,config_obj,'getTransactionDetailsRequest',auth_transaction_id)
            if (transaction_status) and (transaction_status.get('transactionStatus') == 'settledSuccessfully'):
                api_call = authorize_obj.call(cr,uid,config_obj,'CreateCustomerProfileTransaction',active_id,'profileTransRefund',total_amount,cust_profile_id,cust_payment_profile_id,auth_transaction_id,active_model,cc_number,context)
            else:
                api_call =authorize_obj.call(cr,uid,config_obj,'VoidTransaction',cust_profile_id,cust_payment_profile_id,auth_transaction_id)
            print"api_call",api_call
#            else:
#                raise osv.except_osv(_('Error !'),_('Refund Cannot Process now.Please Try Later'))
             
            if api_call:
                if not context.get('return_id',False):
                    current_object.api_response(cr,uid,active_id,api_call,cust_profile_id,cust_payment_profile_id,cc_number,context)
                else:
                    self.pool.get('return.order').api_response(cr,uid,context['return_id'],api_call,cust_profile_id,cust_payment_profile_id,cc_number,context)
                if int(api_call[0]) == 1:
                     
#                    current_object.invoice_pay_customer(cr, uid, [active_id], context=context)
                    workflow.trg_validate(uid, 'account.invoice', active_id, 'invoice_open', cr)
                    current_object.make_payment_of_invoice_authorize(cr, uid, [active_id], context=context)
                    current_object.write(cr, uid,[active_id], {'refund_status':True})
        except Exception, e:
            credit_object.write({'auth_respmsg':str(e)})
        return {'type': 'ir.actions.act_window_close'}

refund_customer()