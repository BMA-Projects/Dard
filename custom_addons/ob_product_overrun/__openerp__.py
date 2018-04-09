# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

{
    'name': 'Overrun Functionality',
    'version': '1.0',
    'category': 'Overrun Functionality',
    'description' : """
    Overrun functionality on sales order line.
    Product contains overrun field for the Quantity.
    Product quantity will be multiplied according to that overrun value percentage while generating PO and MO from SO.
    """,
    'author': 'OfficeBrain',
    'website': 'http://officebrain.com',
    'depends': ['sale', 'product', 'purchase', 'procurement', 'mrp'],
    'data': ['product_overrun_view.xml',
     #        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
