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

{
	'name': 'RSA Encryption',
	'version': '0.6',
	'depends': [
		'base',
	],
	'author': 'OfficeBrain',
    'website': 'http://officebrain.com',
	'category': 'Solaris Custom',
	'complexity': 'normal',
	'description': """
Portable RSA Encryption
=======================

An OpenERP object containing RSA encryption and decryption methods that are PKCS#1 v1.5 compliant.
Can be utilized by any module, just set the dependency on this module and use 
"rsa = self.pool.get('rsa.encryption')" in your code to access the functions.  This code implements
the Python Crypto library (pycrypto).  See full documentation here:  https://pypi.python.org/pypi/pycrypto

To begin, you must generate a set of keys from 'Settings' -> 'Technical' -> 'Security' -> 'Generate New Keys'.
The files will be saved in the server root directory (where openerp-server is) and given read/write
permission ONLY to the owner - whichever account is running OpenERP.

Ensure that any module using this code adds 'rsa_encryption' as a dependency!.  Also make sure anything
you store encrypted in the database is defined as a char field with a size of at least 512 characters
(based on a 2048-bit key).


Functions
=======================
rsa = self.pool.get('rsa.encryption')
	Get the RSA object, must always be done first.

rsa.get_keys(cr, uid, context=None)
	Returns a tuple of the private key and public key objects in that order.  Will only ever return the
	"primary" key defined in OpenERP, so you don't need to search for the key record first.  Should only be
	called for efficiency, pass the correct key to the encrypt and decrypt functions to avoid re-reading the
	key from the disk every time.

rsa.get_pubkey(cr, uid, context=None)
	Returns the public key object from the primary set.  Use this to avoid multiple reads from the disk for
	multiple sequential encrypt() calls.

rsa.get_privkey(cr, uid, context=None)
	Returns the private key object from the primary set.  Use this to avoid multiple reads from the disk for
	multiple sequential decrypt() calls.

rsa.encrypt(cr, uid, value, key=False, context=None)
	Returns a base64 encoded string of the value encrypted.  Will use the key object if passed, otherwise will
	call get_pubkey().

rsa.decrypt(cr, uid, value, key=False, context=None)
	Returns the decoded content of the encrypted value.  The value should be a base64 encoded string from
	encrypt().  Will use the key object if passed, otherwise will call get_privkey(). 
	""",
	'init_xml': [],
	'update_xml': [
		'wizard/key_generator_view.xml',
		'rsa_view.xml',
		'security/ir.model.access.csv',
	],
	'data': [],
	'demo': [],
	'test': [],
	'installable': True,
	'application': False,
}