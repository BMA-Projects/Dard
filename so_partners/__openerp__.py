# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

{
    'name': 'SO Partners',
    'version': '1.1',
    'summary': 'Generic Contact Customization',
    'description' : """
        This module will add the fields like ASI Number, Create Date, Source, Source URL, Extension..
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com',
    'images': [],
    'depends': ['base'],
    'category': 'other',
    'demo': [],
    'data': [
        'so_partner_sequence.xml',
        'so_partner_view.xml',
        # 'security/ir.model.access.csv'
    ],
    'test': [],
    'js': ['static/src/js/*.js'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
