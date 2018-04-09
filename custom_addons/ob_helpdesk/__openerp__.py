# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

{
    'name': 'Support Tickets Helpdesk',
    'category': 'Customer Relationship Management', 
    'version': '1.0',
    'description': """
Support Tickets Management.
===========================
Generated Support Tickets to acknowledgement to the customers. And Support Tickets linked with Sale Order.
Add crm.helpdesk readonly rights for 'Customer Service' group.
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com',
    'depends': ['crm_helpdesk', 'ob_sale_artwork', 'sales_team'],
    'data': [
        'ob_helpdesk_data.xml', 
         'ob_helpdesk_view.xml',
         'security/ob_helpdesk_security.xml',
         'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
