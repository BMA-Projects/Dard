# -*- coding: utf-8 -*-

{
    'name': 'OB Mo Production Order Report',
    'category': '',
    'summary': '',
    'version': '1.0',
    'description': """
Provides ability to retrive work report for Manufacturing order .

    """,
    'author': 'OfficeBrain',
    'depends': ['sale','mrp'],
    'data': [
		'ob_mo_report_view.xml',
        'views/views.xml'
	],
	'installable': True,
	'auto_install': False,
}
