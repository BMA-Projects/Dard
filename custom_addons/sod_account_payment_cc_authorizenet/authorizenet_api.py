# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

from openerp.osv import osv, fields, orm
from lxml import etree
from urllib3 import HTTPSConnectionPool as pool
import time

ENCRYPTED_FIELDS = ['login', 'key']

# Stores authentication credentials
class authorizenet_api(orm.Model):
	_name = 'account.authnet'
	_columns = {
		'name': fields.char('Name', size=64, required=True, help="Identifying name for these credentials."),
		'active': fields.boolean('Active'),
		'test': fields.boolean('Test Mode?', help="Determines what subdomain to send requests to.\nTest mode: apitest.authorize.net\nLive mode: api.authorize.net"),
		'gateway_id': fields.char('Payment Gateway ID', size=16, required=True),
		'create_profile': fields.boolean('Always create profile', help="When 'Always create profile' boolean field is selected at API credential configuration, the customer profile and payment profile is created before sending info to authorize.net"),
		'login': fields.char('API Login ID', size=512, required=True),
		'key': fields.char('Transaction Key', size=512, required=True),
		'url': fields.char('URL Path', size=256, required=True, help="The path of the XML API URL.  Always begins with a leading slash.  The domain will be selected by the test mode checkbox."),
	}
	_defaults = {
		'active': True,
		'url': '/xml/v1/request.api',
	}
	
	# Get the auth.net credentials to use, returns a browse_record object
	def _get_credentials(self, cr, uid, context=None):
		if context is None: context = {}
		# Find the first active set of auth.net credentials
		auth_ids = self.search(cr, uid, [('active','=',True)], limit=1, context=context)
		if not auth_ids:
			raise osv.except_osv('Error', 'No Authorize.net credentials found!')
		
		# Make a duplicate context that will unmask secured data
		ctx = {}
		ctx.update(context)
		ctx['unmask'] = True
		# auth_rec = self.browse(cr, uid, auth_ids[0], ctx)
		auth_rec = self.read(cr, uid, auth_ids[0],[], ctx)
		if auth_rec:
			auth_rec = auth_rec[0]
		del ctx
		return auth_rec
	
	# Prepare XML with credentials for our auth.net account - common to every request
	# Returns an lxml etree object with the root set to the root_string value
	def _get_xml_header(self, cr, uid, root_string, refId=False, context=None):
		if not root_string:
			raise osv.except_osv('Programming Error', 'No string defined for the root XML tag.')
		
		auth_rec = self._get_credentials(cr, uid, context)
		root = etree.Element(root_string, xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd")
		merch_auth = etree.SubElement(root, 'merchantAuthentication')
		etree.SubElement(merch_auth, 'name').text = auth_rec.get('login')
		etree.SubElement(merch_auth, 'transactionKey').text = auth_rec.get('key')
		if refId:
			etree.SubElement(root, 'refId').text = str(refId)
		return root
	
	
	# Takes in an lxml etree object and returns the XML of the result
	def _send_request(self, cr, uid, req_xml_obj, context=None):

		if context is None: context = {}
		auth_rec = self._get_credentials(cr, uid, context)
		
		# Domain is hardcoded, much less likely to change than the path
		if auth_rec.get('test'):
			URL_DOMAIN = 'apitest.authorize.net'
		else:
			URL_DOMAIN = 'api.authorize.net'
		TRANSIT_PATH = auth_rec.get('url')
		# Open HTTPS pool
		https = pool(URL_DOMAIN, port=443)
		req = https.urlopen('POST', TRANSIT_PATH, body=etree.tostring(req_xml_obj), headers={'content-type':'text/xml'})

		res = False
		if req.status == 200:
			# Breaking namespaces specifically to make xpath not such a pain to use
			res = etree.fromstring(req.data.replace(' xmlns=', ' xmlnamespace='))
		else:
			raise osv.except_osv('Error', 'Connection could not be completed to Authorize.net')

		# Commit if Authorize.net request succeeds
		if res.xpath('//resultCode')[0].text == 'Ok':
			cr.commit()	
			
		# Parse the response
		# Make sure the XML sent was valid
		if not context.get('from_transaction'):
			if res.xpath('//resultCode')[0].text != 'Ok':
				cr.rollback()
				errorcode = res.xpath('//messages/message/code')[-1].text
				errordesc = res.xpath('//messages/message/text')[-1].text
				errormsg = "Code - "+errorcode+"\n"+errordesc
				raise osv.except_osv("There was an Error!", errormsg)
		
		# Looks valid, so return the XML text for function-specific parsing
		return res
	
	# Make sense of the payment gateway response data, a long comma-delimited text block
	# Takes in the root XML object and the string of the field the response is in
	def _parse_payment_gateway_response(self, cr, uid, root_xml_obj, response_tag, unparsed_str='', context=None):

		if context is None: context = {}
		if not unparsed_str:
			response_locs = root_xml_obj.xpath('//'+response_tag)
			if not response_locs:
				#print "Couldn't find '%s' in the response XML." % response_tag
				return False
			elif len(response_locs) > 1:
				#print "Found more than one tag?? Something isn't right. '%s' may be the wrong tag." % response_tag
				return False
			unparsed_str = response_locs[0].text
		
		# See AIM guide (non-xml version) for explanation of field mapping starting at page 41
		# Note the importance of the empty map strings - Auth.net purposely leaves those fields
		# unused for future implementation without breaking the API by changing the response length
		res_mapper = ['Response Code','Response Subcode','Response Reason Code','Response Reason Text',
					'Authorization Code','AVS Response','Transaction ID','Invoice Number','Description',
					'Amount','Method','Transaction Type','Customer ID','First Name','Last Name','Company',
					'Address','City','State','ZIP Code','Country','Phone','Fax','Email Address',
					'Ship To First Name','Ship To Last Name','Ship To Company','Ship To Address',
					'Ship To City','Ship To State','Ship To ZIP Code','Ship To Country','Tax','Duty',
					'Freight','Tax Exempt','Purchase Order Number','MD5 Hash','Card Code Response',
					'Cardholder Authentication Verification Response','','','','','','','','','','',
					'Account Number','Card Type','Split Tender ID','Requested Amount','Balance On Card',
					'','','','','','','','','','','','','',]
		
		res = {}
		split_response_list = unparsed_str.split(',')
		res_mapper_len = len(res_mapper)
		
		for item in res_mapper:
			if item:
				res[item] = split_response_list.pop(0) or False
			else:
				split_response_list.pop(0)
		return res

	# Encrypt login key for security purposes
	def create(self, cr, uid, values, context=None):
		if context is None: context = {}
		
		values = self.pool['rsa.encryption'].rsa_create(cr, uid, values, secure_fields=ENCRYPTED_FIELDS, context=context)
		
		result = super(authorizenet_api, self).create(cr, uid, values, context)
		return result
	
	
	# Mask data when reading
	# If context['unmask'] is True, return the fully decrypted values 
	def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
		if context is None: context = {}
		if not isinstance(ids, list): ids = [ids]
		values = super(authorizenet_api, self).read(cr, uid, ids, fields, context, load)
		
		values = self.pool['rsa.encryption'].rsa_read(cr, uid, values, secure_fields=ENCRYPTED_FIELDS, context=context)

		return values
	
	
	# Don't write masked values to the database
	def write(self, cr, uid, ids, values, context=None):
		if context is None: context = {}
		if not isinstance(ids, list): ids = [ids]
		
		values = self.pool['rsa.encryption'].rsa_write(cr, uid, values, secure_fields=ENCRYPTED_FIELDS, context=context)
		
		result = super(authorizenet_api, self).write(cr, uid, ids, values, context)
		return result
	
	
	# Strip out secured fields for duplication
	def copy(self, cr, uid, id, defaults, context=None):
		if context is None: context = {}
		
		defaults = self.pool['rsa.encryption'].rsa_copy(cr, uid, values=defaults, secure_fields=ENCRYPTED_FIELDS, context=context)
		
		return super(authorizenet_api, self).copy(cr, uid, id, defaults, context=context)


class authorizenet_cim(orm.Model):
	_name = 'account.authnet.cim'
	_description = "Customer Information Manager"
	_columns = {
		'name': fields.char('Name', size=64, readonly=True),
		'profile_id': fields.char('Customer Profile ID', size=32, readonly=True),
		'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, required=True),
		'invoice_addr_id': fields.many2one('res.partner', 'Invoice Contact', readonly=True, required=True),
		'payprofile_ids': fields.one2many('account.authnet.cim.payprofile', 'cim_id', 'Payment Profiles', readonly=True),
		'transaction_ids': fields.one2many('credit.card.transaction', 'cim_id', 'Payment History', readonly=True),
		'default_payprofile_id': fields.many2one('account.authnet.cim.payprofile', 'Default Payment Profile', domain="[('cim_id','=',id)]", help="Load this record by default when registering a payment. Won't prevent access to other payment profiles."),
	}
	
	# Launches the wizard to create a payment profile to link to this customer
	def create_payment_profile(self, cr, uid, ids, context=None):
		if context is None: context = {}
		
		if len(ids) != 1:
			return {}
		cim_rec = self.browse(cr, uid, ids, context)[0]
		
		# Start the wizard by returning an action dictionary, defaulting in the partner_id
		context['default_partner_id'] = cim_rec.partner_id.id
		context['default_cim_id'] = ids[0]
		ctx = dict(context)
		ctx['cc_last_four'] = True
		return {
			'name': 'Register a Payment Profile',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'cim.create.payment.profile',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': ctx,
		}
		
	def link_payment_profiles(self, cr, uid, ids, context=None):
		if context is None: context = {}
		
		if len(ids) != 1:
			return {}
		cim_rec = self.browse(cr, uid, ids, context)[0]
		models_data = self.pool.get('ir.model.data')
		dummy, form_view = models_data.get_object_reference(cr, uid, 'sod_account_payment_cc_authorizenet', 'customer_payment_profile_form')
		dummy, tree_view = models_data.get_object_reference(cr, uid, 'sod_account_payment_cc_authorizenet', 'customer_payment_profile_tree')
		return {
			'name': 'Payment Profiles',
			'view_type': 'form',
			'view_mode': 'tree, form',
			'domain': [('cim_id', '=', ids[0])],
			'res_model': 'account.authnet.cim.payprofile',
			'view_id': False,
			 'views': [(False, 'tree'),
                        (False, 'form')],
			'type': 'ir.actions.act_window',
			'target': 'current',
		}

class authorizenet_cim_payprofile(orm.Model):
	_name = 'account.authnet.cim.payprofile'
	_description = "Customer Payment Profiles for Authorize.Net CIM"
	_columns = {
		'name': fields.char('Name', size=64, readonly=True),
		'payprofile_id': fields.char('Payment Profile ID', size=32, readonly=True),
		'cim_id': fields.many2one('account.authnet.cim', 'Customer Profile', readonly=True, required=True),
		'last_four': fields.char('Last Four of CC', size=4, readonly=True),
		'alt_invoice_addr_id': fields.many2one('res.partner', 'Alternate Billing Contact', readonly=True, help="An alternative contact to the default billing contact on the Customer Profile."),
		'cc_exp_month': fields.char('Expiration Month', size=2),
		'cc_exp_year': fields.char('Expiration Year', size=2),
	}


		
	def name_get(self, cr, uid, ids, context=None):
		if context is None: context = {}
		res = []
		for r in self.read(cr, uid, ids, ['name','last_four','cc_exp_month','cc_exp_year']):
			res.append((r['id'], 'CC: %s - %s %s/%s' % (r['last_four'], r['name'], r['cc_exp_month'], r['cc_exp_year'])))
		return res
	
	# Delete entry on Auth.Net, then delete the payment profile locally
	def cim_unlink(self, cr, uid, ids, context=None):
		if context is None: context = {}
		if not ids: return True
		if not isinstance(ids, list): ids = [ids]
		authnet_obj = self.pool['account.authnet']
		
		# Should only see one at a time, but be prepared for anything
		for delete_rec in self.browse(cr, uid, ids, context):
			
			root_obj = authnet_obj._get_xml_header(cr, uid, 'deleteCustomerPaymentProfileRequest', context=context)
			etree.SubElement(root_obj, 'customerProfileId').text = delete_rec.cim_id.profile_id
			etree.SubElement(root_obj, 'customerPaymentProfileId').text = delete_rec.payprofile_id
			cim_id = delete_rec.cim_id.id
			# Delete locally - if the transaction failed, we'll raise an exception and not reach this
			a = self.unlink(cr, uid, ids, context)
			
			# Send response for each one
			response = authnet_obj._send_request(cr, uid, root_obj, context=context)
			
		models_data = self.pool.get('ir.model.data')
		dummy, form_view = models_data.get_object_reference(cr, uid, 'sod_account_payment_cc_authorizenet', 'customer_payment_profile_form')
		dummy, tree_view = models_data.get_object_reference(cr, uid, 'sod_account_payment_cc_authorizenet', 'customer_payment_profile_tree')
		return {
			'name': 'Payment Profiles',
			'view_type': 'form',
			'view_mode': 'tree, form',
			'domain': [('cim_id', '=', cim_id)],
			'res_model': 'account.authnet.cim.payprofile',
			'view_id': False,
			 'views': [(False, 'tree'),
                        (False, 'form')],
			'type': 'ir.actions.act_window',
			'target': 'current',
		}
	
	# Modify expiration date for payment profile
	def modify_expiry_date(self, cr, uid, ids, context=None):
		if context is None: context = {}
		if not ids: return True
		if not isinstance(ids, list): ids = [ids]
		authnet_obj = self.pool['account.authnet']
		curr_recs = self.browse(cr, uid, ids, context)
		
		# Should only see one at a time, but be prepared for anything
		for curr_rec in curr_recs:
			root_obj = authnet_obj.get_xml_header(cr, uid, 'getCustomerPaymentProfileRequest', context=context)
			etree.SubElement(root_obj, 'customerProfileId').text = curr_rec.cim_id.profile_id
			etree.SubElement(root_obj, 'customerPaymentProfileId').text = curr_rec.payprofile_id

			# Send response for each one
			response = authnet_obj._send_request(cr, uid, root_obj, context=context)
			
			# Delete locally - if the transaction failed, we'll raise an exception and not reach this
			self.unlink(cr, uid, ids, context)
		return {}

# AVS_RESPONSE = [
# 			('A','Address (Street) matches, ZIP does not'), 
# 			('B','Address information not provided for AVS check'),
# 			('E','AVS error'),
# 			('G','Non-U.S. Card Issuing Bank'),
# 			('N','No Match on Address (Street) or ZIP'),
# 			('P','AVS not applicable for this transaction'),
# 			('R','Retry – System unavailable or timed out'),
# 			('S','Service not supported by issuer'),
# 			('U','Address information is unavailable'),
# 			('W','Nine digit ZIP matches, Address (Street) does not'),
# 			('X','Address (Street) and nine digit ZIP match'),
# 			('Y','Address (Street) and five digit ZIP match'),
# 			('Z','Five digit ZIP matches, Address (Street) does not'),
# 			]	
#CARD_CODE_RESPONSE = [
#			('M','Match'),
#			('N','No Match'),
#			('P','Not Processed'),
#			('S','Should have been present'),
#			('U','Issuer unable to process request'),
#			]
class credit_card_transaction(orm.Model):
	_name = 'credit.card.transaction'
	_rec_name = 'trans_id' 
	_columns = {
           'trans_id': fields.char('Transaction ID', size=30),
           'cim_id': fields.many2one('account.authnet.cim','Customer Profile'),
           'pim_id': fields.many2one('account.authnet.cim.payprofile', 'Payment Profile'),
           'amount': fields.float('Amount transferred'),
           'invoice_id': fields.many2one('account.invoice', 'Invoice'),
           'sale_id': fields.many2one('sale.order', 'Sales Order Ref'),
           'payment_id': fields.many2one('account.voucher', 'Voucher/Payment'),
           'trans_date': fields.datetime('Transaction Date & Time', readonly=True),
           'message': fields.char('Message', size=300),
           'authCode': fields.char('Authorization Code', size=6),
           'avsResultCode': fields.char('AVS Result', size=300),
           'cvvResultCode': fields.char('CVV Result', size=300),
           'card_type': fields.char('Card Type', size=16, help="The type of card used to pay.  Visa, MasterCard, American Express, etc."),
    } 
	_defaults = {  
		'trans_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
	}
	_order = 'trans_date desc'  
