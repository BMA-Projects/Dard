# -*- coding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################


from openerp.osv import osv, fields
import urllib
from openerp.tools.translate import _



class res_company(osv.Model):
     
     _inherit = 'res.company'
     
res_company()

class res_partner_bank(osv.Model):
    
    _inherit = 'res.partner.bank'
    
    _columns = {
        'ach_payment': fields.boolean('ACH?'),
        'bank_aba_code': fields.char('Bank ABA Code',size=16),
        'echeck_type': fields.selection([('arc','ARC'), ('boc','BOC'), ('ccd','CCD'), ('ppd','PPD'), ('tel','TEL'),('web', 'WEB')], 'Echeck Type'),
        'account_type': fields.selection([('CHECKING','Checking'), ('BUSINESSCHECKING', 'Business Checking'), ('SAVINGS', 'Savings')], 'Account Type')
    }
    
res_partner_bank()

class account_journal(osv.Model):
    
    _inherit = 'account.journal'
    
    _columns = {
        'ach_payment': fields.boolean("ACH payment"),
    }
    
account_journal()

class account_voucher(osv.Model):
    
    _inherit = 'account.voucher'
    
    _columns = {
        'ach_payment': fields.boolean("ACH payment"),
    }
        
    def do_transfer(self, cr, uid, ids, context=None):
        print "do transfer called............................"
        if not context: context = {}
        authnet_obj = self.pool.get('account.authnet')
        credential = authnet_obj._get_credentials(cr, uid, context)
        partner_obj = self.pool.get('res.partner')
        if credential.get('test', False):
            transaction_url = 'https://test.authorize.net/gateway/transact.dll'
        else:
            transaction_url = 'https://secure.authorize.net/gateway/transact.dll'
        parameters, delimiter = {}, '|'
        static_para = {
            'x_recurring_billing': 1,
            'x_method':'echeck',
            'x_version': '3.1',
            'x_type':'AUTH_CAPTURE',
            'x_delim_char':delimiter,
            'x_relay_response': 'FALSE',
            'x_url':'FALSE',
            'x_delim_data':'TRUE',
        }
        parameters.update({
            'x_login': credential.get('login',False),
            'x_tran_key': credential.get('key',False),
        })
        parameters.update(static_para)
        invoice_rec = False
        invoice_obj = self.pool.get('account.invoice')
        if context.get('active_id') and context.get('active_model') == 'account.invoice':
            invoice_rec = invoice_obj.browse(cr, uid, context.get('active_id'), context)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.journal_id and not rec.journal_id.ach_payment:
                raise osv.except_osv('Configuration Error', 'Select Payment method is not configured for ACH payment.')
            if not rec.partner_id.bank_ids: 
                raise osv.except_osv('Error', 'No bank account defined!')
            x_bank_aba_code, x_bank_acct_num, x_bank_acct_type, x_bank_name, x_bank_acct_name, x_echeck_type = None, None, None, None, None, None
            flag = False
            for bank in rec.partner_id.bank_ids:
                 if bank.ach_payment:
                     flag = True
                     pname = rec.partner_id.name
                     x_first_name = ''
                     x_last_name = ''
                     pname = str(rec.partner_id.name or '').split(' ')
                     if len(pname) == 1:
                        x_first_name = pname[0]
                        x_last_name = ''
                     elif len(pname) >= 2:
                        x_first_name = pname[0]
                        x_last_name = pname[1]
                     payment_dict = {
                        'x_first_name': x_first_name,
                        'x_last_name': x_last_name,
                        'x_company': rec.partner_id.name or '',
                        'x_address': rec.partner_id.street or '',
                        'x_city': rec.partner_id.city or '',
                        'x_state': rec.partner_id.state_id and rec.partner_id.state_id.name or '',
                        'x_zip': rec.partner_id.zip or '',
                        'x_country': rec.partner_id.country_id and rec.partner_id.country_id.name or '',
                        'x_phone': rec.partner_id.phone or '',
                        'x_fax': rec.partner_id.fax or '',
                        'x_email': rec.partner_id.email or '',
                        'x_invoice_num': context.get('active_id') and invoice_rec.number or '',
                        'x_description': context.get('active_id') and invoice_rec.comment or '',
                        'x_ship_to_first_name' : x_first_name,
                        'x_ship_to_last_name' : x_last_name,
                        'x_ship_to_company': rec.partner_id.name or '',
                        'x_ship_to_address': rec.partner_id.street or '',
                        'x_ship_to_city': rec.partner_id.city or '',
                        'x_ship_to_state': rec.partner_id.state_id and rec.partner_id.state_id.name or '',
                        'x_ship_to_zip': rec.partner_id.zip or '',
                        'x_ship_to_country': rec.partner_id.country_id and rec.partner_id.country_id.name or '',

                        'x_bank_aba_code' : bank.bank_aba_code,
                        'x_bank_acct_num' : bank.acc_number,
                        'x_bank_acct_type' : bank.account_type,
                        'x_bank_name' : bank.bank_name,
                        'x_bank_acct_name': bank.partner_id.name,
                     }
                     parameters.update(payment_dict)
            if not flag:
                raise osv.except_osv('Error', 'No bank account with ACH payment is defined!')
            parameters.update({
                'x_amount': rec.amount,
            })
        encoded_args = urllib.urlencode(parameters)
        response = str(urllib.urlopen(transaction_url, encoded_args).read()).split(delimiter)
        return response
    
    
    def button_proforma_voucher(self, cr, uid, ids, context=None):
        if not context: context = {}
        if context.get('invoice_type') == 'out_refund':
            refund_vals = self.do_refund(cr, uid, ids, context=context)
        
        mod_obj = self.pool.get('ir.model.data')
        credit_transaction_obj = self.pool.get('credit.card.transaction')
        curr_object = self.browse(cr, uid, ids, context=context)
        record = self.browse(cr, uid, ids, context=context)[0]
        if not record.ach_payment:
            return super(account_voucher,self).button_proforma_voucher(cr, uid, ids, context)
        response = self.do_transfer(cr, uid, ids, context)
        if response[2] != '1':
            error_msg = response[3]
            raise osv.except_osv('Transaction Error', '%s'%(error_msg))
        else:
            invoice_id = context.get('record_id', False)
            cr.execute("select order_id from sale_order_invoice_rel where invoice_id=%s", (invoice_id, ))
            sale_list = map(lambda x: x[0], cr.fetchall())
            sale_id=False
            if sale_list:
                sale_id = sale_list[0]
            trans_vals = {
                'trans_id': response[4] or response[6],
                'cim_id': record.cim_id and record.cim_id.id or False,
                'pim_id': record.cim_payment_id and record.cim_payment_id.id or False,
                'amount': record.amount,
                'invoice_id': invoice_id,
                'sale_id': sale_id,
                'payment_id': record.id
            }
            
            transaction_id = credit_transaction_obj.create(cr, uid, trans_vals, context)
            self.action_send_confirm(cr, uid, context=context)
            self.action_move_line_create(cr, uid, [record.id], context=context)
            res = mod_obj.get_object_reference(cr, uid, 'sod_account_payment_cc_authorizenet', 'view_account_voucher_pay')
            res_id = res and res[1] or False
            message_obj = self.pool.get('account.voucher.pay')
            ref_obj_id = message_obj.search(cr, uid, [('name','=','The payment was processed')], context=context)
            return{
                'name':_('Successful!'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id],
                'res_model': 'account.voucher.pay',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': ref_obj_id[0],
            }
        
        
        return super(account_voucher, self).button_proforma_voucher(cr, uid, ids, context=context)

    def onchange_journal(self, cr, uid, ids, journal_id, line_ids=False, tax_id=False, partner_id=False, date=False, amount=False, ttype=False, company_id=False, context=None):
        res = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context)
        if journal_id:
            journal_rec = self.pool.get('account.journal').browse(cr, uid , journal_id, context)
            res['value'].update({'ach_payment': False})
            if journal_rec.ach_payment:
                res['value'].update({'ach_payment': True})
        return res

    
account_voucher()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: