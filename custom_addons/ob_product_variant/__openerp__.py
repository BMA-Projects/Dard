# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    'name': 'OB Product Variant',
    'version': '1.1',
    'author': 'OfficeBrain',
    'summary': """Product variant charges configuration and apply on sales order""",
    'description': """
    Product variant multi extended and customization for charges.Configuration of Product template with all types of Attributes and dimension of Products and apply charges
    on products attributes and placed sales order.
    """,
    'website': 'http://www.officebrain.com',
    'images': [],
    'depends': ['sale', 'account', 'product','stock'],
    'category': 'Sales Management',
    'data': [
        'ob_product_charges_data.xml',
        'ob_product_variant_view.xml',
        "security/ir.model.access.csv",
        'sale_view.xml',
        'invoice_view.xml',
        'ob_product_variant_report.xml',
        'views/variant_template.xml',
        'ob_product_variant_data.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
