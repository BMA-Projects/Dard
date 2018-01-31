# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Sample Information',
    'version': '2.0',
    'category': 'Sale Management',
    'description': """
    To keep track the quantity of how many sample of which sample type is sent to customer.And what would be the follow up date for that.
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'depends': ['ob_sample_type', 'calendar', 'purchase'],
    'data': [
        'sale_view.xml',
        'purchase_view.xml',
        'sale_sample_email_template.xml',
        'purchase_sample_email_template.xml',
        'sample_followup_cron.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
