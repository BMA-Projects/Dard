# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

{
    'name': 'Tags',
    'version': '1.0',
    'category': 'Tags on Sales and Products',
    'description' : """
    Tags same as customer Tags will be added to all the form views and carry forward to all its related objects.
    """,
    'author': 'OfficeBrain',
    'website': 'http://officebrain.com',
    'depends': ['sale', 'product', 'purchase'],
    'data': [
            'security/ir.model.access.csv',
            'ob_tags_view.xml',
            'views/web_ob_tags_assets.xml',
            'views/product_template_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
