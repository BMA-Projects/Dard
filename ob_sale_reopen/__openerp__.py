# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Sale Order Re-open',
    'version': '1.0',
    'category': 'Sale Management',
    'description': """
    * Allows reopening of sale orders.
    * This module allows to reopen (set to Quotation) Sale Orders in state progress and cancel as associated pickings cancelled if possible.
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['sale', 'purchase', 'mrp'],
    'data': [
       'sale_order_view.xml',
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
