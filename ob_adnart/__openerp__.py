# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

{
    'name': 'Ad-n-Art Changes',
    'version': '1.0',
    'category': 'Ad-n-Art Changes',
    'description': """ Add-n-Art changes in sale order line adding fields and hide some fields.""",
    'author': 'OfficeBrain',
    'website': 'http://officebrain.com',
    'summary': 'Some field related changes from Ad-n-Art',
    'depends': ['sale', 'ob_product_variant', 'stock', 'delivery'],
    'data': [
        'views/report_stockpicking.xml',
        'stock_report.xml',
        'sale_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: