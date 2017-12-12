# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

{
    'name': 'Vendor QA Process',
    'description':  """
Quality assurance Proces for Vendor Approval.
=============================================
* Introduced Risk Level for Vendors/Suppliers, Last Review Date for Product.
* Purchase Manager can approve/disapprove Suppliers.
* Approved Suppliers listed in Quotation/purchase orders.
""",
    'version': '1.0.1',
    'author': 'officebrain',
    'category': 'MISC',
    'website': 'http://www.officebrain.com',
    'depends': ['base', 'product','purchase_requisition',],
    'data': [
        'partner_view.xml',
        ],
    'demo': [],
    'test': [],
    'auto_install': False,
    'installable': True,
    'images': []
}
