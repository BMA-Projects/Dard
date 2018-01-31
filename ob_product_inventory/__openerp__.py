# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    "name" : "Product Inventory",
    "version" : "1.1",
    "author" : "OfficeBeacon",
    "website" : "http://www.officebeacon.com",
    "description": """
            This modulE will add tab for inventory in sale order line and Display related product On Hand inventory details.
    """,
    "depends" : [ "sale","stock","ob_sale_artwork" ],
    'data': [
        'ob_product_inventory.xml',
    ],
    'installable': True,
    "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
