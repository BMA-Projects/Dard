# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'OB DML creation',
    'version': '1.0',
    'category': 'sale management',
    'description': """
       This module add product group and product sequence on product level.
       Once product group & sequence are added, it filter the selection on Order line items.
       Example : Product sequence field on sales order line when adding new product on sales order. 
       Based on the given sequence product list to be filtered while drop down opens up.
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['sale'],
    'data': [
             'security/ir.model.access.csv',
             'product_view.xml',
             'sale_view.xml'
           ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
