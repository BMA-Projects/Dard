# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Sample Type Master',
    'version': '2.0',
    'category': 'Sale Management',
    'description': """
    Sample Type Master for both inventory sample and non-inventory sample
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'depends': ['sale'],
    'data': [
        'sample_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
