# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################
{
    'name': 'Science First Email',
    'version': '1.0',
    'category': 'other',
    'description': """
        This module helps to  email should be sent automatically to the customer.

    """,
    'author': 'OfficeBrain',
    'website': 'http://officebrain.com',
    'images': [],
    'depends': ["email_template","sale","purchase","ob_sale_artwork"],
    'data': ['email_template.xml','email_template_action_rule.xml','account_payment_data.xml','send_auto_email_workflow.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'active':False,
}
