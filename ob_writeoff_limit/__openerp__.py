# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    'name': 'Write-Off Limit',
    'version': '2.0',
    'category': 'Add-n-Art',
    'description': """ Write-Off limit in Invoice for Payment """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'depends': ['account', 'account_voucher'],
    'data': [
        'security/ir.model.access.csv',
        'ob_writeoff_limit_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
