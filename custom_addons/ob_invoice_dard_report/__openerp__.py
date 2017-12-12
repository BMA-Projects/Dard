# -*- coding: utf-8 -*-

{
    'name': 'OB Invoice Report',
    'category': '',
    'summary': '',
    'version': '1.0',
    'description': """
Provides ability to retrive invoice report for sale invoice order .

    """,
    'author': 'OfficeBrain',
    'depends': ['sale','account','mrp','crm', 'account_check_writing','ob_starship'],
    'data': [
        'views/invoice_email_template.xml',
        'invoice_data.xml',
        'views/check_print_report_view.xml',
        'ob_invoice_report_view.xml',
        'company_view_extend.xml',
        'views/views.xml',
        'report_menu.xml',
        'views/product_view.xml',
        'account_voucher_view.xml',
        'wizard/check_print_wizard_view.xml',
	],
	'installable': True,
	'auto_install': False,
}
