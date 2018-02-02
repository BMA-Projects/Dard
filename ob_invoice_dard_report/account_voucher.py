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
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import Warning



class CheckPrintReason(models.Model):
    _name = 'check.print.reason'

    print_reason = fields.Text('Reasons')
    account_voucher_id = fields.Many2one('account.voucher', 'Account Voucher')

class account_voucher(models.Model):
    _inherit = 'account.voucher'

    @api.model
    def get_check_seq_no(self):
        try:
            sequence_check_number_dard  = self.env['ir.model.data'].get_object_reference('ob_invoice_dard_report', 'sequence_check_number_dard')[1]
            seq = self.env['ir.sequence'].browse(sequence_check_number_dard)
            return seq.number_next_actual
        except ValueError:
            return False

    check_seq = fields.Integer(string="Check Sequence Number", default=get_check_seq_no)
    is_printed = fields.Boolean('Is printed', default=True)
    check_print_reason_ids = fields.One2many('check.print.reason', 'account_voucher_id', 'Reasons')

    @api.multi
    def copy(self, default=None):
        if self._context and self._context.get('write_check'):
            raise Warning(_('You cannot duplicate a check print.'))
        return super(account_voucher, self).copy(default)

    @api.multi
    def print_dard_check(self):
        if not self.ids:
            raise osv.except_osv(_('Printing error'), _('No check selected '))
        if self.is_printed:
            self.is_printed = False
            result =  self.pool['report'].get_action(
                self._cr, self._uid, self.id, 'ob_invoice_dard_report.dard_check_print_report_view', context=self._context
            )
            return result
        else:
            return {
                'name': "Check Print",
                'view_mode': 'form',
                'res_model': 'check.print.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
            


    @api.multi
    def get_check_data(self, page_data, result, page_count):
        sequence_check_number_dard  = self.env['ir.model.data'].get_object_reference('ob_invoice_dard_report', 'sequence_check_number_dard')[1]
        seq = self.env['ir.sequence'].browse(sequence_check_number_dard)
        check_number = seq.number_next_actual
        seq.number_next_actual += 1 
        self.check_seq = seq.number_next_actual
        count  = 0
        currency_id = self.company_id and self.company_id.currency_id and self.company_id.currency_id.id or False
        currency_symbol = self.company_id and self.company_id.currency_id and self.company_id.currency_id.symbol or False

        if len(result) == 1:
            for amount in page_data:
                count += amount.get('net_check_amount')
            amount_in_word = self._amount_to_text(count, currency_id)
            for i in [a for a in range(1, 7-len(str(check_number)) )]:
                check_number = '0' + str(check_number)
            return {'check_amount' : count, 'check_number': check_number , 'amount_in_word' : amount_in_word, 'currency_id': currency_symbol}
        else:
            if page_count < len(result):
                for i in [a for a in range(1, 7-len(str(check_number)) )]:
                    check_number = '0' + str(check_number)
                return {'check_amount' : 'xxxxxxxxxxxxxx', 'check_number': check_number, 'amount_in_word' : '*** Void ***', 'currency_id': currency_symbol}
            for data in result.values():
                for amount in data:
                    count += amount.get('net_check_amount')
            amount_in_word = self._amount_to_text(count, currency_id)
            for i in [a for a in range(1, 7-len(str(check_number)) )]:
                check_number = '0' + str(check_number)
            return {'check_amount' : count, 'check_number': check_number, 'amount_in_word': amount_in_word, 'currency_id': currency_symbol}


    @api.multi
    def get_data(self):
        res = {}
        i = 1
        res.update({i:[]})
        count = 0
        check_total = 0
        for line in self.line_dr_ids:
            if line.move_line_id and line.move_line_id.invoice and line.amount:
                if not res.get(i):
                    res.update({i:[]})
                res[i].append({'invoice_no': line.move_line_id.invoice.supplier_invoice_number, 
                    'date':line.move_line_id.invoice.date_invoice,
                    'amount': line.amount_original,
                    'amount_paid': line.amount,
                    'discount_taken': 0,
                    'net_check_amount': line.amount,})
                count += 1
                if count == 13:
                    check_total = 0
                    count = 0
                    i +=1
        return res


class CustomerInvoice(models.Model):
    _inherit = 'account.invoice'

    order_ids = fields.Many2many(
        'sale.order', 'sale_order_invoice_rel', 'invoice_id', 'order_id',
        'Sale Orders')


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    @api.multi
    def write(self, vals):
        res = super(IrSequence, self).write(vals)
        try:
            sequence_check_number_dard  = self.env['ir.model.data'].get_object_reference('ob_invoice_dard_report', 'sequence_check_number_dard')
            if sequence_check_number_dard:
                sequence_check_number_dard = sequence_check_number_dard[1]
            for record in self:
                if vals.get('number_next_actual') and sequence_check_number_dard == record.id:
                    account_voucher_ids = self.env['account.voucher'].search([])
                    for account_voucher_id in account_voucher_ids:
                        account_voucher_id.check_seq = vals.get('number_next_actual')
            return res
        except ValueError:
            return res
