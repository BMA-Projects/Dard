# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Sample Sales Order',
    'version': '2.0',
    'category': 'Sale Management',
    'description': """
    For convert sale order in Sample order and add ref. in purchase order.
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'depends': ['sale', 'purchase', 'procurement', 'ob_sample_type'],
    'data': [
        'security/ob_sale_purchase_sample_security.xml',
        'ob_sale_purchase_sample_view.xml',
        'email_template.xml',
        'sample_followup_cron.xml'
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
