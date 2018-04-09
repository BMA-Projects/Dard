# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Entry',
    'category': 'Hidden',
    'description':"""

""",
    'author': 'OfficeBrain',
    'version': '2.0',
    'category': 'BMA Development',
    'summary':'Sale Order Entry',
    'depends': ['base','crm','delivery','account_voucher', 'sale','sale_stock','ob_tag_master','ob_sale_artwork','account','crm','product','mrp','purchase','stock','ob_sample_type','ob_sale_order_extend','ob_sale_order_tracking'
    ],
    'data' : [
    'security/order_entry_security.xml',            
    'security/ir.model.access.csv',
    'view/order_entry_view.xml',

    ],
    'qweb': [],
    'auto_install': False,
    'installable': True,
    'application': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
