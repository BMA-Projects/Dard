# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class res_users(models.Model):
    _inherit = "res.users"

    writeoff_limit = fields.Float(string='Write-Off Limit', default=0)

class account_voucher(models.Model):
    _inherit = "account.voucher"

#     def _compute_writeoff_amount(self, cr, uid, line_dr_ids, line_cr_ids, amount, type):
#         super(account_voucher, self)._compute_writeoff_amount(cr, uid, line_dr_ids, line_cr_ids, amount, type)
#         print "VAL..........FROM WRITE OFF:"
#         debit = credit = 0.0
#         sign = type == 'payment' and -1 or 1
#         for l in line_cr_ids:
#             if isinstance(l, dict):
#                 credit += l['amount_original']
#         return amount - sign * (credit - debit)

class account_move_line_reconcile(models.Model):
     _inherit = "account.move.line.reconcile"
 
     def trans_rec_addendum_writeoff(self, cr, uid, ids, context=None):
         if not context:
             context = {}
         res = super(account_move_line_reconcile, self).trans_rec_addendum_writeoff(cr, uid, ids, context)
         user_obj = self.pool.get('res.users')
         writeoff_user = user_obj.browse(cr, uid, uid).writeoff_limit
#          mod = res.get('res_model',False)
         writeoff = self.browse(cr, uid, ids, context).writeoff
         if writeoff > writeoff_user:
            raise Warning(_('You are not allowed to write-off this much amount ! Please contact finance manager for the same !!!'))
         return res
