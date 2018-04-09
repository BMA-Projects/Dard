# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'OE Through Wizard',
    'version': '1.0',
    'category': 'Sales Management',
    'description': """
OE Through Wizard
======================================
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'depends': ['ob_product_variant', 'ob_sample_inv', 'delivery', 'ob_sale_artwork'],
    'data': [
         'oe_wizard_view.xml',
         'sale_view.xml',
         'product_details_view.xml'
     ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
