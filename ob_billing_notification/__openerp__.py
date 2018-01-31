# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Billing Notification',
    'version': '1.0',
    'category': 'Notification',
    'description': """
        Notify billing(Account Manager) when product is ready to deliver.
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'depends': ['base_action_rule', 'stock', 'sale'],
#     'data': [
#          'ob_billing_action_rule_data.xml',
#      ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
