# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp.osv import fields, osv

class purchase_purchase(osv.osv):
    _inherit = "purchase.order"

    _columns = {
        'fob': fields.char('FOB', size=64),
        'ship_via' : fields.char('Ship Via', size=64)
    }

    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the request for quotation and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        self.signal_workflow(cr, uid, ids, 'send_rfq')
        return self.pool['report'].get_action(cr, uid, ids, 'ob_purchase_report.report_purchasequotation', context=context)

purchase_purchase()