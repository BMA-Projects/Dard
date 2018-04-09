# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'ob_po_mo_ref_on_so',
    'version': '1.0',
    'category': 'Sales-Purchase Management',
    'description': """
       Define Purchase Order reference in Sale Order to compare po request from various supplier
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['ob_sol_to_po','mrp'],
    'data': [
             'sale_view.xml',
             'purchase_view.xml',
             'mrp_view.xml',
             'security/ir.model.access.csv',
             'views/views.xml'
             ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
