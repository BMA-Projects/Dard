# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

from openerp.osv import osv, fields
import inspect
import re
ENCRYPTED_FIELDS = []

class account_voucher(osv.osv):
	_inherit = 'account.voucher'
	_columns = {
		'use_cc': fields.boolean('Use CC'),
		'new_card': fields.boolean('New Credit card'),
#		'use_cc_on_file': fields.boolean('Use Card on File'),
#		'card_id': fields.many2one('res.partner.bank', 'Card on File'),
		'invoice_addr_id': fields.many2one('res.partner', 'Invoice Address', domain="['|',('partner_id','=',parent_id),('partner_id','=',id)]"),
		'last_four': fields.char('Paid with card ending', size=4, readonly=True),
		'cc_number': fields.char('CC Number', size=512, attrs="{'required': [('new_card','=',True)]}"),
		'cc_cvv': fields.char('CVV', size=4),
		'cc_exp_month': fields.char('Expiration Month', size=2, attrs="{'required': [('new_card','=',True)]}"),
		'cc_exp_year': fields.char('Expiration Year', size=2, attrs="{'required': [('new_card','=',True)]}"),
		'bill_firstname': fields.char('First Name', size=32),
		'bill_lastname': fields.char('Last Name', size=32),
		'bill_street': fields.char('Street', size=60),
		'city_state_zip': fields.char('City/State/Zip', size=128, attrs="{'required': [('new_card','=',True)]}"),
	}
	
	_defaults = { 'use_cc':False }
	
	def onchange_invoice(self, cr, uid, ids, use_cc, invoice_addr_id, new_card, context=None):
		if context is None: context = {}
		res = {
			'bill_firstname': '',
			'bill_lastname': '',
			'bill_street': '',
			'city_state_zip': '' 
			}
		if new_card:
			res['cim_payment_id'] = False
		if use_cc:
			inv_rec = False
			if invoice_addr_id:
				inv_rec = self.pool['res.partner'].browse(cr, uid, invoice_addr_id, context)
			
			# Wait until CC is in to display other info, minor performance hack
			if inv_rec:
				
				# Fill out billing info with best guesses for first/last name, the rest
				# is just for show
				res['bill_firstname'], _, res['bill_lastname'] = inv_rec.name.rpartition(' ')
				if not res['bill_firstname']:
					res['bill_firstname'] = res['bill_lastname']
					res['bill_lastname'] =''
				if inv_rec.street:
					res['bill_street'] = inv_rec.street
					if inv_rec.street2:
						res['bill_street'] += ' ' + inv_rec.street2
				
				# Build up cosmetic city/state/zip field. If these are wrong, the contact
				# should be fixed, not the payment profile 
				res['city_state_zip'] = inv_rec.city or ''
				if inv_rec.state_id:
					res['city_state_zip'] = res['city_state_zip'] and res['city_state_zip'] + ', ' + inv_rec.state_id.code or inv_rec.state_id.code
				if inv_rec.zip:
					res['city_state_zip'] += ' ' + inv_rec.zip
		return {'value': res}
		
	# Set the CC flag to hide/unhide stuff
	def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
		if not journal_id:
			return False
		res = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context)
		journal_rec = self.pool['account.journal'].browse(cr, uid, journal_id)
		if journal_rec.cc_processing:
			res['value']['use_cc'] = True
#			card_ids = self.pool['res.partner.bank'].search(cr, uid, [('partner_id','=',partner_id),('state','=','cc')])
#			if card_ids:
#				res['value']['use_cc_on_file'] = True
#				res['value']['card_id'] = card_ids[0]
				
		else:
			res['value']['use_cc'] = False
#			res['value']['use_cc_on_file'] = False
#			res['value']['card_id'] = False
		
		# Make sure we get the journal's default debit account
		account_id = journal_rec.default_debit_account_id.id or journal_rec.default_credit_account_id.id 
		if account_id:
			res['value']['account_id'] = account_id
		res['value']['amount'] = amount
		return res
	
	
	# Check their default payment term and load up CC payment method if applicable
	def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
		if not journal_id:
			return {}
		
		# MEDIOCRE OPTIMIZATION TRICK - could be done better than this
		# Inspect the call stack. If onchange_journal called this function, that means we likely
		# have the partner and changing it again is useless, so just skip it.
		if inspect.stack()[1][3] == 'onchange_journal':
			return {}
		if not partner_id:
			return {'value': {
						'line_dr_ids': [],
						'line_cr_ids': [],
						'amount': 0.0,
					}}
		if context is None:
			context = {}
		res = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
		res['value']['amount'] = amount
		partner_rec = self.pool['res.partner'].browse(cr, uid, partner_id)
		
		if not context.get('default_invoice_addr_id'):
			inv_partner_ids = self.pool.get('res.partner').search(cr, uid, ['|', ('parent_id', '=', partner_id), ('id', '=', partner_id), ('type', '!=', 'delivery')], context=context)
			if inv_partner_ids:
				res['value']['invoice_addr_id'] = inv_partner_ids[0]
			else:
				# Check for a default invoice address
				addrs = self.pool['res.partner'].address_get(cr, uid, [partner_rec.id], ['invoice'])
		 		
				# If there's a default invoice address, or if not, default address, pass that as the invoice id
				res['value']['invoice_addr_id'] = addrs.get('invoice', False) and addrs['invoice'] or \
													addrs.get('default', False) and addrs['default'] or \
													False
		return res
	
	
	# Encrypt data for temporary storage (before validating)
	def create(self, cr, uid, values, context=None):
		if context is None: context = {}
		
		# Only do cleaning if it's a CC processing journal, otherwise strip any leftover data
		journal_rec = self.pool['account.journal'].browse(cr, uid, values['journal_id'])
		if journal_rec.cc_processing:
			# Strip out any non-digit characters first
			for field in ENCRYPTED_FIELDS:
				if not values[field]:
					del values[field]
				else:
					values[field] = re.sub(r'\D', '', values[field])
			values = self.pool['rsa.encryption'].rsa_create(cr, uid, values, ENCRYPTED_FIELDS, context)
		else:
			for field in ENCRYPTED_FIELDS:
				if field in values: del values[field]
		return super(account_voucher, self).create(cr, uid, values, context)
	
	
	# Don't write masked values to the database
	def write(self, cr, uid, ids, values, context=None):
		if context is None: context = {}
		if not isinstance(ids, list): ids = [ids]
		values = self.pool['rsa.encryption'].rsa_write(cr, uid, values, ENCRYPTED_FIELDS, context)
		return super(account_voucher, self).write(cr, uid, ids, values, context)

	
	# Mask data when reading
	# Use context['unmask'] = True before making read() call to return fully unmasked values
	# OR, use context['cc_last_four'] = True to return the unmasked last 4 digits of the CC number
	def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
		if context is None: context = {}
		values = super(account_voucher, self).read(cr, uid, ids, fields, context, load)
		
		ctx = {}
		ctx.update(context)
		ctx['cc_last_four'] = True
		return self.pool['rsa.encryption'].rsa_read(cr, uid, values, ENCRYPTED_FIELDS, ctx)
	
	# Delete any potential CC data when copying
	def copy(self, cr, uid, id, defaults, context=None):
		if context is None: context = {}
		defaults = self.pool['rsa.encryption'].rsa_copy(cr, uid, defaults, ENCRYPTED_FIELDS, context)
		return super(account_voucher, self).copy(cr, uid, id, defaults, context)
