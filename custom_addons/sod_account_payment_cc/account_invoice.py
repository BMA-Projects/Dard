# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

from openerp.osv import osv, fields
from openerp.addons.edi import EDIMixin
from urllib import urlencode

class account_invoice(osv.osv, EDIMixin):
	_inherit = 'account.invoice'
	
	def _edi_paypal_url(self, cr, uid, ids, field, arg, context=None):
		res = dict.fromkeys(ids, False)
		for inv in self.browse(cr, uid, ids, context=context):
			if inv.type == 'out_invoice' and inv.company_id.paypal_account:
				params = {
					"cmd": "_xclick",
					"business": inv.company_id.paypal_account,
					"item_name": "%s Invoice %s" % (inv.company_id.name, inv.number or ''),
					"invoice": inv.number,
					"amount": inv.residual,
					"currency_code": inv.currency_id.name,
					"button_subtype": "services",
					"no_note": "1",
					"bn": "OpenERP_Invoice_PayNow_" + inv.currency_id.name,
				}
				res[inv.id] = "https://www.paypal.com/cgi-bin/webscr?" + urlencode(params)
				# if inv.testmode:
				# 	res[inv.id] = "https://www.sandbox.paypal.com/cgi-bin/webscr?" + urlencode(params)
		return res
	
	_columns = {
		'is_cc_payment': fields.boolean('Use CC Payment'),
		# 'testmode': fields.boolean('Test Mode?', help='PayPal sandbox can be used to test payments. Sign up for a developer account here.'),
		'paypal_url': fields.function(_edi_paypal_url, type='char', string='Paypal Url'),
	}
	
	# _defaults = {
	# 	'testmode': True,
	# }
	
	
	# Set CC payment flag when a credit card payment term is selected
	def onchange_payment_term_cc(self, cr, uid, ids, payment_term_id):
		# Assume False for CC payments, only set to True if 
		# there is a payment term AND the term is a CC term
		res = {'is_cc_payment': False}
		
		if payment_term_id:
			term_rec = self.pool['account.payment.term'].browse(cr, uid, payment_term_id)
			if term_rec.is_cc_term:
				res['is_cc_payment'] = True
		
		return {'value': res}
	
	
	# Opens Pay invoice window - prefill with some CC data and pick a different view
	def invoice_pay_customer(self, cr, uid, ids, context=None):
		if not ids: return []
		context = context or {}
		
		res = super(account_invoice, self).invoice_pay_customer(cr, uid, ids, context)
		inv = self.browse(cr, uid, ids[0], context=context)
		# Passing the context value of Sales order if Register Payment is clicked on Sales Order
		res['context']['from_sales']= context.get('from_sales')
		
		#Adding current ID record as context
		res['context']['record_id'] = ids[0]
		
		# If it's a credit card payment, default the CC payment method and load a new view
		if inv.is_cc_payment:
			res['name'] = 'Pay Invoice by Credit Card'
# 		if inv.payment_method:
# 			res['context']['default_journal_id'] = inv.payment_method.id
# 			if inv.payment_method.cc_processing:
# 				res['context']['default_use_cc'] = True
		else:
			if inv.is_cc_payment:
				# Find all the CC payment journals and pick the first by default
				cc_journal_id = self.pool['account.journal'].search(cr, uid, [('cc_processing','=',True)])
				# Error checking, bail out if we never set a CC journal
				if not cc_journal_id:
					raise osv.except_osv("Error", "There are no credit card processing journals!  Enable CC Processing on a journal before attempting to accept a payment on an invoice with a credit card payment term.")
				res['context']['default_journal_id'] = cc_journal_id[0]
				res['context']['default_use_cc'] = True
			
			# Otherwise, just get the first cash/bank journal we can
			else:
				journal_ids = self.pool['account.journal'].search(cr, uid, [('type','in',['bank'])])
				if journal_ids:
					res['context']['default_journal_id'] = journal_ids[0]
		
		# Check for a default invoice address. If there's a default invoice
		# address, pass the id to the next screen even if it's not for CC payments.
		# TODO: This should be moved outside of the scope of this module!
		res['context']['default_invoice_addr_id'] = inv.partner_id.id
		return res



        