# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'MRP Operation Extention',
    'version': '1.0',
    'category': 'Manufacturing',
    'description': """
       Notification on MO Routing Operation..
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['mrp','mrp_operations'],
    'data': [
         'ob_mrp_operation_email_template.xml',
         'ob_mrp_operation_action_rule_data.xml',
         'ob_mrp_operation_workflow.xml',
         
     ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


