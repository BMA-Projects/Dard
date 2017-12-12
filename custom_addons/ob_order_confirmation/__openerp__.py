# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Order Confirmation',
    'version': '2.0',
    'category': 'Sales Management',
    'description': """
    Order Confirmation
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'depends': ['ob_product_variant','delivery','ob_scheduled_date'],
    'data': [
        'sale_report.xml',
        'ob_order_ack_template.xml',
        'res_company_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
