# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

{
    'name': 'Check Writing - Office Brain',
    'version': '1.1',
    'author': 'OfficeBrain',
    'category': 'Generic Modules/Accounting',
    'description': """
Module for extend the report of the Check Writing and Check Printing.
================================================
    """,
    'website': 'http://www.officebrain.com',
    'depends' : ['account_check_writing'],
    'data': [
        'account_check_writing_report.xml',
        'views/views.xml',
        'security/ir.model.access.csv',
    ],
    'test': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
