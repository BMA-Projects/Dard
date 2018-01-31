# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Sale Order Extension',
    'version': '1.0',
    'category': 'Sale Management',
    'description': """
        1. Add prepare and reset to draft functionality.
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['calendar', 'mrp', 'sale_stock', 'sale'],
    'data': [
       'sale_order_view.xml',
       'sale_order_workflow.xml',
       'ob_so_reset_cancel_template.xml',
       'ob_sale_action_rule_data.xml',
                   ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
