from openerp import models, fields, api, _
from datetime import datetime,date
from openerp.exceptions import Warning
from openerp.tools.translate import _
from openerp.exceptions import Warning
from lxml import etree
from openerp.osv.orm import setup_modifiers


class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def _compute_limit(self):
        if self.id and self.allow_credit:
            inv_bal = 0
            invoice_obj = self.env['account.invoice']
            sale_obj = self.env['sale.order']
            sale_row = sale_obj.search([('partner_id', '=', self.id),('invoiced', '=', False),('state', 'not in', ['draft','cancel','done','proforma','proforma2','prepared'])])
            if sale_row:
                for r in sale_row:
                    inv_row = invoice_obj.search([('reference', '=', r['name']),('state','in',['draft'])])
                    if inv_row:
                        for inv in inv_row:
                            if inv and inv['state'] == 'draft':
                                inv_bal = inv_bal + inv['amount_total']
                    else:
                        inv_row = invoice_obj.search([('reference', '=', r['name']),('state','not in',['draft','proforma','proforma2'])])
                        if not inv_row:
                            inv_bal = inv_bal + r['amount_total']

            inv_row1 = invoice_obj.search([('partner_id', '=', self.id),('reference', '=', False),('state','in',['draft'])])
            if inv_row1:
                for inv1 in inv_row1:
                    if inv1 and inv1['state'] == 'draft':
                        inv_bal = inv_bal + inv1['amount_total']

            limit = (self.fix_credit_limit - self.credit) - inv_bal
            if limit < 0:
                self.avbl_limit = 0
            else:
                self.avbl_limit = limit
        else:
            self.avbl_limit = 0


    allow_credit = fields.Boolean('Allow Credit?', default=True, help="Check this option for allowing credit limit to customer.")
    allow_advance = fields.Boolean('Check Advance')
    credit_limit = fields.Float(string='Available Credit')
    avbl_advance = fields.Float(string='Available Advance')
    fix_credit_limit = fields.Float('Your Credit Limit')
    alert_after = fields.Float('Alert after (%)')
    limit_alert = fields.Float('Limit Alert After (%)')
    #'payment_history_ids': fields.one2many('partner.payment.history', "partner_id", "Payment History"),
    #avbl_credit_limit = fields.Float(string='Available Credit Limit',readonly=True,default=_default_avbl_credit_limit, track_visibility='always')
    avbl_limit = fields.Float(string='Available Limit',compute='_compute_limit',help="Avaliable credit limit + Advance Payment")

class account_invoice(models.Model):
    _inherit = 'account.invoice'

#    @api.one
#    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
#    def _compute_amount(self):
#        super(account_invoice, self)._compute_amount()
#        print "part limit===",self.partner_id.avbl_limit
#        print "amt===",self.amount_total
#
#        if self.partner_id.allow_credit and self.amount_total > self.avbl_credit_limit:
#            raise Warning(_('You dont have enough credit limit !!!'))


#    @api.multi
#    def write(self, vals):
#        print "valssssss>>>>>>>>>>>>",vals
#        res =
#        account_invoice_tax = self.env['account.invoice.tax']
#        compute_taxes = account_invoice_tax.compute(res)
#        total_amount = 0
#        for k,v in compute_taxes.items():
#            if v.get('tax_amount',False):
#                total_amount += v.get('tax_amount',False)
#        total_amount += res.amount_total
#        print "\ntotal tax,res.amount_total::::",total_tax,res.amount_total
#        return super(account_invoice, self).write(vals)

    @api.model
    def create(self, vals):
        res = super(account_invoice, self).create(vals)
        account_invoice_tax = self.env['account.invoice.tax']
        if res.id and vals.has_key('partner_id') and vals['partner_id'] and not vals.has_key('reference'):
            part_obj = self.env['res.partner'].browse(vals['partner_id'])
            if part_obj.allow_credit:
                adv = 0
                if part_obj.credit < 0:
                    adv = -(part_obj.credit)

                compute_taxes = account_invoice_tax.compute(res)
