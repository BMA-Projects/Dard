# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

{
    'name': 'Sale Scheduled date',
    'version': '1.0',
    'category': 'Sales Management',
    'sequence': 14,
    'description': """
Manage scheduled/ship date on sales quotations/orders, Purchase quotations/orders and Manufacturing orders
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['purchase', 'mrp', 'sale', 'stock', 'procurement_jit'],
    'data': [
         'purchase_view.xml',
         'sale_view.xml',
         'mrp_view.xml',
         'stock_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
