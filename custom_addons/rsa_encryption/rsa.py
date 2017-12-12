# -*- coding: utf-8 -*-
##############################################################################
#
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2013 Solaris, Inc. (<http://www.solarismed.com>)
#	Copyright (C) 2004-2013 OpenERP SA (<http://www.openerp.com>)
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random
import base64
from openerp.osv import osv, fields
import os

class rsa_encryption(osv.Model):
	_name = 'rsa.encryption'
	_description = 'Portable RSA encryption for custom OpenERP code'
	_columns = {
		'name': fields.char('Private Key Name', size=64, required=True),
		'pub_name': fields.char('Public Key Name'),
		'active': fields.boolean('Active'),
		'primary': fields.boolean('Primary', readonly=True, help="Only one primary key should be selected at a time."),
	}
	
	# Return both keys at once as a tuple:
	#	(<pkey object>, <pubkey object>)
	def get_keys(self, cr, uid, context=None):
		if context is None: context = {}
		primary_key_ids = self.search(cr, uid, [('primary','=',True),('active','=',True)], limit=1)
		if not primary_key_ids:
			raise osv.except_osv("Error", "No primary key set available for use. Generate a new set or flag an existing set as primary.")
		key_rec = self.browse(cr, uid, primary_key_ids[0], context)
		pkey = RSA.importKey(open(key_rec.name,'r').read())
		pubkey = RSA.importKey(open(key_rec.pub_name,'r').read())
		return (pkey, pubkey)
	
	def get_pubkey(self, cr, uid, context=None):
		if context is None: context = {}
		rsa_key_path = self.pool.get('ir.config_parameter').get_param(cr, uid, 'rsa.key.path')
		if not rsa_key_path:
			raise osv.except_osv('Configuration Error', "No system Parameter found with name 'rsa.key.path'.")

		abs_path = os.path.abspath('')
		abs_path = "/usr/lib/python2.6/site-packages/openerp-7.0_20140303_001304-py2.6.egg"
		#abs_path = "/usr/lib/python2.6/site-packages/openerp-7.0_20140131_002446-py2.6.egg" #live
		primary_key_ids = self.search(cr, uid, [('primary','=',True),('active','=',True)], limit=1)
		if not primary_key_ids:
			raise osv.except_osv("Error", "No primary key set available for use. Generate a new set or flag an existing set as primary.")
		key_rec = self.browse(cr, uid, primary_key_ids[0], context)
		# filename_pub = abs_path + "/openerp/user_uploads/rsa_keys/" + key_rec.pub_name
		filename_pub = rsa_key_path + key_rec.pub_name
		return RSA.importKey(open(filename_pub,'r').read())
	
	def get_privkey(self, cr, uid, context=None):
		if context is None: context = {}
		rsa_key_path = self.pool.get('ir.config_parameter').get_param(cr, uid, 'rsa.key.path')
		if not rsa_key_path:
			raise osv.except_osv('Configuration Error', "No system Parameter found with name 'rsa.key.path'.")
			
		abs_path = os.path.abspath('')
		abs_path = "/usr/lib/python2.6/site-packages/openerp-7.0_20140303_001304-py2.6.egg"
		#abs_path = "/usr/lib/python2.6/site-packages/openerp-7.0_20140131_002446-py2.6.egg" #live
		primary_key_ids = self.search(cr, uid, [('primary','=',True),('active','=',True)], limit=1)
		if not primary_key_ids:
		    raise osv.except_osv("Error", "No primary key set for use.")
		key_rec = self.browse(cr, uid, primary_key_ids[0], context)
		# filename_pub = abs_path + "/openerp/user_uploads/rsa_keys/" + key_rec.pub_name
		filename_prv = rsa_key_path + key_rec.name
		return RSA.importKey(open(filename_prv,'r').read())
	
	def encrypt(self, cr, uid, value, key=False, context=None):
		if not isinstance(value, str):
			value = str(value)
		if not key:
			key = self.get_pubkey()
		h = SHA.new(value)
		cipher = PKCS1_v1_5.new(key)
		res = base64.encodestring(cipher.encrypt(value + h.digest()))
		return res
	
	def decrypt(self, cr, uid, value, key=False, context=None):
		if not key:
			key = self.get_privkey(cr, uid,)
		dsize = SHA.digest_size
		sentinel = Random.new().read(15 + dsize)
		cipher = PKCS1_v1_5.new(key)
		res = cipher.decrypt(base64.decodestring(value), sentinel)
		
		# Validate results
		digest = SHA.new(res[:-dsize]).digest()
		if digest == res[-dsize:]:
			return res[:-dsize]
		else:
			return False
	
	
	# -----------------------
	# ORM data prep functions
	# -----------------------
	# Use these to quickly and properly account for read/write/create/copy encryption and decryption
	# Doesn't call ORM directly, just cleans the secured values for proper writing or reading
	def rsa_create(self, cr, uid, values, secure_fields, context=None):
		if context is None: context = {}
		pubkey = self.get_pubkey(cr, uid, context)
		
		# Iterate through the list of secured fields and encrypt them
		for secure_field in secure_fields:
			if values.get(secure_field, False):
				values[secure_field] = self.encrypt(cr, uid, values[secure_field], pubkey, context)
		
		# Return values to create with secure fields properly encrypted
		return values
	
	
	# Decrypt a read on the first record if context['unmask'] exists and is True
	# No support for batch decryption at the moment - could be added with context if needed
	def rsa_read(self, cr, uid, values, secure_fields, context=None):
		if context is None: context = {}
		pkey = self.get_privkey(cr, uid, context)
		
		# If read values is a dictionary, not a list, respect that read format
		if not isinstance(values, list):
			for secure_field in secure_fields:
				if values.get(secure_field, False):
					if context.get('unmask', False):
						values[secure_field] = self.decrypt(cr, uid, values[secure_field], key=pkey, context=context)
					# TODO: bad workaround for finding last 4 digits of CC and decrypting!  Not abstracted properly
					elif context.get('cc_last_four', False) and secure_field == 'cc_number':
						decode = self.decrypt(cr, uid, values[secure_field], pkey, context)
						values[secure_field] = 'xxxxxxxxxxxx' + decode[-4:]
						del decode
					else:
						values[secure_field] = 'xxxx' 
		
		# If read values is a list of dictionaries, respect that read format and only operate on the first entry
		# to avoid needless work on list views where read() is called and will return potentially hundreds of items
		elif len(values) == 1:
			for secure_field in secure_fields:
				if values[0].get(secure_field, False):
					if context.get('unmask', False):
						values[0][secure_field] = self.decrypt(cr, uid, values[0][secure_field], key=pkey, context=context)
					elif context.get('cc_last_four', False) and secure_field == 'cc_number':
						decode = self.decrypt(cr, uid, values[0][secure_field], pkey, context)
						values[0][secure_field] = 'xxxxxxxxxxxx' + decode[-4:]
						del decode
					else:
						values[0][secure_field] = 'xxxx' 
		return values
	
	
	# Avoid writing in masked fields by looking for the 'xxxx' mask
	def rsa_write(self, cr, uid, values, secure_fields, context=None):
		if context is None: context = {}
		pubkey = self.get_pubkey(cr, uid, context)
		
		for secure_field in secure_fields:
			# If it's a secured field and it's set to something other than the mask values, re-encrypt it
			if values.get(secure_field, False) and values[secure_field][:4] != 'xxxx':
				values[secure_field] = self.encrypt(cr, uid, values[secure_field], pubkey, context)
		return values
	
	
	# Always strip out encrypted fields when duplicating
	def rsa_copy(self, cr, uid, values, secure_fields, context=None):
		if context is None: context = {}
		for secure_field in secure_fields:
			if values.get(secure_field, False):
				values[secure_field] = False
		return values