#                res.check_tax_lines(compute_taxes)
                total_amount = 0
                for k,v in compute_taxes.items():
                    if v.get('tax_amount',False):
                        total_amount += v.get('tax_amount',False)
                total_amount += res.amount_total
                #tax = self.button_reset_taxes()
                if 'avbl_credit_limit' in vals and total_amount > vals['avbl_credit_limit']:
                    limit = vals['avbl_credit_limit'] + part_obj.credit
                    #raise Warning(_('Your Advance Payment limit is %s  !!! \n And Credit Limit is %s'% (adv,limit)))
                    raise Warning(_('You dont have enough credit limit !!!'))

        else:
            vals['avbl_limit'] = 0

        return res


    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):

        res = super(account_invoice, self).onchange_partner_id(type, partner_id, date_invoice=date_invoice, payment_term=payment_term, partner_bank_id=partner_bank_id, company_id=company_id)
        if partner_id:
            part_obj = self.env['res.partner'].browse(partner_id)
            sale_obj = self.env['sale.order']
            if part_obj.allow_credit:
                total_amount = 0
                inv_bal = 0
                sale_row = sale_obj.search([('partner_id', '=', partner_id), ('invoiced', '=', False),('state', 'not in', ['draft','cancel','done','proforma','proforma2','prepared'])])
                if sale_row:
                    for r in sale_row:
                        inv_row = self.search([('reference', '=', r.name),('state','in',['draft'])])
                        if inv_row:
                            inv_bal = inv_bal + float(inv_row.amount_total)
                        else:
                            inv_row = self.search([('reference', '=', r['name']),('state','not in',['draft','proforma','proforma2'])])
                            if not inv_row:
                                inv_bal = inv_bal + r.amount_total

                inv_row = self.search([('partner_id', '=', partner_id),('reference', '=', False),('state','in',['draft'])])
                if inv_row:
                    for inv1 in inv_row:
                        inv_bal = inv_bal + inv1.amount_total
                limit = (part_obj.fix_credit_limit - part_obj.credit) - inv_bal
                if limit < 0:
                    res['value']['avbl_credit_limit'] = 0
                else:
                    res['value']['avbl_credit_limit'] = limit
            else:
                res['value']['avbl_credit_limit'] = 0
        return res

    avbl_credit_limit = fields.Float(string='Available Limit')
    #avbl_limit = fields.Float(string='Available Limit',compute='_compute_limit',store=True)


