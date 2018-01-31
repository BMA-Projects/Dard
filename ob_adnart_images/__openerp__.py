# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    'name': 'Ad N Art Images',
    'version': '1.0',
    'website' : 'https://www.officebrain.com',
    'category': 'BMA Development',
    'summary': 'Display Product & Artwork Images in Sale Order',
    'description': """
""",
    'author': 'OfficeBrain',
    'depends': ['sale','ob_sale_artwork','report'],
    'data': [
        'sale_view.xml',
        'views/ob_adnart_view_images.xml',
        'views/report_quotation_updated.xml',
    ],
     'qweb' : [
        "static/src/xml/*.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: