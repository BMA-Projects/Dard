# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

{
	'name': 'Authorize.Net API',
	'version': '1.0',
	'depends': [
		'account_voucher',
		'sod_account_payment_cc',
		# 'web_m2x_options',
		'purchase'
		#'partner_main_category'
	],
	'author': 'OfficeBrain',
    'website': 'http://officebrain.com',
	'category': 'other',
	'complexity': 'normal',
	'description': """
Provides Authorize.Net API access for credit card payments.  Can enter card info directly or use
information on file to avoid entering CC information.

This module uses the Python urllib3 library (see documentation: https://pypi.python.org/pypi/urllib3 for more info).
To install this in Ubuntu, use:

sudo apt-get install python-urllib3

If you're using an older version of Ubuntu that doesn't have urllib3 in the repository, you must download the source
code and install it.  Here are the steps to do that:

cd /tmp

wget https://pypi.python.org/packages/source/u/urllib3/urllib3-1.7.tar.gz

tar xf urllib-1.7.tar.gz

cd urllib-1.7

sudo python setup.py install

Restart the OpenERP server once this is done and you should be able to install this module.
	""",
	'init_xml': [],
	'update_xml': [
		'wizard/create_customer_profile_view.xml',
		'wizard/create_payment_profile_view.xml',
		'wizard/account_voucher_pay_view.xml',
		'account_voucher_workflow.xml',
		'account_view.xml',
		'account_voucher_view.xml',
		'res_partner_view.xml',
		'payment_view.xml',
		'authorizenet_api_view.xml',
		'security/ir.model.access.csv',
	],
	'data': [],
	'demo': [],
	'test': [],
	'installable': True,
	'application': False,
}
