# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

from openerp.osv import osv,fields
from lxml import etree
from datetime import datetime
ENCRYPTED_FIELDS = ['cc_number']

class cim_create_payment_profile(osv.TransientModel):
	_name = 'cim.create.payment.profile'
	_columns = {
		'name': fields.char('Name', size=255),
		'partner_id': fields.many2one('res.partner', 'Partner', required=True, readonly=True),
		'cim_id': fields.many2one('account.authnet.cim', 'Customer Profile', readonly=True, required=True),
		'alt_invoice_addr_id': fields.many2one('res.partner', 'Alternate Billing Contact', domain="['|',('parent_id','=',partner_id),('id','=',partner_id)]", help="An alternative contact to the default billing contact on the Customer Profile."),
		'cc_number': fields.char('CC Number', size=512, required=True),
		'cc_cvv': fields.char('CVV', size=512),
		'cc_exp_month': fields.char('Expiration Month', size=2, required=True),
		'cc_exp_year': fields.char('Expiration Year', size=2, required=True),
		'bill_firstname': fields.char('First Name', size=32),
		'bill_lastname': fields.char('Last Name', size=32),
		'bill_street': fields.char('Street', size=60),
		'city_state_zip': fields.char('City/State/Zip', size=128, readonly=True),
	}
	
	def onchange_invoice(self, cr, uid, ids, cim_id, alt_invoice_addr_id, cc_number, context=None):
		if context is None: context = {}
		res = {}
		if cim_id and cc_number and len(cc_number) >= 4:
			inv_rec = False
			if alt_invoice_addr_id:
				inv_rec = self.pool['res.partner'].browse(cr, uid, alt_invoice_addr_id, context)
			else:
				cim_rec = self.pool['account.authnet.cim'].browse(cr, uid, cim_id, context)
				inv_rec = cim_rec.invoice_addr_id
			
			# Wait until CC is in to display other info, minor performance hack
			if inv_rec:
				
				# Fill out billing info with best guesses for first/last name, the rest
				# is just for show
				res['bill_firstname'], _, res['bill_lastname'] = inv_rec.name.rpartition(' ')
				if not res['bill_firstname']:
					res['bill_firstname'] = res['bill_lastname']
					del res['bill_lastname']
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
	
	
	def _prepare_xml(self, cr, uid, ids, wizard_rec, context=None):
		ctx = dict(context)
		
		ctx['unmask'] = True
		record_read = self.read(cr, uid, wizard_rec.id,['cc_number'], ctx)

		if context is None: context = {}
		root = self.pool['account.authnet']._get_xml_header(cr, uid, 'createCustomerPaymentProfileRequest', refId=False, context=context)
		etree.SubElement(root, 'customerProfileId').text = wizard_rec.cim_id.profile_id
		
		# Define the record to pull from - either the default or the alternative
		inv_rec = wizard_rec.alt_invoice_addr_id or wizard_rec.cim_id.invoice_addr_id or False
		if not inv_rec:
			raise osv.except_osv("Error", "No invoicing contact listed in the payment profile or the customer profile.")
		
		payprofile = etree.SubElement(root, 'paymentProfile')
		etree.SubElement(payprofile, 'customerType').text = (inv_rec.is_company or inv_rec.parent_id) and 'business' or 'individual'
		
		# Billing info
		billto = etree.SubElement(payprofile, 'billTo')
		if wizard_rec.bill_firstname: etree.SubElement(billto, 'firstName').text = wizard_rec.bill_firstname
		if wizard_rec.bill_lastname: etree.SubElement(billto, 'lastName').text = wizard_rec.bill_lastname
		etree.SubElement(billto, 'company').text = wizard_rec.partner_id.name
		if wizard_rec.bill_street: etree.SubElement(billto, 'address').text = wizard_rec.bill_street
		if inv_rec.city: etree.SubElement(billto, 'city').text = inv_rec.city
		if inv_rec.state_id: etree.SubElement(billto, 'state').text = inv_rec.state_id.code
		if inv_rec.zip: etree.SubElement(billto, 'zip').text = inv_rec.zip
		if inv_rec.phone: etree.SubElement(billto, 'phoneNumber').text = inv_rec.phone
		if inv_rec.fax: etree.SubElement(billto, 'faxNumber').text = inv_rec.fax
		
		# Credit card info
		payment = etree.SubElement(payprofile, 'payment')
		cc = etree.SubElement(payment, 'creditCard')
		# etree.SubElement(cc, 'cardNumber').text = wizard_rec.cc_number
		etree.SubElement(cc, 'cardNumber').text = record_read[0].get('cc_number')



		# Auth.net CIM requires YYYY-MM formatting, unlike the AIM.  Keeping the layout consistent
		# with what credit cards actually say and just manually making the year 4 characters
		cc_year = wizard_rec.cc_exp_year
		if len(cc_year) == 2:
			cc_year = '20' + cc_year

		etree.SubElement(cc, 'expirationDate').text = cc_year + '-' + wizard_rec.cc_exp_month
		# etree.SubElement(cc, 'expirationDate').text = '2017' + '-' + '05'
		return root
	

	def send_request(self, cr, uid, ids, context=None):
		if context is None: context = {}
		if not ids:
			raise osv.except_osv('Error', 'Error in processing the wizard, no record created.')
		if not isinstance(ids, list): ids = [ids]
		ctx = dict(context)
		cc_last_four= False
		recs = self.read(cr, uid, ids, ['cc_number'], context=context)		
		for rec in recs:
			if 'last_four_digit_cc' in context and context['last_four_digit_cc']:
				cc_last_four = context['last_four_digit_cc'][-4:]
			elif rec.has_key('cc_number') and rec['cc_number']:
				cc_last_four = rec['cc_number'][-4:]
		wizard_rec = self.browse(cr, uid, ids[0], ctx)
		ctx['unmask'] = True
		wizard_rec = self.browse(cr, uid, ids[0], ctx)
		if not wizard_rec.cim_id.profile_id:
			raise osv.except_osv('Error', 'Customer Profile has no valid ID!')
		# Generate document regarding payment profile 
		name = wizard_rec.name or wizard_rec.alt_invoice_addr_id and wizard_rec.alt_invoice_addr_id.name or wizard_rec.cim_id.invoice_addr_id.name or False
		today_date = datetime.today()
		if len(wizard_rec.cc_exp_month) != 2:
			raise osv.except_osv("CC Error", "Expiry Month length is should be 2(two), e.g. 02")
		if int(wizard_rec.cc_exp_year) < int(today_date.strftime('%y')):
		    raise osv.except_osv("CC Error", "Card is already Expired")
		elif int(wizard_rec.cc_exp_year) == int(today_date.strftime('%y')):
		    if int(wizard_rec.cc_exp_month) < int(today_date.strftime('%m')):
		        raise osv.except_osv("CC Error", "Card is already Expired")
		vals = {
			'name': name,
			'cim_id': wizard_rec.cim_id.id,
			#'last_four': wizard_rec.cc_number[-4:],
			'last_four': cc_last_four,
			'cc_exp_month': wizard_rec.cc_exp_month,
			'cc_exp_year': wizard_rec.cc_exp_year,
		}

		if wizard_rec.alt_invoice_addr_id:
			vals['alt_invoice_addr_id'] = wizard_rec.alt_invoice_addr_id.id 
		cim_pay_obj = self.pool['account.authnet.cim.payprofile']

		cim_pay_obj_id = cim_pay_obj.create(cr, uid, vals, context)

		# Generate the XML object
		req_xml_obj = self._prepare_xml(cr, uid, ids, wizard_rec, context)

		# Send the XML object to Authorize.net and return the XML string
		res = self.pool['account.authnet']._send_request(cr, uid, req_xml_obj, context)

		# If we've returned, the XML must be good.  Look for a customer profile ID assigned by auth.net
		profile_id_path = res.xpath("//customerPaymentProfileId")
		
		# Catch any weird remaining errors and tell the user to inform IT so we can better parse fringe results
		if not profile_id_path or not profile_id_path[0].text or len(profile_id_path) > 1:
			cr.rollback()
			errormsg = "Did not find the tag <customerPaymentProfileId> in the XML, but also did not detect an error.  Please copy the following response data and notify IT of this problem.\n\n%s" % etree.tostring(res, pretty_print=True)
			raise osv.except_osv("XML Error", errormsg)
		
		# If we didn't raise an exception yet, we should have a valid payment profile ID to work with,
		# so provide payprofile_id value Payment profile object created before sending request
		cim_pay_obj.write(cr, uid, [cim_pay_obj_id], {'payprofile_id': profile_id_path[0].text}, context)
		
