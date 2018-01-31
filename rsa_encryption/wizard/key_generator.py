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

from Crypto.PublicKey import RSA
from openerp.osv import osv, fields
from openerp.tools.translate import _

class key_generator(osv.TransientModel):
	_name = 'key.generator'
	_columns = {
		'filename_priv': fields.char('Private Key Name', size=64, required=True),
		'filename_pub': fields.char('Public Key Name', size=64, required=True),
		'key_size': fields.selection([('1024','1024'),
									('2048','2048'),
									('4096','4096'),
									('8192','8192')], 'Key Length in bits', required=True),
	}
	
	_defaults = {
		'key_size': '2048',
	}
	
	# Set the public key to <filename_priv>.pub
	def onchange_private(self, cr, uid, ids, filename_priv, context=None):
		if context is None: context = {}
		res = {}
		
		if not filename_priv:
			res['filename_pub'] = ''
		else:
			res['filename_pub'] = filename_priv + '.pub'
		
		return {'value': res}
	
	#Generate the private/public keys with the given filenames and using the defined
	# key size (default 2048)
	def generate_keys(self, cr, uid, ids, context=None):
		if context is None: context = {}
		if not ids: return {}
		if not isinstance(ids, list): ids = [ids]
		
		wizard_rec = self.browse(cr, uid, ids, context)[0]
		# Make sure the filenames aren't blank or bad
		if not wizard_rec.filename_priv:
			raise osv.except_osv("Error", "You must enter a filename for the private key.")
		if not wizard_rec.filename_pub:
			raise osv.except_osv("Error", "You must enter a filename for the public key.")
		if wizard_rec.filename_priv == wizard_rec.filename_pub:
			raise osv.except_osv("Error", "The public and private key filenames are identical, please choose different names.")
		
		pkey = RSA.generate(int(wizard_rec.key_size))
		pubkey = pkey.publickey()
		
		import os
		# Raise OSV exceptions if the files exist - we shouldn't be overwriting an existing RSA key or
		# the data already encrypted using it will be forever lost!

		rsa_key_path = self.pool.get('ir.config_parameter').get_param(cr, uid, 'rsa.key.path')
		if not rsa_key_path:
			raise osv.except_osv('Configuration Error', "No system Parameter found with name 'rsa.key.path'.\n Please create System Parameter to store RSA keys.")
		#abs_path = "/usr/lib/python2.6/site-packages/openerp-7.0_20140303_001304-py2.6.egg"		
		
		if os.path.isfile(wizard_rec.filename_priv):
			raise osv.except_osv('Error', 'The private key already exists.  Please choose a different filename.')
		if os.path.isfile(wizard_rec.filename_pub):
			raise osv.except_osv('Error', 'The public key already exists.  Please choose a different filename.')
		
		# Create the file, export the key, and set the permissions to Read/Write for the owner ONLY
		f = open(rsa_key_path + wizard_rec.filename_priv,'w')
		f.write(pkey.exportKey())
		f.close()
		os.chmod(rsa_key_path + wizard_rec.filename_priv, 0600)
		
		# Repeat for public key, though this could arguably be 0644 instead.
		f = open(rsa_key_path + wizard_rec.filename_pub,'w')
		f.write(pubkey.exportKey())
		f.close()
		os.chmod(rsa_key_path + wizard_rec.filename_pub, 0600)
		
		rsa_obj = self.pool['rsa.encryption']
		
		# Find any existing active key sets, if none exist, make it the primary set
		make_primary = True
		found_keys = rsa_obj.search(cr, uid, [('primary','=',True)])
		if found_keys:
			make_primary = False
		vals = {
			'name': wizard_rec.filename_priv,
			'pub_name': wizard_rec.filename_pub,
			'active': True,
			'primary': make_primary,
		}
		rsa_obj.create(cr, uid, vals, context)
		rsa_view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'rsa_encryption', 'view_rsa_key_tree')[1]
		return {
                'name': _('RSA Keys'),
                'view_type': 'tree',
                'view_mode': 'tree',
                'res_model': 'rsa.encryption',
                'view_id': rsa_view_id,
                'type': 'ir.actions.act_window',
            }
