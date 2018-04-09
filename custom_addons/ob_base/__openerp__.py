# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

{
    'name': 'Office Brain Base',
    'version': '1.0',
    'category': 'Tools',
    'description' : """ 
        This module inherit base module for User's group management report.
    """,
    'author': 'OfficeBrain',
    'website': 'http://officebrain.com',
    'summary': '',
    'sequence': 1,
    'depends': ['base'],
    'data': ['report/user_group_report_view.xml',
            'ob_base_view.xml',
            ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