#		partner_obj = self.pool['res.partner']
		# Link that customer profile to the partner
#		partner_obj.write(cr, uid, [wizard_rec.partner_id.id], {'cim_id':cim_id}, context)
		return cim_pay_obj_id
	
	
	# -------------
	# RSA Functions
	# -------------
	# Encrypt cc info for temporary storage in wizard record
	def create(self, cr, uid, values, context=None):
		if context is None: context = {}
		if values.get('cc_number', False) and len(values['cc_number']) < 4:
			raise osv.except_osv("Error", "Don't jerk me around here, that's way too short of a credit card number.  Get it right.")
		values = self.pool['rsa.encryption'].rsa_create(cr, uid, values, secure_fields=ENCRYPTED_FIELDS, context=context)
		result = super(cim_create_payment_profile, self).create(cr, uid, values, context=context)
		return result
	
	
	# Mask data when reading
	# If context['unmask'] is True, return the fully decrypted values 
	def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
		if context is None: context = {}
		if not isinstance(ids, list): ids = [ids]
		values = super(cim_create_payment_profile, self).read(cr, uid, ids, fields, context, load)
		values = self.pool['rsa.encryption'].rsa_read(cr, uid, values, secure_fields=ENCRYPTED_FIELDS, context=context)
		return values
	
	
	# Don't write masked values to the database
	def write(self, cr, uid, ids, values, context=None):
		if context is None: context = {}
		if not isinstance(ids, list): ids = [ids]
		
		values = self.pool['rsa.encryption'].rsa_write(cr, uid, values, secure_fields=ENCRYPTED_FIELDS, context=context)
		
		result = super(cim_create_payment_profile, self).write(cr, uid, ids, values, context)
		return result
	
	
	# Strip out secured fields for duplication
	def copy(self, cr, uid, id, defaults, context=None):
		if context is None: context = {}
		
		defaults = self.pool['rsa.encryption'].rsa_copy(cr, uid, values=defaults, secure_fields=ENCRYPTED_FIELDS, context=context)
		
		return super(cim_create_payment_profile, self).copy(cr, uid, id, defaults, context=context)
