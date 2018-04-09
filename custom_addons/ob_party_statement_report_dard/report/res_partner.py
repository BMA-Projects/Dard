from openerp.osv import osv, fields
import re
from openerp import tools, api, SUPERUSER_ID


class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def _get_opening_balance(self, cr, uid, ids, from_date, to_date, context=None):
        balance = 0.00
        balance = self._get_debit_balance(cr, uid, ids, from_date, to_date, context=context) - self._get_credit_balance(cr, uid, ids, from_date, to_date, context=context)
        return balance


    def _get_credit_balance(self, cr, uid, ids, from_date, to_date, context=None):
        partner_ids = self.pool.get('res.partner').browse(cr, uid, ids)
        child_list = []
        for partner in partner_ids:
            for child in partner.child_ids:
                child_list.append(child.id)
        if 'type' in context:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('partner_id','in', ids + child_list), ('date_invoice', '<', from_date), ('state', '=', 'open'),
                ('type','in', context.get('type'))])
        else:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('partner_id','in', ids + child_list), ('date_invoice', '<', from_date), ('state', '=', 'open')])
        invoice_recs = self.pool.get('account.invoice').browse(cr, uid, invoice_ids)
        vals = {}
        balance = 0.00
        for invoice in invoice_recs:
            payment_total = 0.0
            if invoice.type == 'out_refund':
                for payment in invoice.payment_ids:
                    if payment.date < from_date and payment.credit:
                        payment_total += payment.credit
                vals[invoice.id] = payment_total
                balance += invoice.amount_total - payment_total
        return balance

    def _get_debit_balance(self, cr, uid, ids, from_date, to_date, context=None):
        partner_ids = self.pool.get('res.partner').browse(cr, uid, ids)
        child_list = []
        for partner in partner_ids:
            for child in partner.child_ids:
                child_list.append(child.id)
        if 'type' in context:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('partner_id','in', ids + child_list), ('date_invoice', '<', from_date), ('state', '=', 'open'),
                ('type','in', context.get('type'))])
        else:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('partner_id','in', ids + child_list), ('date_invoice', '<', from_date), ('state', '=', 'open')])
        invoice_recs = self.pool.get('account.invoice').browse(cr, uid, invoice_ids)
        vals = {}
        balance = 0.00
        for invoice in invoice_recs:
            payment_total = 0.0
            if invoice.type == 'out_invoice':
                for payment in invoice.payment_ids:
                    if payment.date < from_date and payment.credit:
                        payment_total += payment.credit
                vals[invoice.id] = payment_total
                balance += invoice.amount_total - payment_total
        return balance