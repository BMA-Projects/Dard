# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

{
	'name': 'Credit Card Payments',
	'version': '1.0',
	'depends': [
		'sale',
		'account',
		'account_voucher',
		'rsa_encryption',
		# 'default_addresses'
		'payment',
		'payment_paypal',

	],
	'author': 'OfficeBrain',
    'website': 'http://officebrain.com',
	'category': 'other',
	'complexity': 'normal',
	'description': """The foundation for CC API usage.  *DOES NOT PROCESS CREDIT CARDS BY ITSELF!*  That must be supplemented with an additional module adding connectivity to the desired payment processor.

Uses PKCS#1 v1.5 recommendations for storing data securely.  Follows PCI recommendations of encrypting the card number, cvv, expiration month, and expiration year.  Can save cards to contacts within a company or use a card one time on a voucher.  Card data is scrubbed after validating the voucher for security reasons.

Currently the module requires private and public certificates (PEM or DER) in the server folder named 'cc_priv' and 'cc_pub' respectively.  Advise you use chmod 600 on your private certificate for security.""",
	'init_xml': [
		'account_data.xml',
	],
	'update_xml': [
		'account_view.xml',
		'account_invoice_view.xml',
		'account_journal_view.xml',
		'account_voucher_view.xml',
#		'res_partner_bank_view.xml',
	],
	# 'data': ['portal_data.xml'],
	'data' : ['views/paypal_button.xml'],
	'demo': [],
	'test': [],
	'installable': True,
	'application': False,
}
