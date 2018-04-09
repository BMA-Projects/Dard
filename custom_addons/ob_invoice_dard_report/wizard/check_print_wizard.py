# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import Warning

class CheckPrintWizard(models.TransientModel):
    _name = 'check.print.wizard'
    _rec_name = 'print_reason'

    print_reason = fields.Text("Reason")
    is_check_print  = fields.Boolean('Reprint Check', default=False)

    @api.multi
    def check_report_report(self):
        if self._context and self._context.get('active_id'):
            if not self.is_check_print:
                raise Warning(_('Please, select reprint check option.'))
            voucher_id = self.env['account.voucher'].browse(self._context.get('active_id'))
            if voucher_id:
                reason_obj = self.env['check.print.reason']
                reason_id = reason_obj.create({
                    'print_reason' : self.print_reason,
                    'account_voucher_id' : self._context.get('active_id'),
                    })                
                voucher_id.is_printed = True
                return voucher_id.print_dard_check()
