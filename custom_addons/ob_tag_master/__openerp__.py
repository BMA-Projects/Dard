# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Tag Master Changes',
    'version': '2.0',
    'category': 'Tag Master',
    'description': """
       1) Replace String Quotation to Order Entry
       2) The term 'Delivery Address' to be changed to 'Ship To Address'
       3) When clicking on to the 'Print', there should only show 'Order', rather Quotations
       4) Customer Address and Invoice Address is one in the same, so need to remove any one of them
       5) When u click on screen ready.. be able to input a screen# up to six digits
       6) The Order 'Date' should not be editable and it should be fixed
       7) On Quotation Form customer po number should be required field
       8) Email address should not be the required field
       9) Email templates for Missing Artwork, Order to be kept on Hold, Require Additional Shipping, Waiting on Proof Approval
       10) Pre-payment Report with template.
       11) Create cron (scheduler)  which send email when product stock goes less then minimum threshold quantity defined in 'Reordering Rules'.(Steps to Set Receiver email for stock alert ==> Settings > Email > Templates > find template "Stock Reminder Email" > Tab: Email Configuration > set 'To (Emails)')
       12) Generate customer/supplier/customer-supplier sequence number for the partner(company)
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['sale','ob_notification_screen_ready','delivery','ob_scheduled_date', 'ob_product_variant', 'sale_mrp', 'ob_sale_artwork', 'purchase','ob_purchase_report','ob_sale_wise_shipping', 'ob_sale_order_extend'],
    'data': [
        'sale_view.xml',
        'cron_data.xml',
        'data/cust_seq_data.xml',
        'views/res_partner_view.xml',
        'report/product_qty_reminder_email.xml',
        'ob_email_notification_template.xml',
        'ob_pre_payment_notification_template.xml',
        'art_pending.xml',
        'email_template_dard.xml',
        'order_on_hold.xml',
        'require_additional_shipping_info.xml',
        'waiting_on_proof_approval.xml',
        'views/report_saleorder_prepayment.xml',
        'views/report_saleorder.xml',
        'views/report_request_for_quatation_ext_view.xml',
        'views/report_purchase_order_ext_view.xml',
        'views/report_purchase_quotation_inherit.xml',
        'ob_category_code_data.xml',
        'ob_category_code_view.xml',
        'lable_change_view.xml',
        'security/ir.model.access.csv',
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
