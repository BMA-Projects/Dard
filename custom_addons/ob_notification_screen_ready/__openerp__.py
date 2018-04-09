# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Office Brain Notify Screens are Ready',
    'version': '1.0',
    'category': 'Sale Management',
    'description': """
       This module will notify the User and Manufacturing Manager that screens are ready to proceed. 
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['sale','mrp'],
    'data': [
        'sale_order_view.xml',
        'email_template.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
