# -*- coding: utf-8 -*-

{
    'name': 'OB Partner Ageing',
    'category': '',
    'summary': '',
    'version': '1.0',
    'description': """
Provides ability to Ftch an Partner Ageing Report for particular Partner with Document Number and Due date.

    """,
    'author': 'OfficeBrain',
    'depends': ['account'],
    'data': [
		'ob_partner_ageing_view.xml',
        'wizard/aged_partner_balance_view.xml',
        'views/views.xml'
	],
	'installable': True,
	'auto_install': False,
}
