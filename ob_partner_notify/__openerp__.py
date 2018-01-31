# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Partner Notify',
    'version': '1.0',
    'category': 'Tools',
    'description': """
       Notification on New Contact Creation For Credit Limit.
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['base_action_rule', 'base', 'email_template'],
    'data': [
             'ob_partner_notify_template.xml',
             'ob_partner_action_rule_data.xml',
             'res_partner_view.xml'
             ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
