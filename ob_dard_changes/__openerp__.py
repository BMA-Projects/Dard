# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

{
    'name': 'Ob Dard Changers ',
    'category': '',
    'summary': '',
    'version': '1.0',
    'description': """
        1) Hide Label (Source Document ) in Call for Bids Form
        2) Add is_salesperson boolean in res_user for make salesperson/order_processer/responsible
        3) changes name of field 'Internal_reference' to 'Item Number'
    """,
    'author': 'OfficeBrain',
    'depends': ['purchase', 'mrp', 'account','account_voucher', 'sale', 'so_partners',
                'ob_sale_artwork', 'shipping_pragtech', 'ob_scheduled_date', 'crm', 'product','ob_product_variant','ob_product_overrun','ob_tag_master', 'ob_advance_payment8',
                'ob_due_payment','ob_invoice_dard_report','pragtech_shipping_invoice'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/update_last_year_qty_view.xml',
        'wizard/ranking_report_view.xml',
        'views/ob_product_view.xml',
        'views/res_user_view.xml',
        'views/sale_order_view.xml',
        'views/res_partner_view.xml',
        'views/web_ob_dard_assets.xml',
        'views/account_view.xml',
        'views/purchase_order_line_view.xml',
        'ob_product_variant_report_inherit.xml',
        'views/mrp_bom_view.xml',
        'views/stock_picking_report.xml',
        'views/res_partner_cat_data.xml',
        'report/report_saleorder.xml',
        'report/sale_report.xml',
        'report/sale_order_attention.xml',
        'report/sale_order_email_template.xml',
        'report/sale_order_prepayment_attention.xml',
        'views/product_ir_cron_view.xml',
    ],
    'qweb': [
        'static/src/xml/web_ob_dard_field_name.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