class sale_order(models.Model):
    _inherit = 'sale.order'

    has_limit = fields.Boolean('Has Limit', copy=False)
    by_pass = fields.Boolean('By Pass Limit', copy=False)
    
    credit_hold = fields.Char('Credit Status', readonly=True, copy=False)

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids,part=part    , context=context)
        if part:
            partner_info = self.pool.get('res.partner')
            invoice_obj = self.pool.get('account.invoice')
            part_obj = partner_info.browse(cr, uid, part, context=context)
            if part_obj.allow_credit:
                inv_bal = 0
                sale_row = self.search_read(cr, uid, domain=[('partner_id', '=', part),('invoiced', '=', False),('state', 'not in', ['draft','cancel','done','proforma','proforma2','prepared'])], fields=['id','name','amount_total'], context=context)
                if sale_row:
                    for r in sale_row:
                        inv_row = invoice_obj.search_read(cr, uid, domain=[('reference', '=', r['name']),('state','in',['draft'])], fields=['id','amount_total','residual','state'], context=context)
                        if inv_row:
                            for inv in inv_row:
                                if inv and inv['state'] == 'draft':
                                    inv_bal = inv_bal + inv['amount_total']
                        else:
                            inv_row = invoice_obj.search_read(cr, uid, domain=[('reference', '=', r['name']),('state','not in',['draft','proforma','proforma2'])], fields=['id','amount_total','residual','state'], context=context)
                            if not inv_row:
                                inv_bal = inv_bal + r['amount_total']


                inv_row1 = invoice_obj.search_read(cr, uid, domain=[('partner_id', '=', part),('reference', '=', False),('state','in',['draft'])], fields=['id','amount_total','residual','state'], context=context)
                if inv_row1:
                    for inv1 in inv_row1:
                        if inv1 and inv1['state'] == 'draft':
                            inv_bal = inv_bal + inv1['amount_total']

                limit = (part_obj.fix_credit_limit - part_obj.credit) - inv_bal
                if limit < 0:
                    res['value']['avbl_credit_limit'] = 0
                else:
                    res['value']['avbl_credit_limit'] = limit
            else:
                res['value']['avbl_credit_limit'] = 0
        return res

    def _compute_limit(self):
        #self.ensure_one()
        for res in self:
            if res.partner_id and res.partner_id.allow_credit:
                inv_bal = 0
                invoice_obj = self.env['account.invoice']
                sale_row = self.search([('partner_id', '=', res.partner_id.id),('invoiced', '=', False),('state', 'not in', ['draft','cancel','done','proforma','proforma2','prepared'])])
                if sale_row:
                    for r in sale_row:
                        inv_row = invoice_obj.search([('reference', '=', r['name']),('state','in',['draft'])])
                        if inv_row:
                            for inv in inv_row:
                                if inv and inv['state'] == 'draft':
                                    inv_bal = inv_bal + inv['amount_total']
                        else:
                            inv_row = invoice_obj.search([('reference', '=', r['name']),('state','not in',['draft','proforma','proforma2'])])
                            if not inv_row:
                                inv_bal = inv_bal + r['amount_total']

                inv_row1 = invoice_obj.search([('partner_id', '=', res.partner_id.id),('reference', '=', False),('state','in',['draft'])])
                if inv_row1:
                    for inv1 in inv_row1:
                        if inv1 and inv1['state'] == 'draft':
                            inv_bal = inv_bal + inv1['amount_total']

                limit = (res.partner_id.fix_credit_limit - res.partner_id.credit) - inv_bal
                if limit < 0:
                    res.limit = 0
                else:
                    res.avbl_limit = limit
            else:
                res.avbl_limit = 0




    def action_button_confirm(self, cr, uid, ids, context=None):
        if not context: context = {}
        partner_obj = self.pool.get('res.partner')
        invoice_obj = self.pool.get('account.invoice')
        sale_obj = self.browse(cr, uid, ids, context)
        partner_id = sale_obj.partner_id.id or False
        partner_info = partner_obj.browse(cr, uid, partner_id, context=context)
        if partner_id and partner_info.allow_credit:
            adv = 0
            if partner_info.credit < 0:
                adv = -(partner_info.credit)
            if sale_obj.amount_total > (sale_obj.avbl_limit):
                limit = sale_obj.avbl_limit + partner_info.credit
                if not sale_obj.by_pass:
                    if not context.get('from_action_sale_order_credit_limit_form'):
                        cr.execute("update sale_order set has_limit=True where id=%s", (ids[0],))
                        cr.commit()
                        if not context.get('by_pass', False):
                        #raise Warning(_('Your Advance Payment limit is %s  !!! \n And Credit Limit is %s'% (adv,limit)))
                            cr.execute("update sale_order set credit_hold='On Credit Hold' where id=%s", (ids[0],))
                            cr.commit()
                            raise Warning(_('You dont have enough credit limit !!!'))
                else:
                    cr.execute("update sale_order set credit_hold=NULL where id=%s", (ids[0],))
                    cr.commit()
                        
            cr.execute("update sale_order set has_limit=False where id=%s", (ids[0],))
            cr.commit()
            
        cr.execute("update sale_order set credit_hold=NULL where id=%s", (ids[0],))
        cr.commit()
            
#            allowed_limit = 0
#            adv = 0
#            if partner_info.credit < 0:
#                allowed_limit = sale_obj.avbl_credit_limit - partner_info.credit
#                adv = -(partner_info.credit)
#            else:
#                allowed_limit = sale_obj.avbl_credit_limit
#            if sale_obj.amount_total > allowed_limit:
#                raise Warning(_('Your Advance Payment limit is %s  !!! \n And Credit Limit is %s'% (adv,sale_obj.avbl_credit_limit)))
        return super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)

    avbl_credit_limit = fields.Float(string='Available Credit Limit',store=True)
    avbl_limit = fields.Float(string='Available Limit',compute='_compute_limit')
