from openerp import models, fields, api, _
from datetime import datetime,date
from openerp.exceptions import Warning
from openerp.tools.translate import _
from openerp.exceptions import Warning
from lxml import etree
from openerp.osv.orm import setup_modifiers

class res_partner(models.Model):
    _inherit = 'res.partner'

    credit_days = fields.Integer(string='Credit Days')


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    def compute_payment_due_days(self, cr, uid, context=None):
        rec = self.search(cr, uid, [('state', '=', 'open')])
        for id in rec:
            date_due = self.browse(cr, uid, id, context).date_due
            if date_due:
                diff = datetime.now() - datetime.strptime(date_due, "%Y-%m-%d")
                days = diff.days
                self.write(cr,uid, id, {'due_days': days})

    @api.depends('date_invoice', 'date_due','state')
    def _compute_payment_due_days(self):
        for id in self:
            if id.state == "open":
                if not id.date_due:
                    raise Warning(_('Invoice Due Date not defined !!!'))
                diff = datetime.now() - datetime.strptime(id.date_due, "%Y-%m-%d")
                days = diff.days
                id.due_days = days

    @api.depends('date_invoice', 'date_due', 'state')
    def _compute_paid_after(self):
        for id in self:
            if id.state == "paid" and id.type=="out_invoice" and id.date_due:
                date_list = []
                for line_ids in id.payment_ids:
                    date_list.append(line_ids.date)
                if date_list:
                    last_paid_date = max(date_list)
                    diff = datetime.strptime(last_paid_date, "%Y-%m-%d") - datetime.strptime(id.date_due, "%Y-%m-%d")
                    days = diff.days
                    id.paid_after = days

    def _due_days_search(self, operator, value):
        if operator not in ('=', '!=', '<', '<=', '>', '>=', 'in', 'not in'):
            return []
        self._cr.execute("SELECT id FROM account_invoice WHERE due_days %s %s" %(operator, value))
        ids = [t[0] for t in self._cr.fetchall()]
        res = [('id', 'in', ids)]
        return res

    due_days = fields.Integer('Due Days',compute='_compute_payment_due_days', store=True, search='_due_days_search')
    paid_after = fields.Integer('Paid After',compute='_compute_paid_after', store=True)

class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        partner_obj = self.env['res.partner']
        invoice_obj = self.env['account.invoice']
        if self.partner_id.credit_days > 0:
            inv_row = invoice_obj.search_read(domain=[('partner_id', '=', self.partner_id.id),('state','in',['open'])], fields=['id','date_due','due_days'])
            for inv in inv_row:
                for names in self.user_id.groups_id:
                    if names.name != 'Financial Manager':
                        if self.partner_id.credit_days < inv['due_days']:
                            raise Warning(_('There are one or more invoices overdue for this customer, please contact finance manager for the same'))
                    else:
                        continue
        return super(sale_order, self).action_button_confirm()

