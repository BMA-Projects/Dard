# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    "name" : "Product Image",
    "version" : "1.1",
    "author" : "OfficeBeacon",
    "website" : "http://www.officebeacon.com",
    "description": """
            This Module overwrites openerp.web.list.Binary field to show the product image in the listview. A new column with product image is added.
    """,
    "depends" : [ "sale", "sale_stock", "stock" ],
    'data': [
        'views/ob_product_image.xml',
        'product_view.xml',
    ],
    'installable': True,
    "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
