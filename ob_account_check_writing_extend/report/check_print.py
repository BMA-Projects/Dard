# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw

class report_print_check_extended(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_print_check_extended, self).__init__(cr, uid, name, context)
        self.number_lines = 0
        self.number_add = 0
        self.localcontext.update({
            'time': time,
            'get_lines': self.get_lines,
            'fill_stars' : self.fill_stars,
            'check_validation': self.check_validation,
        })
        
    def check_validation(self, obj):
        tot_amt = 0
        for line in obj.line_dr_ids:
            tot_amt += line.amount
        if obj.amount < tot_amt:
            return ''
#             print "this is writeofffff",obj.id
        return ''
        
    def fill_stars(self, amount):
        if amount:
            amount = amount.replace('Dollars','')
            if len(amount) < 100:
                stars = 100 - len(amount)
                return ' '.join([amount,'*'*stars])

            else: return amount
    
    def get_lines(self, voucher_lines):
        result = []
        self.number_lines = len(voucher_lines)
        for i in range(0, min(10,self.number_lines)):
            if i < self.number_lines:
                v_line = voucher_lines[i]
                invoice = v_line.move_line_id.invoice
                discount_amt = 0
                if invoice.invoice_line:
                    
                    for i_line in invoice.invoice_line:
                        orig_amt = i_line.quantity * i_line.price_unit
                        discount_amt += orig_amt - i_line.price_subtotal

                res = {
                    'date_due' : v_line.date_due and v_line.date_due or False,
                    'name' : v_line.move_line_id.invoice.number,
                    'amount_original' : v_line.amount_original+discount_amt and v_line.amount_original+discount_amt or False,
                    'amount_unreconciled' : v_line.amount_original - (v_line.amount_unreconciled) or False,
                    'amount' : v_line.amount and v_line.amount or False,
                    'amount_due' : v_line.amount_original - v_line.amount,
                    'date_original': v_line.date_original and v_line.date_original or False,
                    'discount_taken': discount_amt or '',
                }
            else:
                res = {
                    'date_due' : False,
                    'name' : False,
                    'amount_original' : False,
                    'amount_unreconciled' : False,
                    'amount' : False,
                    'amount_due' : False,
                    'date_original': '',
                    'discount_taken': False,
                }
            result.append(res)
        return result



report_sxw.report_sxw(
    'report.account.print.check.middle.extended',
    'account.voucher',
    'addons/account_check_writing/report/check_print_middle_extended.rml',
    parser=report_print_check_extended,header=False
)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
