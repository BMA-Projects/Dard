# -*- coding: utf-8 -*-

{
    'name': 'OB Due Payment',
    'category': 'Due Payment',
    'summary': 'New features of Due Payment',
    'version': '1.0',
    'description': """Due Payment""",
    'author': 'OfficeBrain',
    'depends': ['base','account','sale'],
    'data': [
        'res_partner_view.xml',
        'res_partner_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}
