# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    'name': 'Artwork OfficeBrain',
    'version': '1.0',
    'website' : 'https://www.officebrain.com',
    'category': 'BMA Development',
    'summary': 'Approval process of Artwork.',
    'description': """
Approval process of Artwork.
============================

    1) Added activity log for sale order in partner form.
    2) Added Virtual Images per Sale order line.
    3) Added Virtual Images History.
    
Need to add two System Parameters as follow:
--------------------------------------------
* global.path : path of the openerp where openerp-server file exists.
* global.web.path : path where web module exists.
""",
    'author': 'OfficeBrain',
    'depends': ['sale','ob_product_multi_images','mrp','sale_stock','purchase','procurement'],
    'data': [
        'sale_view.xml',
        'security/ir.model.access.csv',
        'security/ob_sale_security.xml',
        'sale_order_line_sequence.xml',
        'views/ob_sale_artwork.xml',
        'email_template.xml',
        'sale_order_line_data.xml',
        'mail_compose_message_view.xml',
    ],
     'qweb' : [
        "static/src/xml/*.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: