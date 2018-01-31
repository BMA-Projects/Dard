# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import netsvc
from openerp import models, fields, api, _
from openerp.tools.translate import _
from openerp import workflow



class res_company(models.Model):
    _inherit = 'res.company'

    ext_logo = fields.Binary('Extra Logo')
    

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('name')
    def _onchange_refund_invoice_number(self):
        if self.name:
            self.refund_invoice_number = self.name

    @api.multi
    def action_invoice_sent(self):
        res = super(account_invoice, self).action_invoice_sent()
        inv_number = ''
        if self.number:
            split_number = list(self.number.rpartition('/'))
            if len(split_number) == 3 and res.get('context', False):
                inv_number = split_number[2]
                context = res.get('context').update({'inv_number': inv_number})
        return res        

    refund_invoice_number = fields.Char('Refund Invoice Number',track_visibility='onchange')
     
    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        self.sent = True
        return self.env['report'].get_action(self, 'ob_invoice_dard_report.report_invoice_document')
    
    
