# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    'name': 'Reply To OfficeBrain',
    'version': '1.0',
    'website' : 'https://www.officebrain.com',
    'category': 'BMA Development',
    'summary': 'Auto Fill-up Reply To from User.',
    'description': """
Auto Fill-up Reply To from User.
""",
    'author': 'OfficeBrain',
    'depends': ['mail'],
    'data': [
        'res_users_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: