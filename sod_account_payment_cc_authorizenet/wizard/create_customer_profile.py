# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

from openerp.osv import osv, fields
from lxml import etree

class cim_create_customer_profile(osv.TransientModel):
	_name = 'cim.create.customer.profile'
	_columns = {
		'name': fields.char('Name', size=255),
		'partner_id': fields.many2one('res.partner', 'Partner', required=True),
		'invoice_addr_id': fields.many2one('res.partner', 'Billing Contact', domain="['|',('parent_id','=',partner_id),('id','=',partner_id)]", required=True, help="This contact will be used to register the billing information."),
	}
	
	def onchange_invoice(self, cr, uid, ids, invoice_addr_id, context=None):
		if context is None: context = {}
		res = {}
		if invoice_addr_id:
			partner_obj = self.pool['res.partner']
			partner_rec = partner_obj.browse(cr, uid, invoice_addr_id, context)
			name = partner_rec.name
			if partner_rec.parent_id:
				name = partner_rec.parent_id.name + ', ' + name
			res['name'] = name
		return {'value': res}
	
	
	def _prepare_xml(self, cr, uid, ids, wizard_rec, context=None):
		if context is None: context = {}
		root = self.pool['account.authnet']._get_xml_header(cr, uid, 'createCustomerProfileRequest', refId=False, context=context)
		profile = etree.SubElement(root, 'profile')
		etree.SubElement(profile, 'merchantCustomerId').text = str(wizard_rec.partner_id.id)
		etree.SubElement(profile, 'description').text = wizard_rec.name
		
		if wizard_rec.invoice_addr_id.email:
			etree.SubElement(profile, 'email').text = wizard_rec.invoice_addr_id.email
		elif wizard_rec.partner_id.email:
			etree.SubElement(profile, 'email').text = wizard_rec.partner_id.email
		
		return root
	
	
	def send_request(self, cr, uid, ids, context=None):
		if context is None: context = {}
		if not ids:
			raise osv.except_osv('Error', 'Error in processing the wizard, no record created.')
		if not isinstance(ids, list): ids = [ids]
		
		wizard_rec = self.browse(cr, uid, ids[0], context)
		cim_obj = self.pool['account.authnet.cim']
		partner_obj = self.pool['res.partner']
		
		# Preparing local customer profile record
		vals = {
			'name': wizard_rec.name or wizard_rec.invoice_addr_id.name,
			'partner_id': wizard_rec.partner_id.id,
			'invoice_addr_id': wizard_rec.invoice_addr_id.id,
		}
		cim_id = cim_obj.create(cr, uid, vals, context)
		# Link that customer profile to the partner
		partner_obj.write(cr, uid, [wizard_rec.partner_id.id], {'cim_id':cim_id}, context)
		
		# Generate the XML object
		req_xml_obj = self._prepare_xml(cr, uid, ids, wizard_rec, context)
		
		#print "\nSending:\n\n",etree.tostring(req_xml_obj),"\n"

		# Send the XML object to Authorize.net and return the XML string
		res = self.pool['account.authnet']._send_request(cr, uid, req_xml_obj, context)
		
		# If we've returned, the XML must be good.  Look for a customer profile ID assigned by auth.net
		profile_id_path = res.xpath("//customerProfileId")
		
		# Catch any weird remaining errors and tell the user to inform IT so we can better parse fringe results
		if not profile_id_path or not profile_id_path[0].text or len(profile_id_path) > 1:
			cr.rollback()
			errormsg = "Did not find the tag <customerProfileId> in the XML, but also did not detect an error.  Please copy the following response data and notify IT of this problem.\n\n%s" % etree.tostring(res, pretty_print=True)
			raise osv.except_osv("XML Error", errormsg)
		
		# If we didn't raise an exception yet, we should have a valid profile ID to work with,
		# so create the profile and assign it to the partner
		cim_obj.write(cr, uid, [cim_id], {'profile_id': profile_id_path[0].text}, context)
		return cim_id
