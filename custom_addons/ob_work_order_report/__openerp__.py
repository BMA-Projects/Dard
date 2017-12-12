# -*- coding: utf-8 -*-

{
    'name': 'OB Work Order',
    'category': '',
    'summary': '',
    'version': '1.0',
    'description': """
Provides ability to retrive work report for Manufacturing order .

    """,
    'author': 'OfficeBrain',
    'depends': ['sale','mrp','ob_adnart_so','ob_sale_artwork'],
    'data': [
		'ob_work_order_report_view.xml',
        # 'wizard/aged_partner_balance_view.xml',
        'views/views.xml'
	],
	'installable': True,
	'auto_install': False,
}
