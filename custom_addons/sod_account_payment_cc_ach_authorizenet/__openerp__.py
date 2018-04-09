# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

{
    'name': 'Authorize.Net ACH Payment',
    'version': '0.1',
    'depends': [
        'sod_account_payment_cc_authorizenet'
    ],
    'author': 'OfficeBrain',
    'website': 'http://officebrain.com',
    'category': 'Solaris Custom',
    'complexity': 'normal',
    'description': """
Provides Authorize.Net API access for echeck(ACH) payments.

    """,
    'init_xml': [],
    'data': ['sod_account_payment_cc_ach_authorizenet_view.xml'],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: