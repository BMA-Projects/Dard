# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler

class purchase_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(purchase_order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
        	'time': time,
        	'get_ack_confirm' : self.get_ack_confirm

        })

    def get_ack_confirm(self,obj):
    	ack = ''
    	conf = ''
       	if obj.state not in ('draft','cancel'):
       		ack = 'YES'
       	else:
       		ack = 'NO'
       	if obj.state not in ('draft','sent','cancel'):
       		conf = 'YES'
       	else:
       		conf = 'NO'
       	return {'ack': ack, 'conf' : conf}

report_sxw.report_sxw('report.new.purchase_order','purchase.order','addons/ob_purchase_report/report/purchase_order.rml',
                      parser=purchase_order, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

