# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'ob adnart sale order extends',
    'version': '1.0',
    'category': 'Sales Management',
    'description': """
       Sales Order extends for adnart.
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['sale','stock','sale_stock', 'ob_scheduled_date','ob_sale_artwork','ob_product_overrun','ob_adnart_product'],
    'data': [ 
            'security/ir.model.access.csv',
            'sale_view.xml',
            'mrp_view.xml'],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: