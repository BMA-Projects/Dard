# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    'name': 'Sales Goal OfficeBrain',
    'version': '1.0',
    'website' : 'https://www.officebrain.com',
    'category': 'BMA Development',
    'summary': 'Identify the sales goal.',
    'description': """
Identify the sales goal of the customer and actual sales for particular customer.
""",
    'author': 'OfficeBrain',
    'depends': ['account'],
    'data': [
        'res_partner_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: