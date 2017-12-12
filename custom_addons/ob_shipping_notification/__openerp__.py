# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Shipping Notification',
    'version': '1.0',
    'category': 'Warehouse Management',
    'description': """
        Notify shipping when billing completes invoice.
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'depends': ['base_action_rule', 'stock_account'],
    'data': [
         'ob_shipping_action_rule_data.xml',
         'ob_shipping_notification_template.xml',
     ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
