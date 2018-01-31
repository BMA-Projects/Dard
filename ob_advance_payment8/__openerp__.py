# -*- coding: utf-8 -*-

{
    'name': 'OB Credit Limit',
    'category': 'Credit Limit',
    'summary': 'New features of credit limit',
    'version': '1.0',
    'description': """Credit Limit""",
    'author': 'OfficeBrain',
    'depends': ['base','account','sale'],
    'data': [
        #'security/ob_project_enhance_security.xml',
        #'security/ir.model.access.csv',
        #'web_kanban.xml',
        #'wizard/test.xml',
        'wizard/credit_payment_view.xml',
        'res_partner_view.xml',
        
    ],
    'installable': True,
    'auto_install': False,
}
