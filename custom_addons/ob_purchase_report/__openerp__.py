# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    'name': 'Purchase Order Report',
    'version': '1.0',
    'category': 'Purchase',
    'description': """
       1) This module generate purchase order report for DARD.
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['purchase'],
    'data': [
             'purchase_view.xml',
             'ob_purchase_report.xml',
             'views/report_purchasequotation.xml',
     ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: