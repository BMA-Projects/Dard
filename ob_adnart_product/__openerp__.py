# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'ob adnart oe',
    'version': '1.0',
    'category': 'product management',
    'description': """
       Product extends for adnart.
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['sale','stock','account', 'sale_stock', 'ob_scheduled_date'],
    'data': [ 
             'security/ir.model.access.csv',
             'product_view.xml',
             'sale_view.xml'],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: