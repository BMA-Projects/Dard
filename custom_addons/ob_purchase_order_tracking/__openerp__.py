# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    'name': 'Purchase Order Tracking',
    'version': '1.0',
    'category': 'Purchase Management',
    'description': """Track Purchase Orders""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'depends': ['sale','purchase','ob_sol_to_po'],
    'data': [
         'po_track_sequence.xml',
         'ob_po_track_view.xml',
         'purchase_view.xml',
         'views/views.xml'
     ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: