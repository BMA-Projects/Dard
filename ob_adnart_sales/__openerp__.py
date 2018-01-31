# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    'name': 'AdnArt Customer Customization',
    'version': '1.0',
    'website': 'https://www.officebrain.com',
    'category': 'BMA Development',
    'summary': 'Generic Customer Customization',
    'description': """
    Following fields are added in the customer form:
        1. Adding the customer ID field.
        2. Adding the customer Code field.
        3. Adding the supplier ID field.
""",
    'author': 'OfficeBrain',
    'depends': ['base'],
    'data': [
        'sales.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: