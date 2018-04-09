# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'OB Sale Wise Shipping',
    'version': '1.0',
    'category': 'Tag Master',
    'description': """Allow to create delivery order per sale order line""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['sale','sale_stock','delivery'],
    'data': [
        'wizard/sale_line_split_wizard.xml',
        'res_partner_view.xml',
        'sale_view.xml'
    ],
    'css': [],
    'js': [],
    'qweb' : [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
