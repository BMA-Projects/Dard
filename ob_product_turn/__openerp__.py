# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    'name': 'Product Turn',
    'version': '1.0',
    'category': 'Product Configuration',
    'description': """
       1) This module calculate Product Turn.
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['product','sale_stock'],
    'data': [
             'wizard/ob_product_turn_report_wizard_view.xml',
             'ob_product_turn_view.xml',
     ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
