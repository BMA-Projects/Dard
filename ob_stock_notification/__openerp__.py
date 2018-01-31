# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Stock Extention',
    'version': '1.0',
    'category': 'Warehouse Management',
    'description': """
Notify Warehouse Manager
========================

178 - Notify Warehouse Manager when the product is moved from one location to another. when product is pulled for any location then it should send notification to the Warehouse Manager(s).

As the product is moved from stock location to customer location (in case of sale) or from supplier to stock location (in case of purchase), Warehouse Manager will be notified with mail.
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'depends': ['base_action_rule', 'stock'],
    'data': [
         'ob_stock_action_rule_data.xml',
         'ob_stock_notification_template.xml',
     ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
