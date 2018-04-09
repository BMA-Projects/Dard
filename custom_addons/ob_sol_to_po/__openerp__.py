# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Purchase Order from SOL',
    'version': '1.0',
    'category': 'Purchase Management',
    'description': """
Create purchase order from Sales line
===========================================================================
Story : 1844

At the time of Sales Order confirmation following action needs to be taken:
    * A link to be added on sales line.
    * On click of that link:

Following field to be available:
    * Selection of Active supplier defined on product
    * Selection of Partner for shipping address
    * Qty field (Default qty should be as per sales line)

On the basis of above information Purchase order to be created in draft stage.
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['stock', 'sale', 'procurement_jit', 'purchase'],
    'data': [
             'wizard/purchase_details_view.xml',
             'data/parameter_sale_config.xml',
             'sale_view.xml',
             'purchase_view.xml',
             'sale_config_view.xml'
            ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=
